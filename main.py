import json

import gi

from gui.SudokuGui import show_window, Position, Field

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

label: Gtk.Label
fields: dict[Position, Field]
sections: list[dict[Position, Field]]


def solve_sudoku(button: Gtk.Button):
    for i in range(9):
        for j in range(9):
            if convert_to_int(fields[Position(i, j)].entry.get_text()) != 0:
                css_provider = Gtk.CssProvider()
                css_provider.load_from_path("gui/style.css")
                style_context: Gtk.StyleContext = fields[Position(i, j)].entry.get_style_context()
                style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
                style_context.add_class("red_entry")
    changed_something = True
    while changed_something:
        changed_something = False
        for i in range(9):
            for j in range(9):
                if convert_to_int(fields[Position(i, j)].entry.get_text()) != 0:
                    continue
                for y in range(1, 10):
                    fields[Position(i, j)].labels[y].set_visible(not check_number_present(y, Position(i, j)))

        for i in range(9):
            for j in range(9):
                if convert_to_int(fields[Position(i, j)].entry.get_text()) != 0:
                    continue
                possible_numbers: list[int] = list()
                for y in range(1, 10):
                    if fields[Position(i, j)].labels[y].get_visible():
                        possible_numbers.append(y)
                if len(possible_numbers) == 1:
                    changed_something = True
                    fields[Position(i, j)].labels[possible_numbers[0]].set_visible(False)
                    fields[Position(i, j)].entry.set_text(str(possible_numbers[0]))

        if check_solved():
            label.set_text("Solved Sudoku")
            return
    label.set_text("Didn't manage to solve Sudoku :-(")


def check_solved():
    for i in range(9):
        for j in range(9):
            if convert_to_int(fields[Position(i, j)].entry.get_text()) == 0:
                return False
    return True


def check_number_present(number: int, pos: Position) -> bool:
    return check_number_present_horizontal(number, pos) or \
           check_number_present_vertical(number, pos) or \
           check_number_preset_same_cube(number, pos)


def check_number_present_horizontal(number: int, pos: Position) -> bool:
    for i in range(9):
        if i == pos.x:
            continue
        if convert_to_int(fields[Position(i, pos.y)].entry.get_text()) == number:
            return True
    return False


def check_number_present_vertical(number: int, pos: Position) -> bool:
    for i in range(9):
        if i == pos.y:
            continue
        if convert_to_int(fields[Position(pos.x, i)].entry.get_text()) == number:
            return True
    return False


def check_number_preset_same_cube(number: int, pos: Position) -> bool:
    section: list[Gtk.Entry]
    for section_tmp in sections:
        if pos in section_tmp.keys():
            section = [field.entry for field in section_tmp.values()]
            section.remove(section_tmp[pos].entry)
            break
    else:
        raise AssertionError()
    for entry in section:
        if convert_to_int(entry.get_text()) == number:
            return True
    return False


def convert_to_int(text: str) -> int:
    n: int
    try:
        n = int(text)
    except ValueError:
        n = 0
    return n


def save_sudoku(button: Gtk.Button):
    json_dict: dict[str, int] = dict()
    for position, field in fields.items():
        json_dict[f'{position.x};{position.y}'] = convert_to_int(field.entry.get_text())
    with open("saved_sudoku.json", "w") as output_file:
        json.dump(json_dict, output_file)


def recreate_sudoku():
    with open("saved_sudoku.json") as input_file:
        saved_sudoku: dict[str, int] = json.load(input_file)
    for pos, value in saved_sudoku.items():
        if value == 0:
            continue
        fields[Position(int(pos[0]), int(pos[2]))].entry.set_text(str(value))


if __name__ == '__main__':
    label, fields, sections = show_window(solve_sudoku)
    # label, fields, sections = show_window(save_sudoku)
    recreate_sudoku()
    Gtk.main()
