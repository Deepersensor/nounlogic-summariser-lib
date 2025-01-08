import re
from typing import Tuple, List, Dict
import os

def preprocess_text(text: str, config: Dict, filename: str) -> Tuple[str, str]:
    """
    Preprocess the text to filter out non-summarisable content and handle specific sections.

    Args:
        text (str): Sanitized original text.
        config (Dict): Configuration settings.
        filename (str): Name of the file being processed.

    Returns:
        Tuple[str, str]: Tuple containing the processed text and appended summary content.
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
    questions_file = f"{os.path.splitext(filename)[0]}-questions.txt"
    with open(questions_file, 'w', encoding='utf-8') as qf:
        qf.write('\n'.join(questions_content))
    
    # Append summary content to {filename}-summary file
    summary_file = f"{os.path.splitext(filename)[0]}-summary.txt"
    with open(summary_file, 'a', encoding='utf-8') as sf:
        sf.write('\n'.join(summary_content) + '\n')
    
    # Combine processed text ensuring only 60% is selected
    combined_text = ' '.join(processed_text)
    selected_length = int(len(combined_text.split()) * 0.6)
    selected_text = ' '.join(combined_text.split()[:selected_length])
    
    return selected_text, summary_file

def discard_close_sentences(text: str, common_words_threshold: int) -> str:
    """
    Discard sentences that are in close proximity based on common words.

    Args:
        text (str): The text to process.
        common_words_threshold (int): Number of common words to consider proximity.

    Returns:
        str: The text after discarding close sentences.
    """
    sentences = re.split(r'(?<=[.!?]) +', text)
    filtered_sentences = []
    previous_sentence = ""
    
    for sentence in sentences:
        common_words = set(previous_sentence.lower().split()) & set(sentence.lower().split())
        if len(common_words) < common_words_threshold:
            filtered_sentences.append(sentence)
            previous_sentence = sentence
        else:
            previous_sentence = sentence  # Update without adding
    return ' '.join(filtered_sentences)
