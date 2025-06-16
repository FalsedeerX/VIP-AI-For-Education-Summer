from typing import List, Optional, Tuple, Union

import pdf2image
from pathlib import Path
from tqdm import tqdm
from PIL import Image

import torch
from torch.utils.data import DataLoader
from transformers.utils.import_utils import is_flash_attn_2_available

from colpali_engine.models import ColQwen2_5, ColQwen2_5_Processor
from colpali_engine.compression.token_pooling import HierarchicalTokenPooler
from colpali_engine.utils.torch_utils import get_torch_device

class ColPali:
    """
    Initialize the ColPali model for document retrieval and processing.
    Args:
        pool_factor (int, optional): Factor for hierarchical token pooling.
            If None, no pooling is applied. Defaults to 3.
        device (Union[str, torch.device], optional): Device to run the model on.
            If None, automatically detects the best available device. Defaults to None.
    """

    def __init__(self, pool_factor: Optional[int] = 3, device: Optional[Union[str, torch.device]] = None):
        self.device = device or get_torch_device()

        self.model = ColQwen2_5.from_pretrained(
            "vidore/colqwen2.5-v0.2",
            torch_dtype=torch.bfloat16,
            device_map=self.device,
            attn_implementation="flash_attention_2" if is_flash_attn_2_available() else None,
        ).eval()

        self.processor = ColQwen2_5_Processor.from_pretrained("vidore/colqwen2.5-v0.2", use_fast=True)

        self.pooler = HierarchicalTokenPooler() if pool_factor is not None else None
        self.pool_factor = pool_factor

    def embed_images(self, images: List[Image.Image], context_prompts: Optional[List[str]] = None, batch_size: int = 1) -> torch.Tensor:
        all_embeddings: List[torch.Tensor] = []

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
                image_embeddings = self.model(**batch_doc)

            all_embeddings.append(image_embeddings)

        embeddings_tensor = torch.cat(all_embeddings, dim=0)

        if self.pooler is not None:
            return self.pooler.pool_embeddings(embeddings_tensor, pool_factor=self.pool_factor)
        else:
            return embeddings_tensor

    def score(self, queries: List[str], image_embeddings: torch.Tensor) -> torch.Tensor:
        batch_queries = self.processor.process_queries(queries).to(self.device)

        with torch.inference_mode():
            query_embeddings = self.model(**batch_queries)

        return self.processor.score_multi_vector(query_embeddings, image_embeddings)

    def search(self, queries: List[str], image_embeddings: torch.Tensor, top_k: int = 3) -> torch.return_types.topk:
        scores = self.score(queries, image_embeddings.to(self.device)).squeeze()

        return torch.topk(scores, top_k)

    def create_plaid_index(self, image_embeddings: torch.Tensor) -> torch.Tensor:
        device = "cpu" if self.device in ("mps", torch.mps) else self.device

        return self.processor.create_plaid_index(image_embeddings, device=device)

    def plaid_search(self, queries: List[str], plaid_index: torch.Tensor, top_k: int = 3) -> List[List[Tuple[int, float]]]:
        batch_queries = self.processor.process_queries(queries).to(self.device)

        with torch.inference_mode():
            query_embeddings = self.model(**batch_queries)

        return self.processor.get_topk_plaid(query_embeddings, plaid_index, k=top_k, device=self.device)[0] # Remove extra dimension

    def embed_pdf(self, file_path: Path, batch_size: int = 1) -> Tuple[List[Image.Image], torch.Tensor]:
        print(f"Embedding {file_path.name}...")
        images = pdf2image.convert_from_path(file_path)

        return images, self.embed_images(images, batch_size=batch_size)