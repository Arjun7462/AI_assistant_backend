import os
from dotenv import load_dotenv
load_dotenv()
import subprocess
import uuid
from google.cloud import speech
from google.cloud import texttospeech

path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if path and os.path.exists(path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path
else:
    raise FileNotFoundError("❌ GOOGLE_APPLICATION_CREDENTIALS is not set or the file doesn't exist.")

# Load Google Cloud client
speech_client = speech.SpeechClient()
tts_client = texttospeech.TextToSpeechClient()

# Convert any audio file to 16kHz mono WAV using ffmpeg
def convert_to_wav(input_path):
    output_path = f"temp/{uuid.uuid4()}.wav"
    command = [
        "ffmpeg", "-y", "-i", input_path,
        "-ar", "16000", "-ac", "1", output_path
    ]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path

# Transcribe WAV using Google STT
def transcribe_audio(input_path):
    wav_path = convert_to_wav(input_path)

    with open(wav_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US"
    )

    response = speech_client.recognize(config=config, audio=audio)
    os.remove(wav_path)

    result = ""
    for res in response.results:
        result += res.alternatives[0].transcript + " "
    return result.strip()

# Convert Gemini reply text to MP3 speech
def text_to_speech(text):
    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = tts_client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    output_path = f"temp/{uuid.uuid4()}.mp3"
    with open(output_path, "wb") as out:
        out.write(response.audio_content)
    return output_path