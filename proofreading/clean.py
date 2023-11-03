import os, sys
import re, json
from bs4 import BeautifulSoup, NavigableString
import data
from data import RULES, text_style
from utils import get_current_branch, replace_text
from data import zh_chars, numbers, alphanumeric, zh_punct, zh_chars_punct

# Todo:
#   - Add lang check before run functions.
#   - Order of execution of functions.

def chinese_spacing(content, *_):  # only use the first argument
    # Add one space between Chinese and alphanumeric OR alphanumeric and Chinese
    content = re.sub(rf'({zh_chars})\s*({alphanumeric})', r'\1 \2', content)
    content = re.sub(rf'({alphanumeric})\s*({zh_chars})', r'\1 \2', content)
    
    # remove space between Chinese characters and Chinese punctuations
    content = re.sub(rf'({zh_chars})\s*({zh_punct})', r'\1\2', content)
    content = re.sub(rf'({zh_punct})\s*({zh_chars})', r'\1\2', content)
    
    # remove space between Chinese punctuations
    content = re.sub(rf'({zh_punct})\s*({zh_punct})', r'\1\2', content)

    # remove space between Chinese punctuations and alphanumeric
    content = re.sub(rf'({zh_punct})\s*({alphanumeric})', r'\1\2', content)
    content = re.sub(rf'({alphanumeric})\s*({zh_punct})', r'\1\2', content)

    return content

def chinese_punctuation(content, *_):  # only use the first argument
    # change comma (,) after Chinese characters or punctuations to full-width
    content = re.sub(rf'({zh_chars_punct})\s*,', r'\1，', content)

    # change ( before Chinese characters or punctuations to full-width
    content = re.sub(rf'\(\s*({zh_chars_punct})', r'（\1', content)

    # change ) after Chinese characters or punctuations to full-width
    content = re.sub(rf'({zh_chars_punct})\s*\)', r'\1）', content)

    # change ; after Chinese characters or punctuations to full-width
    content = re.sub(rf'({zh_chars_punct})\s*\;', r'\1；', content)

    return content

def number_spacing(content, lang, *_):
    # Todo: generalize for edge cases

    # remove space between numbers
    content = re.sub(rf'({numbers})\s*({numbers})', r'\1\2', content)

    # Check language
    if lang == 'zh' or lang.startswith('zh-'):
        # remove space error like: 10. 1, 10 .1, 10 . 1
        content = re.sub(r'(\d)\s*\.\s*(\d)', r'\1.\2', content)
    return content
 
def process_file(rule, file_path):
    """Process HTML like files, write directly."""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        soup = BeautifulSoup(content, 'html.parser')

    # Extract xml:lang attribute from the html tag for lang_file
    html_tag = soup.find('html')
    lang_file = html_tag.get('xml:lang', '')  # Default to empty string if attribute is not present

    # This recursive function goes through the html tags and appends all text it finds
    def recursive_extract(tag, lang, line_num):
        lang = tag.get('xml:lang', lang)
        # if not lang == lang_file:  # debug
        #     print(f"DEBUG: found new lang {lang}")

        if hasattr(tag, 'sourceline'):
            line_num = tag.sourceline

        for child in tag.children:
            if isinstance(child, NavigableString):
                if hasattr(child, 'sourceline'):
                    line_num = child.sourceline
                adjusted_text = globals()[rule["name"]](child, lang, line_num, file_path, False)
                child.replace_with(adjusted_text)
            else:
                recursive_extract(child, lang, line_num)

    for tag in soup.find_all(data.html_text_tags):
        recursive_extract(tag, lang_file, 1)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print(f"Processed: {file_path}")

def apply_rule(rule, path, rules):
    # Add missing key value to rule
    rule_default = next((d for d in rules if d["name"] == "default"), None)
    if rule_default and rule:
        # Add from default
        for key, value in rule_default.items():
            if key not in rule:
                rule[key] = value

    for root, dirs, files in os.walk(path):
        # Modify 'dirs' in-place to remove directories that start with a dot.
        # This also ensures that os.walk doesn't traverse into these directories.
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            check_hidden = not file.startswith('.')
            check_name = os.path.basename(file) not in rule["skip_file"]
            check_extension = file.split('.')[-1] in rule["extension"]
            if check_hidden and check_name and check_extension:
                # print(f"processing file {file}") # debug
                file_path = os.path.join(root, file)
                process_file(rule, file_path)

def main():
    rules = json.loads(RULES)

    if len(sys.argv) < 2 or sys.argv[1] not in ["clean", "--no-git-check"]:
        print("Invalid arguments")
        return

    rule_name = None
    path = None
    if "-r" in sys.argv:
        rule_name = sys.argv[sys.argv.index("-r") + 1]
    path = os.path.expanduser(sys.argv[-1])

    # Git check
    if '--no-git-check' not in sys.argv:
        branch_name, repo_path = get_current_branch(path)

        if not branch_name: 
            print(f"path: {text_style['RED_BOLD']}{os.path.abspath(path)}{text_style['RESET']}")
            print(f"Git repository {text_style['RED_BOLD']}not found{text_style['RESET']} in the path. Do you want to continue anyway?")
            choice = input("(y/n): ").strip().lower()
            if choice != 'y':
                sys.exit(0)

    if rule_name == "all" or rule_name is None:
        sys.exit(0) # Todo
        # for rule in rules:
        #     apply_rule(rule, path)
    else:
        for rule in rules:
            if rule["name"] == rule_name:
                apply_rule(rule, path, rules)
                break
        else:
            print(f"Rule named {rule_name} not found.")

if __name__ == "__main__":
    main()