import openai

openai.api_key = "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"  # optional if using env variable

def transcribe_audio(file_path):
    """
    Transcribe audio file using OpenAI's Whisper API.
    file_path: path to .wav, .mp3, or .m4a file
    """
    try:
        with open(file_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="tl"  # Tagalog
            )
        return transcript.text
    except Exception as e:
        print("Error transcribing:", e)
        return None

# Example usage
if __name__ == "__main__":
    text = transcribe_audio("/home/cj/Desktop/smartstick/SmartStick/test.wav")
    print("Transcribed text:", text)
