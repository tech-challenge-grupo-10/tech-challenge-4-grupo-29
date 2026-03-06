import pytest
from unittest.mock import MagicMock, patch, mock_open
import os
import sys

# Add src to sys.path if not already there
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analyzers.text import TextAnalyzer

@pytest.fixture
def mock_env(monkeypatch):
    monkeypatch.setenv("DOCUMENTINTELLIGENCE_ENDPOINT", "http://test-endpoint")
    monkeypatch.setenv("DOCUMENTINTELLIGENCE_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")

def test_text_analyzer_init_success(mock_env):
    analyzer = TextAnalyzer()
    assert analyzer.document_intelligence_client is not None
    assert analyzer.client is not None

def test_text_analyzer_init_failure(monkeypatch):
    # Remove env vars to trigger exit
    monkeypatch.delenv("DOCUMENTINTELLIGENCE_ENDPOINT", raising=False)
    monkeypatch.delenv("DOCUMENTINTELLIGENCE_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    
    with pytest.raises(SystemExit):
        TextAnalyzer()

@patch("src.analyzers.text.DocumentIntelligenceClient")
def test_analyze_success(mock_client_class, mock_env):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_poller = MagicMock()
    mock_result = MagicMock()
    mock_result.content = "Detected text content"
    mock_poller.result.return_value = mock_result
    mock_client.begin_analyze_document.return_value = mock_poller
    
    analyzer = TextAnalyzer()
    
    with patch("builtins.open", mock_open(read_data=b"pdf content")):
        result = analyzer.analyze("dummy.pdf")
        
    assert result == {"text": "Detected text content"}
    mock_client.begin_analyze_document.assert_called_once()

@patch("src.analyzers.text.DocumentIntelligenceClient")
def test_analyze_no_content(mock_client_class, mock_env):
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    mock_poller = MagicMock()
    mock_result = MagicMock()
    mock_result.content = None
    mock_poller.result.return_value = mock_result
    mock_client.begin_analyze_document.return_value = mock_poller
    
    analyzer = TextAnalyzer()
    
    with patch("builtins.open", mock_open(read_data=b"pdf content")):
        result = analyzer.analyze("dummy.pdf")
        
    assert result is None

@patch("src.analyzers.text.OpenAI")
def test_compose_report(mock_openai_class, mock_env):
    mock_openai = MagicMock()
    mock_openai_class.return_value = mock_openai
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "AI Generated Report"
    mock_openai.chat.completions.create.return_value = mock_response
    
    analyzer = TextAnalyzer()
    report = analyzer.compose_report("input text")
    
    assert report == "AI Generated Report"
    mock_openai.chat.completions.create.assert_called_once()
