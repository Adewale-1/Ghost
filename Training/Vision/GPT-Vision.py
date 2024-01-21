import openai
import base64
import os
from dotenv import load_dotenv
from openai import OpenAI
from Parser import Parser  # Change this to something happens

load_dotenv()

# # Use the correct OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def encode_image(image):
    with open(image, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


image_path = "image.png"
base64_image = encode_image(image_path)
output_file_path = "output.txt"
text = Parser()

# Write the base64 encoded image to the text file
with open(output_file_path, "w") as output_file:
    output_file.write(base64_image)


client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                },
                {
                    "type": "text",
                    "text": f"""In this image,Use DFS to find the following 1.Classification of edges into tree, back, forward, or cross edges.2. Arrival/Departure times
3. Deermination of whether the graph is cyclic or acyclic using classification results.
4. Depending on your answer in 3. above, a topological ordering.You can use this context: {text}""",
                },
            ],
        }
    ],
    max_tokens=300,
)

print(response.choices[0])
