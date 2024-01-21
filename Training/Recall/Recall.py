from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
import openai
import random
import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile
import json
from flask_cors import CORS
from collections.abc import Iterable  # instead of from collections import Iterable

# Get pdf file from user

load_dotenv()
import logging


# Set up basic logging
logging.basicConfig(
    filename="Recall.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
)





# # ////////

# Get text from pdf file
def get_text_from_pdf(pdf_files):
    text = ""
    for pdf_file_path in pdf_files:
        try:
            pdf_reader = PdfReader(pdf_file_path)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:  # Check if text extraction is successful
                    text += page_text
        except FileNotFoundError:
            print(f"File not found: {pdf_file_path}")
    return text


# Get the text chunk from the pdf text
def get_text_chunk(text):
    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len
    )
    chunks = text_splitter.split_text(text)

    return chunks


def generate_questions(text_chunks, num_questions):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    questions = []

    for _ in range(num_questions):
        # Select a random text chunk
        random_chunk = random.choice(text_chunks)

        prompt = (
            "Please generate a challenging review question regarding the topic discussed below that requires deep "
            "understanding and critical thinking for a student to answer. The question should encourage the student to "
            "demonstrate their knowledge and grasp of the subject matter in detail\n\n"
            + random_chunk
        )

        # Use OpenAI API to generate a question using the chat completions endpoint
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",  # Ensure to specify the right model here
            messages=[
                {
                    "role": "system",
                    "content": "You are a knowledgeable tutor generating review questions for a student.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        question_text = response["choices"][0]["message"]["content"]
        print(f"Raw OpenAI response: '{question_text}'")  # Print out the raw response

        questions.append(question_text.strip())

    return questions


# Create Vector Store
"""
    Embeddings
"""


def get_vectorStore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_vectorStoreWithHuggingFace(text_chunks):
    embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


# Create the Chat
def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    memory = ConversationBufferMemory(memory_key="history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=vectorstore.as_retriever(), memory=memory
    )
    return conversation_chain


app = Flask(__name__)
CORS(app)





@app.route("/", methods=["POST"])
def process_pdfs():
    # Check if the POST request has the 'files' part
    if "files" not in request.files:
        logging.error("No files in request")
        return jsonify({"error": "No files part in the request"}), 400

    # Get the list of files from the request
    files = request.files.getlist("files")
    print(files)
    num_questions = request.form.get("num_questions", type=int, default=10)

    # Store the file paths temporarily
    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            saved_filepaths = [save_file(file, tmpdirname) for file in files]
            raw_text = get_text_from_pdf(saved_filepaths)
            text_chunks = get_text_chunk(raw_text)
            global questions_store
            questions_store = generate_questions(text_chunks, num_questions)
            print("\n Questions generated")
            return jsonify({"status": "success"})
    except Exception as e:
        logging.error(
            f"Error processing PDFs: {e}", exc_info=True
        )  # Log the exception with stack trace
        return jsonify({"error": str(e)}), 500


@app.route("/questions", methods=["GET"])
def get_questions():
    # Return the stored questions
    global questions_store
    print("Getting...")
    return jsonify({"questions": questions_store})


def save_file(file, tmpdirname):
    # Your existing logic to save the file
    if file and file.filename.endswith(".pdf"):
        filename = secure_filename(file.filename)
        filepath = os.path.join(tmpdirname, filename)
        file.save(filepath)
        return filepath


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
