import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()


def notify_medical_team(risk_level: str) -> bool:
    """
    Envia um e-mail de alerta para a equipe médica via Gmail SMTP.
    Retorna True se o envio foi bem-sucedido, False caso contrário.
    """
    smtp_from = os.getenv("SMTP_FROM")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_to = os.getenv("SMTP_TO")

    if not all([smtp_from, smtp_password, smtp_to]):
        print("Aviso: Variáveis SMTP não configuradas. Notificação não enviada.")
        return False

    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"⚠️ ALERTA DE SAÚDE MENTAL — {timestamp}"
    msg["From"] = smtp_from
    msg["To"] = smtp_to

    body = f"""\
Sistema de Pré-Diagnóstico Multimodal detectou um alerta.

Horário: {timestamp}
Diagnóstico: {risk_level}

---
Este é um alerta automático gerado pelo Sistema de Análise de Saúde Mental Multimodal.
NÃO substitui avaliação de profissional de saúde mental capacitado.
"""
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(smtp_from, smtp_password)
            server.sendmail(smtp_from, smtp_to, msg.as_string())
        print(f"✅ Notificação de alerta enviada para {smtp_to}")
        return True
    except Exception as e:
        print(f"❌ Falha ao enviar notificação: {e}")
        return False
