"""
Script for proofreading (pr).

Usage:
    python pr.py pr <directory>

Arguments:
    pr: start the proofreading process

    directory: path to the directory to check

    --no-branch-check: skip git branch check

    -r {all|NAME_OF_RULE}
        if 'all' or null, check all rules;
        if others, try check the rule with that name.
    --

Features:
    - List the line in question with line number and lines nearby.
    - Press 'e' to open the file in editor.

Dependencies:

Install Dependencies:

"""

import sys, subprocess
import os
import json
from lxml import etree
import utils

RULES = """
[
    {
        "name": "default",
        "location": ["./"],
        "extension": ["svg", "xhtml"],
        "tag": ["h", "p", "text", "figcaption"],
        "switch": "prompt",
        "skip_file": []
    },
    {
        "name": "punctuation_line_end",
        "extension": ["xhtml"],
        "tag": ["p", "figcaption"],
        "switch": "prompt",
        "skip_file": ["loi.xhtml", "titlepage.xhtml"]
    }
]
"""

RED_BOLD = "\033[1;31m"
BLUE_BOLD = "\033[1;34m"
RESET = "\033[0m"

def process_rule(rule, file_path):
    parser = etree.HTMLParser(recover=True)  # recover=True helps in parsing malformed XML
    with open(file_path, 'r', encoding='utf-8') as f:
        tree = etree.parse(f, parser=parser)

    # This recursive function goes through the XML tree and appends all text it finds
    def recursive_extract(node, processAll):
        # processAll: process tags within selected tag without check for selection.

        # Remove endnotes numbers
        if node.tag == "a" and node.get('epub:type') in ['noteref', 'backlink']:
            # If yes, skip its text and children
            return

        if node.tag in rule["tag"]: 
            processAll = True

        # Process tags in the rules only
        if node.text:
            if processAll or (node.tag in rule["tag"]): 
                yield node.text
            else:
                # Replace text content with spaces but retain line breaks
                yield "\n".join(" " * len(line) for line in node.text.split("\n"))
    
        # If the node has children, recursively call this function on each child
        for child in node:
            yield from recursive_extract(child, processAll)
            # If the child node has tail text, append it
            if child.tail:
                yield child.tail

    # Joining the yielded results to get the entire text content
    content = ''.join(recursive_extract(tree.getroot(), False))
    
    if content:
        # Add one line in front for compensate the lost which might caused by the first xml line in xhtml files
        content = '\n' + content
        getattr(utils, rule["name"])(content, file_path, rule)

def apply_rule(rule, path):
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
                process_rule(rule, file_path)
    
import os
import subprocess

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

def main():
    rules = json.loads(RULES)
    
    if len(sys.argv) < 2 or sys.argv[1] not in ["pr", "--no-branch-check"]:
        print("Invalid arguments")
        return

    rule_name = None
    path = None
    if "-r" in sys.argv:
        rule_name = sys.argv[sys.argv.index("-r") + 1]
    path = sys.argv[-1]

    # Git branch check
    if '--no-branch-check' not in sys.argv:
        branch_name, repo_path = get_current_branch(path)

        if not branch_name: 
            print(f"path: {RED_BOLD}{os.path.abspath(path)}{RESET}")
            print(f"Git repository {RED_BOLD}not found{RESET} in the path. Do you want to continue anyway?")
            choice = input("(y/n): ").strip().lower()
            if choice != 'y':
                sys.exit(1)
        elif branch_name != "base":
            print(f"git repo: {RED_BOLD}{repo_path}{RESET}")
            print(f"branch: {RED_BOLD}{branch_name}{RESET}")
            print(f"It is advised to proofreading in {BLUE_BOLD}base{RESET} branch. Do you want to continue anyway?")
            choice = input("(y/n): ").strip().lower()
            if choice != 'y':
                sys.exit(1)

    if rule_name == "all" or rule_name is None:
        for rule in rules:
            apply_rule(rule, path)
    else:
        for rule in rules:
            if rule["name"] == rule_name:
                apply_rule(rule, path)
                break
        else:
            print(f"Rule named {rule_name} not found.")

if __name__ == "__main__":
    main()