from pyannote.audio import Pipeline
import torch
from dotenv import load_dotenv

load_dotenv()

# 1. Carrega o pipeline (requer um token de acesso do Hugging Face)

pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")

# Envia para GPU se disponível
pipeline.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))

# 2. Executa a diarização no seu arquivo
# O parâmetro num_speakers=2 ajuda a precisão se você já souber a quantidade
diarization = pipeline("/home/hipolito/Developer/pos-fiap/tech-challenge-4-grupo-29/audio-wav-16khz.wav", num_speakers=2)

print(diarization)

# 3. Exibe quem falou em cada momento
for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"Início: {turn.start:.1f}s | Fim: {turn.end:.1f}s | Falante: {speaker}")