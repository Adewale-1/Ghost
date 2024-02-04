from ast import List
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
import openai
import random
import os
import logging


load_dotenv()



class Recall_Processor:
    def __init__(self, amount_or_questions: int):
        self.questions_store = []
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.num_questions = amount_or_questions

    # Get text from pdf file
    def get_text_from_pdf(self, pdf_files) -> str:
        """
        Extracts and concatenates text from a list of PDF files.

        Keyword arguments:
        pdf_files -- List of file paths to PDF documents.

        Return: A single string containing all extracted text from the PDFs.
        """
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
    def get_text_chunk(self, text):
        """
        Splits the text into manageable chunks.

        Keyword arguments:
        text -- A large string of text to be split.

        Return: A list of text chunks based on specified chunking parameters.
        """

        text_splitter = CharacterTextSplitter(
            separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len
        )
        chunks = text_splitter.split_text(text)

        return chunks

    def generate_questions(self, text_chunks):
        """
        Generates questions using OpenAI's API based on provided text chunks.

        Keyword arguments:
        text_chunks -- List of text chunks used for question generation.
        num_questions -- The number of questions to generate.

        Return: A list of generated questions.
        """
        questions = []

        for _ in range(self.num_questions):
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
                model="gpt-4-1106-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a knowledgeable tutor generating review questions for a student.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            question_text = response["choices"][0]["message"]["content"]
            # print(f"Raw OpenAI response: '{question_text}'")  # Print out the raw response

            questions.append(question_text.strip())

        return questions

    # Create Vector Store
    """
        Embeddings



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
        
    """