import re
import display
import curses

sentense_end_puctuation = ['.', '?', '!', '……', '。', '？', '！', '······']

def punctuation_line_end(content, file_path, rule):
    line_numbers = []

    for idx, line in enumerate(content.splitlines(True), start=1):
        if not line.strip():
            continue  # Skip empty lines

        # checks if line ends with Chinese or English character
        if not line.strip().endswith(tuple(sentense_end_puctuation)):  # Handle end with space elsewhere
            line_numbers.append(idx)
    
    if line_numbers:
        curses.wrapper(display.text, line_numbers, content, file_path, rule)
        # display.display_text(line_numbers, content, file_path, rule)
