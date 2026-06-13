from dotenv import load_dotenv
import os

load_dotenv()

print("KEY:", os.getenv("MISTRAL_API_KEY"))

from langchain_mistralai import ChatMistralAI

model = ChatMistralAI(model="mistral-small-latest")

response = model.invoke("hello")
print(os.getenv("MISTRAL_API_KEY"))
print(response.content)
