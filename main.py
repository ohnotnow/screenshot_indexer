import glob
import subprocess
import time
import os
import re
import argparse
from pathlib import Path
import ollama
import psutil
from yaspin import yaspin
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import chromadb

vision_model = 'llava'
text_model = 'mistral'


def ensure_required_models_available():
    models = ollama.list()
    vision_model_available = False
    text_model_available = False
    for model in models["models"]:
        if model['name'].startswith(vision_model):
            vision_model_available = True
        if model['name'].startswith(text_model):
            text_model_available = True
    if not vision_model_available:
        with yaspin(text=f"Downloading required vision model : {vision_model} (this may take a few minutes)", color="yellow") as spinner:
            ollama.pull(vision_model)
    if not text_model_available:
        with yaspin(text=f"Downloading required text model : {text_model} (this may take a few minutes)", color="yellow") as spinner:
            ollama.pull(text_model)

def start_chromadb():
    print("Starting ChromaDB server...")
    db_path = Path.home() / "chroma_data"
    log_path = Path.home() / "chroma_logs"
    return subprocess.Popen(["chroma", "run", "--path", db_path, "--log-path", log_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def stop_chromadb(process):
    print("Stopping ChromaDB server...")
    process.terminate()
    process.wait()

def is_process_running(process_name):
    for proc in psutil.process_iter():
        try:
            if process_name.lower() in proc.name().lower():
                print(f"Found process {process_name}")
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def ensure_chromadb_available():
    if not is_process_running("chroma"):
        chromadb_process = start_chromadb()
        time.sleep(5)
    else:
        chromadb_process = None
    return chromadb_process

def add_description_to_chroma(file_path, description, collection):
    collection.add(
        documents=[description], # we embed for you, or bring your own
        metadatas=[{"source": file_path}], # filter on arbitrary metadata!
        ids=[file_path], # must be unique for each doc
    )

def get_image_description(filename, image_prompt="What is in this image?"):
    response = ollama.chat(model=vision_model, messages=[
        {
            'role': 'user',
            'content': image_prompt,
            'images': [filename]
        },
    ])
    return response['message']['content']

def get_matching_files(pattern, max_files=0):
    files = glob.glob(pattern)
    pattern = re.compile(r'Screenshot 20\d{2}-\d{2}-\d{2} at \d{2}\.\d{2}\.\d{2}\.png')
    matches = [file for file in files if pattern.match(file)]
    if max_files == 0:
        return matches
    else:
        return matches[:max_files]

def main():
    ensure_required_models_available()
    parser = argparse.ArgumentParser(description="Rename files based on their content")
    parser.add_argument("--pattern", help="The pattern to match files against", default="Screenshot *.png")
    parser.add_argument("--max-files", help="The maximum number of files to process", default=0, type=int)
    parser.add_argument("--update", help="Update the screenshot description db", action="store_true")
    parser.add_argument("--query", help="Query the screenshot description db", type=str, default="")
    args = parser.parse_args()
    pattern = args.pattern
    max_files = args.max_files
    local_chroma = ensure_chromadb_available()
    client = chromadb.HttpClient()
    collection = client.get_or_create_collection("screenshots")
    if args.update:
        matching_files = get_matching_files(pattern, max_files)
        if len(matching_files) == 0:
            print(f"No files found that match the pattern '{pattern}*'")
            exit(1)

        for i, filename in enumerate(matching_files):
            if args.update:
                existing = collection.get(ids=[filename])
                if len(existing['ids']) > 0:
                    print(f"Skipping {filename} as it already has a description")
                else:
                    print(f"Getting description of file {i+1} of {len(matching_files)}: {filename}")
                    description = get_image_description(filename)
                    add_description_to_chroma(filename, description, collection)

    if args.query:
        results = collection.query(query_texts=[args.query], n_results=5, include=["documents", 'distances',])
        ids = results['ids'][0]
        documents = results['documents'][0]
        id_document_pairs = list(zip(ids, documents))
        for id, document in id_document_pairs:
            print(f"Filename: {id}, Description: {document}")

    if local_chroma:
        stop_chromadb(local_chroma)

if __name__ == "__main__":
    main()
