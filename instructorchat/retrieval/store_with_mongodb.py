from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from datetime import datetime, timezone
import pymupdf4llm
import re
import uuid
import sys
import importlib
import logging
from urllib.parse import quote_plus
import certifi
from pathlib import Path
from haystack.dataclasses import Document  # Updated import for Haystack 2.x

# Initialize the embedder globally
chunk_embedder = SentenceTransformer("thenlper/gte-large")

def embed_text(text, meta):
    meta_text = " ".join(str(meta.get(key, "")) for key in ['folders', 'title', 'tags', 'timestamp'])
    embedding_input = f"{text} {meta_text}"
    embedding = chunk_embedder.encode(embedding_input).tolist()
    return embedding


def clean_text(md_text):
    lines = md_text.splitlines()
    fixed_lines = []
    i = 0

    while i < len(lines):
        current = lines[i].strip()
        
        # Look for break between blocks
        if current == "" and i > 0 and i < len(lines) - 1:
            prev = lines[i - 1].strip()
            next_ = lines[i + 1].strip()

            # Look for mid-sentence break
            if re.search(r'[a-zA-Z]$', prev) and re.match(r'^[a-z]', next_):
                # Merge prev + next
                combined = prev + " " + next_
                fixed_lines[-1] = combined  
                i += 2
                continue
        
        fixed_lines.append(current)
        i += 1

    return "\n".join(fixed_lines)


def chunk_text(text, min_length=300, max_length=1000):

    delimiter_pattern = r'(?:\n{2,}|#+\s|(?<=\n)\*\*[^\n]+\*\*(?=\n))'
    raw_chunks = re.split(delimiter_pattern, text)
    
    matches = list(re.finditer(delimiter_pattern, text))
    for i in range(len(matches)):
        delimiter = text[matches[i].start():matches[i].end()]
        raw_chunks[i+1] = delimiter + raw_chunks[i+1] if i+1 < len(raw_chunks) else raw_chunks[i+1]

    final_chunks = []
    buffer = ""
    
    def split_long_chunk(chunk):
        # Try to split by sentence ends if possible
        sentences = re.split(r'(?<=[.?!])\s+', chunk)
        chunks = []
        temp = ""
        for sentence in sentences:
            if len(temp) + len(sentence) < max_length:
                temp += sentence + " "
            else:
                if temp.strip():
                    chunks.append(temp.strip())
                temp = sentence + " "
        if temp.strip():
            chunks.append(temp.strip())
        return chunks

    for part in raw_chunks:
        part = part.strip()
        if not part:
            continue
        if len(buffer) + len(part) < min_length:
            buffer += " " + part
        else:
            if buffer:
                chunk = buffer.strip()
                if len(chunk) > max_length:
                    final_chunks.extend(split_long_chunk(chunk))
                else:
                    final_chunks.append(chunk)
                buffer = ""
            if len(part) > max_length:
                final_chunks.extend(split_long_chunk(part))
            else:
                buffer = part

    if buffer.strip():
        chunk = buffer.strip()
        if len(chunk) > max_length:
            final_chunks.extend(split_long_chunk(chunk))
        else:
            final_chunks.append(chunk)
    
    return final_chunks

def store_documents(file_path: str, collection_name: str = "ece20875") -> tuple[bool, str]:
    """
    Store documents from a file into MongoDB.
    
    Args:
        file_path (str): Path to the file to store (must be in KnowledgeBase directory)
        collection_name (str): Name of the MongoDB collection to store in (default: "ece20875")
    
    Returns:
        tuple[bool, str]: (success status, message)
    """
    # Simple logger setup
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)

    try:
        # Connect to MongoDB
        username = quote_plus("voquangtri2021")
        password = quote_plus("Voquangtri123@")
        mongo = MongoClient(
            f"mongodb+srv://{username}:{password}@test.funii81.mongodb.net/?retryWrites=true&w=majority&appName=Test",
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000
        )
        # Test the connection
        mongo.admin.command('ping')
        db = mongo["rag_database"]
        collection = db[collection_name]
        logger.info("Successfully connected to MongoDB Atlas")
        logger.info(f"Embedding model loaded: thenlper/gte-large")

        # Process file
        file = file_path.split(".")
        if len(file) != 2:
            return False, "Invalid file path format"
            
        module_name = file[0]
        ext = file[-1]

        if ext == 'py':
            # Import the module
            try:
                # Add retrieval directory to path if needed
                retrieval_path = Path(__file__).parent
                if str(retrieval_path) not in sys.path:
                    sys.path.append(str(retrieval_path))
                module = importlib.import_module(f"KnowledgeBase.{module_name}")
            except ImportError as e:
                return False, f"Failed to import module: {str(e)}"
                
            logger.info(f"Beginning the storing of {module_name}...")

            if not hasattr(module, 'docs'):
                return False, "Module must contain a 'docs' variable with Haystack Documents"

            for doc in module.docs:
                logger.info(f"Processing document: {doc.meta['title']}")
                chunks = [doc.content]  # chunking not necessary for QA posts
                mongo_chunk_list = []
                
                for ch in chunks:
                    embedding = embed_text(ch, doc.meta)
                    mongo_chunk = {
                        "chunk_id": str(uuid.uuid4()),
                        "chunk_text": ch,
                        "embedding": embedding,
                    }
                    mongo_chunk_list.append(mongo_chunk)

                mongo_doc = {
                    "_id": str(uuid.uuid4()),
                    "filename": doc.meta['title'],
                    "file_type": "txt",
                    "file_path": f"KnowledgeBase/{file_path}",
                    "folders": doc.meta['folders'],
                    "chunks": mongo_chunk_list,
                    "created_at": datetime.now(timezone.utc),
                    "metadata": doc.meta
                }
                collection.insert_one(mongo_doc)
                logger.info(f"Stored document with ID: {mongo_doc['_id']} and {len(mongo_chunk_list)} chunk(s) in collection '{collection.name}'")

        elif ext == 'pdf':
            try:
                md_text = pymupdf4llm.to_markdown(f"{module_name}.pdf")
            except Exception as e:
                return False, f"Failed to process PDF: {str(e)}"
                
            meta = {
                "title": module_name,
                "folders": ['FOO', 'BAR'],
                "timestamp": datetime.now(timezone.utc),
                "tags": ['FOO', 'BAR']
            }

            logger.info(f"Processing document: {meta['title']}")
            doc = clean_text(md_text)
            chunks = chunk_text(doc)
            mongo_chunk_list = []

            for ch in chunks:
                embedding = embed_text(ch, meta)
                mongo_chunk = {
                    "chunk_id": str(uuid.uuid4()),
                    "chunk_text": ch,
                    "embedding": embedding,
                }
                mongo_chunk_list.append(mongo_chunk)

            mongo_doc = {
                "_id": str(uuid.uuid4()),
                "filename": meta['title'],
                "file_type": "pdf",
                "file_path": f"KnowledgeBase/{file_path}",
                "folders": meta['folders'],
                "chunks": mongo_chunk_list,
                "created_at": datetime.now(timezone.utc),
                "metadata": meta
            }
            collection.insert_one(mongo_doc)
            logger.info(f"Stored document with ID: {mongo_doc['_id']} and {len(mongo_chunk_list)} chunk(s) in collection '{collection.name}'")

        else:
            return False, f"Unsupported file type '.{ext}'"

        return True, "Successfully stored all documents"

    except Exception as e:
        error_msg = f"Error during document storage: {str(e)}"
        logger.error(error_msg)
        return False, error_msg

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python store_with_mongodb.py <file>")
        sys.exit(1)
        
    success, message = store_documents(sys.argv[1])
    if not success:
        print(f"Error: {message}")
        sys.exit(1)
    print(message)