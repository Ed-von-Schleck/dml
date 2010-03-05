# -*- coding: utf-8
from subprocess import Popen, PIPE
import sys

def q_test():
    p = Popen(['./dml', './tests/dmls/short_play.dml', '-q'], stdout=PIPE, stderr=PIPE)
    stdout_data, stderr_data = p.communicate()
    assert stdout_data == ""
    assert stderr_data == ""

def notq_test():
    p = Popen(['./dml', './tests/dmls/short_play.dml'], stdout=PIPE, stderr=PIPE)
    stdout_data, stderr_data = p.communicate()
    assert stdout_data != ""
    assert stderr_data == ""
