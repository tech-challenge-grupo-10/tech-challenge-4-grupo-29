import os

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult

from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()

class TextAnalyzer:
    """Classe responsável por ler laudos médicos, receitas e relatórios médicos para ajudara a identificar risco psicológico."""
    
    def __init__(self):
        try:
            endpoint = os.environ["DOCUMENTINTELLIGENCE_ENDPOINT"]
            key = os.environ["DOCUMENTINTELLIGENCE_API_KEY"]
            api_key=os.environ["OPENAI_API_KEY"]
        except KeyError:
            print("Please set the DOCUMENTINTELLIGENCE_ENDPOINT, DOCUMENTINTELLIGENCE_API_KEY and OPENAI_API_KEY environment variables.")
            exit()

        credential = AzureKeyCredential(key)
        self.document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=credential)
        self.client = OpenAI(api_key=api_key)

    def analyze(self, pdf_path):
        with open(pdf_path, "rb") as f:
            poller = self.document_intelligence_client.begin_analyze_document(
                model_id="prebuilt-read", 
                body=f
            )

            result: AnalyzeResult = poller.result()

            if result.content:
                return {"text": result.content}

            else:
                print("No documents found in the result.")
                return None

    def compose_report(self, text):
        prompt = f"""
            Analise o conteúdo destes documents:
            ${text}

            Regras:
            - Quando identificar um laudo médico, verifique está correto e adequado e traga os possíveis tratamentos que podem ser realizados em continuidade ao que foi identificado pelo médico
            - Quando identificar um receituário medicamentoso, verifique se este é o melhor tratamento para o paciente, caso hajam outros tratamentos descreva os pontos positivos e negativos comparados a receita apresentada
            - Componha um análise sobre o conteúdo de todos os documentos presentes e como eles se relacionam para ajudar o paciente.
            - Ao final monte uma tabela de resumo.
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "Você é um médico psiquiatra com mais de 20 anos de experiência. Analise o texto abaixo e me diga se há indícios de depressão, ansiedade ou qualquer outro transtorno mental. Seja objetivo e direto."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
