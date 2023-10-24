"""
Todo:
  - vim open to specified column
"""

import curses
import unicodedata
import os

def text(screen, line_numbers, text, file_path, rule):
    """
    Display specified lines from a multiline text in a curses interface.

    Parameters:
    - screen: The window object provided by curses.wrapper().
    - line_numbers: A list of line numbers to display from the text.
    - text: A multiline string.
    - file_path: The path to the file (for display purposes).
    - rule_json: A JSON string containing formatting rules. Currently, this function only expects a 'name' key.

    Key Controls:
    - q: Quit the display.
    - Right Arrow / Down Arrow / n / Space / Enter: Go to the next line number. Exit if already on the last page.
    - Left Arrow / Up Arrow / p: Go back to the previous line number.
    """

    lines_nearby = 2  # print out how many lines with text before and after each

    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    
    def print_centered(window, y, text, attr=0):
        width = window.getmaxyx()[1]
        startx = (width // 2) - (len(text) // 2)
        window.addstr(y, startx, text, attr)

    def gather_surrounding_lines(line_no, lines):
        above = []
        below = []
        
        # Gather lines with text above
        idx = line_no - 1
        while len(above) < lines_nearby and idx >= 0:
            if lines[idx].strip():
                above.insert(0, lines[idx])
            idx -= 1
        
        # Gather lines with text below
        idx = line_no + 1
        while len(below) < lines_nearby and idx < len(lines):
            if lines[idx].strip():
                below.append(lines[idx])
            idx += 1
        
        return above, [lines[line_no]], below

    text_lines = text.splitlines()
    idx = 0
    width = screen.getmaxyx()[1] - 4  # Add some space in boarder
    
    def char_width(char):
        """Determine the width of a character in a terminal."""
        width = unicodedata.east_asian_width(char)
        if width in ('F', 'W'):
            return 2
        else:
            return 1

    def wrap_text(line_no, line, available_width):
        line_label = f"Line {line_no}:"
        full_line = line.strip()  # Strip the line for standard display

        wrapped_lines = [(line_label, "")]  # Line label is inserted as a separate line

        current_line = ""
        current_length = 0
        for char in full_line:
            if current_length + char_width(char) > available_width:
                wrapped_lines.append(("", current_line))
                current_line = ""
                current_length = 0
            current_line += char
            current_length += char_width(char)
        if current_line:
            wrapped_lines.append(("", current_line))

        return wrapped_lines
    
    scroll_offset = 0
    max_y, _ = screen.getmaxyx()

    while True:
        screen.clear()
        print_centered(screen, 1, rule["name"])
        screen.addstr(3, 2, file_path)

        line_no = line_numbers[idx] - 1
        above, center, below = gather_surrounding_lines(line_no, text_lines)
        
        y_pos = 5

        lines_to_display = []
        for block, style in [(above, curses.A_NORMAL), (center, curses.A_BOLD | curses.color_pair(1)), (below, curses.A_NORMAL)]:
            for line in block:
                actual_line_no = text_lines.index(line) + 1
                wrapped = wrap_text(actual_line_no, line, width)
                lines_to_display.extend([(l[0], l[1], style) for l in wrapped])
            lines_to_display.append((("", "", curses.A_NORMAL)))  # Insert an empty line after processing an original block

        # Display lines based on the scroll offset
        for i in range(scroll_offset, len(lines_to_display)):
            if y_pos >= max_y - 2:  # Adjusted for the extra empty line
                break
            line_label, line_content, line_style = lines_to_display[i]
            if line_label:
                screen.addstr(y_pos, 2, line_label, curses.A_BOLD | curses.color_pair(2))
                y_pos += 1
            if line_content:
                screen.addstr(y_pos, 2, line_content, line_style)
                y_pos += 1

        screen.refresh()

        # Wait for user input
        key = screen.getch()

        # Check for 'e' key press
        if key == ord('e'):
            curses.endwin()  # End curses mode temporarily
            os.system(f'gnome-terminal -t "proofreading: {rule["name"]}" --hide-menubar -- vim +{line_no + 1} {file_path}')  # Gnome
            curses.doupdate()  # Redraw the curses screen after returning
        elif key == ord('q'):
            break
        elif key in [curses.KEY_RIGHT, ord('n'), ord(' '), 10, 13]:
            if idx < len(line_numbers) - 1:
                idx += 1
            else:
                break  # If we're at the last line number, exit the loop
        elif key == curses.KEY_DOWN:
            # Only scroll down if there's more to display
            if y_pos - max_y + 2 + scroll_offset < len(lines_to_display):  # Adjusted for the extra empty line
                scroll_offset += 1
        elif key == curses.KEY_UP:
            if scroll_offset > 0:
                scroll_offset -= 1
        elif key in [curses.KEY_LEFT, ord('p')] and idx > 0:
            idx -= 1
        curses.endwin()
