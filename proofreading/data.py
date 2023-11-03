"""
Dictionary and other variables.
"""

# Tags in html like files that contains texts
html_text_tags = ["h1", "h2", "h3", "h4", "h5", "h6", "p", "figcaption", "title"]

html_like_extensions = ["html", "htm", "xhtml"]

# characters and punctuations
zh_chars = r'[\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\U0002a700-\U0002b73f\U0002b740-\U0002b81f\U0002b820-\U0002ceaf\U0002ceb0-\U0002ebef\U00030000-\U0003134f]'
numbers = r'[0-9]'
alphanumeric = r'[A-Za-z0-9]'
typography_quotation = r'[“”‘’]'
full_width_punct = r'[，。！？、：；…—～《》「」『』【】〔〕〈〉〖〗〘〙〚〛（）［］｛｝｟｠｢｣]'
zh_punct = typography_quotation[:-1] + full_width_punct[1:]
zh_chars_punct = f'{zh_chars[:-1]}{zh_punct[1:]}'

RULES = f'''
[
    {{
        "name": "default",
        "location": ["./"],
        "extension": ["svg", "xhtml"],
        "tag": ["h", "p", "text", "figcaption"],
        "switch": "prompt",
        "skip_file": []
    }},
    {{
        "name": "punctuation_line_end",
        "extension": ["xhtml"],
        "tag": ["p", "figcaption"],
        "skip_file": ["loi.xhtml", "titlepage.xhtml"]
    }},
    {{
        "name": "chinese_spacing",
        "extension": "{html_like_extensions}",
        "tag": "{html_text_tags}"
    }},
    {{
        "name": "number_spacing",
        "extension": "{html_like_extensions}",
        "tag": "{html_text_tags}"
    }},
    {{
        "name": "replace_text",
        "extension": "{html_like_extensions}",
        "tag": "{html_text_tags}"
    }},
    {{
        "name": "chinese_punctuation",
        "extension": "{html_like_extensions}",
        "tag": "{html_text_tags}"
    }}
]
'''

text_style = {
    "RED_BOLD": "\033[1;31m",
    "BLUE_BOLD": "\033[1;34m",
    "RESET": "\033[0m"
}

# Text to replace.
# The 'lang" key define what language and variation this rule apply.
# Chinese:
#   - Some Chinese characters have different variations, we follow rules below:
#       a. If it's a traditional type used in zh-Hant, keep it in zh-Hant.
#       b. If the variations are hard to distinguish and makes no differences in the whole original text (for example: 晩, 晚), use the modern one.
#       b. Use the most common type in zh-Hans.

text_replace = {
    '晩': {
        'replace': '晚',
        'lang': 'zh',
        'switch': 'auto',
        'type': 'variant',
    },
    '硏': {
        'replace': '研',
        'lang': 'zh-Hans',
        'switch': 'auto',
        'type': 'hant2hans',
    },
    '槪': {
        'replace': '概',
        'lang': 'zh-Hans',
        'switch': 'auto',
        'type': 'hant2hans',
    },
    '尙': {
        'replace': '尚',
        'lang': 'zh-Hans',
        'switch': 'auto',
        'type': 'hant2hans',
    },
    '著': {
        'replace': '着',
        'lang': 'zh-Hans',
        'switch': 'prompt',
        'type': 'hant2hans',
        'notes': 'zh-TW use 著 for all, zh-CN use 着 in some situations',
    },
    '値': {
        'replace': '值',
        'lang': 'zh-Hans',
        'switch': 'auto',
        'type': 'hant2hans',
    },
    '鄕': {
        'replace': '乡',
        'lang': 'zh-Hans',
        'switch': 'auto',
        'type': 'hant2hans',
    },
    '倂': {
        'replace': '并',
        'lang': 'zh-Hans',
        'switch': 'auto',
        'type': 'hant2hans',
    },
    '一一': {
        'replace': '——',
        'lang': 'zh',
        'switch': 'prompt',
        'type': 'error_ocr',
    },
    '処': {
        'replace': '处',
        'lang': 'zh-Hans',
        'switch': 'auto',
        'type': 'hant2hans',
    },
    '関': {
        'replace': '关',
        'lang': 'zh-Hans',
        'switch': 'auto',
        'type': 'hant2hans',
    },
    '濶': {
        'replace': '阔',
        'lang': 'zh-Hans',
        'switch': 'auto',
        'type': 'hant2hans',
    },
    '敍': {
        'replace': '叙',
        'lang': 'zh-Hans',
        'switch': 'auto',
        'type': 'hant2hans',
    },
    '塡': {
        'replace': '填',
        'lang': 'zh-Hans',
        'switch': 'auto',
        'type': 'hant2hans',
    },
    '郷': {
        'replace': '鄕',
        'lang': 'zh-Hant',
        'switch': 'auto',
        'type': 'variant',
    },
    '髪': {
        'replace': '髮',
        'lang': 'zh',
        'switch': 'auto',
        'type': 'variant',
    }
}



