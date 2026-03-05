

class TextAnalyzer:
    """Classe responsável por transcrever o áudio e aplicar NLP para risco psicológico."""
    
    def __init__(self):
        pass
        # Whisper: modelo 'base' ou 'tiny' para rodar bem em CPU
        # self.client = 
        # Analisador de sentimento multilingue para marcadores de agressividade/depressão (negatividade)
        #self.sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment", device=-1)

    def analyze(self, pdf_path):
        """Transcreve e analisa o sentimento do texto."""
        try:
            # 1. Transcrição
            transcription = self.transcriber.transcribe(pdf_path, fp16=False) # fp16=False evita warnings na CPU
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
