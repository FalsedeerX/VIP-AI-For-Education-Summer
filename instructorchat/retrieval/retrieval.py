# for embedding queries and documents, then retrieve relevant docs using an LLM retriever.
# at the moment, i'm thinking of adding these docs as 'context' to gpt-4o's input. But this seems to be costful in the future after scaling, so I'm not sure if openai or other
# companies offer a different service for this RAG system. 
# also, i want to research and find other architecture for better designing our RAG system.

from instructorchat.retrieval.documents import imported_docs, evals
from instructorchat.retrieval.scoring import texas_hybrid_score

from haystack import Pipeline, Document
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.builders import PromptBuilder
from haystack_integrations.components.generators.ollama import OllamaGenerator



class Retrieval:
    def __init__(self):
        self.docs = imported_docs
        self.spare_pipeline = None
        self.dense_pipeline = None
        self.lmbda = 0.9

    def populate_pipelines(self) -> None:
        document_cleaner = DocumentCleaner()
        document_splitter = DocumentSplitter(split_by="sentence", split_length=4)
        document_embedder = SentenceTransformersDocumentEmbedder(
            model="thenlper/gte-large", meta_fields_to_embed=['folders', 'title', 'tags', 'timestamp']
        )

        document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")
        document_writer = DocumentWriter(document_store=document_store, policy=DuplicatePolicy.OVERWRITE)

        indexing_pipeline = Pipeline()
        indexing_pipeline.add_component("cleaner", document_cleaner)
        indexing_pipeline.add_component("splitter", document_splitter)
        indexing_pipeline.add_component("embedder", document_embedder)
        indexing_pipeline.add_component("writer", document_writer)

        indexing_pipeline.connect("cleaner", "splitter")
        indexing_pipeline.connect("splitter", "embedder")
        indexing_pipeline.connect("embedder", "writer")

        indexing_pipeline.run({"cleaner": {"documents": self.docs}})

        self.dense_pipeline = Pipeline()
        self.dense_pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder(model="thenlper/gte-large"))
        self.dense_pipeline.add_component("retriever_with_embeddings",
            InMemoryEmbeddingRetriever(document_store=document_store, scale_score=True, top_k=10)
        )
        self.dense_pipeline.connect("text_embedder", "retriever_with_embeddings")

        self.spare_pipeline = Pipeline()
        self.spare_pipeline.add_component("retriever", InMemoryBM25Retriever(document_store=document_store, scale_score=True, top_k=10))

    def retrieve_documents(self, query: str, lmbda: float = 0.9) -> dict:
        if not self.spare_pipeline or not self.dense_pipeline:
            self.populate_pipelines()

        dense_candidates = self.dense_pipeline.run({"text_embedder": {"text": query}})
        sparse_candidates = self.spare_pipeline.run({"retriever": {"query": query}})
        score_dict = texas_hybrid_score(dense_candidates, sparse_candidates, lmbda)

        top_document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")
        top_docs = [d for d in self.docs if d.meta['title'] in list(score_dict.keys())[:10]]

        # clean top documents
        top_document_cleaner = DocumentCleaner()
        top_document_splitter = DocumentSplitter(split_by="sentence", split_length=1)
        top_document_embedder = SentenceTransformersDocumentEmbedder(
            model="thenlper/gte-large", meta_fields_to_embed=['folders', 'title', 'tags', 'timestamp']
        )
        top_document_writer = DocumentWriter(document_store=top_document_store, policy=DuplicatePolicy.OVERWRITE)

        top_indexing_pipeline = Pipeline()
        top_indexing_pipeline.add_component("cleaner", top_document_cleaner)
        top_indexing_pipeline.add_component("splitter", top_document_splitter)
        top_indexing_pipeline.add_component("embedder", top_document_embedder)
        top_indexing_pipeline.add_component("writer", top_document_writer)

        top_indexing_pipeline.connect("cleaner", "splitter")
        top_indexing_pipeline.connect("splitter", "embedder")
        top_indexing_pipeline.connect("embedder", "writer")
        # process top documents
        top_indexing_pipeline.run({"cleaner": {"documents": top_docs}})

        layer_dense_pipeline = Pipeline()
        layer_dense_pipeline.add_component("text_embedder", SentenceTransformersTextEmbedder(model="thenlper/gte-large"))
        layer_dense_pipeline.add_component("retriever_with_embeddings",
            InMemoryEmbeddingRetriever(document_store=top_document_store, scale_score=True, top_k=3))
        
        layer_dense_pipeline.connect("text_embedder", "retriever_with_embeddings")

        doc_results = layer_dense_pipeline.run({"text_embedder": {"text": query}})

        retrieved_documents = doc_results["retriever_with_embeddings"]["documents"]

        return {
            #"retrieval" : retrieved_documents,
            "contents" : [desc.content for desc in retrieved_documents],
            "titles" : [desc.meta["title"] for desc in retrieved_documents],
            "tags" : [desc.meta["tags"] for desc in retrieved_documents],
            "folders" : [desc.meta["folders"] for desc in retrieved_documents]
        }

    def create_prompt_with_retrievals(self, query: str, contexts: str) -> str:
        prompt = f"""
            Use the following context to answer the question:
            Context:
            {contexts}

            Question:
            {query}
        """
        return prompt
