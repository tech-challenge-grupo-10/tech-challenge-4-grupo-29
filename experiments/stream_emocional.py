# stream_emocional.py
import json
from datetime import datetime, timedelta

# Dados de entrada (emoções detectadas)
emocoes = [{'start': 0, 'end': 10, 'emotion': 'sad', 'score': '45.61%'}, {'start': 10, 'end': 20, 'emotion': 'happy', 'score': '55.78%'}, {'start': 20, 'end': 30, 'emotion': 'sad', 'score': '74.27%'}, {'start': 30, 'end': 40, 'emotion': 'sad', 'score': '76.24%'}, {'start': 40, 'end': 50, 'emotion': 'sad', 'score': '76.78%'}, {'start': 50, 'end': 60, 'emotion': 'sad', 'score': '39.66%'}, {'start': 60, 'end': 70, 'emotion': 'calm', 'score': '82.14%'}, {'start': 70, 'end': 80, 'emotion': 'sad', 'score': '77.23%'}, {'start': 80, 'end': 90, 'emotion': 'sad', 'score': '93.52%'}, {'start': 90, 'end': 100, 'emotion': 'sad', 'score': '96.61%'}, {'start': 100, 'end': 110, 'emotion': 'sad', 'score': '92.42%'}, {'start': 110, 'end': 120, 'emotion': 'fearful', 'score': '86.07%'}, {'start': 120, 'end': 130, 'emotion': 'happy', 'score': '92.39%'}, {'start': 130, 'end': 140, 'emotion': 'fearful', 'score': '74.25%'}, {'start': 140, 'end': 150, 'emotion': 'sad', 'score': '94.13%'}, {'start': 150, 'end': 160, 'emotion': 'sad', 'score': '93.34%'}, {'start': 160, 'end': 170, 'emotion': 'sad', 'score': '96.29%'}, {'start': 170, 'end': 180, 'emotion': 'sad', 'score': '93.42%'}, {'start': 180, 'end': 190, 'emotion': 'calm', 'score': '73.56%'}, {'start': 190, 'end': 200, 'emotion': 'fearful', 'score': '90.21%'}, {'start': 200, 'end': 210, 'emotion': 'sad', 'score': '83.82%'}, {'start': 210, 'end': 220, 'emotion': 'sad', 'score': '74.59%'}, {'start': 220, 'end': 230, 'emotion': 'disgust', 'score': '58.05%'}, {'start': 230, 'end': 240, 'emotion': 'fearful', 'score': '62.44%'}, {'start': 240, 'end': 250, 'emotion': 'fearful', 'score': '49.08%'}, {'start': 250, 'end': 260, 'emotion': 'fearful', 'score': '46.51%'}, {'start': 260, 'end': 270, 'emotion': 'disgust', 'score': '27.03%'}, {'start': 270, 'end': 280, 'emotion': 'happy', 'score': '61.20%'}, {'start': 280, 'end': 290, 'emotion': 'surprised', 'score': '86.75%'}, {'start': 290, 'end': 300, 'emotion': 'happy', 'score': '73.43%'}, {'start': 300, 'end': 310, 'emotion': 'disgust', 'score': '88.32%'}, {'start': 310, 'end': 320, 'emotion': 'disgust', 'score': '73.27%'}, {'start': 320, 'end': 330, 'emotion': 'happy', 'score': '46.65%'}, {'start': 330, 'end': 340, 'emotion': 'disgust', 'score': '41.72%'}, {'start': 340, 'end': 350, 'emotion': 'happy', 'score': '88.07%'}, {'start': 350, 'end': 360, 'emotion': 'fearful', 'score': '93.70%'}, {'start': 360, 'end': 370, 'emotion': 'fearful', 'score': '37.32%'}, {'start': 370, 'end': 380, 'emotion': 'disgust', 'score': '72.18%'}, {'start': 380, 'end': 390, 'emotion': 'fearful', 'score': '95.17%'}, {'start': 390, 'end': 400, 'emotion': 'fearful', 'score': '78.66%'}, {'start': 400, 'end': 410, 'emotion': 'sad', 'score': '55.02%'}, {'start': 410, 'end': 420, 'emotion': 'fearful', 'score': '96.06%'}, {'start': 420, 'end': 430, 'emotion': 'sad', 'score': '40.66%'}, {'start': 430, 'end': 440, 'emotion': 'sad', 'score': '53.69%'}, {'start': 440, 'end': 450, 'emotion': 'calm', 'score': '95.02%'}, {'start': 450, 'end': 460, 'emotion': 'sad', 'score': '74.53%'}, {'start': 460, 'end': 470, 'emotion': 'fearful', 'score': '95.05%'}, {'start': 470, 'end': 480, 'emotion': 'fearful', 'score': '76.61%'}, {'start': 480, 'end': 490, 'emotion': 'sad', 'score': '50.52%'}, {'start': 490, 'end': 500, 'emotion': 'fearful', 'score': '85.35%'}, {'start': 500, 'end': 510, 'emotion': 'fearful', 'score': '95.47%'}, {'start': 510, 'end': 520, 'emotion': 'disgust', 'score': '96.64%'}, {'start': 520, 'end': 530, 'emotion': 'disgust', 'score': '80.12%'}, {'start': 530, 'end': 540, 'emotion': 'disgust', 'score': '80.05%'}, {'start': 540, 'end': 550, 'emotion': 'disgust', 'score': '79.21%'}, {'start': 550, 'end': 560, 'emotion': 'fearful', 'score': '35.38%'}, {'start': 560, 'end': 570, 'emotion': 'fearful', 'score': '66.10%'}, {'start': 570, 'end': 580, 'emotion': 'surprised', 'score': '73.26%'}, {'start': 580, 'end': 590, 'emotion': 'happy', 'score': '80.86%'}, {'start': 590, 'end': 600, 'emotion': 'sad', 'score': '88.67%'}, {'start': 600, 'end': 610, 'emotion': 'fearful', 'score': '89.50%'}, {'start': 610, 'end': 620, 'emotion': 'sad', 'score': '68.50%'}, {'start': 620, 'end': 630, 'emotion': 'fearful', 'score': '61.96%'}, {'start': 630, 'end': 640, 'emotion': 'fearful', 'score': '91.72%'}, {'start': 640, 'end': 650, 'emotion': 'fearful', 'score': '88.38%'}, {'start': 650, 'end': 660, 'emotion': 'fearful', 'score': '96.57%'}, {'start': 660, 'end': 670, 'emotion': 'fearful', 'score': '87.38%'}, {'start': 670, 'end': 680, 'emotion': 'happy', 'score': '64.22%'}, {'start': 680, 'end': 690, 'emotion': 'disgust', 'score': '52.13%'}, {'start': 690, 'end': 700, 'emotion': 'sad', 'score': '51.61%'}, {'start': 700, 'end': 710, 'emotion': 'fearful', 'score': '78.52%'}, {'start': 710, 'end': 720, 'emotion': 'fearful', 'score': '77.49%'}, {'start': 720, 'end': 730, 'emotion': 'disgust', 'score': '44.45%'}, {'start': 730, 'end': 740, 'emotion': 'fearful', 'score': '65.95%'}, {'start': 740, 'end': 750, 'emotion': 'fearful', 'score': '65.45%'}, {'start': 750, 'end': 760, 'emotion': 'fearful', 'score': '82.71%'}, {'start': 760, 'end': 770, 'emotion': 'fearful', 'score': '49.08%'}, {'start': 770, 'end': 780, 'emotion': 'fearful', 'score': '92.99%'}, {'start': 780, 'end': 790, 'emotion': 'happy', 'score': '74.66%'}, {'start': 790, 'end': 800, 'emotion': 'sad', 'score': '84.29%'}, {'start': 800, 'end': 810, 'emotion': 'sad', 'score': '93.96%'}, {'start': 810, 'end': 820, 'emotion': 'fearful', 'score': '64.15%'}, {'start': 820, 'end': 830, 'emotion': 'sad', 'score': '73.60%'}, {'start': 830, 'end': 840, 'emotion': 'sad', 'score': '62.58%'}, {'start': 840, 'end': 850, 'emotion': 'sad', 'score': '65.16%'}, {'start': 850, 'end': 860, 'emotion': 'sad', 'score': '67.73%'}, {'start': 860, 'end': 870, 'emotion': 'sad', 'score': '85.07%'}, {'start': 870, 'end': 880, 'emotion': 'sad', 'score': '53.04%'}, {'start': 880, 'end': 890, 'emotion': 'fearful', 'score': '46.81%'}, {'start': 890, 'end': 900, 'emotion': 'fearful', 'score': '59.65%'}, {'start': 900, 'end': 910, 'emotion': 'fearful', 'score': '60.36%'}, {'start': 910, 'end': 920, 'emotion': 'fearful', 'score': '76.26%'}, {'start': 920, 'end': 930, 'emotion': 'sad', 'score': '95.56%'}, {'start': 930, 'end': 938.5386875, 'emotion': 'sad', 'score': '90.81%'}]



def gerar_stream_emocional():
    start_time = datetime.now()
    current_time = start_time

    for emocao in emocoes:
        # Calcular o tempo de início e fim em segundos
        start_sec = int(emocao['start'])
        end_sec = int(emocao['end'])

        # Gerar dados para cada segundo no intervalo
        for sec in range(start_sec, end_sec):
            # Calcular o timestamp atual
            current_time = start_time + timedelta(seconds=sec)
            timestamp = current_time.isoformat()

            # Determinar valores com base na emoção
            if emocao['emotion'] in ['sad', 'fearful', 'disgust']:
                # Emoções negativas -> estresse/taquicardia
                sistolica = 130 + (float(emocao['score'][:-1]) * 0.5)
                diastolica = 85 + (float(emocao['score'][:-1]) * 0.3)
                spo2 = 95 - (float(emocao['score'][:-1]) * 0.1)
            elif emocao['emotion'] == 'happy':
                # Felicidade -> valores normais
                sistolica = 120
                diastolica = 80
                spo2 = 98
            else:
                # Calma/surpresa -> valores levemente elevados
                sistolica = 125
                diastolica = 82
                spo2 = 97

            # Limitar valores para realismo médico
            sistolica = max(90, min(180, sistolica))
            diastolica = max(60, min(120, diastolica))
            spo2 = max(85, min(100, spo2))

            # Gerar registro
            registro = {
                'timestamp': timestamp,
                'emocao': emocao['emotion'],
                'intensidade': emocao['score'],
                'sistolica': round(sistolica, 1),
                'diastolica': round(diastolica, 1),
                'spo2': round(spo2, 1),
                'estresse': 'alto' if emocao['emotion'] in ['sad', 'fearful', 'disgust'] else 'baixo'
            }

            yield json.dumps(registro)

# Exemplo de uso
for registro in gerar_stream_emocional():
    print(registro)