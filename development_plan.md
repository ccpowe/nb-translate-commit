# Project Development Plan: AI-Powered Jupyter Notebook Translator

## 1. Project Overview

**Goal:** To develop an intelligent agent using LangGraph that automates the translation and enrichment of Jupyter Notebooks (`.ipynb` files).

**Final Deliverable:** A Python application that accepts a path to a Jupyter Notebook and a target language, then generates a new, enhanced version with the `_translated` suffix. This new file will contain:
*   **Markdown Cells:** Original text paired with translations, and original images paired with generated descriptions.
*   **Code Cells:** Original code augmented with explanatory comments and translated existing comments.

The primary aim is to make educational content in Jupyter Notebooks more accessible across different languages, supporting flexible source-to-target language translation.

## 2. Technical Selection

*   **Core Framework:** **LangGraph** - To orchestrate the workflow as a state machine, managing the notebook processing from start to finish.
*   **LLM Interaction:** **OpenAI-compatible SDK** via **OpenRouter** - Using OpenRouter as the API gateway to access multiple models with a unified interface. This provides flexibility to switch between different models while maintaining consistent code.
*   **Notebook Parsing:** **`nbformat`** - The official Python library for reading, writing, and manipulating the JSON structure of Jupyter Notebooks.
*   **Language Model (LLM):** **google/gemini-2.5-flash-preview-05-20** via OpenRouter - A powerful multimodal model that can handle text translation, code commenting, and image description within a single API, simplifying the architecture.
*   **Environment Management:** `pip` with a `requirements.txt` file to manage dependencies, and `.env` file for API configuration.
*   **Documentation Reference:** **Context7** for accessing official documentation during development.

## 3. Architecture Design

The application will be modeled as a stateful graph where each node performs a specific task. The state will be passed between nodes, carrying the notebook data as it gets processed.

### 3.1. State Definition

We'll define a central state object that tracks the entire process.

```python
from typing import TypedDict, List, Dict

class AgentState(TypedDict):
    """
    Represents the state of the notebook processing workflow.
    """
    input_path: str          # Path to the original .ipynb file
    output_path: str         # Path for the new, translated .ipynb file
    notebook_content: Dict   # The entire notebook structure, parsed by nbformat
    processed_cells: List[Dict] # List of cells after processing
    target_language: str     # The language to translate to (e.g., "Chinese", "Spanish", "French", etc.)
```

### 3.2. LangGraph Flow

The graph will manage the flow of operations, processing each cell according to its type.

**(Entry Point)** -> `load_and_parse_notebook` -> `process_cells_router` -> ... (loop) ... -> `rebuild_notebook` -> **(End Point)**

### 3.3. Node Functions

1.  **`load_and_parse_notebook`**:
    *   **Input:** `AgentState` (with `input_path` and `target_language`).
    *   **Action:**
        *   Reads the `.ipynb` file from `input_path` using `nbformat`.
        *   Stores the parsed content in `notebook_content`.
        *   Generates the `output_path`.
        *   Initializes `processed_cells` as an empty list.
    *   **Output:** Updated `AgentState`.

2.  **`process_cells_router` (Conditional Edge)**:
    *   **Action:** This is not a standard node but a conditional function that directs the flow. It inspects the `notebook_content` and routes to the next appropriate node.
    *   **Logic:**
        *   If there are still unprocessed cells, pick the next one.
        *   If the cell is `markdown`, return "process_markdown".
        *   If the cell is `code`, return "process_code".
        *   If all cells are processed, return "rebuild_notebook".

3.  **`process_markdown_cell`**:
    *   **Input:** `AgentState` (with the current cell to process).
    *   **Action:** This is a multi-task node.
        *   It parses the Markdown source to identify text blocks and image tags (`![alt](src)`).
        *   **For Text:** Sends the text to the LLM for translation, carefully instructing the model to preserve Markdown syntax. Appends the translation below the original text with the `**中文翻译：**` marker.
        *   **For Images:** For each image, it calls a helper function `get_image_data(src)` to fetch the image bytes (whether from a URL, local path, or embedded base64). It then sends the image data to the vision model and asks for a detailed description. The description is inserted below the image tag with the `**图片说明：**` marker.
    *   **Output:** Appends the modified cell to the `processed_cells` list in `AgentState`.

4.  **`process_code_cell`**:
    *   **Input:** `AgentState` (with the current cell to process).
    *   **Action:**
        *   Sends the entire code block to the LLM.
        *   The prompt will instruct the LLM to:
            1.  Add detailed, line-by-line comments explaining the code's function.
            2.  Translate any existing English comments into the `target_language`.
    *   **Output:** Appends the modified cell to the `processed_cells` list in `AgentState`.

5.  **`rebuild_notebook`**:
    *   **Input:** `AgentState` (with the complete `processed_cells` list).
    *   **Action:**
        *   Takes the `processed_cells` and updates the `cells` key in the original `notebook_content`.
        *   Uses `nbformat.write()` to save the modified `notebook_content` to the `output_path`.
    *   **Output:** Final state. The process is complete.

## 4. Development Steps & Priority

### Priority 1: Foundation (I/O and Structure)

1.  **Project Setup:**
    *   Initialize a Git repository.
    *   Set up a virtual environment.
    *   Create `requirements.txt` with `langgraph`, `openai`, `nbformat`, `python-dotenv`, and `requests`.
    *   Create `.env` file with the following configuration:
        ```
        API_KEY=sk-or-v1-3a6118b505755ea749f953ef5dfbade9b18bf5e7cd1b070
        MODEL_NAME=google/gemini-2.5-flash-preview-05-20
        MODEL_BASE_URL=https://openrouter.ai/api/v1
        ```
    *   Use **Context7** to access official documentation for LangGraph, OpenAI SDK, and nbformat during development.
2.  **Implement Notebook I/O:**
    *   Create the main script.
    *   Implement the `load_and_parse_notebook` function to correctly read an `.ipynb` file.
    *   Implement a basic `rebuild_notebook` function that writes the *unmodified* data to a new file.
    *   **Goal:** Ensure a notebook can be read and written back perfectly before adding any processing.

### Priority 2: Core Features (Parallel Development)

These modules can be developed concurrently after the foundation is stable.

1.  **Code Cell Commenting:**
    *   Implement the `process_code_cell` node.
    *   Develop a robust prompt that encourages the LLM to add comments without altering the code itself.
    *   Test with various code complexities.
2.  **Markdown Text Translation:**
    *   Begin implementing the `process_markdown_cell` node, focusing only on text.
    *   Develop a prompt that translates content while strictly preserving Markdown formatting (headings, links, bold, etc.).
    *   Test with complex Markdown documents.
3.  **Image Description:**
    *   Implement the `get_image_data(src)` helper function. This is critical and must handle:
        *   Web URLs (using a library like `requests`).
        *   Local file paths.
        *   Base64-encoded images embedded directly in the Markdown (`data:image/...`).
    *   Integrate this into `process_markdown_cell`, sending the image data to the vision model.
    *   Develop a prompt to generate concise yet descriptive explanations.

### Priority 3: Integration and Refinement

1.  **Build the Graph:** Assemble all the nodes and the conditional router in LangGraph.
2.  **End-to-End Testing:** Run the full agent on a variety of real-world notebooks.
3.  **Error Handling:** Implement robust error handling (e.g., for invalid file paths, failed API calls, broken image links).
4.  **Configuration:** 
    *   Make the `target_language` a command-line argument (e.g., `--target-language "Spanish"`).
    *   Load environment variables from `.env` file for API configuration.
    *   Support multiple target languages with appropriate labels (e.g., "翻译" for Chinese, "Translation" for English, "Traducción" for Spanish).

## 5. Key Code Samples / Pseudocode

**Environment Configuration:**
```python
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client with OpenRouter configuration
client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("MODEL_BASE_URL")
)

model_name = os.getenv("MODEL_NAME")
```

**`nbformat` Usage:**
```python
import nbformat

# Reading a notebook
with open('input.ipynb', 'r', encoding='utf-8') as f:
    nb_content = nbformat.read(f, as_version=4)

# Writing a notebook
with open('output.ipynb', 'w', encoding='utf-8') as f:
    nbformat.write(nb_content, f)
```

**Pseudocode for `process_markdown_cell`:**
```python
def process_markdown_cell(cell):
    original_source = cell['source']
    new_source_lines = []
    
    # Regex to find images: !\\[.*\\]\\(.*\\)
    image_pattern = re.compile(r'!\\[(.*)\\]\\(.*\\)')
    
    # Simple approach: split by lines
    for line in original_source.split('\n'):
        new_source_lines.append(line) # Add original line
        
        match = image_pattern.match(line)
        if match:
            # It's an image line
            alt_text, src = match.groups()
            image_data = get_image_data(src) # Helper to fetch image bytes
            description = vision_model.describe(image_data, target_language)
            new_source_lines.append(f"**{get_description_label(target_language)}：** {description}")
        elif line.strip():
            # It's a text line, translate it
            translation = text_model.translate(line, target_language)
            new_source_lines.append(f"**{get_translation_label(target_language)}：** {translation}")
            
    cell['source'] = '\n'.join(new_source_lines)
    return cell
```

## 6. Risks and Challenges

*   **Maintaining Markdown Formatting:** LLMs can be inconsistent in preserving complex Markdown. **Solution:** Process text paragraph by paragraph instead of line by line. Use few-shot prompting with examples of correct preservation.
*   **Multi-language Label Support:** Different target languages require different labels for translations and descriptions. **Solution:** Create a helper function to map target languages to appropriate labels (e.g., "翻译" for Chinese, "Translation" for English, "Traducción" for Spanish).
*   **Unified Image Data Access:** Images can be stored in many ways. **Solution:** The `get_image_data(src)` helper function is critical. It must contain logic to check if `src` is a URL, a local file path, or a base64 string and handle each case appropriately.
*   **API Rate Limits & Cost:** Processing a large notebook with many cells and images can be slow and expensive. **Solution:** Implement batching for API calls where possible. Add optional delays between calls. Provide user feedback on progress.
*   **Large File Handling:** Very large notebooks might exceed memory or state-passing limits. **Solution:** Process the notebook cell by cell, only appending the result to the `processed_cells` list, rather than passing the entire growing content in the state at every step.
*   **Model Compatibility:** Ensuring the Gemini model through OpenRouter works correctly with both text and vision tasks. **Solution:** Use Context7 to reference official documentation and test thoroughly with sample content before full implementation.
*   **Idempotency:** Running the agent on an already translated file would produce messy results. **Solution:** Before starting, check if the output file already exists. If so, warn the user and ask for confirmation to overwrite.
