import string

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango


class Position:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self):
        return self.x

    def __str__(self):
        return f'Position(x={self.x};y={self.y})'


class Field:
    def __init__(self, entry: Gtk.Entry, labels: dict[int, Gtk.Label]):
        self.entry: Gtk.Entry = entry
        self.labels: dict[int, Gtk.Label] = labels


class DigitEntry(Gtk.Entry, Gtk.Editable):

    def __init__(self):
        super(DigitEntry, self).__init__()

    def do_insert_text(self, new_text: str, length: int, position: int):
        new_text_copy = new_text
        new_text = ''.join([c for c in new_text if c in string.digits[1:]])
        new_position = len(new_text) + 1

        if new_text or new_text_copy == "0":
            self.get_buffer().set_text(new_text, len(new_text))
            return new_position
        else:
            return position


class MyWindow(Gtk.Window):
    def __init__(self, callback: callable):
        super().__init__(title="Sudoku Solver")

        self.set_default_size(800, 840)
        self.connect("destroy", Gtk.main_quit)

        self.fields: dict[Position, Field] = dict()
        self.sections: list[dict[Position, Field]] = list()

        main_box = Gtk.Box()
        main_box.set_orientation(Gtk.Orientation.VERTICAL)
        main_box.set_margin_start(10)
        main_box.set_margin_end(10)

        master_grid = Gtk.Grid()
        master_grid.set_row_homogeneous(True)
        master_grid.set_column_homogeneous(True)
        master_grid.set_row_spacing(25)
        master_grid.set_column_spacing(25)
        for j in range(9):
            child_grid = Gtk.Grid()
            child_grid.set_row_homogeneous(True)
            child_grid.set_column_homogeneous(True)
            child_grid.set_row_spacing(8)
            child_grid.set_column_spacing(8)

            self.sections.append(dict())
            for i in range(9):
                entry = DigitEntry()
                entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
                entry.set_max_width_chars(1)
                entry.set_width_chars(1)
                entry.props.xalign = 0.5
                pango: Pango.FontDescription = entry.get_pango_context().get_font_description()
                pango.set_size(pango.get_size() * 2)
                entry.modify_font(pango)

                # entry.modify_font(Pango.FontDescription('Dejavu Sans Mono 20'))
                child_grid.attach(entry, i % 3, i / 3, 1, 1)

                labels: dict[int, Gtk.Label] = dict()

                small_numbers_grid = Gtk.Grid()
                small_numbers_grid.set_row_homogeneous(True)
                small_numbers_grid.set_column_homogeneous(True)
                for y in range(9):
                    label = Gtk.Label()
                    label.set_text(str(y + 1))
                    labels[y + 1] = label
                    small_numbers_grid.attach(label, y % 3, y / 3, 1, 1)
                child_grid.attach(small_numbers_grid, i % 3, i / 3, 1, 1)
                field = Field(entry, labels)
                self.fields[Position(i % 3 + (j % 3) * 3, int(i / 3) + int(j / 3) * 3)] = field
                self.sections[-1][Position(i % 3 + (j % 3) * 3, int(i / 3) + int(j / 3) * 3)] = field

            master_grid.attach(child_grid, j % 3, j / 3, 1, 1)
        main_box.pack_start(master_grid, True, True, 12)

        self.status = Gtk.Label()
        self.status.set_text("Enter Sudoku")
        main_box.pack_start(self.status, False, False, 5)

        solve_button = Gtk.Button()
        solve_button.set_label("Solve Sudoku")
        solve_button.connect("clicked", callback)
        main_box.pack_start(solve_button, False, False, 5)

        self.add(main_box)


def show_window(button_press_callback: callable) -> tuple[Gtk.Label, dict[Position, Field], dict[int, list[Field]]]:
    win = MyWindow(button_press_callback)
    win.show_all()
    for labels in [label.labels.values() for label in win.fields.values()]:
        for label in labels:
            label.set_visible(False)
    return win.status, win.fields, win.sections
