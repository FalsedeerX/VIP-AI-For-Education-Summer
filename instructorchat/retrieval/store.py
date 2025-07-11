from pymongo import MongoClient
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
import traceback
import certifi
import pymupdf4llm
import re
import uuid
import sys
import importlib
import logging
import os

from instructorchat.retrieval.colpali import ColPali


def format_meta(text: str, meta: dict) -> str:
    meta_text = " ".join(str(meta.get(key, "")) for key in ['folders', 'title', 'tags', 'timestamp'])
    return f"{meta_text} {text}"


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
        final_chunks.extend(split_long_chunk(chunk) if len(chunk) > max_length else [chunk])

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
        load_dotenv()

        # Connect to MongoDB
        # username = quote_plus("voquangtri2021")
        # password = quote_plus("Voquangtri123@")
        mongo = MongoClient(
            os.environ["MONGO_URL"],
            tls=True,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=5000
        )
        # Test the connection
        mongo.admin.command('ping')
        db = mongo["rag_database"]

        collection = db[collection_name]
        logger.info("Successfully connected to MongoDB Atlas")

        colpali = ColPali(device="cuda:0", quantized=True)

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

            all_texts = [format_meta(doc.content, doc.meta) for doc in module.docs]
            colpali.pool_factor = 5
            all_embeddings = colpali.embed_texts(all_texts, batch_size=8)

            for i, doc in enumerate(module.docs):
                logger.info(f"Processing document: {doc.meta['title']}")
                chunks = [doc.content]  # chunking not necessary for QA posts
                mongo_chunk_list = []

                mongo_chunk_list = [{
                    "chunk_id": str(uuid.uuid4()),
                    "chunk_text": all_texts[i],
                    "embedding": all_embeddings[i].tolist(),
                }]

                mongo_doc = {
                    "_id": str(uuid.uuid4()),
                    "filename": doc.meta['title'],
                    "file_type": "txt",
                    "file_path": f"KnowledgeBase/{sys.argv[1]}",
                    "folders": doc.meta['folders'],
                    "chunks": mongo_chunk_list,
                    "created_at": datetime.now(timezone.utc),
                    "metadata": doc.meta
                }
                collection.insert_one(mongo_doc)
                logger.info(f"Storing document with ID: {mongo_doc['_id']} and {len(mongo_chunk_list)} chunk(s) in collection '{collection.name}'")

        elif ext == 'pdf':
            img_save_dir = Path(f"KnowledgeBase/pdf2img/{module_name}")
            img_save_dir.mkdir(parents=True, exist_ok=True)

            md_pages = pymupdf4llm.to_markdown(f"KnowledgeBase/{module_name}.pdf", page_chunks=True)
            docs_dir = "./KnowledgeBase"
            path = Path(docs_dir) / f"{module_name}.pdf"
            images, embeddings = colpali.embed_pdf(path)
            infos = [{'text': p1['text'], 'image': p2, 'embed': p3} for p1, p2, p3 in zip(md_pages, images, embeddings)]

            for page_num, info in enumerate(infos, start=1):

                meta = {
                    "title": f"{module_name}_{page_num}",
                    "folders": ['FOO', 'BAR'],
                    "timestamp": datetime.now(timezone.utc),
                    "tags": ['FOO', 'BAR']
                }  # TODO: Make user give meta

                image_path = img_save_dir / f"{meta['title']}.png"
                info['image'].save(image_path)

                logger.info(f"Processing document: {meta['title']}")

                doc = clean_text(info['text'])
                chunks = chunk_text(doc)
                mongo_chunk_list = []

                for ch in chunks:
                    # embedding = embed_text(ch, meta)
                    embedding = None

                    mongo_chunk = {
                        "chunk_id": str(uuid.uuid4()),
                        "chunk_text": ch,
                        "embedding": embedding,
                    }
                    mongo_chunk_list.append(mongo_chunk)

                mongo_doc = {
                    "_id": str(uuid.uuid4()),
                    "filename": f"{module_name}",
                    "file_type": "pdf",
                    "file_path": f"KnowledgeBase/{module_name}.pdf",
                    "image_name": meta['title'],
                    "image_path": str(image_path),
                    "embedding": info['embed'].tolist(),
                    "folders": meta['folders'],
                    "chunks": mongo_chunk_list,
                    "created_at": datetime.now(timezone.utc),
                    "metadata": meta
                }
                collection.insert_one(mongo_doc)
                logger.info(f"Storing document with ID: {mongo_doc['_id']} and {len(mongo_chunk_list)} chunk(s) in collection '{collection.name}'")

        else:
            return False, f"Unsupported file type '.{ext}'"

        return True, "Successfully stored all documents"

    except Exception as e:
        logger.error(traceback.format_exc())
        error_msg = f"Error during document storage: {str(e)}"
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
