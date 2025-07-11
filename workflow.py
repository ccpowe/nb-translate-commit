"""
Main LangGraph workflow for Jupyter Notebook translation
"""
from langgraph.graph import StateGraph, START, END
from typing import Any, Dict
from state import AgentState
from notebook_io import load_and_parse_notebook, rebuild_notebook
from cell_processors import (
    process_markdown_cell, 
    process_code_cell, 
    route_cell_processing,
    skip_unsupported_cell
)

def create_notebook_translator_workflow():
    """
    Create and return the compiled LangGraph workflow for notebook translation
    
    Returns:
        Compiled StateGraph workflow
    """
    
    # Initialize the workflow
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("load_and_parse_notebook", load_and_parse_notebook)
    workflow.add_node("process_markdown_cell", process_markdown_cell)
    workflow.add_node("process_code_cell", process_code_cell)
    workflow.add_node("skip_unsupported_cell", skip_unsupported_cell)
    workflow.add_node("rebuild_notebook", rebuild_notebook)
    
    # Define edges
    # Start with loading the notebook
    workflow.add_edge(START, "load_and_parse_notebook")
    
    # After loading, route to appropriate cell processing
    workflow.add_conditional_edges(
        "load_and_parse_notebook",
        route_cell_processing,
        {
            "process_markdown_cell": "process_markdown_cell",
            "process_code_cell": "process_code_cell",
            "skip_unsupported_cell": "skip_unsupported_cell",
            "rebuild_notebook": "rebuild_notebook",
            "END": END
        }
    )
    
    # After processing markdown, route to next cell
    workflow.add_conditional_edges(
        "process_markdown_cell",
        route_cell_processing,
        {
            "process_markdown_cell": "process_markdown_cell",
            "process_code_cell": "process_code_cell",
            "skip_unsupported_cell": "skip_unsupported_cell",
            "rebuild_notebook": "rebuild_notebook", 
            "END": END
        }
    )
    
    # After processing code, route to next cell
    workflow.add_conditional_edges(
        "process_code_cell", 
        route_cell_processing,
        {
            "process_markdown_cell": "process_markdown_cell",
            "process_code_cell": "process_code_cell",
            "skip_unsupported_cell": "skip_unsupported_cell",
            "rebuild_notebook": "rebuild_notebook",
            "END": END
        }
    )
    
    # After skipping unsupported cell, route to next cell
    workflow.add_conditional_edges(
        "skip_unsupported_cell",
        route_cell_processing,
        {
            "process_markdown_cell": "process_markdown_cell",
            "process_code_cell": "process_code_cell",
            "skip_unsupported_cell": "skip_unsupported_cell",
            "rebuild_notebook": "rebuild_notebook",
            "END": END
        }
    )
    
    # After rebuilding, we're done
    workflow.add_edge("rebuild_notebook", END)
    
    # Compile the workflow
    compiled_workflow = workflow.compile()
    
    return compiled_workflow

def run_notebook_translation(input_path: str, target_language: str) -> dict:
    """
    Run the complete notebook translation workflow
    
    Args:
        input_path: Path to the input Jupyter notebook
        target_language: Target language for translation
        
    Returns:
        Final state dictionary with results
    """
    # Create the workflow
    workflow = create_notebook_translator_workflow()
    
    # Initial state
    initial_state = {
        "input_path": input_path,
        "target_language": target_language,
        "notebook_content": {},
        "processed_cells": [],
        "current_cell_index": 0,
        "total_cells": 0,
        "output_path": "",
        "error_message": None
    }
    
    print(f"🚀 Starting notebook translation workflow...")
    print(f"📁 Input: {input_path}")
    print(f"🌍 Target language: {target_language}")
    print("-" * 50)
    
    # Run the workflow with increased recursion limit
    try:
        # Configure with higher recursion limit to handle large notebooks
        config: Dict[str, Any] = {"recursion_limit": 100}  # Increased from default 25
        final_state = workflow.invoke(initial_state, config=config)
        
        if final_state.get("error_message"):
            print(f"❌ Translation failed: {final_state['error_message']}")
        else:
            print("-" * 50)
            print(f"✅ Translation completed successfully!")
            print(f"📄 Output saved to: {final_state['output_path']}")
            print(f"📊 Processed {len(final_state['processed_cells'])} cells")
        
        return final_state
        
    except Exception as e:
        error_msg = f"Workflow execution failed: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "error_message": error_msg,
            "input_path": input_path,
            "target_language": target_language
        } 