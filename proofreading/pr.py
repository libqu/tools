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
from utils import get_current_branch
from data import RULES, text_style

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
                file_path = os.path.join(root, file)
                process_rule(rule, file_path)

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
            print(f"path: {text_style.RED_BOLD}{os.path.abspath(path)}{text_style.RESET}")
            print(f"Git repository {text_style.RED_BOLD}not found{text_style.RESET} in the path. Do you want to continue anyway?")
            choice = input("(y/n): ").strip().lower()
            if choice != 'y':
                sys.exit(0)
        elif branch_name != "base":
            print(f"git repo: {text_style.RED_BOLD}{repo_path}{text_style.RESET}")
            print(f"branch: {text_style.RED_BOLD}{branch_name}{text_style.RESET}")
            print(f"It is advised to proofreading in {text_style.BLUE_BOLD}base{text_style.RESET} branch. Do you want to continue anyway?")
            choice = input("(y/n): ").strip().lower()
            if choice != 'y':
                sys.exit(0)

    if rule_name == "all" or rule_name is None:
        for rule in rules:
            apply_rule(rule, path, rules)
    else:
        for rule in rules:
            if rule["name"] == rule_name:
                apply_rule(rule, path, rules)
                break
        else:
            print(f"Rule named {rule_name} not found.")

if __name__ == "__main__":
    main()