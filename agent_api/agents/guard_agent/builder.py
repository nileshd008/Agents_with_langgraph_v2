
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

guard_llm = ChatOpenAI(
            model="nvidia/Nemotron-Content-Safety-3.5",
            api_key=os.environ["DEEPINFRA_API_KEY"],
            base_url="https://api.deepinfra.com/v1/openai",
            temperature=0.1
        )