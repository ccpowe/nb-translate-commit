"""
State definition for the Jupyter Notebook Translator Agent
"""
from typing import TypedDict, List, Dict, Optional

class AgentState(TypedDict):
    """
    Represents the state of the notebook processing workflow.
    """
    input_path: str                     # Path to the original .ipynb file
    output_path: str                    # Path for the new, translated .ipynb file
    notebook_content: Dict              # The entire notebook structure, parsed by nbformat
    processed_cells: List[Dict]         # List of cells after processing
    target_language: str                # The language to translate to (e.g., "Chinese", "Spanish", "French", etc.)
    current_cell_index: int             # Index of the current cell being processed
    total_cells: int                    # Total number of cells in the notebook
    error_message: Optional[str]        # Error message if processing fails 