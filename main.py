from typing import List, Tuple
import sys
from PySide2.QtWidgets import QApplication, QLabel

CountryData = List[Tuple[str, float]]


def read_data(filename: str) -> CountryData:
    data: CountryData = []
    with open(filename) as f:
        for line in f:
            tokens: List[str] = line.rstrip().split('\t')
            data.append((tokens[0], float(tokens[1])))
    return data


def main() -> None:
    print(read_data('tests/data.txt'))


if __name__ == '__main__':
    app = QApplication()
    label = QLabel("Hello World")
    label.show()
    sys.exit(app.exec_())
