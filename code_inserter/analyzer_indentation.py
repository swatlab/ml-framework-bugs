import argparse
import copy
import os
import re
import subprocess
import sys

class AnalyzerIndentation:
    # https://stackoverflow.com/a/13649013/9876427
    def getIndentationLevel(self, code_line):
        """
        returns the number of leading spaces in  (one line of code)
        """
        return len(code_line) - len(code_line.lstrip(" "))

    def addIndentationLevel(self, original_line, trace_call):
        # apply same level of indentation
        number_spaces = self.getIndentationLevel(original_line)
        added_spaces = " " * number_spaces

        for trace_line in trace_call:
            trace_line = added_spaces + trace_line
        return trace_call

        # open file to trace
        # insert trace at original_line's next line

# Old is_unindented_insertable() and python_auto_insert.py : checkout 6538f42
