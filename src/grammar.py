# -*- coding: utf-8
"""
the high-level dml grammar

This is something of a definition of the grammar of dml. Actually one can think
of the dml-parsing happening in three steps: First the lexer, forming tokens
and sorting out comments and macros, then parser-entry and friends, and this
grammar here, which is more high level. Theoretically, all syntactical parsing
could be done here, but having things like * and = only count as delimiters
after newlines makes the parser more relaxed (won't complain if * and = is used
in blocks, for an instance). Having that implemented here would seriously harm
readibility of this file.
"""

from __future__ import print_function
from __future__ import unicode_literals

states = {
    "start": ([], {
        "macro_data": "head",
        "cmd_line_option": "start",
        "act_del": "act",
        "scene_del": "scene",
        "cast_del": "cast",
        "title_del": "title",
        "end": "end"}),
    "title": ([], {
        "data": "title",
        "title_del": "title_body"}),
    "cast": ([], {
        "data": "cast",
        "cast_del": "cast_body"}),
    "act": ([], {
        "data": "act",
        "act_del": "body"}),
    "scene": ([], {
        "data": "scene",
        "scene_del": "body"}),

    "actor": ([], {
        "data": "actor",
        "key_del": "dialog"}),
    "inline_dir": ([], {
        "data": "inline_dir",
        "inline_dir_del": "dialog"}),
    "dialog": (["inline_dir"], {
        "data": "dialog",
        "key_del": "actor",
        "inline_dir_del": "inline_dir",
        "new_paragraph": "body",
        "end": "end"}),
    "block": ([], {
        "data": "block",
        "new_paragraph": "body",
        "end": "end"}),
    "body": (["actor", "dialog", "block"], {
        "key_del": "actor",
        "block_start": "block",
        "act_del": "act",
        "scene_del": "scene",
        "new_paragraph": "body",
        "end": "end"}),

    "title_tag": ([], {
        "data": "title_tag",
        "key_del": "title_value"}),
    "title_value": ([], {
        "data": "title_value",
        "key_del": "title_tag",
        "new_paragraph": "title_body",
        "end": "end"}),
    "title_block": ([], {
        "data": "title_block",
        "new_paragraph": "title_body",
        "end": "end"}),
    "title_body": (["title_tag", "title_value", "title_block"], {
        "key_del": "title_tag",
        "block_start": "title_block",
        "act_del": "act",
        "scene_del": "scene",
        "cast_del": "cast",
        "new_paragraph": "title_body",
        "end": "end"}),

    "actor_dec": ([], {
        "data": "actor_dec",
        "key_del": "cast_body"}),
    "actor_des": ([], {
        "data": "actor_des",
        "key_del": "actor_dec",
        "new_paragraph": "cast_body",
        "end": "end"}),
    "cast_block": ([], {
        "data": "cast_block",
        "new_paragraph": "cast_body",
        "end": "end"}),
    "cast_body": (["actor_dec", "actor_des", "cast_block"], {
        "key_del": "actor_dec",
        "block_start": "cast_block",
        "act_del": "act",
        "scene_del": "scene",
        "new_paragraph": "cast_body",
        "end": "end"}),

    "head": ([], {
        "act_del": "act",
        "scene_del": "scene",
        "cast_del": "cast",
        "title_del": "title",
        "new_paragraph": "head",
        "macro_data": "head",
        "end": "end"}),
}
