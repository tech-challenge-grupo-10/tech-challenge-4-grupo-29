import os
import numpy as np
import librosa
from transformers import pipeline

class AudioAnalyzer:
    """Classe responsável por extrair áudio e analisar sentimentos/características sonoras."""
    
    def __init__(self):
        # Usando um modelo leve de classificação de áudio (pode exigir internet na 1ª execução)
        try:
            self.audio_classifier = pipeline("audio-classification", model="superb/wav2vec2-base-superb-er", device=-1) # device=-1 força CPU
        except Exception as e:
            print(f"Aviso: Não foi possível carregar o modelo de áudio HF. Usaremos fallback. Erro: {e}")
            self.audio_classifier = None

    def extract_audio(self, video_path, output_audio_path="temp_audio.wav"):
        """Extrai o áudio de um arquivo de vídeo usando moviepy."""
        try:
            video = VideoFileClip(video_path)
            if video.audio is None:
                raise ValueError("O vídeo não contém faixa de áudio.")
            video.audio.write_audiofile(output_audio_path, logger=None)
            video.close()
            return output_audio_path
        except Exception as e:
            raise RuntimeError(f"Erro na extração de áudio: {str(e)}")

    def analyze(self, audio_path):
        """Analisa o áudio extraído (emoção e features acústicas)."""
        results = {"emotions": None, "mfcc_mean": None}
        
        try:
            # 1. Classificação de Emoção via HuggingFace
            if self.audio_classifier:
                predictions = self.audio_classifier(audio_path)
                # Formatar saída: {'sad': 0.8, 'angry': 0.1, ...}
                results["emotions"] = {pred['label']: pred['score'] for pred in predictions}
            
            # 2. Extração de Features Acústicas com Librosa (MFCC para estresse vocal)
            y, sr = librosa.load(audio_path, sr=16000)
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            results["mfcc_mean"] = np.mean(mfccs, axis=1).tolist()
            
            return results
        except Exception as e:
            return {"Erro": f"Falha na análise de áudio: {str(e)}"}
