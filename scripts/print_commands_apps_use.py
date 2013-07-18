
import sys

searches_list = sys.argv[1]

with open(searches_list) as searches:
    for search in searches.readlines():
        parts = search.strip().split('|')
        for part in parts:
            if len(part) == 0:
                continue
            part = part.strip()
            print part.split()[0].lower()
