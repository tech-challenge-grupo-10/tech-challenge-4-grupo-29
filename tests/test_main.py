import pytest
from io import StringIO
import sys

def test_main_output(capsys):
    from src.main import create_app
    app = create_app()
    assert app is not None