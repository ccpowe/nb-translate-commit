"""
Cell processing modules for different notebook cell types
"""
import re
from state import AgentState
from llm_client import LLMClient, get_image_data
from config import get_translation_label, get_description_label
from typing import Dict, Any
import copy

# Initialize LLM client
llm_client = LLMClient()

def process_markdown_cell(state: AgentState) -> AgentState:
    """
    Process a markdown cell: translate text and describe images
    
    Args:
        state: AgentState with current cell to process
        
    Returns:
        Updated AgentState with processed cell added to processed_cells
    """
    try:
        current_index = state["current_cell_index"]
        if current_index >= len(state["notebook_content"]["cells"]):
            state["error_message"] = "Cell index out of range"
            return state
            
        cell = state["notebook_content"]["cells"][current_index]
        
        # Create a copy of the cell to modify
        processed_cell = copy.deepcopy(cell)
        
        if cell["cell_type"] != "markdown":
            state["error_message"] = f"Expected markdown cell, got {cell['cell_type']}"
            return state
        
        original_source = cell["source"]
        target_language = state["target_language"]
        
        # Process the source content
        new_source_lines = []
        
        # Regex to find images: ![alt](src)
        image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
        
        # Process the content by sections (separated by blank lines or headers)
        if isinstance(original_source, list):
            source_text = ''.join(original_source)
        else:
            source_text = original_source
        source_lines = source_text.split('\n')
        
        current_section = []
        sections = []
        
        # Group lines into sections
        for line in source_lines:
            if line.strip() == "" or line.startswith('#'):
                if current_section:
                    sections.append(current_section)
                    current_section = []
                if line.strip():  # Add the header line to start new section
                    current_section.append(line)
            else:
                current_section.append(line)
        
        # Add the last section if exists
        if current_section:
            sections.append(current_section)
        
        # Process each section
        for section in sections:
            if not section:
                continue
                
            section_text = '\n'.join(section)
            
            # Add original section
            new_source_lines.extend(section)
            
            # Check for images in the section
            image_matches = image_pattern.findall(section_text)
            for alt_text, src in image_matches:
                try:
                    # Get image data and generate description
                    # Pass input_path to resolve relative image paths
                    image_data = get_image_data(src, state.get("input_path"))
                    description = llm_client.describe_image(image_data, target_language)
                    description_label = get_description_label(target_language)
                    new_source_lines.append("")
                    new_source_lines.append(f"**{description_label}：**")
                    new_source_lines.append(description)
                    print(f"✅ Generated image description for: {src}")
                except Exception as e:
                    print(f"⚠️ Could not process image {src}: {e}")
            
            # Translate the section if it contains meaningful text
            if any(line.strip() and not line.startswith('!') for line in section):
                try:
                    # Translate the entire section
                    translation = llm_client.translate_text(section_text, target_language)
                    translation_label = get_translation_label(target_language)
                    
                    # Add translation with better formatting
                    new_source_lines.append("")
                    new_source_lines.append(f"**{translation_label}：**")
                    new_source_lines.append(translation)
                    print(f"✅ Translated section: {section_text[:50]}...")
                except Exception as e:
                    print(f"⚠️ Could not translate section: {e}")
            
            # Add spacing between sections
            new_source_lines.append("")
        
        # Update the cell source
        processed_cell["source"] = new_source_lines
        
        # Add to processed cells
        state["processed_cells"].append(processed_cell)
        state["current_cell_index"] += 1
        
        print(f"📝 Processed markdown cell {current_index + 1}/{state['total_cells']}")
        
        return state
        
    except Exception as e:
        state["error_message"] = f"Error processing markdown cell: {str(e)}"
        print(f"Error: {state['error_message']}")
        return state

def process_code_cell(state: AgentState) -> AgentState:
    """
    Process a code cell: add explanatory comments and translate existing comments
    
    Args:
        state: AgentState with current cell to process
        
    Returns:
        Updated AgentState with processed cell added to processed_cells
    """
    try:
        current_index = state["current_cell_index"]
        if current_index >= len(state["notebook_content"]["cells"]):
            state["error_message"] = "Cell index out of range"
            return state
            
        cell = state["notebook_content"]["cells"][current_index]
        
        # Create a copy of the cell to modify
        processed_cell = copy.deepcopy(cell)
        
        if cell["cell_type"] != "code":
            state["error_message"] = f"Expected code cell, got {cell['cell_type']}"
            return state
        
        original_source = cell["source"]
        target_language = state["target_language"]
        
        # Convert source to string if it's a list
        if isinstance(original_source, list):
            code_content = ''.join(original_source)
        else:
            code_content = original_source
        
        try:
            # Add comments and translate existing ones
            enhanced_code = llm_client.add_code_comments(code_content, target_language)
            
            # Clean up any markdown code block wrapping that might have been added
            enhanced_code = enhanced_code.strip()
            if enhanced_code.startswith('```python'):
                enhanced_code = enhanced_code[9:]  # Remove ```python
            elif enhanced_code.startswith('```'):
                enhanced_code = enhanced_code[3:]   # Remove generic ```
            if enhanced_code.endswith('```'):
                enhanced_code = enhanced_code[:-3]  # Remove ending ```
            enhanced_code = enhanced_code.strip()
            
            processed_cell["source"] = enhanced_code
            print(f"✅ Enhanced code cell {current_index + 1}/{state['total_cells']}")
        except Exception as e:
            print(f"⚠️ Could not enhance code cell: {e}")
            # Keep original code if enhancement fails
            processed_cell["source"] = original_source
        
        # Add to processed cells
        state["processed_cells"].append(processed_cell)
        state["current_cell_index"] += 1
        
        print(f"💻 Processed code cell {current_index + 1}/{state['total_cells']}")
        
        return state
        
    except Exception as e:
        state["error_message"] = f"Error processing code cell: {str(e)}"
        print(f"Error: {state['error_message']}")
        return state

def route_cell_processing(state: AgentState) -> str:
    """
    Router function to determine which processing node to use next
    
    Args:
        state: Current AgentState
        
    Returns:
        Next node name or END
    """
    try:
        # Check for errors
        if state.get("error_message"):
            return "END"
        
        # Check if we've processed all cells
        current_index = state["current_cell_index"]
        total_cells = state["total_cells"]
        
        if current_index >= total_cells:
            print("🎉 All cells processed successfully!")
            return "rebuild_notebook"
        
        # Get the current cell type
        cell = state["notebook_content"]["cells"][current_index]
        cell_type = cell["cell_type"]
        
        if cell_type == "markdown":
            return "process_markdown_cell"
        elif cell_type == "code":
            return "process_code_cell"
        else:
            # For other cell types (raw, etc.), just copy as-is
            processed_cell = copy.deepcopy(cell)
            state["processed_cells"].append(processed_cell)
            state["current_cell_index"] += 1
            print(f"⏭️ Skipped {cell_type} cell {current_index + 1}/{total_cells}")
            
            # Check if there are more cells to process after skipping this one
            if state["current_cell_index"] >= total_cells:
                return "rebuild_notebook"
            else:
                # Get the next cell type to route to appropriate processor
                next_cell = state["notebook_content"]["cells"][state["current_cell_index"]]
                next_cell_type = next_cell["cell_type"]
                if next_cell_type == "markdown":
                    return "process_markdown_cell"
                elif next_cell_type == "code":
                    return "process_code_cell"
                else:
                    # If next cell is also unsupported, create a special routing
                    return "skip_unsupported_cell"
            
    except Exception as e:
        state["error_message"] = f"Error in routing: {str(e)}"
        print(f"Error: {state['error_message']}")
        return "END"

def skip_unsupported_cell(state: AgentState) -> AgentState:
    """
    Skip unsupported cell types by copying them as-is
    
    Args:
        state: AgentState with current cell to process
        
    Returns:
        Updated AgentState with cell copied to processed_cells
    """
    try:
        current_index = state["current_cell_index"]
        if current_index >= len(state["notebook_content"]["cells"]):
            return state
            
        cell = state["notebook_content"]["cells"][current_index]
        
        # Copy cell as-is
        processed_cell = copy.deepcopy(cell)
        state["processed_cells"].append(processed_cell)
        state["current_cell_index"] += 1
        
        print(f"⏭️ Skipped {cell['cell_type']} cell {current_index + 1}/{state['total_cells']}")
        
        return state
        
    except Exception as e:
        state["error_message"] = f"Error skipping cell: {str(e)}"
        return state 