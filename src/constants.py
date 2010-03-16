# -*- coding: utf-8

from __future__ import unicode_literals

from collections import namedtuple

MACRO_NAME, OUTPUT, TOC, PAPER_SIZE, TITLE, CAST, ACT, BODY, TOKEN, FORCE_NEWLINE = range(10)
names = "Macro Name", "ouput", "Table Of Contents", "Paper Size", "Title", "Cast", "Act", "Body", "Token", "Force Newline"

States = namedtuple("States", "START HEAD TITLE TITLE_BODY TITLE_BLOCK CAST CAST_BODY CAST_BLOCK ACT SCENE BODY BLOCK ACTOR DIALOG TITLE_TAG TITLE_VALUE ACTOR_DEC ACTOR_DES INLINE_DIR END")
states = States(*xrange(20))

SinkEvents = namedtuple("SinkEvents", "START END DATA MACRO_DATA")
sink_events = SinkEvents(*xrange(4))
