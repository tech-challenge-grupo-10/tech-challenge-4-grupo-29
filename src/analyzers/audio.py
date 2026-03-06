import os
import numpy as np
import librosa
from transformers import pipeline
from openai import OpenAI
from dotenv import load_dotenv

class AudioAnalyzer:
    """Classe responsável por extrair áudio e analisar sentimentos/características sonoras."""
    
    def __init__(self):
        try:
            # Usando um modelo leve de classificação de áudio
            self.audio_classifier = pipeline("audio-classification", model="Dpngtm/wav2vec2-emotion-recognition", device=-1)
            # Configura o pipeline de transcrição
            self.transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-tiny", device=-1)

            self.client = OpenAI()

        except Exception as e:
            print(f"Aviso: Não foi possível carregar o modelo de áudio HF. Usaremos fallback. Erro: {e}")
            self.audio_classifier = None

    def analyze_emotions(self, audio_path):
        """Analisa o áudio extraído (emoção e transcrito)."""
        # Carrega o áudio e garante a taxa de amostragem de 16kHz exigida pelo Wav2Vec2
        speech, sr = librosa.load(audio_path, sr=16000)
        duration = librosa.get_duration(y=speech, sr=sr)
        
        results = []
        
        # Percorre o áudio em blocos de window_size_sec
        for start_time in range(0, int(duration), int(10)):
            end_time = min(start_time + 10, duration)
            
            # Extrai o segmento do áudio
            start_sample = int(start_time * sr)
            end_sample = int(end_time * sr)
            audio_segment = speech[start_sample:end_sample]
            
            # Classifica a emoção do segmento
            prediction = self.audio_classifier(audio_segment)
            top_emotion = prediction[0]
            
            results.append({
                "start": start_time,
                "end": end_time,
                "emotion": top_emotion['label'],
                "score": f"{top_emotion['score']:.2%}"
            })
        
        return results
    
    def transcript(self, audio_path):
        # Executa a transcrição com marcações de tempo
        return self.transcriber(audio_path, return_timestamps=True)

    def compose_report(self, emotions, transcript):
        prompt = f"""
            Analise o conteúdo destas extrações a partir do audio de uma conversa entre paciente e terapeuta:
            
            Esta aqui são as emoções extraídas do conteúdo:
            ${emotions}

            Esta aqui é o transcrito:
            ${transcript}

            Preciso que monte uma análise e correlacione as emoções da paciente com o contéudo do transcrito observando a situação da paciente e descrevendo como está o seu perfil psicológico
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "Você é um médico psiquiatra com mais de 20 anos de experiência. Analise o texto abaixo e me diga se há indícios de depressão, ansiedade ou qualquer outro transtorno mental. Seja objetivo e direto."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content