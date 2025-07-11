"""
LLM Client for interacting with OpenRouter API
"""
from openai import OpenAI
from config import Config
import base64
import requests
from typing import Union, Dict, Any, Optional
import os

class LLMClient:
    """Client for interacting with multimodal LLM via OpenRouter"""
    
    def __init__(self):
        Config.validate_config()
        self.client = OpenAI(
            api_key=Config.API_KEY,
            base_url=Config.MODEL_BASE_URL
        )
        self.model_name = Config.MODEL_NAME or "google/gemini-2.5-flash-preview-05-20"
    
    def translate_text(self, text: str, target_language: str) -> str:
        """
        Translate text to the target language while preserving Markdown formatting
        """
        prompt = f"""
You are a professional translator. You MUST translate the following text from English to {target_language}.

CRITICAL REQUIREMENTS:
1. You MUST actually translate the text content to {target_language}, not repeat the English
2. Preserve ALL Markdown formatting exactly (headers, links, bold, italic, code blocks, etc.)
3. Only translate the actual text content, not the Markdown syntax
4. Maintain the same structure and formatting
5. If there are code snippets, translate only the comments, not the code itself
6. Return ONLY the translated text in {target_language}, no additional explanations
7. If the text is already in {target_language}, return it as-is

Examples:
- English: "This is a tutorial" → Chinese: "这是一个教程"
- English: "# Introduction" → Chinese: "# 简介"

Text to translate to {target_language}:
{text}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a professional translator specialized in maintaining Markdown formatting."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            content = response.choices[0].message.content
            return content.strip() if content else text
        except Exception as e:
            print(f"⚠️ Translation error: {e}")
            if "401" in str(e) or "auth" in str(e).lower():
                print("💡 Hint: Check your API key configuration in .env file")
            return text  # Return original text if translation fails
    
    def add_code_comments(self, code: str, target_language: str) -> str:
        """
        Add explanatory comments to code and translate existing comments
        """
        prompt = f"""
You are a coding expert and translator. Analyze the following code and:

CRITICAL REQUIREMENTS:
1. Add detailed, line-by-line comments explaining what the code does
2. Translate any existing English comments to {target_language}
3. Keep the original code EXACTLY the same - only add/modify comments
4. Write NEW comments in {target_language}
5. Use appropriate comment syntax for the programming language (# for Python, // for JavaScript, etc.)
6. Place comments ABOVE the relevant lines or at the end of lines
7. Make comments educational and helpful for understanding
8. IMPORTANT: Do NOT wrap the code in markdown code blocks (```). Return ONLY the commented code.

Example for Python:
# 导入pandas库用于数据处理
import pandas as pd
# 读取CSV文件并创建DataFrame
data = pd.read_csv('file.csv')

Code to analyze and add {target_language} comments (return ONLY the commented code, no markdown wrapping):
{code}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": f"You are a coding expert who adds helpful comments in {target_language}."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            content = response.choices[0].message.content
            return content.strip() if content else code
        except Exception as e:
            print(f"⚠️ Code commenting error: {e}")
            if "401" in str(e) or "auth" in str(e).lower():
                print("💡 Hint: Check your API key configuration in .env file")
            return code  # Return original code if processing fails
    
    def describe_image(self, image_data: bytes, target_language: str) -> str:
        """
        Generate a description of an image in the target language
        """
        # Convert image bytes to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        prompt = f"""
Describe this image in detail in {target_language}. 
Provide a comprehensive description that would help someone understand the content and context of the image.
Focus on:
1. Main objects, people, or subjects in the image
2. Setting, background, and environment
3. Colors, composition, and visual elements
4. Any text or important details visible
5. Overall mood or purpose of the image

Provide only the description, no additional text.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.3
            )
            content = response.choices[0].message.content
            return content.strip() if content else f"[Unable to generate image description]"
        except Exception as e:
            print(f"Image description error: {e}")
            return f"[Unable to generate image description: {str(e)}]"

def get_image_data(src: str, input_path: Optional[str] = None) -> bytes:
    """
    Helper function to fetch image data from various sources
    
    Args:
        src: Image source (URL, local path, or base64)
        input_path: Path to the notebook file (used to resolve relative paths)
    """
    try:
        # Check if it's a base64 encoded image
        if src.startswith('data:image/'):
            # Extract base64 data
            base64_data = src.split(',')[1]
            return base64.b64decode(base64_data)
        
        # Check if it's a URL
        elif src.startswith('http://') or src.startswith('https://'):
            response = requests.get(src, timeout=30)
            response.raise_for_status()
            return response.content
        
        # Assume it's a local file path
        else:
            # Try absolute path first
            if os.path.exists(src):
                with open(src, 'rb') as f:
                    return f.read()
            
            # If not found and we have input_path, try relative to notebook directory
            elif input_path is not None:
                notebook_dir = os.path.dirname(os.path.abspath(input_path))
                relative_path = os.path.join(notebook_dir, src)
                if os.path.exists(relative_path):
                    with open(relative_path, 'rb') as f:
                        return f.read()
                else:
                    raise FileNotFoundError(f"Image file not found: {src} (tried absolute and relative to {notebook_dir})")
            else:
                raise FileNotFoundError(f"Image file not found: {src}")
                
    except Exception as e:
        print(f"Error loading image from {src}: {e}")
        # Return a placeholder or raise the exception
        raise e 