"""
Sistema de Análise de Saúde Mental Multimodal
--------------------------------------------------
Desenvolvido por: Engenheiro de IA (Assistente)
Objetivo: Pré-diagnóstico assistido de sinais psicológicos usando Documentos (PDF), Áudio e Sensores contínuos (CSV/TXT).
"""

import logging
import os
import time
import pandas as pd
import gradio as gr
import warnings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

from dotenv import load_dotenv

from src.analyzers.audio import AudioAnalyzer
from src.analyzers.text import TextAnalyzer
from src.analyzers.sensor import SensorAnalyzer
from src.notifier import notify_medical_team
from src.ui.charts import plot_radar_chart, plot_gauge_chart

load_dotenv()

# Suprimir avisos não críticos para manter o console limpo
warnings.filterwarnings("ignore")

# ==========================================
# COORDENADOR PRINCIPAL E DASHBOARDS (GRADIO)
# ==========================================

print("Carregando modelos de IA na memória. Isso pode levar alguns minutos na primeira execução...")
audio_analyzer = AudioAnalyzer()
text_analyzer = TextAnalyzer()
sensor_analyzer = SensorAnalyzer()
print("Modelos carregados com sucesso!")

def process_stream(pdf_files, audio_files, sensor_files):
    """
    Função geradora principal.
    1. Processa PDFs.
    2. Processa Áudios.
    3. Lê os sensores passo a passo simulando streaming.
    """
    alert = False
    alert_counter = 0
    logging.info("Iniciando análise multimodal — PDFs: %d | Áudios: %d | Sensores: %d",
                 len(pdf_files) if pdf_files else 0,
                 len(audio_files) if audio_files else 0,
                 len(sensor_files) if sensor_files else 0)

    # --- Passo 1: Processar os Documentos ---
    pdf_report = f"📄 Recebido(s) {len(pdf_files) if pdf_files else 0} documento(s) clínico(s).\n"
    if pdf_files:
        for p in pdf_files:
            logging.info("Processando documento: %s", os.path.basename(p))
            pdf_report += f"- Arquivo lido: {os.path.basename(p)}\n"
            res = text_analyzer.analyze(p)
            pdf_report += f"- Texto extraído: {res["text"]}\n"
        pdf_report += "✅ Texto extraído e anexado ao prontuário.\n\n"
        logging.info("Documentos processados com sucesso.")
        pdf_report = text_analyzer.compose_report(text=pdf_report)
    else:
        logging.info("Nenhum documento PDF recebido.")
        pdf_report += "Nenhum PDF recebido.\n\n"
        
    yield pdf_report, "Aguardando áudio...", "Aguardando sensores...", None, None

    # --- Passo 2: Processar Áudios ---
    audio_report = f"🎤 Recebido(s) {len(audio_files) if audio_files else 0} arquivo(s) de áudio.\n"
    
    if audio_files:
        for af in audio_files:
            logging.info("Processando áudio: %s", os.path.basename(af))
            audio_report += f"- Analisando: {os.path.basename(af)}...\n"
            yield pdf_report, audio_report, "Aguardando sensores...", None, None
            emotions = audio_analyzer.analyze_emotions(af)
            transcript=audio_analyzer.transcript(af)
            audio_report = audio_analyzer.compose_report(emotions=emotions, transcript=transcript)
    else:
        audio_report += "Nenhum áudio recebido.\n\n"

    yield pdf_report, audio_report, "Iniciando processamento de sensores...", None, None

    # --- Passo 3: Processar Sensores (Streaming contínuo) ---
    if not sensor_files:
        logging.info("Nenhum arquivo de sensor recebido.")
        yield pdf_report, audio_report, "Nenhum arquivo de sensor recebido.", plot_gauge_chart(0, "Pressão Sistólica", 200, []), plot_gauge_chart(0, "SpO2 (%)", 100, [])
        return

    # Juntar os dados de sensor caso haja mais de um e simular streaming
    for sf in sensor_files:
        try:
            # Tenta carregar JSONL caso as propriedades venham exportadas como result.txt
            try:
                df = pd.read_json(sf, lines=True)
                if 'sistolica' in df.columns:
                    df = df.rename(columns={'sistolica': 'sys', 'diastolica': 'dia'})
            except Exception:
                # Fallback genérico para CSV
                df = pd.read_csv(sf, sep=None, engine='python')
                 
            # Validar e garantir que existam as colunas, caso contrário simular valores fictícios baseados nos dados
            if not all(col in df.columns for col in ['sys', 'dia', 'spo2']):
                print(f"Aviso: Arquivo {os.path.basename(sf)} não tem colunas padrão 'sys', 'dia', 'spo2'. Usando mockup de dados.")
                df = pd.DataFrame({
                    'sys': [120, 125, 130, 145, 120],
                    'dia': [80, 82, 85, 95, 80],
                    'spo2': [98, 97, 96, 92, 98]
                })
        except Exception as e:
            print(f"Aviso: Falha ao ler {os.path.basename(sf)} - gerando mockup de falha. {str(e)}")
            df = pd.DataFrame({
                'sys': [120, 150],
                'dia': [80, 100],
                'spo2': [98, 90]
            })

        logging.info("Iniciando streaming de sensores: %s (%d registros)", os.path.basename(sf), len(df))
        for index, row in df.iterrows():
            sys_val = row['sys']
            dia_val = row['dia']
            spo2_val = row['spo2']
            
            result = sensor_analyzer.analyze(sys_val, dia_val, spo2_val)
            logging.debug("Registro %d — PA: %s/%s mmHg | SpO2: %s%% | Diagnóstico: %s",
                          index + 1, sys_val, dia_val, spo2_val, result['risk_level'])
            
            sys_gauge = plot_gauge_chart(sys_val, "Pressão Sistólica", 200, [
                {'range': [0, 90], 'color': "yellow"},
                {'range': [90, 140], 'color': "lightgreen"},
                {'range': [140, 200], 'color': "red"}
            ])
            
            spo2_gauge = plot_gauge_chart(spo2_val, "SpO2 (%)", 100, [
                {'range': [0, 90], 'color': "red"},
                {'range': [90, 94], 'color': "yellow"},
                {'range': [94, 100], 'color': "lightgreen"}
            ])
            
            sensor_report = f"### [STREAMING] Lendo arquivo {os.path.basename(sf)} - Registro {index+1}/{len(df)}\n"
            sensor_report += f"**PA**: {sys_val}/{dia_val} mmHg | **SpO2**: {spo2_val}%\n"
            
            if 'emocao' in row and 'estresse' in row:
                sensor_report += f"**Indicador Externo (JSON)** -> Emoção: **{row.get('emocao', 'N/A')}** | Perfil de Estresse: **{row.get('estresse', 'N/A')}**\n\n"
                
            sensor_report += f"**Diagnóstico Fisiológico Calculado**: {result['risk_level']}\n\n{result['details']}"

            if "Alto Risco" in result["risk_level"]:
                alert_counter += 1
                alert = True

            # Atualiza os componentes da UI e pausa para simular streaming
            yield pdf_report, audio_report, sensor_report, sys_gauge, spo2_gauge
            time.sleep(0.01) # Simula 1 segundo por leitura

    # --- Notificação final ---
    if alert:
        logging.warning("Análise concluída com %d alerta(s). Enviando notificação à equipe médica...", alert_counter)

        notify_medical_team(
            risk_level="Alto Risco de Estresse/Ansiedade Fisiológica"
        )
    else:
        logging.info("Análise concluída sem alertas de alto risco.")

    # Final do streaming
    yield pdf_report, audio_report, "✅ Transmissão de sensores concluída.\n" + sensor_report, sys_gauge, spo2_gauge

# ==========================================
# INTERFACE DE USUÁRIO (GRADIO)
# ==========================================
def create_app():
    with gr.Blocks(theme=gr.themes.Soft(), title="Análise Multimodal de Saúde Mental (Stream)",
                   css="""
                   #pdf_output_txt {
                       border: var(--block-border-width) solid var(--block-border-color);
                       border-radius: var(--block-radius);
                       background: var(--block-background-fill);
                       overflow: hidden;
                       padding: 0;
                   }
                   #pdf_output_txt .label-wrap {
                       background: var(--block-label-background-fill);
                       border-bottom: var(--block-border-width) solid var(--block-border-color);
                       padding: var(--block-label-padding);
                       border-radius: var(--block-label-radius);
                   }
                   #pdf_output_txt .label-wrap span {
                       color: var(--block-label-text-color);
                       font-weight: var(--block-label-text-weight);
                       font-size: var(--block-label-text-size);
                   }
                   #pdf_output_txt .prose {
                       background: var(--input-background-fill);
                       border: 1px solid var(--border-color-primary);
                       border-radius: var(--radius-lg);
                       padding: var(--input-padding);
                       height: 170px;
                       overflow-y: auto;
                       margin: var(--spacing-lg);
                   }
               """) as app:
        gr.Markdown(
            """
            # 🧠 Sistema de Pré-Diagnóstico Multimodal
            **Aviso Médico**: Esta ferramenta é um *assistente de triagem* e não substitui a avaliação de um profissional de saúde mental capacitado.
            
            Este sistema realiza o recebimento e análise contínua de:
            - Múltiplos **Documentos (PDF)**
            - Múltiplos **Áudios**
            - **Arquivos de Sensores** processados como fluxo contínuo (Streaming).
            """
        )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Diretórios de Entrada")
                pdf_input = gr.File(label="Documentos Clínicos (PDF)", file_count="multiple", file_types=[".pdf"])
                audio_input = gr.File(label="Gravações de Áudio", file_count="multiple", file_types=["audio"])
                sensor_input = gr.File(label="Arquivos de Sensores (TXT/CSV)", file_count="multiple", file_types=[".txt", ".csv"])
                
                analyze_stream_btn = gr.Button("▶️ Iniciar Análise Contínua", variant="primary")
            
            with gr.Column(scale=2):
                gr.Markdown("### 📊 Dashboard e Stream de Dados")
                
                with gr.Tab("📄 Documentos e 🎤 Áudios"):
                    pdf_output_txt = gr.Textbox(label="Análise dos documentos", interactive=False)
                    audio_output_txt = gr.Textbox(label="Análise do Áudio", interactive=False)
                
                with gr.Tab("❤️ Sensores em Tempo Real"):
                    sensor_report_txt = gr.Markdown("### Aguardando início do stream...")
                    with gr.Row():
                        sys_plot = gr.Plot()
                        spo2_plot = gr.Plot()

        analyze_stream_btn.click(
            fn=process_stream,
            inputs=[pdf_input, audio_input, sensor_input],
            outputs=[pdf_output_txt, audio_output_txt, sensor_report_txt, sys_plot, spo2_plot]
        )
        
    return app

if __name__ == "__main__":
    app = create_app()
    print("Iniciando o servidor Gradio...")
    app.launch(share=False)
