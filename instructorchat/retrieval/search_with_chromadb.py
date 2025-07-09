from pymongo import MongoClient
# from urllib.parse import quote_plus
from typing import List, Dict, Final
import argparse
import time
import openai
import logging
import torch

from instructorchat.retrieval.colpali import ColPali

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Define available folders for classification
AVAILABLE_FOLDERS: Final[List[str]] = ['project', 'logistics', 'course_content', 'exam', 'hw1', 'hw2', 'hw3', 'hw4', 'hw5',
                                       'hw6', 'hw7', 'hw8', 'hw9', 'hw10', 'other']
INCLUDE: Final[int] = 1

# Connect to MongoDB Atlas
# username = quote_plus("voquangtri2021")
# password = quote_plus("Voquangtri123@")
mongo = MongoClient("mongodb+srv://rag:pass@test-aie.dadfdhw.mongodb.net/?retryWrites=true&w=majority&appName=test-aie")
db = mongo["rag_database"]
collection = db["ece20875"]

# Set up ColPali class
colpali = ColPali(device="cuda:0", quantized=True)

async def classify_query(query: str, api_key: str) -> str:
    """Classify the query into one of the available folders using GPT-4-mini."""
    try:
        client = openai.AsyncOpenAI(api_key=api_key)

        # Create a prompt for classification
        system_prompt = f"""You are a query classifier. Your task is to classify the user's query into one of these folders: {', '.join(AVAILABLE_FOLDERS)}.
        Choose the most relevant folder based on the query content. If the query is about homework, choose the specific homework folder (hw1-hw10).
        If the query is about exams, use 'exam'. If it's about course logistics, use 'logistics'. If it's about the project, use 'project'.
        If it's about course material, such as questions about data science, Python, probability, statistics or other relevant topics, use 'course_content'.
        For anything else, use 'other'. Respond with ONLY the folder name, nothing else."""

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.1,  # Low temperature for more consistent classification
        )

        folder = response.choices[0].message.content.strip().lower()

        # Validate the folder is in our list
        if folder not in AVAILABLE_FOLDERS:
            return 'other'

        return folder

    except Exception as e:
        logger.error(f"Error in query classification: {str(e)}")
        return 'other'

async def retrieve_relevant_context(query: str, api_key: str) -> List[Dict]:
    """Retrieve relevant context for the query using classification and vector search."""
    try:
        # First classify the query
        folder = await classify_query(query, api_key)
        logger.info(f"Query classified into folder: {folder}")

        # Then use vector search to get relevant content
        results = vector_search(folder, query, top_k=5)

        # Format the results for context
        context = []
        for doc in results:
            context.append({
                "title": doc["filename"],
                "content": doc["chunk"]["chunk_text"],
                "metadata": doc["metadata"]
            })

        return context

    except Exception as e:
        logger.error(f"Error in context retrieval: {str(e)}")
        return []


def vector_search(folder, query, top_k=3):

    # explain, add pdf later
    filtered_docs = collection.find({"folders": folder})

    docs_for_chroma = []
    for doc in filtered_docs:
        for chunk in doc['chunks']:
            docs_for_chroma.append({
                "id": chunk['chunk_id'],
                "title": doc['filename'],
                "embedding": chunk['embedding'] if doc['file_type'] == "txt" else doc['embedding']
            })

    ids = [d["id"] for d in docs_for_chroma]
    embeddings = [torch.tensor(d["embedding"]).to(dtype=torch.bfloat16) for d in docs_for_chroma]
    top_k = colpali.search([query], embeddings, top_k=3)
    scores, indices = top_k.values, top_k.indices
    matching_ids = [ids[int(i)] for i in indices[0]]
    matching_scores = [float(s) for s in scores[0]]

    found_chunks = []
    for chunk_id, score in zip(matching_ids, matching_scores):
        doc = collection.find_one(
            {"chunks.chunk_id": chunk_id},
            {"chunks.$": INCLUDE, "filename": INCLUDE, "metadata": INCLUDE, "file_type": INCLUDE, "image_path": INCLUDE}
        )
        if doc and "chunks" in doc:
            found_chunks.append({
                "chunk_id": chunk_id,
                "score": score,
                "filename": doc["filename"],
                "metadata": doc["metadata"],
                "chunk": doc["chunks"][0],
                "image_dir": doc["image_path"] if doc['file_type'] == "pdf" else None
            })

    return found_chunks


# Run this for demo
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=str, help="Folder to search")
    args = parser.parse_args()

    print(f"\nSearching folder: {args.folder}\n")
    print("Type your query below. Type 'exit' to quit.\n")

    while True:
        query = input("Query: ").strip()
        if query.lower() in ["exit", "quit"]:
            print("Exiting.")
            break

        start = time.time()
        results = vector_search(args.folder, query)
        end = time.time()
        print(f"\nTop results for: \"{query}\"\n")
        for i, doc in enumerate(results, 1):
            chunk = doc["chunk"]
            print(f"[{i}] Doc: {doc['filename']} | Chunk ID: {chunk.get('chunk_id', 'N/A')}")
            print(chunk.get("chunk_text", "[No text found]"))
            print("-" * 80)
        print(f"Time: {(end - start)*1000:.1f} ms")
