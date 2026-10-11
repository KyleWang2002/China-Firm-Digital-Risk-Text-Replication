"""CSV and filesystem helpers that preserve stock codes as strings."""
import csv
from pathlib import Path


def read_rows(path):
    with Path(path).open('r', encoding='utf-8-sig', newline='') as stream:
        yield from csv.DictReader(stream)


def write_rows(path, rows, headers):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
