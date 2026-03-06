# 🧠 Sistema de Análise de Saúde Mental Multimodal

Este projeto é um assistente de triagem para auxílio no pré-diagnóstico de sinais psicológicos. Ele utiliza modelos de Inteligência Artificial para analisar diferentes fontes de dados, como documentos clínicos (PDF), gravações de áudio e dados de sensores fisiológicos (TXT/CSV), fornecendo uma visão integrada e contínua do estado do paciente.

---

## 🚀 Funcionalidades

- **📄 Análise de Documentos (PDF):** Extração de texto e análise de prontuários ou relatórios clínicos.
- **🎤 Análise de Áudio:** Transcrição e identificação de emoções em gravações de voz.
- **❤️ Monitoramento de Sensores (Streaming):** Processamento em tempo real de dados como Pressão Arterial (Sistólica/Diastólica) e Saturação de Oxigênio (SpO2).
- **📊 Dashboard Interativo:** Interface amigável construída com Gradio para visualização de relatórios e gráficos (gauge, radar) em tempo real.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.13+
- **Interface:** [Gradio](https://gradio.app/)
- **Análise de Dados:** Pandas, NumPy
- **IA e ML:** OpenAI/GenAI, Transformers, DeepFace, Librosa, PyTorch/TensorFlow (keras)
- **Processamento de PDF:** Azure AI Document Intelligence
- **Visualização:** Plotly
- **Gerenciamento de Pacotes:** [uv](https://github.com/astral-sh/uv)

---

## ⚙️ Pré-requisitos

Antes de começar, você precisará ter instalado:
- [Python 3.13](https://www.python.org/)
- [uv](https://github.com/astral-sh/uv) (Recomendado para gerenciamento de dependências e execução)

---

## 🔧 Instalação e Execução

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/tech-challenge-4-grupo-29.git
   cd tech-challenge-4-grupo-29
   ```

2. **Configure as variáveis de ambiente:**
   Crie um arquivo `.env` na raiz do projeto com suas chaves de API necessárias (OpenAI, Azure, etc.):
   ```env
   # Exemplo
   OPENAI_API_KEY=sua_chave_aqui
   DOCUMENT_INTELLIGENCE_ENDPOINT=seu_endpoint_aqui
   DOCUMENT_INTELLIGENCE_KEY=sua_chave_aqui
   ```

3. **Inicie a aplicação utilizando o `uv`:**
   O projeto utiliza o `taskipy` para facilitar a execução.
   ```bash
   uv run task start
   ```
   A interface abrirá automaticamente no seu navegador, geralmente em `http://127.0.0.1:7860`.

### 🐳 Execução via Docker

O projeto também pode ser executado em um container Docker, que já inclui um servidor NGINX configurado como proxy reverso.

1. **Certifique-se de que o Docker está instalado.**
2. **Construa a imagem:**
   ```bash
   docker build -t tech-challenge-4-saude-mental .
   ```
3. **Execute o container:**
   ```bash
   docker run -p 80:80 --env-file .env tech-challenge-4-saude-mental
   ```
   A aplicação estará disponível na porta 80: `http://localhost`.

---

## 🧪 Testes

Para rodar os testes unitários e verificar a cobertura:
```bash
# Rodar testes
uv run task test

# Rodar testes com relatório de cobertura
uv run task test-coverage
```

---

## 📂 Estrutura do Projeto

- `src/`: Código fonte principal.
  - `analyzers/`: Módulos de análise (áudio, texto, sensores).
  - `ui/`: Componentes da interface e gráficos.
  - `main.py`: Ponto de entrada da aplicação.
- `data/`: Diretório para arquivos de exemplo e datasets.
- `tests/`: Testes automatizados.
- `pyproject.toml`: Configurações de dependências e tarefas.

---

> [!IMPORTANT]
> **Aviso Médico**: Esta ferramenta é um *assistente de triagem* e não substitui de forma alguma a avaliação de um profissional de saúde mental capacitado.