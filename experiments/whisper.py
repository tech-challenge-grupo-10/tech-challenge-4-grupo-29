from transformers import pipeline

# Configura o pipeline de transcrição
transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-tiny")

# Executa a transcrição com marcações de tempo
result = transcriber("/home/hipolito/Developer/pos-fiap/tech-challenge-4-grupo-29/audio-wav-16khz.wav", return_timestamps=True)

# O resultado conterá o texto completo e uma lista de 'chunks' com tempos
for chunk in result["chunks"]:
    print(f"Tempo: {chunk['timestamp']} - Texto: {chunk['text']}")