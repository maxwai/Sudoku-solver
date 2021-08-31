from gui.SudokuGui import show_window


def dummy():
    pass


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


if __name__ == '__main__':
    label, fields = show_window(solve_sudoku)
    # label, fields = show_window(save_sudoku)
    with open("saved_sudoku.json") as intput_file:
        saved_sudoku: dict[str, int] = json.load(intput_file)
    for pos, value in saved_sudoku.items():
        if value == 0:
            continue
        fields[Position(int(pos[0]), int(pos[2]))].entry.set_text(str(value))
    Gtk.main()
