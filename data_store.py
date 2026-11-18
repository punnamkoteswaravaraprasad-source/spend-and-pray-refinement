"""Serialized CSV writes for the single-process classroom demo."""
import csv
from threading import RLock
from pathlib import Path

_lock = RLock()


def append_unique(path, fields, row, identity):
    path = Path(path)
    with _lock:
        path.parent.mkdir(parents=True, exist_ok=True)
        existing = []
        if path.exists() and path.stat().st_size:
            with path.open(newline='', encoding='utf-8-sig') as source:
                reader = csv.DictReader(source)
                fields = reader.fieldnames or fields
                existing = list(reader)
        prior = next((r for r in existing if r.get(identity) == row[identity]), None)
        if prior:
            return prior
        with path.open('a', newline='', encoding='utf-8') as target:
            writer = csv.DictWriter(target, fieldnames=fields, extrasaction='ignore')
            if not existing and target.tell() == 0:
                writer.writeheader()
            writer.writerow(row)
        return row
