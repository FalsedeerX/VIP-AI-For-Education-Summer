from typing import List, Optional, Tuple
import torch
from PIL import Image
from transformers.utils.import_utils import is_flash_attn_2_available
import platform
from colpali_engine.models import ColQwen2_5, ColQwen2_5_Processor
import pdf2image
from pathlib import Path

class ColPali():
    def __init__(self):
        device = "mps" if platform.system() == "Darwin" and torch.backends.mps.is_available() else "cuda:0"

        self.model = ColQwen2_5.from_pretrained(
            "vidore/colqwen2.5-v0.2",
            torch_dtype=torch.bfloat16,
            device_map=device,
            attn_implementation="flash_attention_2" if is_flash_attn_2_available() else None,
        ).eval()

        self.processor = ColQwen2_5_Processor.from_pretrained("vidore/colqwen2.5-v0.2", use_fast=True)

    def embed_images(self, images: List[Image.Image], context_prompts: Optional[List[str]] = None, batch_size: int = 1) -> torch.Tensor:
        all_embeddings = []

        for i in range(0, len(images), batch_size):
            batch_imgs = images[i:i + batch_size]
            batch_prompts = context_prompts[i:i + batch_size] if context_prompts else None
            batch_images = self.processor.process_images(batch_imgs, batch_prompts).to(self.model.device)

            with torch.inference_mode():
                image_embeddings = self.model(**batch_images)

            all_embeddings.append(image_embeddings)
            print(f"Embedded {i + batch_size}/{len(images)} images")

        return torch.cat(all_embeddings, dim=0)

    def score(self, queries: List[str], image_embeddings: torch.Tensor) -> torch.Tensor:
        batch_queries = self.processor.process_queries(queries).to(self.model.device)

        with torch.inference_mode():
            query_embeddings = self.model(**batch_queries)

        return self.processor.score_multi_vector(query_embeddings, image_embeddings)

    def search(self, query: str, image_embeddings: torch.Tensor, top_k: int = 3) -> torch.return_types.topk:
        scores = self.score([query], image_embeddings).squeeze()

        return torch.topk(scores, top_k)

    def embed_pdf(self, file_path: Path, batch_size: int = 1) -> Tuple[List[Image.Image], torch.Tensor]:
        print(f"Embedding {file_path.name}...")
        images = pdf2image.convert_from_path(file_path)

        return images, self.embed_images(images, batch_size=batch_size)