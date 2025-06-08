from typing import List, Optional
import torch
from PIL import Image
from transformers.utils.import_utils import is_flash_attn_2_available

from colpali_engine.models import ColQwen2_5, ColQwen2_5_Processor
import platform

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

    def embed_images(self, images: List[Image.Image], context_prompts: Optional[List[str]] = None) -> torch.Tensor:
        batch_images = self.processor.process_images(images, context_prompts).to(self.model.device)

        with torch.no_grad():
            image_embeddings = self.model(**batch_images)

        return image_embeddings

    def score(self, queries: List[str], image_embeddings: torch.Tensor) -> torch.Tensor:
        batch_queries = self.processor.process_queries(queries).to(self.model.device)

        with torch.no_grad():
            query_embeddings = self.model(**batch_queries)

        return self.processor.score_multi_vector(query_embeddings, image_embeddings)