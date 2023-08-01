import re

shrek_csv = ""
_RE_COMBINE_WHITESPACE = re.compile(r"\s+")

with open('data/SHREK.txt', 'r', encoding="utf-8") as f:
    lines = f.readlines()
    cs_count = 0
    cs_line = ""
    for line in lines:
        if line.strip():
            if cs_count == 0:
                shrek_csv += _RE_COMBINE_WHITESPACE.sub(" ", line).strip()
                shrek_csv += ","
                cs_count = 1
                continue
            if cs_count == 1 or cs_count == 2:
                if cs_count == 1:
                    cs_line += "\""
                cs_line += line
                cs_count = 2
                continue
        else:
            if cs_count == 0:
                continue
            if cs_count == 1:
                cs_line += ","
            if cs_count == 2:
                cs_line += "\""
            my_str = _RE_COMBINE_WHITESPACE.sub(" ", cs_line).strip()
            shrek_csv += my_str
            shrek_csv += "\n"
            cs_count = 0
            cs_line = ""

text_file = open("data/shrekv2.csv", "wt")
n = text_file.write(shrek_csv)
text_file.close()
