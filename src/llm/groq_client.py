# src/llm/groq_client.py

import os
import logging

from dotenv import load_dotenv
from groq import Groq, APIStatusError
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


logger = logging.getLogger(__name__)

def generate(prompt: str) -> dict:
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0,
        )

        return {
            "text": response.choices[0].message.content,
            "model": "llama-3.1-8b-instant"
        }
    except APIStatusError as e:
        logger.warning(f"Groq API error ({e.status_code}), falling back to Gemini. Details: {str(e)}")
        
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY not found in environment for fallback.")
            
        gemini_client = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=gemini_api_key
        )
        msg = HumanMessage(content=prompt)
        gemini_response = gemini_client.invoke([msg])
        
        return {
            "text": gemini_response.content,
            "model": "gemini-2.5-flash"
        }
