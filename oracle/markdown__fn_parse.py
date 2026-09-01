"""markdown-fn-parse-conformance-oracle -- deterministic CONFORMANCE oracle for `markdown` (python).

WHAT THIS DECIDES: given a candidate callable and one canonical input, it decides whether the candidate
agrees with the proven reference. It is a *conformance* decider over a fixed, published corpus -- it does
not decide correctness in general, and it says nothing about inputs outside the corpus.

SCOPE (declared, so the boundary is visible rather than discovered): the corpus is the canonical Exercism
test data for this task, 8 input/output pairs, listed in `probes/probes.jsonl`. Inputs outside that
set are simply not covered; `decide` answers only about the input it is given.

PROVENANCE: the reference body comes from the Exercism reference solution for `markdown` (MIT, Exercism);
the type annotations were added by harvest, the body is unchanged (checked at AST level). The capability
was PROVEN by the exercism testsuite (pin=99f454493468bd66) and re-executed by harvest in a sealed sandbox
(unshare -rn) -- verify-not-relay, not a copied ledger label.
"""

TASK = "markdown"
CWE = "markdown"          # a publish-motor egyseges mezonevet var; itt a feladat azonositoja


def decide(fn, value, expect):
    """PASS iff fn(value) == expect. Determinista, nincs halozat, nincs allapot."""
    try:
        return "PASS" if fn(value) == expect else "FAIL"
    except Exception:                                      # noqa: BLE001
        return "FAIL"


import re

def parse_line(line, in_list, in_list_append):
    result = check_headers(line)
    list_match = re.match('\\* (.*)', result)
    if list_match:
        if not in_list:
            result = '<ul>' + wrap(list_match.group(1), 'li')
            in_list = True
        else:
            result = wrap(list_match.group(1), 'li')
    elif in_list:
        in_list_append = True
        in_list = False
    if not re.match('<h|<ul|<li', result):
        result = wrap(result, 'p')
    if list_match is None:
        result = re.sub('(.*)(<li>)(.*)(</li>)(.*)', '\\1\\2<p>\\3</p>\\4\\5', result)
    while check_bold(result):
        result = check_bold(result)
    while check_italic(result):
        result = check_italic(result)
    if in_list_append:
        result = '</ul>' + result
        in_list_append = False
    return {'line': result, 'in_list': in_list, 'in_list_append': in_list_append}

def check_bold(line):
    bold_pattern = '(.*)__(.*)__(.*)'
    bold_match = re.match(bold_pattern, line)
    if bold_match:
        return bold_match.group(1) + wrap(bold_match.group(2), 'strong') + bold_match.group(3)
    else:
        return None

def check_headers(line):
    pattern = '# (.*)'
    for index in range(6):
        if re.match(pattern, line):
            return wrap(line[index + 2:], 'h' + str(index + 1))
        pattern = '#' + pattern
    return line

def check_italic(line):
    italic_pattern = '(.*)_(.*)_(.*)'
    italic_match = re.match(italic_pattern, line)
    if italic_match:
        return italic_match.group(1) + wrap(italic_match.group(2), 'em') + italic_match.group(3)
    else:
        return None

def wrap(line, tag):
    return '<{tag}>{line}</{tag}>'.format(line=line, tag=tag)

def parse(markdown: str) -> str:
    lines = markdown.split('\n')
    html = ''
    in_list = False
    in_list_append = False
    for line in lines:
        result = parse_line(line, in_list, in_list_append)
        html += result['line']
        in_list = result['in_list']
        in_list_append = result['in_list_append']
    if in_list:
        html += '</ul>'
    return html

REFERENCE = parse
