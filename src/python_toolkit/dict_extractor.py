#!/usr/bin/env python3
"""
Dictionary Extractor - Extract complete artifact structures from Python files
Outputs comprehensive JSON with all artifact data from all files
"""
import os
import sys
import json
import ast
import traceback
import argparse
import shlex
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

class DictionaryExtractor:
    def __init__(self, folder_path: str, output_file: str = "extracted_artifacts.json"):
        self.folder_path = Path(folder_path)
        self.output_file = output_file
        self.extracted_data = {}
        self.stats = {
            'files_processed': 0,
            'files_with_errors': 0,
            'total_artifacts': 0
        }
    
    def extract_value_from_node(self, node):
        """Extract value from AST node, handling various node types."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.List):
            return [self.extract_value_from_node(item) for item in node.elts]
        elif isinstance(node, ast.Tuple):
            return tuple(self.extract_value_from_node(item) for item in node.elts)
        elif isinstance(node, ast.Dict):
            result = {}
            for key_node, value_node in zip(node.keys, node.values):
                key = self.extract_value_from_node(key_node)
                value = self.extract_value_from_node(value_node)
                result[key] = value
            return result
        elif isinstance(node, ast.Name):
            return f"<{node.id}>"  # Mark as variable reference
        elif isinstance(node, ast.Call):
            return f"<function_call:{self.extract_value_from_node(node.func)}>"
        else:
            return f"<{type(node).__name__}>"

    def extract_artifacts_from_file(self, file_path: Path) -> Dict[str, Any]:
        """Extract __artifacts_v2__ or __artifacts__ from a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse the file content into an AST
            tree = ast.parse(content)
            
            artifacts = {}
            
            # Walk through the AST to find dictionary assignments
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    # Check if it's a dictionary assignment
                    if (len(node.targets) == 1 and 
                        isinstance(node.targets[0], ast.Name) and
                        isinstance(node.value, ast.Dict)):
                        
                        var_name = node.targets[0].id
                        
                        # Look for artifacts dictionaries
                        if var_name in ['__artifacts__', '__artifacts_v2__']:
                            # Extract dictionary manually from AST
                            try:
                                dict_value = {}
                                for key_node, value_node in zip(node.value.keys, node.value.values):
                                    key = self.extract_value_from_node(key_node)
                                    value = self.extract_value_from_node(value_node)
                                    dict_value[key] = value
                                
                                # Store all artifacts from this file
                                if isinstance(dict_value, dict):
                                    artifacts.update(dict_value)
                                    self.stats['total_artifacts'] += len(dict_value)
                                
                            except Exception as e:
                                print(f"  Warning: Could not process artifacts in '{file_path.name}': {e}")
                                continue
            
            return artifacts
        
        except SyntaxError as e:
            print(f"  Syntax error in {file_path}: {e}")
            self.stats['files_with_errors'] += 1
            return {}
        except Exception as e:
            print(f"  Error processing {file_path}: {e}")
            self.stats['files_with_errors'] += 1
            return {}
    
    def scan_folder(self) -> Dict[str, Any]:
        """Scan folder for Python files and extract artifacts."""
        if not self.folder_path.exists():
            raise FileNotFoundError(f"Folder '{self.folder_path}' does not exist.")
        
        # Get all Python files in the folder (including subdirectories)
        python_files = list(self.folder_path.glob('**/*.py'))
        
        # Filter out extractor files
        excluded_files = {'dictionary_extractor.py', 'run_extractor.py', 'debug_parser.py', 'run_extractor_safe.py', 'dict_extractor.py'}
        python_files = [f for f in python_files if f.name not in excluded_files]
        
        print(f"Found {len(python_files)} Python files to process...")
        
        for py_file in python_files:
            print(f"Processing: {py_file.relative_to(self.folder_path)}")
            self.stats['files_processed'] += 1
            
            # Extract artifacts from the file
            file_artifacts = self.extract_artifacts_from_file(py_file)
            
            if file_artifacts:
                file_name = py_file.name
                self.extracted_data[file_name] = file_artifacts
        
        return self.extracted_data
    
    def save_to_json(self) -> None:
        """Save extracted data to JSON file."""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.extracted_data, f, indent=2, ensure_ascii=False)
    
    def print_stats(self) -> None:
        """Print extraction statistics."""
        print(f"\n{'='*50}")
        print("EXTRACTION STATISTICS")
        print(f"{'='*50}")
        print(f"Files processed: {self.stats['files_processed']}")
        print(f"Files with errors: {self.stats['files_with_errors']}")
        print(f"Files with artifacts: {len(self.extracted_data)}")
        print(f"Total artifacts extracted: {self.stats['total_artifacts']}")
        print(f"Output saved to: {self.output_file}")
    
    def run(self) -> None:
        """Main execution method."""
        try:
            print(f"Scanning folder: {self.folder_path}")
            self.scan_folder()
            self.save_to_json()
            self.print_stats()
            
        except Exception as e:
            print(f"Error during execution: {e}")
            traceback.print_exc()

def validate_args(args):
    """Validate command line arguments."""
    if not args.input_path:
        raise argparse.ArgumentError(None, 'No INPUT_PATH provided. Run the program again.')
    
    if not args.output_path:
        raise argparse.ArgumentError(None, 'No OUTPUT_PATH provided. Run the program again.')
    
    if not os.path.exists(args.input_path):
        raise argparse.ArgumentError(None, f'Input path \'{args.input_path}\' does not exist!')
    
    if not os.path.exists(args.output_path):
        try:
            os.makedirs(args.output_path)
        except Exception as e:
            raise argparse.ArgumentError(None, f'Could not create output directory: {str(e)}')

def main():
    """Main function - processes command line arguments and runs the extractor."""
    parser = argparse.ArgumentParser(
        description="Dictionary Extractor - Extract complete artifact structures from Python files"
    )
    parser.add_argument(
        "-i", "--input_path",
        required=True,
        help="Input folder path to scan for Python files"
    )
    parser.add_argument(
        "-o", "--output_path",
        help="Output folder path for the JSON file (default: current directory)",
        default="."
    )
    
    # If no arguments provided, use sys.argv
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    try:
        args = parser.parse_args()
        validate_args(args)
        
        # Generate automatic output filename with timestamp
        output_file = os.path.join(args.output_path, f"extracted_artifacts.json")
        
        # Create extractor and run
        extractor = DictionaryExtractor(args.input_path, output_file)
        extractor.run()
        
    except Exception as e:
        print(f"Error occurred: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
