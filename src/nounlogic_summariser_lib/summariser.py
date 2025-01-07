import json
import os
from .interface import sanitize_text, chunk_text
from .convert import convert_pdf_to_md
from ollama import Client

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

    Returns:
        str: Summarized text.
    """
    tokens = config['token_limit']
    prompt = config['prompt_template']
    ollama_config = config['ollama']

    client = Client(host=ollama_config['host'], port=ollama_config['port'])
    
    chunks = chunk_text(text, tokens)
    summaries = []

    for chunk in chunks:
        response = client.summarize(
            model=ollama_config['model'],
            prompt=f"{prompt}\n\n{chunk}",
            timeout=ollama_config.get('timeout', 30)
        )
        summaries.append(response['summary'])

    return '\n'.join(summaries)

def process_file(file_path, config):
    """Process and summarize the given file.

    Args:
        file_path (str): Path to the input file.
        config (dict): Configuration settings.
    """
    _, ext = os.path.splitext(file_path)
    if ext.lower() == '.pdf' and config['conversion']['pdf_to_md']:
        text = convert_pdf_to_md(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

    sanitized = sanitize_text(text)
    summary = summarize_text(sanitized, config)
    output_path = f"{os.path.splitext(file_path)[0]}{config['output_suffix']}"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(summary)
    _, ext = os.path.splitext(file_path)

    if ext.lower() == '.pdf' and config['conversion']['pdf_to_md']:
        text = convert_pdf_to_md(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

    sanitized = sanitize_text(text)
    summary = summarize_text(sanitized, config)
    output_path = f"{os.path.splitext(file_path)[0]}{config['output_suffix']}"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(summary)
