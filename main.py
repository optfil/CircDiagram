from typing import List, Tuple, TextIO
import os
import csv
import sys
from PySide2.QtWidgets import QLineEdit, QPushButton, QApplication, QVBoxLayout, QDialog

CountryData = List[Tuple[str, float]]


class Form(QDialog):

    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.edit = QLineEdit("Write my name here", None)
        self.button = QPushButton(None, "Show Greetings", None)

        layout = QVBoxLayout()
        layout.addWidget(self.edit)
        layout.addWidget(self.button)

        self.setLayout(layout)

        self.button.clicked.connect(self.greetings)

    def greetings(self):
        print("Hello %s" % self.edit.text())


def read_data_txt(filename: str) -> CountryData:
    data: CountryData = []
    with open(filename) as f:
        for line in f:
            tokens: List[str] = line.rstrip().split('\t')
            data.append((tokens[0], float(tokens[1])))
    return data


def guess_csv_locale(filename: str) -> str:
    n_lines: int = 0
    n_lines_with_semicolon: int = 0
    with open(filename) as f:
        for line in f:
            n_lines += 1
            if line.count(';') > 0:
                n_lines_with_semicolon += 1
    if n_lines == 0:
        return 'eng'
    elif n_lines_with_semicolon > n_lines // 2:
        return 'rus'
    else:
        return 'eng'


def read_data_csv(filename: str) -> CountryData:
    data: CountryData = []
    loc: str = guess_csv_locale(filename)
    with open(filename) as f:
        if loc == 'rus':
            reader: csv.reader = csv.reader(f, delimiter=';')
            for line in reader:
                data.append((line[0], float(line[1].replace(',', '.'))))
        elif loc == 'eng':
            reader: csv.reader = csv.reader(f, delimiter=',')
            for line in reader:
                data.append((line[0], float(line[1])))
        else:
            raise RuntimeError('Unknown locale {}'.format(loc))
    return data


def read_data(filename: str) -> CountryData:
    ext: str = os.path.splitext(filename)[1]
    if ext == '.txt':
        return read_data_txt(filename)
    elif ext == '.csv':
        return read_data_csv(filename)
    else:
        raise RuntimeError('Cannot read data from file {}: unregistered extension'.format(filename))


def main() -> None:
    print(read_data('tests/data.csv'))


if __name__ == '__main__':
    main()
    # app = QApplication()
    # form: Form = Form()
    # form.show()
    # sys.exit(app.exec_())
