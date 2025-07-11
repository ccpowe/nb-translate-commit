"""
Configuration module for the Jupyter Notebook Translator
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for API and model settings"""
    
    # OpenRouter API configuration
    API_KEY = os.getenv("API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME")
    MODEL_BASE_URL = os.getenv("MODEL_BASE_URL")
    
    # Default settings
    DEFAULT_TARGET_LANGUAGE = "Chinese"
    
    @classmethod
    def validate_config(cls):
        """Validate that required configuration is present"""
        missing_vars = []
        
        if not cls.API_KEY:
            missing_vars.append("API_KEY")
        if not cls.MODEL_NAME:
            missing_vars.append("MODEL_NAME")
        if not cls.MODEL_BASE_URL:
            missing_vars.append("MODEL_BASE_URL")
        
        if missing_vars:
            error_msg = f"Missing environment variables: {', '.join(missing_vars)}\n"
            error_msg += "Please create a .env file with the following content:\n\n"
            error_msg += "API_KEY=your_openrouter_api_key\n"
            error_msg += "MODEL_NAME=google/gemini-2.5-flash-preview-05-20\n"
            error_msg += "MODEL_BASE_URL=https://openrouter.ai/api/v1\n\n"
            error_msg += "You can copy env_example.txt to .env and edit it with your API key."
            raise ValueError(error_msg)
        
        return True

def get_translation_label(target_language: str) -> str:
    """Get the appropriate translation label for the target language"""
    labels = {
        "chinese": "翻译",
        "english": "Translation", 
        "spanish": "Traducción",
        "french": "Traduction",
        "german": "Übersetzung",
        "japanese": "翻訳",
        "korean": "번역",
        "russian": "Перевод",
        "portuguese": "Tradução",
        "italian": "Traduzione"
    }
    return labels.get(target_language.lower(), "Translation")

def get_description_label(target_language: str) -> str:
    """Get the appropriate image description label for the target language"""
    labels = {
        "chinese": "图片说明",
        "english": "Image Description",
        "spanish": "Descripción de Imagen", 
        "french": "Description d'Image",
        "german": "Bildbeschreibung",
        "japanese": "画像説明",
        "korean": "이미지 설명",
        "russian": "Описание изображения",
        "portuguese": "Descrição da Imagem",
        "italian": "Descrizione dell'Immagine"
    }
    return labels.get(target_language.lower(), "Image Description") 