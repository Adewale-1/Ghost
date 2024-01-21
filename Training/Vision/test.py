from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter


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
    with open("outputFile.txt", "w") as output_file:
        # convert the tesxt to string
        texts = str(texts)
        output_file.write(texts)


if __name__ == "__main__":
    Parser()
