import string

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self):
        return self.x

    def __str__(self):
        return f'Position(x={self.x};y={self.y})'


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

        self.fields: dict[Position, Gtk.Entry] = dict()

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
            for i in range(9):
                entry = DigitEntry()
                entry.set_input_purpose(Gtk.InputPurpose.DIGITS)
                entry.set_max_width_chars(1)
                entry.set_width_chars(1)
                entry.props.xalign = 0.5
                self.fields[Position(i % 3 + (j % 3) * 3, int(i / 3) + int(j / 3) * 3)] = entry
                child_grid.attach(entry, i % 3, i / 3, 1, 1)

                small_numbers_grid = Gtk.Grid()
                small_numbers_grid.set_row_homogeneous(True)
                small_numbers_grid.set_column_homogeneous(True)
                for y in range(9):
                    label = Gtk.Label()
                    # label.set_text(str(y+1))
                    small_numbers_grid.attach(label, y % 3, y / 3, 1, 1)
                child_grid.attach(small_numbers_grid, i % 3, i / 3, 1, 1)

            master_grid.attach(child_grid, j % 3, j / 3, 1, 1)
        main_box.pack_start(master_grid, True, True, 12)

        status = Gtk.Label()
        status.set_text("Enter Sudoku")
        main_box.pack_start(status, False, False, 5)

        solve_button = Gtk.Button()
        solve_button.set_label("Solve Sudoku")
        solve_button.connect("clicked", callback)
        main_box.pack_start(solve_button, False, False, 5)

        self.add(main_box)


def show_window(button_press_callback: callable):
    win = MyWindow(button_press_callback)
    win.show_all()
    Gtk.main()
