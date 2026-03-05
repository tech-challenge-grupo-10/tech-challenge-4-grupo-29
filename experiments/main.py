from transformers import pipeline
import torch
import librosa
from dotenv import load_dotenv

load_dotenv()

def analyze_emotion_with_timestamps(audio_path, window_size_sec=3.0):
    """
    Divide o áudio em janelas de tempo e identifica a emoção de cada segmento.
    """
    
    #model_id = "alefiury/wav2vec2-xls-r-300m-pt-br-spontaneous-speech-emotion-recognition"
    model_id = "Dpngtm/wav2vec2-emotion-recognition"
    classifier = pipeline("audio-classification", model=model_id)
    
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
        # O modelo do Alefiury retorna as probabilidades para cada classe
        prediction = classifier(audio_segment)
        top_emotion = prediction[0] # A primeira é sempre a de maior score
        
        results.append({
            "start": start_time,
            "end": end_time,
            "emotion": top_emotion['label'],
            "score": f"{top_emotion['score']:.2%}"
        })
    
    return results

if __name__ == "__main__":
    file_path = "/home/hipolito/Developer/pos-fiap/tech-challenge-4-grupo-29/audio-wav-16khz.wav" # Substitua pelo seu arquivo
    emotions_timeline = analyze_emotion_with_timestamps(file_path)

    print(f"{'Início':<8} | {'Fim':<8} | {'Emoção Dominante':<18} | {'Confiança'}")
    print("-" * 55)
    print(emotions_timeline)
    for res in emotions_timeline:
        print(f"{res['start']:>5}s    | {res['end']:>5}s    | {res['emotion']:<18} | {res['score']}")