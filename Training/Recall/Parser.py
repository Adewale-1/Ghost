from typing_extensions import Concatenate
from PyPDF2 import PdfReader

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter

from langchain.vectorstores import FAISS

import os

from dotenv import load_dotenv
from openai import OpenAI
import openai
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.indexes import VectorstoreIndexCreator
import base64


load_dotenv()
# Use the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()


def Parser():
    pdfreader = PdfReader("File.pdf")

    raw_text = ""
    for i, page in enumerate(pdfreader.pages):
        content = page.extract_text()
        if content:
            raw_text += content

    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=800,
        chunk_overlap=200,
        length_function=len,
    )
    texts = text_splitter.split_text(raw_text)

    return texts


def execute_Parser(texts):
    # Download embeddings from OpenAI
    embeddings = OpenAIEmbeddings()

    document_search = FAISS.from_texts(texts, embeddings)

    # print(document_search)
    chain = load_qa_chain(OpenAI(), chain_type="stuff")

    # Ask questions from pdf
    query = input("Enter your search question: ")
    # query = "What is the Konigsberg Bridge Problem?"
    docs = document_search.similarity_search(query)
    output = chain.run(input_documents=docs, question=query)
    return output


if __name__ == "__main__":
    text = Parser()
    output = execute_Parser(text)
    # print(text)
    print(output)
