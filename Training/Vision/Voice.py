import openai
import base64
import os
from dotenv import load_dotenv
from openai import OpenAI
from Parser import *
import os
import time
import pygame


load_dotenv()
# Use the correct OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

output = execute_Parser(Parser())
print(output)

response = client.audio.speech.create(
    model="tts-1",
    voice="echo",
    input=f"{word}",
)


response.stream_to_file("output.mp3")

pygame.mixer.init()

# Load  MP3 file
pygame.mixer.music.load('output.mp3')

# Play the MP3 file
pygame.mixer.music.play()

# Wait for the music to play completely
while pygame.mixer.music.get_busy():
    time.sleep(1)

# Stop playing
pygame.mixer.music.stop()

# Delete the MP3 file
os.remove('output.mp3')
print("MP3 file deleted.")

