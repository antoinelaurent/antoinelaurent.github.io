#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from datetime import date

import bibparse  # uses your updated, Py3-ready bibparse.py

# ---------- helpers ----------

def tidy(string: str) -> str:
    if not string:
        return ""
    replacements = [
        ("{", ""), ("}", ""),
        ("\\'a", "á"), ("\\'e", "é"), ('\\"e', "ë"), ("\\`e", "è"),
        ("\\'i", "í"), ('\\"i', "ï"), ("\\`i", "ì"),
        ("\\'o", "ó"), ("\\'u", "ú"),
    ]
    for old, new in replacements:
        string = string.replace(old, new)
    return string


def print_tab_title(f, title, papers):
    href = ''.join(title.split())
    f.write(f'<li><a href="#{href}" data-toggle="tab">{title} ({len(papers)})</a></li>\n')


# Backward-compatible signature: your call `print_tab_content(f, title, papers, active=True)` still works.
def print_tab_content(
    f,
    title,
    papers,
    active: bool = False,
    pdf_dir: Path = Path("download/pdfs"),
    bib_href: str = "/laurent.bib",
):
    href = ''.join(title.split())

    def year_key(p):
        try:
            return int(p.data.get('Year', 0))
        except Exception:
            return 0

    sorted_papers = sorted(papers, key=year_key, reverse=True)
    active_cls = "in active" if active else "in"

    f.write(f'<div class="tab-pane fade {active_cls}" id="{href}">\n')
    f.write(f'<div class="accordion" id="accordion{href}">\n')

    previous_year = None
    for paper in sorted_papers:
        year = paper.data.get('Year', '')
        if year != previous_year:
            f.write(f'<h3>{year}</h3>\n')
            previous_year = year

        key = paper.key
        title_txt = tidy(paper.data.get('Title', key))
        authors = tidy(', '.join(paper.data.get('Author', '').split(' and ')))

        f.write('<div class="accordion-group">\n')
        f.write('  <div class="accordion-heading">\n')
        f.write(
            f'    <a class="accordion-toggle" data-toggle="collapse" '
            f'       data-parent="#accordion{href}" href="#collapse{key}_{href}" '
            f'       onClick="_gaq.push([\'_trackEvent\',\'Publications\',\'Abstract\',\'{key}\']);">{title_txt}</a>\n'
        )
        f.write('  </div>\n')

        f.write(f'  <div id="collapse{key}_{href}" class="accordion-body collapse">\n')
        f.write('    <div class="accordion-inner">\n')

        # Authors / Venue / Abstract
        if authors:
            f.write(f'      {authors}\n')
        if 'Booktitle' in paper.data:
            f.write(f'<p><em>{tidy(paper.data["Booktitle"])}</em></p>\n')
        if 'Journal' in paper.data:
            f.write(f'<p><em>{tidy(paper.data["Journal"])}</em></p>\n')
        if 'Abstract' in paper.data:
            f.write(f'<blockquote><p>{tidy(paper.data["Abstract"])}</p></blockquote>\n')

        # Bib link
        f.write(
            f'<i class="icon-tags"></i> '
            f'<a href="{bib_href}" onClick="_gaq.push([\'_trackEvent\',\'Publications\',\'Bibtex\',\'{key}\']);">.bib</a> '
            f'[{key}] | '
        )

        # PDF link (if present)
        pdf_path = pdf_dir / f"{key}.pdf"
        if pdf_path.is_file():
            f.write(
                f'<i class="icon-book"></i> '
                f'<a href="/{pdf_path.as_posix()}" onClick="_gaq.push([\'_trackEvent\',\'Publications\',\'Download\',\'{key}\']);">.pdf</a>'
            )

        f.write('    </div>\n')
        f.write('  </div>\n')
        f.write('</div>\n')

    f.write('</div>\n')
    f.write('</div>\n')


# ---------- main script body (keeps your original flow) ----------

def main():
    # Parse bib
    papers = bibparse.parse_bib('laurent.bib')

    inproceedings = [paper for paper in papers if paper.btype == 'inproceedings']
    articles      = [paper for paper in papers if paper.btype == 'article']
    chapters      = [paper for paper in papers if paper.btype == 'inbook']

    # Ensure output dirs exist
    Path('research').mkdir(parents=True, exist_ok=True)
    Path('download/pdfs').mkdir(parents=True, exist_ok=True)

    # Write HTML (UTF-8)
    with open('research/publications.html', 'w', encoding='utf-8') as f:
        f.write('---\n')
        f.write('layout: page\n')
        f.write('title: "Publications"\n')
        f.write('description: ""\n')
        f.write(f'tagline: "last updated on {date.today().strftime("%B %d, %Y")}"\n')
        f.write('group: research\n')
        f.write('---\n')

        # Keep your Jekyll include literally
        f.write('{% include JB/setup %}\n')

        # Tabs
        f.write('<ul class="nav nav-tabs">\n')
        print_tab_title(f, 'All', papers)
        print_tab_title(f, 'Journal articles', articles)
        print_tab_title(f, 'Book chapters', chapters)
        print_tab_title(f, 'Conference and workshop proceedings', inproceedings)
        f.write('</ul>\n')

        # Tab contents
        f.write('<div id="myTabContent" class="tab-content">\n')
        print_tab_content(f, 'All', papers, active=True)
        print_tab_content(f, 'Journal articles', articles)
        print_tab_content(f, 'Book chapters', chapters)
        print_tab_content(f, 'Conference and workshop proceedings', inproceedings)
        f.write('</div>\n')

    # Append analytics.js if present (safer than os.system/cat)
    analytics = Path('analytics.js')
    if analytics.is_file():
        with open('research/publications.html', 'a', encoding='utf-8') as out, \
             open(analytics, 'r', encoding='utf-8') as src:
            out.write(src.read())

if __name__ == "__main__":
    main()

