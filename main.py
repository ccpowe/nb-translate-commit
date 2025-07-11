#!/usr/bin/env python3
"""
Main entry point for the Jupyter Notebook Translator
"""
import argparse
import sys
import os
from pathlib import Path
from workflow import run_notebook_translation
from config import Config

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(
        description="AI-Powered Jupyter Notebook Translator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py example.ipynb --target-language Chinese
  python main.py notebook.ipynb --target-language Spanish
  python main.py /path/to/notebook.ipynb --target-language French

Supported languages: Chinese, English, Spanish, French, German, Japanese, Korean, Russian, Portuguese, Italian
        """
    )
    
    parser.add_argument(
        "input_path",
        nargs="?",  # Make input_path optional
        help="Path to the input Jupyter notebook (.ipynb file)"
    )
    
    parser.add_argument(
        "--target-language", "-t",
        default=Config.DEFAULT_TARGET_LANGUAGE,
        help=f"Target language for translation (default: {Config.DEFAULT_TARGET_LANGUAGE})"
    )
    
    parser.add_argument(
        "--check-config", "-c",
        action="store_true",
        help="Check configuration and exit"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="Notebook Translator 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Check configuration if requested
    if args.check_config:
        try:
            Config.validate_config()
            print("✅ Configuration is valid")
            print(f"📡 API Base URL: {Config.MODEL_BASE_URL}")
            print(f"🤖 Model: {Config.MODEL_NAME}")
            print(f"🔑 API Key: {'*' * 20}{Config.API_KEY[-10:] if len(Config.API_KEY) > 10 else '*' * len(Config.API_KEY)}")
            return 0
        except Exception as e:
            print(f"❌ Configuration error: {e}")
            return 1
    
    # Ensure input_path is provided for non-config operations
    if not args.input_path:
        print("❌ Error: input_path is required when not using --check-config")
        parser.print_help()
        return 1
    
    # Validate input file
    input_path = Path(args.input_path)
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {input_path}")
        return 1
    
    if not input_path.suffix.lower() == '.ipynb':
        print(f"❌ Error: Input file must be a Jupyter notebook (.ipynb)")
        return 1
    
    # Validate configuration
    try:
        Config.validate_config()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Make sure you have set up your .env file with:")
        print("   API_KEY=your_openrouter_api_key")
        print("   MODEL_NAME=google/gemini-2.5-flash-preview-05-20")
        print("   MODEL_BASE_URL=https://openrouter.ai/api/v1")
        return 1
    
    # Check if output file already exists
    output_path = input_path.parent / f"{input_path.stem}_translated{input_path.suffix}"
    if output_path.exists():
        response = input(f"⚠️ Output file already exists: {output_path}\nOverwrite? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("❌ Operation cancelled")
            return 1
    
    # Run the translation
    try:
        result = run_notebook_translation(
            input_path=str(input_path),
            target_language=args.target_language
        )
        
        if result.get("error_message"):
            print(f"❌ Translation failed: {result['error_message']}")
            return 1
        else:
            print("🎉 Translation completed successfully!")
            return 0
            
    except KeyboardInterrupt:
        print("\n❌ Translation interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 