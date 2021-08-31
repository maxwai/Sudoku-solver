import json
from time import sleep

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

    # put the small numbers up this only needs to happen once since the numbers only go away
    for i in range(9):
        for j in range(9):
            if convert_to_int(fields[Position(i, j)].entry.get_text()) != 0:
                continue
            for y in range(1, 10):
                if not check_number_present(y, Position(i, j)):
                    fields[Position(i, j)].labels[y].set_text(str(y))

    changed_something = True
    while changed_something:
        changed_something = False
        while Gtk.events_pending():
            Gtk.main_iteration()
        sleep(0.2)

        # remove the small numbers that are no longer needed
        for i in range(9):
            for j in range(9):
                if convert_to_int(fields[Position(i, j)].entry.get_text()) != 0:
                    continue
                for y in range(1, 10):
                    if check_number_present(y, Position(i, j)):
                        fields[Position(i, j)].labels[y].set_text("")

        # reduce some small numbers
        for section in sections:
            clean_dict: dict[Position, Field] = dict()
            for pos, field in section.items():
                if convert_to_int(field.entry.get_text()) == 0:
                    clean_dict[pos] = field
            for pos, field in clean_dict.items():
                possible_numbers: set[int] = get_possible(field.labels)
                if len(possible_numbers) == len(clean_dict):
                    continue
                fields_with_same_numbers = 1
                not_same_fields: list[dict[int, Gtk.Label]] = list()
                for pos2, field2 in [item for item in clean_dict.items() if item[0] != pos]:
                    possible_numbers2: set[int] = get_possible(field2.labels)
                    if possible_numbers2 == possible_numbers:
                        fields_with_same_numbers += 1
                    elif not possible_numbers.isdisjoint(possible_numbers2):
                        not_same_fields.append(field2.labels)
                if fields_with_same_numbers == len(possible_numbers):
                    for number in possible_numbers:
                        for labels in not_same_fields:
                            changed_something = True
                            labels[number].set_text("")

        # fill out the fields where a number is only possible in one field
        for section in sections:
            clean_dict: dict[int, list[Field]] = dict()
            for pos, field in section.items():
                if convert_to_int(field.entry.get_text()) == 0:
                    for number in get_possible(field.labels):
                        if number not in clean_dict:
                            clean_dict[number] = list()
                        clean_dict[number].append(field)
            for number, field in [[entry[0], entry[1][0]] for entry in clean_dict.items() if len(entry[1]) == 1]:
                changed_something = True
                for label1 in field.labels.values():
                    label1.set_text("")
                field.entry.set_text(str(number))

        # fill out the fields where only one number is possible
        for i in range(9):
            for j in range(9):
                if convert_to_int(fields[Position(i, j)].entry.get_text()) != 0:
                    continue
                possible_numbers: set[int] = get_possible(fields[Position(i, j)].labels)
                if len(possible_numbers) == 1:
                    changed_something = True
                    number = possible_numbers.pop()
                    fields[Position(i, j)].labels[number].set_text("")
                    fields[Position(i, j)].entry.set_text(str(number))

        # check if it is solved
        if check_solved():
            # check if it is solved correctly
            for i in range(9):
                for j in range(9):
                    if check_number_present(convert_to_int(fields[Position(i, j)].entry.get_text()), Position(i, j)):
                        label.set_text("Made an error somewhere :-(")
                        return
            label.set_text("Solved the Sudoku")
            return
    # the tools did not suffice to solve the Sudoku
    label.set_text("Didn't manage to solve Sudoku :-(")


def get_possible(labels: dict[int, Gtk.Label]) -> set[int]:
    possible_numbers: set[int] = set()
    for y in range(1, 10):
        if labels[y].get_text() == str(y):
            possible_numbers.add(y)
    return possible_numbers


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
