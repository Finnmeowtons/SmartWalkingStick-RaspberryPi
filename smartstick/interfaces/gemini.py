import re
from google.genai import Client, types
from smartstick.utils.config import GEMINI_API_KEY, get_path

client = Client(api_key=GEMINI_API_KEY)

def clean_text(text: str) -> str:
    # Remove unneccesarry char
    text = re.sub(r"[*_`]", "", text)
    return text.strip()

def polish_music_command(raw_text: str) -> str:
    try:
        prompt = "Extract only the music title from this input, no extra words: " + raw_text

        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=[prompt]
        )
        return response.text.strip()
    except Exception as e:
        print(f"Gemini error: {e}")
        return raw_text  # fallback

def ask_gemini(prompt: str) -> str:
    try:
        full_prompt = (
            "Answer concise and clearly for a visually impaired person. also in taglish(like a conyo in bgc)"
            "Give details yet short unless they want more details."
            "Ignore 'tanungin mo kay kumare/kumpare' its just a voice command trigger."
            "Output only the description itself. Do not mention"
            "No introductions like 'Sure, here is...'"
            "No extra context like 'as if...'"
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


def detect_online(image_path: str, prompt: str = "Describe objects in this image simply and shortly(in taglish like conyo in bgc), for a blind person.") -> str:
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
