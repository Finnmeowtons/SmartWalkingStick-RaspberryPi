import re
from google.genai import Client, types
from smartstick.utils.config import GEMINI_API_KEY, get_path

# Initialize Gemini client
client = Client(api_key=GEMINI_API_KEY)

def clean_text(text: str) -> str:
    # Remove markdown asterisks, underscores, etc.
    text = re.sub(r"[*_`]", "", text)
    # Remove extra whitespace
    return text.strip()

def ask_gemini(prompt: str) -> str:
    """
    Send a text prompt to Gemini and return a concise response suitable for blind users.
    """
    try:
        # Concatenate the instruction with the user prompt
        full_prompt = (
            "Answer concise and clearly for a visually impaired person. also in taglish(like a conyo in bgc)"
            "Give details yet short unless they want more details."
            "Ignore 'tanungin mo kay kumare/kumpare' its just a voice command trigger."
            + prompt
        )
        print(full_prompt)
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=[full_prompt]
        )
        print(response.text)

        return clean_text(response.text)
    except Exception as e:
        return f"Error: {e}"


def detect_online(image_path: str, prompt: str = "Describe objects in this image simply and shortly, for a blind person.") -> str:
    """
    Send an image + prompt to Gemini and return a description.
    """
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/jpeg',
                ),
                prompt
            ]
        )
        print(response.text)
        return response.text

    except FileNotFoundError:
        return f"Error: File not found - {image_path}"
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    image_path = get_path("images", "detect.jpg")
    # print(detect_online(image_path))
    # print(ask_gemini("magkano ang bangus, paano ba siya nabubuhay"))
