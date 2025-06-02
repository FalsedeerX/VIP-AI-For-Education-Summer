import argparse
from pathlib import Path
import os

from deepeval.synthesizer import Synthesizer

def generate_from_docs(docs_dir: str = "documents", save_dir: str = "eval_data"):
    """
    Generates an evaluation set from the RAG documents.
    """
    synthesizer = Synthesizer()

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
        else:
            file_paths.append(str(file_path))

    synthesizer.generate_goldens_from_docs(file_paths)

    for temp_file in temp_dir.iterdir():
        temp_file.unlink()
    temp_dir.rmdir()

    synthesizer.save_as(file_type="json", directory=save_dir)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=str, default="documents")
    parser.add_argument("--output-dir", type=str, default="eval_data")
    args = parser.parse_args()

    generate_from_docs(args.input_dir, args.output_dir)

if __name__ == "__main__":
    main()