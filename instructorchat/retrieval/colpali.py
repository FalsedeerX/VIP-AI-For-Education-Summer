from typing import List, Optional, Tuple

import pdf2image
from pathlib import Path
from tqdm import tqdm
from PIL import Image
import os
import warnings

import torch
from torch.utils.data import DataLoader
from transformers.utils.import_utils import is_flash_attn_2_available
from transformers.utils.quantization_config import BitsAndBytesConfig

from colpali_engine.models import ColQwen2_5, ColQwen2_5_Processor
from colpali_engine.compression.token_pooling import HierarchicalTokenPooler
from colpali_engine.utils.torch_utils import get_torch_device

from rerankers import Reranker

from fast_plaid.search.fast_plaid import FastPlaid

from instructorchat.utils import images_to_base64


class ColPali:
    """
    Initialize the ColPali model for document retrieval and processing.
    Args:
        pool_factor (int, optional): Factor for hierarchical token pooling.
            If None, no pooling is applied. Defaults to 3.
        device (Union[str, torch.device], optional): Device to run the model on.
            If None, automatically detects the best available device. Defaults to None.
    """

    def __init__(self, pool_factor: Optional[int] = 3, device: Optional[str] = None, quantized: bool = False):
        self.device = torch.device(device) if device is not None else torch.device(get_torch_device())

        if quantized:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,  # Set False for 8-bit
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16
            )

            self.model = ColQwen2_5.from_pretrained(
                "vidore/colqwen2.5-v0.2",
                torch_dtype=torch.bfloat16,
                device_map=self.device,
                attn_implementation="flash_attention_2" if is_flash_attn_2_available() else None,
                quantization_config=bnb_config,
            ).eval()
        else:
            self.model = ColQwen2_5.from_pretrained(
                "vidore/colqwen2.5-v0.2",
                torch_dtype=torch.bfloat16,
                device_map=self.device,
                attn_implementation="flash_attention_2" if is_flash_attn_2_available() else None,
            ).eval()

        self.processor = ColQwen2_5_Processor.from_pretrained("vidore/colqwen2.5-v0.2", use_fast=True)

        self.pooler = HierarchicalTokenPooler() if pool_factor is not None else None
        self.pool_factor = pool_factor

    def embed_images(
            self,
            images: List[Image.Image],
            context_prompts: Optional[List[str]] = None,
            batch_size: int = 1
        ) -> List[torch.Tensor]:

        embeddings: List[torch.Tensor] = []

        dataloader = DataLoader(
            dataset=range(len(images)),
            batch_size=batch_size,
            shuffle=False,
            collate_fn=lambda x: self.processor.process_images(
                [images[i] for i in x],
                [context_prompts[i] for i in x] if context_prompts is not None else None
            )
        )

        for batch_doc in tqdm(dataloader):
            with torch.inference_mode():
                batch_doc = {k: v.to(self.device) for k, v in batch_doc.items()}
                image_embeddings: torch.Tensor = self.model(**batch_doc)

            embeddings.extend(list(torch.unbind(image_embeddings.cpu())))

        if self.pooler is not None:
            return self.pooler.pool_embeddings(embeddings, pool_factor=self.pool_factor)
        else:
            return embeddings

    def embed_texts(self, texts: List[str], batch_size: int = 4) -> List[torch.Tensor]:
        embeddings = []

        dataloader = DataLoader(
            dataset=texts,
            batch_size=batch_size,
            shuffle=False,
            collate_fn=lambda batch_texts: self.processor(
                text=batch_texts,
                return_tensors="pt",
                padding=True,
                truncation=True,
            )
        )

        for batch_inputs in tqdm(dataloader):
            try:
                torch.cuda.reset_peak_memory_stats()
                with torch.inference_mode():
                    batch_inputs = {k: v.to(self.device) for k, v in batch_inputs.items()}
                    text_embeddings = self.model(**batch_inputs)  # shape: [batch, seq_len, dim]
                    attention_mask = batch_inputs["attention_mask"]  # shape: [batch, seq_len]

                peak = torch.cuda.max_memory_allocated() / 1e6
                print(f"Peak GPU memory: {peak:.2f} MB")

                # Trim padded tokens per sample
                for emb, mask in zip(text_embeddings, attention_mask):
                    num_tokens = mask.sum().item()
                    trimmed = emb[-num_tokens:].cpu()  # shape: [num_tokens, dim]
                    embeddings.append(trimmed)

            except torch.cuda.OutOfMemoryError:
                print("OOM on batch — skipping text batch.")
                continue

        # After full loop
        if self.pooler is not None:
            return self.pooler.pool_embeddings(embeddings, pool_factor=self.pool_factor)
        else:
            return embeddings

    def score(self, queries: List[str], image_embeddings: List[torch.Tensor]) -> torch.Tensor:
        batch_queries = self.processor.process_queries(queries).to(self.device)

        with torch.inference_mode():
            query_embeddings = self.model(**batch_queries)

        return self.processor.score_multi_vector(query_embeddings, image_embeddings, device=self.device)

    def search(self, queries: List[str], image_embeddings: List[torch.Tensor], top_k: int = 3) -> torch.return_types.topk:
        scores = self.score(queries, image_embeddings)

        return torch.topk(scores, top_k)

    def create_plaid_index(self, image_embeddings: List[torch.Tensor]) -> FastPlaid:
        device = "cpu" if self.device in ("mps", torch.mps) else self.device

        return self.processor.create_plaid_index(image_embeddings, device=device)

    def plaid_search(self, queries: List[str], plaid_index: FastPlaid, top_k: int = 3) -> List[List[Tuple[int, float]]]:
        batch_queries = self.processor.process_queries(queries).to(self.device)

        with torch.inference_mode():
            query_embeddings = self.model(**batch_queries)

        return self.processor.get_topk_plaid(query_embeddings, plaid_index, k=top_k, device=self.device)[0] # Remove extra dimension

    def embed_pdf(
        self,
        file_path: Path,
        batch_size: int = 1,
        img_max_width: int = 512,
        img_max_height: int = 512
    ) -> tuple[List[Image.Image], torch.Tensor]:
        print(f"Converting {file_path.name} to images...")
        images = pdf2image.convert_from_path(file_path)

        images = self.resize_images(images, max_width=img_max_width, max_height=img_max_height)

        print(f"Embedding {file_path.name}...")
        return images, self.embed_images(images, batch_size=batch_size)

    def resize_images(self, images: List[Image.Image], max_width: int = 512, max_height: int = 512) -> List[Image.Image]:
        resized = []

        for img in images:
            img_resized = img.copy()
            img_resized.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            resized.append(img_resized)

        return resized


class InMemoryColPali:
    def __init__(self, docs_dir: str = "documents", use_fast_plaid: bool = True, reranking: bool = False) -> None:
        self.colpali = ColPali()

        if (use_fast_plaid and
                not (self.colpali.device == torch.cuda or (isinstance(self.colpali.device, str) and "cuda" in self.colpali.device))):
            warnings.warn(f"CUDA is recommended for FastPlaid. Current device is {self.colpali.device}")

        if reranking:
            self.reranker = Reranker(
                "monovlm",
                device=self.colpali.device,
                attention_implementation="flash_attention_2" if is_flash_attn_2_available() else None
            )

        self.use_fast_plaid = use_fast_plaid
        self.index(docs_dir)

    def index(self, docs_dir: str = "documents") -> None:
        file_paths = []

        for name in os.listdir(docs_dir):
            file_path = Path(docs_dir) / name
            if file_path.suffix == ".pdf":
                file_paths.append(file_path)

        self.embeddings: List[torch.Tensor] = []
        self.images: List[Image.Image] = []

        for pdf_file in file_paths:
            images, embeddings = self.colpali.embed_pdf(pdf_file)
            self.images.extend(images)
            self.embeddings.extend(embeddings)

        if self.use_fast_plaid:
            self.plaid_index = self.colpali.create_plaid_index(self.embeddings)

    def search(self, query: str, top_k: int = 3) -> List[Image.Image]:
        if self.use_fast_plaid:
            search_results = self.colpali.plaid_search([query], self.plaid_index, top_k)[0]

            result_images: List[Image.Image] = []

            for img_idx, _ in search_results:
                result_images.append(self.images[img_idx])

            return result_images
        else:
            search_results = self.colpali.search([query], self.embeddings, top_k)

            result_images: List[Image.Image] = []

            for img_idx in search_results.indices.squeeze():
                result_images.append(self.images[img_idx])

            return result_images

    def rerank(self, query: str, images: List[Image.Image], top_k: int = 1) -> List[Image.Image]:
        base64_list = images_to_base64(images)

        results = self.reranker.rank(query, base64_list)

        return [images[result.doc_id] for result in results.top_k(top_k)]
