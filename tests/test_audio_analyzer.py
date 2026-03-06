import pytest
from unittest.mock import MagicMock, patch
import os
import sys
import numpy as np

# Add src to sys.path if not already there
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analyzers.audio import AudioAnalyzer

@pytest.fixture
def mock_openai_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")

@patch("src.analyzers.audio.pipeline")
@patch("src.analyzers.audio.OpenAI")
def test_audio_analyzer_init_success(mock_openai, mock_pipeline, mock_openai_env):
    # Setup mock pipelines
    mock_pipeline.side_effect = [MagicMock(), MagicMock()]
    
    analyzer = AudioAnalyzer()
    
    assert analyzer.audio_classifier is not None
    assert analyzer.transcriber is not None
    assert analyzer.client is not None
    assert mock_pipeline.call_count == 2

@patch("src.analyzers.audio.pipeline")
def test_audio_analyzer_init_failure(mock_pipeline, mock_openai_env):
    # Make pipeline loading fail
    mock_pipeline.side_effect = Exception("HF Load Error")
    
    analyzer = AudioAnalyzer()
    
    assert analyzer.audio_classifier is None
    # transcriber won't be set because of the exception in __init__ block
    assert not hasattr(analyzer, 'transcriber')

@patch("src.analyzers.audio.librosa.load")
@patch("src.analyzers.audio.librosa.get_duration")
@patch("src.analyzers.audio.pipeline")
def test_analyze_emotions(mock_pipeline, mock_duration, mock_load, mock_openai_env):
    # Setup mocks
    mock_audio_classifier = MagicMock()
    mock_transcriber = MagicMock()
    mock_pipeline.side_effect = [mock_audio_classifier, mock_transcriber]
    
    # Mock audio data (pulse wave)
    mock_load.return_value = (np.zeros(160000), 16000)
    mock_duration.return_value = 15.0 # 15 seconds to test windows
    
    # Mock classifier output
    mock_audio_classifier.return_value = [{"label": "happy", "score": 0.95}]
    
    analyzer = AudioAnalyzer()
    results = analyzer.analyze_emotions("dummy_audio.wav")
    
    # Should have 2 segments (0-10s, 10-15s)
    assert len(results) == 2
    assert results[0]["emotion"] == "happy"
    assert results[0]["score"] == "95.00%"
    assert results[1]["start"] == 10

@patch("src.analyzers.audio.pipeline")
def test_transcript(mock_pipeline, mock_openai_env):
    mock_audio_classifier = MagicMock()
    mock_transcriber = MagicMock()
    mock_pipeline.side_effect = [mock_audio_classifier, mock_transcriber]
    
    mock_transcriber.return_value = {"text": "Hello world", "chunks": []}
    
    analyzer = AudioAnalyzer()
    result = analyzer.transcript("dummy_audio.wav")
    
    assert result["text"] == "Hello world"
    mock_transcriber.assert_called_once_with("dummy_audio.wav", return_timestamps=True)

@patch("src.analyzers.audio.pipeline")
@patch("src.analyzers.audio.OpenAI")
def test_compose_report(mock_openai_class, mock_pipeline, mock_openai_env):
    mock_openai = MagicMock()
    mock_openai_class.return_value = mock_openai
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Audio Analysis Report"
    mock_openai.chat.completions.create.return_value = mock_response
    
    analyzer = AudioAnalyzer()
    report = analyzer.compose_report("emotions list", "transcript text")
    
    assert report == "Audio Analysis Report"
    mock_openai.chat.completions.create.assert_called_once()
