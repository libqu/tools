import os, sys, subprocess, re
from . import display
import curses
from . import data

sentense_end_puctuation = { 
    "en": ['.', '?', '!', '……'],
    "zh": ['。', '？', '！', '······']
}

def punctuation_line_end(content, file_path, rule):
    line_numbers = []

    puctuation_lsit = [item for sublist in sentense_end_puctuation.values() for item in sublist]

    for idx, line in enumerate(content.splitlines(True), start=1):
        if not line.strip():
            continue  # Skip empty lines

        # checks if line ends with Chinese or English character
        if not line.strip().endswith(tuple(puctuation_lsit)):  # Handle end with space elsewhere
            line_numbers.append(idx)
    
    if line_numbers:
        curses.wrapper(display.text, line_numbers, content, file_path, rule)

def get_current_branch(path):
    """Get the current git branch and the repo path."""
    while path:
        if os.path.isdir(os.path.join(path, '.git')):
            result = subprocess.run(
                ['git', '-C', path, 'rev-parse', '--abbrev-ref', 'HEAD'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                return result.stdout.strip(), os.path.abspath(path)
        
        # Move up in directory tree
        parent = os.path.dirname(path)
        if parent == path:  # reached the root
            break
        path = parent

    return None, None

def get_single_keypress():
    # UNIX-based system (Linux, macOS)
    if sys.platform in ['linux', 'darwin']:
        import tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            # Check for Ctrl+C and raise KeyboardInterrupt if detected
            if ch == '\x03':
                raise KeyboardInterrupt
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    # Windows
    elif sys.platform == 'win32':
        import msvcrt
        ch = msvcrt.getch().decode('utf-8')
        if ch == '\x03':  # Check for Ctrl+C
            raise KeyboardInterrupt
        return ch

    else:
        raise NotImplementedError("Platform not supported")
    
def replace_text(text, lang, line_num, file_path):
    # Todo:
    #   - Options to replace what if found multiple in one chunk.

    RED_BOLD = "31;1"
    BLUE_BOLD = "34;1"

    def highlight_text(text, keyword, color_code):
        """Highlight the given keyword in the text with given color code."""
        return re.sub(f"({keyword})", lambda m: f"\033[{color_code}m{m.group(1)}\033[0m", text)

    for key, value in data.text_replace.items():
        # Check for language matching conditions
        if lang == value['lang'] or (lang.startswith("zh-") and value['lang'] in ["zh", "any"]):
            occurrences = text.count(key)

            if occurrences == 0:
                continue

            # If switch is 'auto', replace directly
            if value['switch'] == 'auto':
                text = text.replace(key, value['replace'])
            else:
                # Show the replace prompt with highlighting
                highlighted_text = highlight_text(text, key, RED_BOLD)
                replace_text = highlight_text(value['replace'], value['replace'], BLUE_BOLD)
                print(f"\n>>> Replace '{key}' below with '{replace_text}'? (y/e/n)\n\n{highlighted_text}\n")
                # user_input = input("(y/n/e)? ")
                user_input = get_single_keypress()

                # Depending on user choice, perform action
                if user_input == 'y':
                    text = text.replace(key, value['replace'])
                elif user_input == 'e':
                    os.system(f'gnome-terminal -t "clean: replace" --hide-menubar -- vim +{line_num} {file_path}')  # Gnome
                    break

    return text