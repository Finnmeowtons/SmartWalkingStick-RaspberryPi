import google.generativeai as genai
from smartstick.utils.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model_gemini = genai.GenerativeModel('gemini-2.5-flash-lite')

def ask_gemini(prompt):
    try:
        response = model_gemini.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"
