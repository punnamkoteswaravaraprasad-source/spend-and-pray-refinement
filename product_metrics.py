"""Read historical quantities without inferring historical prices."""
import re
from collections import defaultdict
from catalog import PRODUCTS


def product_units(rows):
    aliases = {p['name'].casefold(): p['name'] for p in PRODUCTS}
    aliases.update({(p['name'] + ' Hot Sauce').casefold(): p['name'] for p in PRODUCTS})
    units, unparsed = defaultdict(int), 0
    for row in rows:
        for entry in (row.get('items') or '').split(';'):
            match = re.fullmatch(r'\s*(.+?)\s+[x×]\s*(\d+)\s*', entry, re.IGNORECASE)
            if not match or int(match[2]) <= 0:
                unparsed += 1
                continue
            name = aliases.get(match[1].strip().casefold(), match[1].strip())
            units[name] += int(match[2])
    return dict(units), unparsed
