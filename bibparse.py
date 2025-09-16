#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple, naive BibTeX parser (Python 3 version)

Original author: Vassilios Karakoidas (2008) - vassilios.karakoidas@gmail.com
Ported/updated for Python 3 with small robustness tweaks.
"""

import re
import os
from io import StringIO


class BibtexEntry:
    def __init__(self, bibfile: str):
        self.key = ''
        self.data = {}
        self.btype = ''
        self.data['filename'] = bibfile

    def getKey(self, key: str) -> bool:
        return key.lower().strip() == self.key.lower()

    def search(self, keywords):
        for word in keywords:
            for (k, v) in self.data.items():
                try:
                    if word.lower() in v.lower():
                        return True
                except AttributeError:
                    # Non-string value in self.data
                    continue
        return False

    def __get_pdf_name(self):
        if not self.key:
            return None

        m = re.match(r'(.+/[^.]+)\.bib', self.data.get('filename', ''))
        if m is None:
            return None

        filename = f"{m.group(1).strip()}/{self.key.lower()}.pdf"
        if os.path.isfile(filename):
            return filename
        return None

    def has_pdf(self) -> bool:
        return self.__get_pdf_name() is not None

    def export(self) -> str:
        return self.__str__()

    def totext(self):
        return

    def tohtml(self):
        return

    def __str__(self) -> str:
        result = StringIO()
        result.write(f"@{self.btype.lower().strip()}{{{self.key.strip()},\n")

        for k, v in self.data.items():
            # Keep original behavior of Title-casing keys
            try:
                result.write(f"\t{k.title().strip()} = {{{v.strip()}}},\n")
            except AttributeError:
                # If v is not a string, coerce
                result.write(f"\t{k.title().strip()} = {{{v}}},\n")

        filename = self.__get_pdf_name()
        if filename is not None:
            result.write(f"\tpdf-file = {{{filename}}},\n")

        result.write('}\n')
        return result.getvalue()


def parse_bib(bibfile: str):
    """Parse a .bib file and return a list of BibtexEntry."""
    bibitems = []

    # Regex for entry header lines like: @Article{ Key,
    re_head = re.compile(r'@([a-zA-Z]+)\s*\{\s*(.*),')

    current = None

    with open(bibfile, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()

            # New entry head?
            mr = re_head.match(line)
            if mr is not None:
                if current is not None:
                    bibitems.append(current)
                current = BibtexEntry(bibfile)
                current.key = mr.group(2).strip()
                current.btype = mr.group(1).strip()
                continue

            # Key = {Value} or "Value"
            if '=' in line and current is not None:
                kv_data = line.split('=', 1)
                key = kv_data[0].strip()

                # Capture {...} or "..."
                mr = re.search(r'["{](.+?)["}]', kv_data[1].strip())
                if mr is not None:
                    current.data[key] = mr.group(1).strip()

    # Append the last entry if file ended right after an entry
    if current is not None:
        bibitems.append(current)

    return bibitems

