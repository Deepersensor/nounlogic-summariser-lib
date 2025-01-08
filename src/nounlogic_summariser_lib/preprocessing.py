import re
from typing import Tuple, List, Dict, Set
import os
import string
from collections import Counter
import math

def calculate_sentence_importance(sentence: str, total_sentences: List[str]) -> float:
    """Calculate sentence importance based on multiple factors."""
    # Term frequency scoring
    words = sentence.lower().split()
    all_words = [w for s in total_sentences for w in s.lower().split()]
    word_freq = Counter(all_words)
    
    # Calculate TF-IDF like score
    score = sum(math.log(1 + word_freq[word]) for word in words)
    
    # Bonus for key phrases
    key_phrases = ['important', 'significant', 'key', 'main', 'crucial', 'essential']
    synonyms_map = {
        'important': ['vital', 'pivotal', 'paramount'],
        'significant': ['noteworthy', 'meaningful'],
        'main': ['primary', 'principal'],
        # ...existing synonyms...
    }
    # Check for synonyms
    for phrase, synonyms in synonyms_map.items():
        for word in synonyms:
            if word in words:
                score += 2  # Same bonus as direct key phrase
    
    # Length normalization
    score = score / (len(words) + 1)  # Avoid division by zero
    
    # Position bonus (sentences at start/end of sections often more important)
    if len(total_sentences) > 0:
        position = total_sentences.index(sentence)
        if position < len(total_sentences) * 0.2 or position > len(total_sentences) * 0.8:
            score *= 1.2
    
    return score

def get_text_statistics(text: str) -> Dict:
    """Get statistical information about the text."""
    sentences = re.split(r'(?<=[.!?]) +', text)
    words = text.lower().split()
    
    return {
        'sentence_count': len(sentences),
        'word_count': len(words),
        'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
        'unique_words': len(set(words)),
        'lexical_density': len(set(words)) / len(words) if words else 0
    }

def smart_chunk_detection(text: str) -> List[str]:
    """Intelligently detect text chunks based on content similarity."""
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = []
    current_topic_words = set()
    
    for sentence in sentences:
        words = set(sentence.lower().split())
        
        # If there's significant topic shift, start new chunk
        if len(current_topic_words) > 0 and len(words & current_topic_words) / len(words) < 0.3:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_topic_words = words
        else:
            current_topic_words |= words
        
        current_chunk.append(sentence)
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def preprocess_text(text: str, config: Dict, filename: str, input_dir: str) -> Tuple[str, List[str]]:
    """
    Preprocess the text to filter out non-summarisable content and handle specific sections.

    Args:
        text (str): Sanitized original text.
        config (Dict): Configuration settings.
        filename (str): Name of the file being processed.
        input_dir (str): Directory of the input file.

    Returns:
        Tuple[str, List[str]]: Tuple containing the processed text and appended summary content.
    """
    processed_text = []
    summary_content = []
    questions_content = []
    output_suffix = config['output']['suffix']

    # 1. Break text into sections based on common academic headings
    sections = re.split(r'\n\s*\n', text)
    
    for section in sections:
        # 2. Filter out sentences with 5 words or less
        sentences = re.split(r'(?<=[.!?]) +', section)
        filtered_sentences = [s for s in sentences if len(s.split()) > 5]
        
        # Reconstruct the section
        filtered_section = ' '.join(filtered_sentences)
        
        # 3. Filter out tutor marked assessments and append to questions file
        tutor_marks = re.finditer(r'\bTUTOR\b.*?\bMARKED\b(?:.*?\bASSIGNMENT\b)?', filtered_section, re.IGNORECASE)
        for match in tutor_marks:
            proximity = config['preprocessing']['tutor_marked_proximity']
            max_words = config['preprocessing']['tutor_marked_max_words']
            
            pattern = rf'(\bTUTOR\b\W+(?:\w+\W+){{0,{proximity}}}\bMARKED\b(?:\W+\bASSIGNMENT\b)?)'
            assessments = re.findall(pattern, filtered_section, re.IGNORECASE)
            
            for assessment in assessments:
                # Find text between assessment and last question mark before it
                start = filtered_section.find(assessment)
                preceding_text = filtered_section[:start]
                last_qm = preceding_text.rfind('?')
                if last_qm != -1:
                    relevant_text = preceding_text[last_qm+1:start]
                else:
                    relevant_text = preceding_text[:start]
                
                words = relevant_text.split()
                if len(words) <= max_words:
                    questions_content.append(relevant_text)
                    # Remove the relevant text from the section
                    filtered_section = filtered_section.replace(relevant_text, '')
        
        # 4. Extract 'conclusion' and 'summary' sections
        conclusion_summary = re.findall(r'\b(conclusion|summary)\b(?!\w)', filtered_section, re.IGNORECASE)
        for term in conclusion_summary:
            pattern = rf'\b{term}\b\s*[^A-Za-z]'
            matches = re.finditer(pattern, filtered_section, re.IGNORECASE)
            for match in matches:
                # Ensure 'conclusion' or 'summary' is not part of another word
                term_start = match.start()
                term_end = match.end()
                preceding_char = filtered_section[term_start -1] if term_start > 0 else ' '
                following_char = filtered_section[term_end] if term_end < len(filtered_section) else ' '
                if not preceding_char.isalpha() and not following_char.isalpha():
                    # Extract the section
                    section_pattern = rf'\b{term}\b\s*:?\s*(.*?)(?=\n|$)'
                    section_match = re.search(section_pattern, filtered_section, re.IGNORECASE | re.DOTALL)
                    if section_match:
                        section_text = section_match.group(1).strip()
                        if len(section_text.split()) <= config['preprocessing']['summary_max_words']:
                            summary_content.append(section_text)
                            # Remove from main text
                            filtered_section = filtered_section.replace(section_match.group(0), '')
        
        # 5. Discard unnecessary spaces and empty lines
        filtered_section = re.sub(r'\s+', ' ', filtered_section).strip()
        
        # 6. Discard numbers in close proximity
        num_proximity = config['preprocessing']['number_proximity']
        filtered_section = re.sub(r'\b\d+\b(?:\W+\b\d+\b){0,' + str(num_proximity) + '}', '', filtered_section)
        
        # 7. Discard sentences in close proximity
        common_words_threshold = config['preprocessing']['common_words_threshold']
        filtered_section = discard_close_sentences(filtered_section, common_words_threshold)
        
        # 8. Prioritize chunks of text closer to each other
        # Assuming headers are already removed by section splitting
        
        # 9. Append capitalized word groups to summary
        capital_pattern = rf'([A-Z]{{2,}}(?:\s+[A-Z]{{2,}}){{0,{config["preprocessing"]["capital_proximity"]}}})'
        capital_matches = re.findall(capital_pattern, filtered_section)
        summary_content.extend(capital_matches)
        # Remove from main text
        filtered_section = re.sub(capital_pattern, '', filtered_section)
        
        # 10. Scan for table of contents regions
        toc_pattern = r'(\.{5,})'
        toc_matches = re.finditer(toc_pattern, filtered_section)
        for match in toc_matches:
            toc_start = match.start()
            toc_end = toc_start
            while toc_end < len(filtered_section) and filtered_section[toc_end] == '.':
                toc_end += 1
            toc_region = filtered_section[toc_start:toc_end]
            if len(toc_region.split()) <= config['preprocessing']['toc_max_words']:
                summary_content.insert(0, toc_region)
                # Remove from main text
                filtered_section = filtered_section.replace(toc_region, '')
        
        # 11. Prioritize texts after 'course objectives'
        course_obj_pattern = r'\bcourse objectives\b\s*(.*?)\s*(?=\n|$)'
        course_obj_matches = re.findall(course_obj_pattern, filtered_section, re.IGNORECASE | re.DOTALL)
        for obj in course_obj_matches:
            summary_content.append(obj.strip())
            # Remove from main text
            filtered_section = filtered_section.replace(obj, '')
        
        processed_text.append(filtered_section)
    
    # Write questions to {filename}-questions file
    questions_file = os.path.join(input_dir, f"{os.path.splitext(filename)[0]}-questions.txt")
    with open(questions_file, 'w', encoding='utf-8') as qf:
        qf.write('\n'.join(questions_content))
    
    # Combine processed text ensuring only 60% is selected
    combined_text = ' '.join(processed_text)
    selected_length = int(len(combined_text.split()) * 0.6)
    selected_text = ' '.join(combined_text.split()[:selected_length])

    # Get text statistics for smart processing
    stats = get_text_statistics(text)
    
    # Adjust thresholds based on text statistics
    if stats['lexical_density'] > 0.7:  # High unique word ratio indicates complex text
        config['preprocessing']['summary_max_words'] = int(config['preprocessing']['summary_max_words'] * 1.2)
    
    # Add intelligent chunk detection
    processed_chunks = smart_chunk_detection(selected_text)
    
    # Enhanced final processing
    final_text = final_process_text(processed_chunks, config, filename, stats)

    return final_text, summary_content

def discard_close_sentences(text: str, common_words_threshold: int) -> str:
    """Enhanced sentence proximity detection."""
    sentences = re.split(r'(?<=[.!?]) +', text)
    filtered_sentences = []
    sentence_vectors = {}
    
    # Create simple vector representation for each sentence
    for sentence in sentences:
        words = sentence.lower().split()
        vector = Counter(words)
        sentence_vectors[sentence] = vector
    
    # Compare sentences using cosine similarity
    for i, sentence in enumerate(sentences):
        if i == 0:
            filtered_sentences.append(sentence)
            continue
            
        prev_vector = sentence_vectors.get(filtered_sentences[-1], Counter())
        curr_vector = sentence_vectors.get(sentence, Counter())
        
        # Check for empty vectors to prevent division by zero
        if len(prev_vector) == 0 or len(curr_vector) == 0:
            similarity = 0
        else:
            common_words = set(prev_vector.keys()) & set(curr_vector.keys())
            similarity = len(common_words) / (math.sqrt(len(prev_vector)) * math.sqrt(len(curr_vector)))
        
        if similarity < common_words_threshold / 10:  # Normalize threshold
            filtered_sentences.append(sentence)
        # Optionally, else:
            # _logger.debug(f"Discarded sentence due to high similarity: {sentence}")
    
    return ' '.join(filtered_sentences)

def final_process_text(chunks: List[str], config: Dict, filename: str, stats: Dict) -> str:
    """Enhanced final processing with improved intelligence."""
    all_sentences = []
    for chunk in chunks:
        sentences = re.split(r'(?<=[.!?]) +', chunk)
        all_sentences.extend(sentences)
    
    # Calculate importance scores for all sentences
    sentence_scores = [
        (i, calculate_sentence_importance(s, all_sentences))
        for i, s in enumerate(all_sentences)
    ]
    
    # Dynamic batch size based on text statistics
    avg_batch_size = min(50, max(10, int(stats['sentence_count'] / 10)))
    
    processed_sentences = []
    batch_start = 0
    
    while batch_start < len(all_sentences):
        batch_end = min(batch_start + avg_batch_size, len(all_sentences))
        batch = all_sentences[batch_start:batch_end]
        batch_scores = sentence_scores[batch_start:batch_end]
        
        # Calculate how many sentences to keep (60%)
        keep_count = max(1, int(len(batch) * 0.6))
        
        # Sort by importance score
        sorted_batch = sorted(batch_scores, key=lambda x: x[1], reverse=True)
        
        # Keep the most important sentences while maintaining order
        keep_indices = sorted([x[0] for x in sorted_batch[:keep_count]])
        
        for i in range(batch_start, batch_end):
            if i in keep_indices:
                processed_sentences.append(all_sentences[i])
        
        batch_start = batch_end
    
    final_text = ' '.join(processed_sentences)
    
    # Save preprocessed summary if enabled
    if config.get('save_preprocessed', False):
        preprocessed_file = os.path.join(input_dir, f"{os.path.splitext(filename)[0]}-preprocessed.txt")
        with open(preprocessed_file, 'w', encoding='utf-8') as pf:
            pf.write(final_text)
            pf.flush()  # Ensure immediate writing
    
    return final_text
