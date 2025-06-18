import os
from pathlib import Path
from typing import List

from haystack.dataclasses import Document
from haystack.core.pipeline import Pipeline
from haystack.components.routers.file_type_router import FileTypeRouter
from haystack.components.converters.txt import TextFileToDocument
from haystack.components.converters.pypdf import PyPDFToDocument
from haystack.components.converters.markdown import MarkdownToDocument
from haystack.components.writers.document_writer import DocumentWriter
from haystack.components.joiners.document_joiner import DocumentJoiner
from haystack.components.preprocessors.document_cleaner import DocumentCleaner
from haystack.components.preprocessors.document_splitter import DocumentSplitter
from haystack.components.embedders import SentenceTransformersDocumentEmbedder

def add_docs_from_files(document_store, docs_dir: str = "documents") -> List[Document]:
    file_paths = [docs_dir / Path(name) for name in os.listdir(docs_dir)]

    indexing = Pipeline()
    indexing.add_component("router", FileTypeRouter(["text/plain", "application/pdf", "text/markdown"]))
    indexing.add_component("text_converter", TextFileToDocument())
    indexing.add_component("pdf_converter", PyPDFToDocument())
    indexing.add_component("markdown_converter", MarkdownToDocument())
    indexing.add_component("document_joiner", DocumentJoiner())
    indexing.add_component("cleaner", DocumentCleaner())
    indexing.add_component("splitter", DocumentSplitter(split_by="sentence", split_length=4))
    indexing.add_component("embedder", SentenceTransformersDocumentEmbedder(
        model="thenlper/gte-large", meta_fields_to_embed=['file_path']
    ))
    indexing.add_component("writer", DocumentWriter(document_store))

    indexing.connect("router.text/plain", "text_converter.sources")
    indexing.connect("router.application/pdf", "pdf_converter.sources")
    indexing.connect("router.text/markdown", "markdown_converter.sources")
    indexing.connect("text_converter", "document_joiner")
    indexing.connect("pdf_converter", "document_joiner")
    indexing.connect("markdown_converter", "document_joiner")

    indexing.connect("document_joiner", "cleaner")
    indexing.connect("cleaner", "splitter")
    indexing.connect("splitter", "embedder")
    indexing.connect("embedder", "writer")

    return indexing.run({"router": {"sources": file_paths}}, include_outputs_from={"embedder"})["embedder"]["documents"]