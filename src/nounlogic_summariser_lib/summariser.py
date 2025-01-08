import json
import os
import logging  # Added import for logging
from .interface import sanitize_text, chunk_text
from .convert import convert_pdf_to_md
from ollama import chat
from .preprocessing import preprocess_text, final_process_text

_logger = logging.getLogger(__name__)  # Initialize the logger

def load_config(config_path='config.json'):
    """Load configuration from a JSON file.

    Args:
        config_path (str): Path to the config file.

    Returns:
        dict: Configuration dictionary.
    """
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config

def summarize_text(text, config):
    """Summarize the given text using Ollama.

    Args:
        text (str): Sanitized text.
        config (dict): Configuration settings.

    Yields:
        str: Summarized text chunks.
    """
    tokens = config['token_limit']
    prompt = config['prompt_template']
    ollama_config = config['ollama']

    chunks = chunk_text(text, tokens)

    for chunk in chunks:
        response = chat(
            model=ollama_config['model'],
            messages=[{"role": "user", "content": f"{prompt}\n\n{chunk}"}]
        )
        # Access the content of the response
        yield response.message.content

def process_file(file_path, config):
    """Process and summarize the given file.

    Args:
        file_path (str): Path to the input file.
        config (dict): Configuration settings.
    """
    _, ext = os.path.splitext(file_path)
    input_dir = os.path.dirname(os.path.abspath(file_path))
    base_name = os.path.splitext(os.path.basename(file_path))[0]

    # Create output paths
    metadata_path = os.path.join(input_dir, f"{base_name}-metadata.txt")
    summary_path = os.path.join(input_dir, f"{base_name}-summary.txt")
    final_summary_path = os.path.join(input_dir, f"{base_name}_summarised.txt")

    if ext.lower() == '.pdf' and config['conversion']['pdf_to_md']:
        text = convert_pdf_to_md(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

    sanitized = sanitize_text(text)
    
    # Preprocess the text and get initial metadata/summaries
    selected_text, initial_summaries = preprocess_text(sanitized, config, base_name, input_dir)
    
    # Save metadata separately
    with open(metadata_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(initial_summaries))
    
    # Process chunks with Ollama
    with open(summary_path, 'w', encoding='utf-8') as f, \
         open(final_summary_path, 'w', encoding='utf-8') as final_f:
        
        # Write initial summaries first
        f.write('\n\n=== Initial Metadata and Key Points ===\n\n')
        f.write('\n'.join(initial_summaries))
        f.write('\n\n=== Generated Summaries ===\n\n')
        
        # Process text chunks with Ollama
        for chunk_summary in summarize_text(selected_text, config):
            if chunk_summary and chunk_summary.strip():
                f.write(f"{chunk_summary}\n\n")
                final_f.write(f"{chunk_summary}\n\n")
                _logger.info(f"Wrote summary chunk to {summary_path}")
                final_f.flush()  # Ensure immediate writing
                f.flush()

    _logger.info(f"Completed summarization. Files saved in {input_dir}")
    return final_summary_path
