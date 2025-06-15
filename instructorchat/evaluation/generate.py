import argparse
from pathlib import Path
import os
from PIL import Image
from typing import List, Tuple
import base64
import json
from io import BytesIO

from deepeval.synthesizer import Synthesizer
from openai import OpenAI
import pdf2image
from pydantic import BaseModel

def generate_from_docs(docs_dir: str = "documents", save_dir: str = "eval_data") -> None:
    """
    Generates an evaluation set from the RAG documents.
    """
    synthesizer = Synthesizer(max_concurrent=10, model="gpt-4.1")

    temp_dir = Path(docs_dir) / "temp_text_files"
    temp_dir.mkdir(exist_ok=True)

    file_paths = []
    for name in os.listdir(docs_dir):
        file_path = Path(docs_dir) / name
        if file_path == temp_dir:  # Exclude the temp_text_files directory itself
            continue
        if file_path.suffix == ".md":
            temp_file_path = temp_dir / f"{file_path.stem}.txt"
            with open(file_path, "r") as md_file, open(temp_file_path, "w") as txt_file:
                txt_file.write(md_file.read())
            file_paths.append(str(temp_file_path))
        elif file_path.suffix in (".txt", ".pdf", ".docx"):
            file_paths.append(str(file_path))

    synthesizer.generate_goldens_from_docs(file_paths)

    for temp_file in temp_dir.iterdir():
        temp_file.unlink()
    temp_dir.rmdir()

    synthesizer.save_as(file_type="json", directory=save_dir)

def encode_image(image: Image.Image) -> str:
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def generate_from_pdfs_visual(pdfs_dir: str = "documents", save_dir: str="eval_data") -> None:
    images: List[Image.Image] = []
    image_sources: List[Tuple[int, str]] = []

    for name in os.listdir(pdfs_dir):
        file_path = Path(pdfs_dir) / name

        if file_path.suffix == ".pdf":
            pdf_images = pdf2image.convert_from_path(file_path)
            images.extend(pdf_images)
            image_sources.extend(enumerate([str(file_path)] * len(pdf_images)))

    print("Converted PDFs")


    class Questions(BaseModel):
        class QAPair(BaseModel):
            input: str
            expected_output: str

        questions: list[QAPair]

    QA_generation_prompt = """
Your task is to write factoid questions (input) and answers (expected_output) given a image.
Your factoid questions should be answerable with a specific, concise piece of factual information from the image.
Your factoid questions should be formulated in the same style as questions users could ask in a search engine.
Your factoid questions should be questions someone could ask without seeing the image.
This means that your factoid questions SHOULD NOT reference the image provided or any specific examples contained in it, rather,
the image should be used as a knowledge base to answer the question.
"""
    # client = OpenAI()

    # def get_QA(image: Image.Image):
    #     response = client.chat.completions.create(
    #         model="gpt-4.1",
    #         temperature=0.1,
    #         # This is to enable JSON mode, making sure responses are valid json objects
    #         response_format={
    #             "type": "json_schema",
    #             "json_schema": {
    #                 "name": "FactoidQuestions",
    #                 "schema": Questions.model_json_schema(),
    #             }
    #         },
    #         messages=[
    #             {
    #                 "role": "system",
    #                 "content": QA_generation_prompt
    #             },
    #             {
    #                 "role": "user",
    #                 "content": [
    #                     {
    #                         "type": "image_url",
    #                         "image_url": {
    #                             "url": f"data:image/jpeg;base64,{encode_image(image)}"
    #                         },
    #                     },
    #                 ]
    #             }
    #         ],
    #     )

    #     return response.choices[0].message.content

    # results = []
    # for idx, image in enumerate(images[1:2]):
    #     output = get_QA(image)
    #     assert output
    #     qa = json.loads(output)["questions"]
    #     page_index, file = image_sources[idx]
    #     qa = [{"page_index": page_index, "source_file": file, **pair} for pair in qa]

    #     results.extend(qa)

    # os.makedirs(save_dir, exist_ok=True)
    # with open(os.path.join(save_dir, "image_eval_data.json"), "w") as f:
    #     json.dump(results, f, indent=4)

    tasks = []
    sources = []

    for idx, image in enumerate(images):
        task = {
            "custom_id": f"task-{idx}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4.1",
                "temperature": 0.1,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "FactoidQuestions",
                        "schema": Questions.model_json_schema(),
                    }
                },
                "messages": [
                    {
                        "role": "system",
                        "content": QA_generation_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{encode_image(image)}"
                                },
                            },
                        ]
                    }
                ],
            }
        }

        page_index, file = image_sources[idx]
        tasks.append(task)
        sources.append({
            "source_file": file,
            "page_index": page_index
        })

    file_name = "eval_data/batch_tasks_question_generation.jsonl"
    with open(file_name, 'w') as file:
        for obj in tasks:
            file.write(json.dumps(obj) + '\n')

    sources_file_name = "eval_data/batch_tasks_question_generation_sources.json"
    with open(sources_file_name, 'w') as file:
        json.dump(sources, file, indent=4)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=str, default="documents")
    parser.add_argument("--output-dir", type=str, default="eval_data")
    args = parser.parse_args()

    generate_from_pdfs_visual(args.input_dir, args.output_dir)

if __name__ == "__main__":
    main()