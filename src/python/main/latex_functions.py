#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Holder for many latex commands that need to be adjusted
based off python calculations
"""

titleTeX = """
\\begin{{titlepage}}
    \\centering
    \\hrule

    \\begin{{tikzpicture}}[remember picture,overlay,shift={{(current page.center)}}]
        \\draw (0, 5) node {{\\Huge \\bfseries Tweet Archive}};
        \\draw (0, 3) node {{\\includegraphics[width=0.15\\textwidth]{{twitter_logo.png}}}};
        \\draw (0, 1) node {{\\large A series of collected tweets for user:}};
        \\draw (0, 0) node {{\\LARGE \\bfseries @{screenName}}};
        \\draw (0, -1) node {{\\large \\emph{{collected between:}}}};
        \\draw (0, -2) node {{\\large {fromDate} -- {toDate}}};
        \\draw (0, -10) node {{\\bfseries Version 1}};
    \\end{{tikzpicture}}

    \\vspace{{0.95\paperheight}}
    \\hrule

    \\newpage

\\end{{titlepage}}

"""

tweetTeX = "\\tweet{{{}}}{{{}}}{{{}}}{{{}}}{{{}}}{{{}}}{{{}}}{{{}}}"
mediaTeX = "\\tweetmedia{{{}}}"
threadTeX = "\\threadline{{{}}}"
ruleTeX = "\\threadrule\n"
