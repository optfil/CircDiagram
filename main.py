from typing import List, Tuple

CountryData = List[Tuple[str, float]]


def read_data(filename: str) -> CountryData:
    return []


def main() -> None:
    print(read_data('tests/data.txt'))


if __name__ == '__main__':
    main()
