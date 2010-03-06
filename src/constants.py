# -*- coding: utf-8

from __future__ import unicode_literals

from collections import namedtuple

MACRO_NAME, OUTPUT, TOC, PAPER_SIZE, TITLE, CAST, ACT, BODY, TOKEN, FORCE_NEWLINE = range(10)
names = "Macro Name", "ouput", "Table Of Contents", "Paper Size", "Title", "Cast", "Act", "Body", "Token", "Force Newline"

States = namedtuple("States", "START HEAD TITLE TITLE_BODY TITLE_BLOCK CAST CAST_BODY CAST_BLOCK ACT BODY BLOCK ACTOR DIALOG TITLE_TAG TITLE_VALUE ACTOR_DEC ACTOR_DES INLINE_DIR END")
states = States(*xrange(19))

Events = namedtuple("Events", "START CMD_LINE_OPTION MACRO_DATA TITLE_DEL CAST_DEL ACT_DEL DATA KEY_START KEY_END INLINE_DIR_START INLINE_DIR_END NEW_PARAGRAPH BLOCK_START BLOCK_END END")
events = Events(*xrange(15))

SinkEvents = namedtuple("SinkEvents", "START END DATA MACRO_DATA")
sink_events = SinkEvents(*xrange(4))
