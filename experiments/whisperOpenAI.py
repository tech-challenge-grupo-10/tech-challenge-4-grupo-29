from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

# Abre o arquivo de áudio
audio_file = open("/home/hipolito/Developer/pos-fiap/tech-challenge-4-grupo-29/audio-wav-16khz.wav", "rb")

# Chama o serviço Whisper
transcript = client.audio.transcriptions.create(
  model="whisper-1", 
  file=audio_file
)

print(transcript.text)