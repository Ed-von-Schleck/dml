# -*- coding: utf-8
"""
the high-level dml grammar

This is something of a definition of the grammar of dml. Actually one can think
of the dml-parsing happening in three steps: First the lexer, forming tokens
and sorting out comments and macros, then parser-entry and friends, and then
this grammar here, which is more high level. Theoretically, all syntactical
parsing could be done here, but having things like * and = only count as
delimiters after newlines makes the parser more relaxed (won't complain if *
and = is used in blocks, for an instance). Having that implemented here would
seriously harm readibility of this file.
"""

from __future__ import print_function
from __future__ import unicode_literals

states = {
    b"start": ([], {
        b"new_paragraph": b"head",
        b"macro_data": b"head",
        b"cmd_line_option": b"start",
        b"act_del": b"act",
        b"scene_del": b"scene",
        b"cast_del": b"cast",
        b"title_del": b"title",
        b"end": b"end"}),
    b"title": ([], {
        b"data": b"title",
        b"title_del": b"title_body"}),
    b"cast": ([], {
        b"data": b"cast",
        b"cast_del": b"cast_body"}),
    b"act": ([], {
        b"data": b"act",
        b"act_del": b"body"}),
    b"scene": ([], {
        b"data": b"scene",
        b"scene_del": b"body"}),

    b"actor": ([], {
        b"data": b"actor",
        b"key_del": b"dialog"}),
    b"inline_dir": ([], {
        b"data": b"inline_dir",
        b"inline_dir_del": b"dialog"}),
    b"dialog": ([b"inline_dir"], {
        b"data": b"dialog",
        b"key_del": b"actor",
        b"inline_dir_del": b"inline_dir",
        b"new_paragraph": b"empty_line",
        b"end": b"end"}),
    b"block": ([], {
        b"data": b"block",
        b"new_paragraph": b"empty_line",
        b"end": b"end"}),
    b"body": ([b"actor", b"dialog", b"block", b"empty_line"], {
        b"key_del": b"actor",
        b"block_start": b"block",
        b"act_del": b"act",
        b"scene_del": b"scene",
        b"new_paragraph": b"empty_line",
        b"end": b"end"}),
    b"empty_line": ([], {
        b"key_del": b"actor",
        b"block_start": b"block",
        b"act_del": b"act",
        b"scene_del": b"scene",
        b"new_paragraph": b"empty_line",
        b"end": b"end"}),
    b"title_tag": ([], {
        b"data": b"title_tag",
        b"key_del": b"title_value"}),
    b"title_value": ([], {
        b"data": b"title_value",
        b"key_del": b"title_tag",
        b"new_paragraph": b"title_body",
        b"end": b"end"}),
    b"title_block": ([], {
        b"data": b"title_block",
        b"new_paragraph": b"title_body",
        b"end": b"end"}),
    b"title_body": ([b"title_tag", b"title_value", b"title_block"], {
        b"key_del": b"title_tag",
        b"block_start": b"title_block",
        b"act_del": b"act",
        b"scene_del": b"scene",
        b"cast_del": b"cast",
        b"new_paragraph": b"title_body",
        b"end": b"end"}),

    b"actor_dec": ([], {
        b"data": b"actor_dec",
        b"key_del": b"cast_body"}),
    b"actor_des": ([], {
        b"data": b"actor_des",
        b"key_del": b"actor_dec",
        b"new_paragraph": b"cast_body",
        b"end": b"end"}),
    b"cast_block": ([], {
        b"data": b"cast_block",
        b"new_paragraph": b"cast_body",
        b"end": b"end"}),
    b"cast_body": ([b"actor_dec", b"actor_des", b"cast_block"], {
        b"key_del": b"actor_dec",
        b"block_start": b"cast_block",
        b"act_del": b"act",
        b"scene_del": b"scene",
        b"new_paragraph": b"cast_body",
        b"end": b"end"}),

    b"head": ([], {
        b"act_del": b"act",
        b"scene_del": b"scene",
        b"cast_del": b"cast",
        b"title_del": b"title",
        b"new_paragraph": b"head",
        b"macro_data": b"head",
        b"end": b"end"}),
        
    b"end": ([], {
        b"end": b"end"}),
}
