import re

def sanitize_text(text):
    """Remove non-understandable characters from text.

    Args:
        text (str): Original text.

    Returns:
        str: Sanitized text.
    """
    sanitized = re.sub(r'[^A-Za-z0-9\s.,;:!?\'"-]', '', text)
    return sanitized

def chunk_text(text, token_limit):
    """Break text into chunks based on token limit.

    Args:
        text (str): Sanitized text.
        token_limit (int): Maximum number of tokens per chunk.

    Returns:
        list: List of text chunks.
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_tokens = 0

    for word in words:
        # Break earlier on question mark or heading
        if '?' in word or word.strip().endswith(':'):
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_tokens = 0
        current_tokens += len(word.split())
        if current_tokens > token_limit:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_tokens = len(word.split())
        else:
            current_chunk.append(word)

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks
