#!/usr/bin/env python3

import re

def makeurl(issue, repo = ''):
    if not repo:
        repo = 'godot'

    return f'https://github.com/{repo}/issues/{issue}'

tests = [
    { 'text': '#100', 'results' : [ makeurl(100) ] },
    { 'text': 'godot#100', 'results' : [ makeurl(100) ] },
    { 'text': 'issue-bot#100', 'results' : [ makeurl(100, 'issue-bot') ] },
    { 'text': '#100,text', 'results' : [ makeurl(100) ] },
    { 'text': '#100,#101,#102', 'results' : [ makeurl(100), makeurl(101), makeurl(102) ] },
    { 'text': 'text #100,#101,#102 text', 'results' : [ makeurl(100), makeurl(101), makeurl(102) ] },
    { 'text': 'text issue-bot#100,godot#101,collada-exporter#102 text', 'results' : [ makeurl(100, 'issue-bot'), makeurl(101), makeurl(102, 'collada-exporter') ] },
    { 'text': 'text #100', 'results' : [ makeurl(100) ] },
    { 'text': 'text #100 text', 'results' : [ makeurl(100) ] },
    { 'text': 'text #100 #101 text', 'results' : [ makeurl(100), makeurl(101) ] },
    { 'text': 'godot#100', 'results' : [ makeurl(100) ] },
    { 'text': 'text godot#100 text', 'results' : [ makeurl(100) ] },
    { 'text': 'godot#100 text', 'results' : [ makeurl(100) ] },
    { 'text': 'repo.name#100 text', 'results' : [ makeurl(100, 'repo.name') ] },
    { 'text': '(#100) text', 'results' : [ makeurl(100) ] },
    { 'text': '(repo#100) text', 'results' : [ makeurl(100, 'repo') ] },

    { 'text': 'just a bunch of text', 'results' : [  ] },
    { 'text': 'Bunch of ## nonsense ##sdf $$', 'results' : [  ] },
]

prog = re.compile('([A-Za-z0-9_.-]+)?#(\d+)')
for test in tests:
    text = test['text']
    result = []

    print(re.match(prog, text))
    for match in re.finditer(prog, text):
        result.append(makeurl(match.group(2), match.group(1)))

    if test['results'] != result:
        print(f'FAILED for {text}: expected {test["results"]} got: {result}')

