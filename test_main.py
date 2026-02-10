import pytest
from io import StringIO
import sys

def test_main_output(capsys):
    # Redirect stdout to capture print output
    captured = StringIO()
    sys.stdout = captured

    # Import and call the function
    from main import main
    main()

    # Get the output and restore stdout
    output = captured.getvalue()
    sys.stdout = sys.__stdout__

    # Verify the output
    assert "Hello from tech-challenge-4-grupo-29!" in output