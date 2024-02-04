from fastapi import FastAPI, UploadFile, File, Request
from typing import List
import shutil
import tempfile
import os
import logging

from Recall import Recall_Processor

"""
    API declaration and initialization
"""
app = FastAPI()


# Set up basic logging
logging.basicConfig(
    filename="Recall.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
)


# Initialize questions_store as a global variable
questions_store = []


recall_object = Recall_Processor(7)


@app.post("/questions/generate")
async def process_pdfs(files: List[UploadFile] = File(...)) -> dict:
    """
    FastAPI endpoint to process uploaded PDF files, extract text, generate questions,
    and store them. Handles POST requests with PDF files.

    Parameters:
    files (List[UploadFile]): A list of uploaded PDF files.

    Returns:
    JSON response indicating the success or failure of PDF processing and question generation.
    """

    # Store the file paths temporarily
    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            saved_filepaths = []
            for file in files:
                file_path = f"{tmpdirname}/{file.filename}"
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                saved_filepaths.append(file_path)
            print("\nQuestions are being generated...\n")
            raw_text = recall_object.get_text_from_pdf(saved_filepaths)
            text_chunks = recall_object.get_text_chunk(raw_text)
            global questions_store

            """
               TODO: Store the questions in a database based on user id-> FireStore
            """
            questions_store = recall_object.generate_questions(text_chunks)
            print("\nQuestions generated successfully✅")

            return {"status": "success"}
    except Exception as e:
        logging.error(
            f"Error processing PDFs: {e}", exc_info=True
        )  # Log the exception with stack trace
        return {"error": str(e)}


@app.get("/questions/retreive")
async def get_questions() -> dict:
    # Return the stored questions
    global questions_store
    print("Retrieving Questions...")
    return {"questions": questions_store}


async def save_file(file: UploadFile, tmpdirname: str) -> str:
    """
    Saves an uploaded file to a temporary directory.

    Keyword arguments:
    file -- file object to be saved
    tmpdirname -- path to the temporary directory

    Return: Path to the saved file.
    """
    file_path = os.path.join(tmpdirname, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path
