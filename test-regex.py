#!/usr/bin/env python3

import re

def makeurl(issue, repo = ''):
    if not repo:
        repo = 'godot'

    return f'https://github.com/godotengine/{repo}/issues/{issue}'

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

    { 'text': 'https://github.com/godotengine/issue-bot/issues/2', 'results': [ makeurl(2, 'issue-bot') ] },
    { 'text': 'https://github.com/godotengine/godot/pull/100', 'results': [ makeurl(100) ] },
    { 'text': 'https://github.com/godotengine/godot/pull/100#issuecomment-1', 'results': [ makeurl(100) ] },

    { 'text': 'a long line of text with an url https://github.com/godotengine/godot/issues/100 and some tags #102 repo#103', 'results': [ makeurl(102), makeurl(103, 'repo'), makeurl(100) ] },

    { 'text': 'just a bunch of text', 'results' : [  ] },
    { 'text': 'Bunch of ## nonsense ##sdf $$', 'results' : [  ] },
]

tag_prog = re.compile('([A-Za-z0-9_.-]+)?#(\d+)')
url_prog = re.compile('github.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/(issues|pull)/(\d+)\S*')
for test in tests:
    text = test['text']
    result = []

    for match in re.finditer(tag_prog, text):
        result.append(makeurl(match.group(2), match.group(1)))

    for match in re.finditer(url_prog, text):
        result.append(makeurl(match.group(4), match.group(2)))

    if test['results'] != result:
        print(f'FAILED for {text}: expected {test["results"]} got: {result}')

