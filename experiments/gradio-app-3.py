"""
Sistema de Análise de Saúde Mental Multimodal
--------------------------------------------------
Desenvolvido por: Engenheiro de IA (Assistente)
Objetivo: Pré-diagnóstico assistido de sinais psicológicos usando Vídeo, Áudio, Texto e Sensores.

Dependências necessárias:
pip install gradio deepface moviepy openai-whisper transformers librosa plotly pandas numpy opencv-python tf-keras torch torchaudio soundfile

Nota: Requer 'ffmpeg' instalado no sistema (necessário para o Whisper e MoviePy).
"""

import os
import cv2
import gradio as gr
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from moviepy import VideoFileClip
import whisper
from transformers import pipeline
import librosa
from deepface import DeepFace
import warnings

# Suprimir avisos não críticos para manter o console limpo
warnings.filterwarnings("ignore")

# ==========================================
# MÓDULO 1: ANÁLISE DE VÍDEO (FACES E EMOÇÕES)
# ==========================================
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

# ==========================================
# MÓDULO 2: ANÁLISE DE ÁUDIO
# ==========================================
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

# ==========================================
# MÓDULO 3: ANÁLISE DE TEXTO E TRANSCRIÇÃO
# ==========================================
class TextAnalyzer:
    """Classe responsável por transcrever o áudio e aplicar NLP para risco psicológico."""
    
    def __init__(self):
        # Whisper: modelo 'base' ou 'tiny' para rodar bem em CPU
        #self.transcriber = whisper.load_model("base")
        # Analisador de sentimento multilingue para marcadores de agressividade/depressão (negatividade)
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment", device=-1)

    def analyze(self, audio_path):
        """Transcreve e analisa o sentimento do texto."""
        try:
            # 1. Transcrição
            transcription = self.transcriber.transcribe(audio_path, fp16=False) # fp16=False evita warnings na CPU
            text = transcription['text'].strip()
            
            if not text:
                return {"text": "Nenhuma fala detectada.", "sentiment": None}
            
            # 2. Análise de Sentimento (NLP)
            # O modelo nlptown retorna de 1 star (muito negativo) a 5 stars (muito positivo)
            # Podemos mapear estrelas baixas para possíveis marcadores de depressão/estresse
            chunks = [text[i:i+500] for i in range(0, len(text), 500)] # Evita limite de tokens do BERT
            sentiments = []
            for chunk in chunks:
                if chunk.strip():
                    sentiments.append(self.sentiment_analyzer(chunk)[0])
            
            return {"text": text, "sentiment": sentiments}
            
        except Exception as e:
            return {"Erro": f"Falha na análise de texto: {str(e)}"}

# ==========================================
# MÓDULO 4: ANÁLISE DE SENSORES
# ==========================================
class SensorAnalyzer:
    """Classe responsável por avaliar dados fisiológicos."""
    
    def analyze(self, sys, dia, spo2):
        """
        Avalia a pressão arterial e SpO2.
        Lógica de alerta: PA > 140/90 (14/9) ou SpO2 < 94% em repouso.
        """
        risks = []
        is_stressed = False
        
        # Análise Pressão Arterial
        if sys > 140 or dia > 90:
            risks.append("⚠️ ALERTA: Pressão Arterial elevada (> 140/90 mmHg). Possível indicador de estresse agudo ou hipertensão.")
            is_stressed = True
        elif sys < 90 or dia < 60:
            risks.append("⚠️ ALERTA: Pressão Arterial baixa (< 90/60 mmHg).")
        else:
            risks.append("✅ Pressão Arterial dentro dos padrões normais.")
            
        # Análise SpO2
        if spo2 < 94:
            risks.append("⚠️ ALERTA: Saturação de Oxigênio (SpO2) perigosamente baixa (< 94%). Possível indicador de ansiedade severa (hiperventilação/hipoventilação) ou problema fisiológico.")
            is_stressed = True
        else:
            risks.append("✅ Saturação de Oxigênio normal.")
            
        risk_level = "Alto Risco de Estresse/Ansiedade Fisiológica" if is_stressed else "Padrão Fisiológico Estável"
        
        return {
            "risk_level": risk_level,
            "details": "\n".join(risks),
            "sys": sys,
            "dia": dia,
            "spo2": spo2
        }

# ==========================================
# COORDENADOR PRINCIPAL E DASHBOARDS (GRADIO)
# ==========================================

# Instanciar as classes globalmente para carregar os modelos apenas uma vez
print("Carregando modelos de IA na memória. Isso pode levar alguns minutos na primeira execução...")
video_analyzer = VideoAnalyzer(sample_rate=1.0) # 1 frame por segundo
audio_analyzer = AudioAnalyzer()
#text_analyzer = TextAnalyzer()
sensor_analyzer = SensorAnalyzer()
print("Modelos carregados com sucesso!")

def plot_radar_chart(emotions_dict, title):
    """Gera um gráfico de radar interativo usando Plotly."""
    if not emotions_dict or "Erro" in emotions_dict:
        return go.Figure().add_annotation(text="Dados insuficientes para o gráfico", showarrow=False)
        
    categories = list(emotions_dict.keys())
    values = list(emotions_dict.values())
    
    # Fechar o polígono do radar
    categories.append(categories[0])
    values.append(values[0])
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=title
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, max(values) if max(values) > 0 else 100])),
        showlegend=False,
        title=title
    )
    return fig

def plot_gauge_chart(value, title, max_val, thresholds):
    """Gera um gráfico de velocímetro (Gauge) para sensores."""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = value,
        title = {'text': title},
        gauge = {
            'axis': {'range': [None, max_val]},
            'bar': {'color': "darkblue"},
            'steps': thresholds
        }
    ))
    fig.update_layout(height=300)
    return fig

def process_multimodal_input(video_file):
    """Função principal que coordena Vídeo, Áudio e Texto."""
    if video_file is None:
        return None, None, "Nenhum vídeo fornecido.", "Aguardando entrada..."

    video_path = video_file
    
    # 1. Análise de Vídeo
    video_emotions = video_analyzer.analyze(video_path)
    video_plot = plot_radar_chart(video_emotions, "Micro-expressões Faciais Média (DeepFace)")
    
    # 2 & 3. Análise de Áudio e Texto
    try:
        audio_path = audio_analyzer.extract_audio(video_path)
        audio_results = audio_analyzer.analyze(audio_path)
        #text_results = text_analyzer.analyze(audio_path)
        
        # Limpar arquivo temporário de áudio
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
    except Exception as e:
        audio_results = {"Erro": str(e)}
        text_results = {"text": "Erro na extração de áudio.", "sentiment": None}

    # Gerar plot de áudio (se disponível)
    if "emotions" in audio_results and audio_results["emotions"]:
         audio_plot = plot_radar_chart(audio_results["emotions"], "Emoções Vocais (HuggingFace)")
    else:
         # Fallback para plot vazio caso o modelo de áudio falhe
         audio_plot = plot_radar_chart({"Neutro": 100}, "Emoções Vocais (Modelo Indisponível/Erro)")

    # Formatar resultados de texto
    transcription = text_results.get("text", "")
    sentiments = text_results.get("sentiment", [])
    
    sentiment_text = f"Transcrição:\n{transcription}\n\nAnálise de Marcadores Linguísticos:\n"
    if sentiments:
        for i, s in enumerate(sentiments):
            # nlptown retorna ex: '1 star', '2 stars'
            sentiment_text += f"Trecho {i+1}: {s['label']} (Confiança: {s['score']:.2f})\n"
            if s['label'] in ['1 star', '2 stars']:
                 sentiment_text += "  -> ⚠️ Risco: Linguagem altamente negativa/depressiva detectada.\n"
            elif s['label'] == '5 stars':
                 sentiment_text += "  -> ✅ Positividade detectada.\n"
    else:
        sentiment_text += "Não foi possível analisar o sentimento."

    return video_plot, audio_plot, sentiment_text

def process_sensors(sys, dia, spo2):
    """Processa dados de sensores e gera gráficos."""
    result = sensor_analyzer.analyze(sys, dia, spo2)
    
    # Gráficos
    sys_gauge = plot_gauge_chart(sys, "Pressão Sistólica", 200, [
        {'range': [0, 90], 'color': "yellow"},
        {'range': [90, 140], 'color': "lightgreen"},
        {'range': [140, 200], 'color': "red"}
    ])
    
    spo2_gauge = plot_gauge_chart(spo2, "SpO2 (%)", 100, [
        {'range': [0, 90], 'color': "red"},
        {'range': [90, 94], 'color': "yellow"},
        {'range': [94, 100], 'color': "lightgreen"}
    ])
    
    report = f"### Diagnóstico Fisiológico: {result['risk_level']}\n\n{result['details']}"
    
    return report, sys_gauge, spo2_gauge

# ==========================================
# INTERFACE DE USUÁRIO (GRADIO)
# ==========================================
with gr.Blocks(theme=gr.themes.Soft(), title="Análise Multimodal de Saúde Mental") as app:
    gr.Markdown(
        """
        # 🧠 Sistema de Pré-Diagnóstico Multimodal
        **Aviso Médico**: Esta ferramenta é um *assistente de triagem* e não substitui a avaliação de um profissional de saúde mental capacitado.
        """
    )
    
    with gr.Tabs():
        # TAB 1: Vídeo, Áudio e Texto
        with gr.TabItem("🎥 Análise Comportamental (Vídeo/Voz)"):
            gr.Markdown("Faça upload de um vídeo do paciente relatando seu estado ou respondendo a um questionário padrão.")
            
            with gr.Row():
                with gr.Column(scale=1):
                    video_input = gr.Video(label="Upload de Vídeo")
                    analyze_media_btn = gr.Button("Iniciar Análise Multimodal", variant="primary")
                
                with gr.Column(scale=2):
                    gr.Markdown("### 📊 Dashboards de Expressão e Emoção")
                    with gr.Row():
                        video_output_plot = gr.Plot(label="Expressão Facial")
                        audio_output_plot = gr.Plot(label="Tom de Voz")
            
            with gr.Row():
                text_output = gr.Textbox(label="Transcrição e NLP (Marcadores Linguísticos)", lines=8, interactive=False)

            analyze_media_btn.click(
                fn=process_multimodal_input,
                inputs=[video_input],
                outputs=[video_output_plot, audio_output_plot, text_output]
            )
            
        # TAB 2: Sensores (Fisiologia)
        with gr.TabItem("❤️ Dados Fisiológicos (Sensores)"):
            gr.Markdown("Insira os dados coletados de wearables ou aferição manual em repouso.")
            
            with gr.Row():
                with gr.Column():
                    sys_input = gr.Number(label="Pressão Sistólica (mmHg) - ex: 140 para 14", value=120)
                    dia_input = gr.Number(label="Pressão Diastólica (mmHg) - ex: 90 para 9", value=80)
                    spo2_input = gr.Number(label="Saturação de Oxigênio SpO2 (%)", value=98, maximum=100)
                    analyze_sensor_btn = gr.Button("Avaliar Risco Fisiológico", variant="primary")
                    
                with gr.Column():
                    sensor_report = gr.Markdown("### Aguardando dados...")
                    
            with gr.Row():
                sys_plot = gr.Plot()
                spo2_plot = gr.Plot()

            analyze_sensor_btn.click(
                fn=process_sensors,
                inputs=[sys_input, dia_input, spo2_input],
                outputs=[sensor_report, sys_plot, spo2_plot]
            )

# Ponto de entrada
if __name__ == "__main__":
    print("Iniciando o servidor Gradio...")
    app.launch(share=False)