import cv2
import pandas as pd
import numpy as np
from deepface import DeepFace

class VideoAnalyzer:
    """Classe responsável por analisar micro-expressões faciais em vídeos."""
    
    def __init__(self, sample_rate=1.0):
        # sample_rate: analisar 1 frame por segundo para poupar a CPU
        self.sample_rate = sample_rate

    def analyze(self, video_path):
        """Extrai frames do vídeo e analisa emoções usando DeepFace."""
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Tratamento para vídeos sem informação de FPS
            if fps == 0 or np.isnan(fps):
                fps = 30 
                
            frame_interval = int(fps * self.sample_rate)
            
            emotions_list = []
            frame_count = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    try:
                        # enforce_detection=False para não quebrar se não achar rosto em um frame
                        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False, silent=True)
                        # DeepFace pode retornar uma lista se achar múltiplos rostos, pegamos o primeiro
                        if isinstance(result, list):
                            result = result[0]
                        emotions_list.append(result['emotion'])
                    except Exception as e:
                        # Rosto não detectado neste frame específico, ignora
                        pass
                        
                frame_count += 1
            
            cap.release()
            
            if not emotions_list:
                return {"Erro": "Nenhuma face detectada no vídeo ou vídeo inválido."}, None
                
            # Média das emoções ao longo do vídeo
            df_emotions = pd.DataFrame(emotions_list)
            avg_emotions = df_emotions.mean().to_dict()
            
            return avg_emotions
            
        except Exception as e:
            return {"Erro": f"Falha ao processar vídeo: {str(e)}"}
