import os
from pathlib import Path
from typing import Optional

from haystack.core.pipeline import Pipeline
from haystack.components.routers.file_type_router import FileTypeRouter
from haystack.components.converters.txt import TextFileToDocument
from haystack.components.converters.pypdf import PyPDFToDocument
from haystack.components.converters.markdown import MarkdownToDocument
from haystack.components.writers.document_writer import DocumentWriter
from haystack.components.joiners.document_joiner import DocumentJoiner
from haystack_integrations.document_stores.chroma import ChromaDocumentStore

def build_document_store(docs_dir: str = "documents", persistent_path: Optional[str] = None) -> ChromaDocumentStore:
    file_paths = [docs_dir / Path(name) for name in os.listdir(docs_dir)]

    document_store = ChromaDocumentStore(persist_path=persistent_path)

    indexing = Pipeline()
    indexing.add_component("router", FileTypeRouter(["text/plain", "application/pdf", "text/markdown"]))
    indexing.add_component("text_converter", TextFileToDocument())
    indexing.add_component("pdf_converter", PyPDFToDocument())
    indexing.add_component("markdown_converter", MarkdownToDocument())
    indexing.add_component("document_joiner", DocumentJoiner())
    indexing.add_component("writer", DocumentWriter(document_store))

    indexing.connect("router.text/plain", "text_converter.sources")
    indexing.connect("router.application/pdf", "pdf_converter.sources")
    indexing.connect("router.text/markdown", "markdown_converter.sources")
    indexing.connect("text_converter", "document_joiner")
    indexing.connect("pdf_converter", "document_joiner")
    indexing.connect("markdown_converter", "document_joiner")

    indexing.connect("document_joiner", "writer")

    indexing.run({"router": {"sources": file_paths}})

    return document_store

if __name__ == "__main__":
    print(build_document_store().search(["How do you make a histogram?"], 3))