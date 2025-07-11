"""
Jupyter Notebook I/O operations
"""
import nbformat
import os
from pathlib import Path
from state import AgentState
from typing import Dict, Any

def load_and_parse_notebook(state: AgentState) -> AgentState:
    """
    Load and parse a Jupyter Notebook file
    
    Args:
        state: AgentState with input_path and target_language
    
    Returns:
        Updated AgentState with notebook_content and other initialized fields
    """
    try:
        # Validate input path
        if not os.path.exists(state["input_path"]):
            state["error_message"] = f"Input file not found: {state['input_path']}"
            return state
        
        # Read the notebook
        with open(state["input_path"], 'r', encoding='utf-8') as f:
            notebook_content = nbformat.read(f, as_version=4)
        
        # Generate output path with _translated suffix
        input_path = Path(state["input_path"])
        output_path = input_path.parent / f"{input_path.stem}_translated{input_path.suffix}"
        
        # Update state
        state.update({
            "notebook_content": notebook_content,
            "output_path": str(output_path),
            "processed_cells": [],
            "current_cell_index": 0,
            "total_cells": len(notebook_content.cells),
            "error_message": None
        })
        
        print(f"Loaded notebook: {state['input_path']}")
        print(f"Total cells: {state['total_cells']}")
        print(f"Output will be saved to: {state['output_path']}")
        
        return state
        
    except Exception as e:
        state["error_message"] = f"Error loading notebook: {str(e)}"
        print(f"Error: {state['error_message']}")
        return state

def rebuild_notebook(state: AgentState) -> AgentState:
    """
    Rebuild the notebook with processed cells and save to output path
    
    Args:
        state: AgentState with processed_cells and output_path
    
    Returns:
        Updated AgentState with completion status
    """
    try:
        if state.get("error_message"):
            print(f"Cannot rebuild notebook due to error: {state['error_message']}")
            return state
        
        # Create a copy of the original notebook structure
        output_notebook = state["notebook_content"].copy()
        
        # Replace cells with processed ones
        output_notebook["cells"] = state["processed_cells"]
        
        # Ensure output directory exists
        output_path = Path(state["output_path"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the notebook
        with open(state["output_path"], 'w', encoding='utf-8') as f:
            nbformat.write(output_notebook, f)
        
        print(f"✅ Translated notebook saved to: {state['output_path']}")
        
        return state
        
    except Exception as e:
        error_msg = f"Error saving notebook: {str(e)}"
        state["error_message"] = error_msg
        print(f"Error: {error_msg}")
        return state

def validate_notebook_structure(notebook_content: Dict[Any, Any]) -> bool:
    """
    Validate that the notebook has the expected structure
    
    Args:
        notebook_content: Parsed notebook content
    
    Returns:
        True if valid, False otherwise
    """
    try:
        # Check for required fields
        required_fields = ['cells', 'metadata', 'nbformat', 'nbformat_minor']
        for field in required_fields:
            if field not in notebook_content:
                return False
        
        # Check that cells is a list
        if not isinstance(notebook_content['cells'], list):
            return False
        
        # Check each cell has required fields
        for cell in notebook_content['cells']:
            if 'cell_type' not in cell or 'source' not in cell:
                return False
        
        return True
        
    except Exception:
        return False 