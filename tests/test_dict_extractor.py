import os
import json
import tempfile
from pathlib import Path
import pytest
from python_toolkit.dict_extractor import DictionaryExtractor

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)

@pytest.fixture
def sample_python_file(temp_dir):
    content = '''
__artifacts_v2__ = {
    "artifact1": {
        "name": "test1",
        "value": 123
    },
    "artifact2": {
        "name": "test2",
        "value": ["a", "b", "c"]
    }
}
'''
    file_path = temp_dir / "test.py"
    with open(file_path, "w") as f:
        f.write(content)
    return file_path

def test_dictionary_extractor(temp_dir, sample_python_file):
    output_file = temp_dir / "output.json"
    extractor = DictionaryExtractor(str(temp_dir), str(output_file))
    extractor.run()
    
    # Check if output file exists
    assert output_file.exists()
    
    # Check content
    with open(output_file) as f:
        data = json.load(f)
    
    assert "test.py" in data
    assert "artifact1" in data["test.py"]
    assert data["test.py"]["artifact1"]["name"] == "test1"
    assert data["test.py"]["artifact1"]["value"] == 123
    assert data["test.py"]["artifact2"]["value"] == ["a", "b", "c"]

def test_dictionary_extractor_empty_folder(temp_dir):
    output_file = temp_dir / "output.json"
    extractor = DictionaryExtractor(str(temp_dir), str(output_file))
    extractor.run()
    
    # Check if output file exists with empty data
    assert output_file.exists()
    with open(output_file) as f:
        data = json.load(f)
    assert data == {} 