import re

from show_extractor import *
from glob import glob
from pathlib import PurePath

def emit_header():
    header = """
<html>
  <head>
    <meta charset="UTF-8">
    <style rel="stylesheet">
      body {
	  font-family:Sans-Serif;
	  line-height: 1.5em;
	  background-color: #FAFAFA
      }
      ul {
	  float:left;
	  color:#444;
	  margin:5px;
	  width:250px;

      }
      div {
	  margin-left:20px
      }
      h1 {
	  font-weight: 600;
	  margin-bottom:0px;
	  line-height:120%;
	  margin-left: 30px;
	  margin-top: 15px;
          clear:both;
      }
      h2 {
	  margin-top:5px;
	  padding-bottom:4px;
	  margin-left:-20px;
	  margin-bottom:5px;
	  border-bottom: 4px solid #777;
      }
      p {
	  margin-left:30px;
	  font-size:1.2em;
	  margin-bottom: 0px;
      }
    </style>
  </head>
  <body>
    <p>Shows extracted from the Content section of the  8K/Exhibit 99.1 SEC filings of Netflix.</p>
"""
    print(header)

def emit_footer():
    footer = """
  </body>
</html>
"""
    print(footer)

def emit_heading(year):
    print(f"<h1>{year}</h1>")

def emit_content_list(quarter, shows):
    html = f"<ul><h2>{quarter}</h2>"
    html += "".join(map(
        lambda s: f"<li><a href='https://netflix.com/search?q={s}'>{s}</a></li>", shows))
    html += "</ul>"
    print(html)

def apply_manual_corrections(shows):
    # this function exists to clean shows that are a quirk of parsing
    # a manually generated, inconsistent html file

    blacklist = ["and", "Marvel’s"]
    shows = list(filter(lambda s: s not in blacklist, shows))

    # shows are already deduplicated but sometimes the same content
    # might appear in different casing e.g. Set it Up / Set It Up so
    # while we want to keep the original casing, we need to dedupe in
    # a case insensitive way
    unique_shows = set()
    display_shows = set()
    for show in shows:
        # clean certain artifacts, like dangling punctuation
        show = show.strip(".").strip(": ")
        if not "(" in show and show.endswith(")"):
            show = show.strip(")")

        if show.lower() not in unique_shows:
            unique_shows.add(show.lower())
            display_shows.add(show)

    return sorted(list(display_shows))

if __name__ == '__main__':
    data_dir = './data/'
    yqre = re.compile('^8K-Exhibit-91-(\d{4})-(Q[1-4])\.html$')
    current_year = '0'
    emit_header()
    for path in sorted(list(glob(data_dir + "*.html")), reverse=True):
        html,text = extract_content_section(path)
        shows = apply_manual_corrections(get_shows_html(html))

        file = PurePath(path).name
        year, quarter = yqre.match(file).groups()
        if year != current_year:
            if current_year != '0':
                print("</div>")
            emit_heading(year)
            print("<div>")
            current_year = year

        emit_content_list(quarter,shows)
    emit_footer()
