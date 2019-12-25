import argparse
import copy
import os
import re
import subprocess
import sys

class AnalyzerIndentation:
    def getIndentationLevel(self, code_line):
        """
        returns the number of leading spaces in code_line (one line of code)
        reference: https://stackoverflow.com/a/13649013/9876427
        """
        print("the code line : ", code_line)
        return len(code_line) - len(code_line.lstrip(" "))

    def addIndentationLevel(self, original_line, trace_call):
        # apply same level of indentation
        number_spaces = self.getIndentationLevel(original_line)
        print("step 3 spaces : ", number_spaces)
        
        new_trace_call = []
        index_new_trace_call = 0
        for trace_line in trace_call:
            added_space_length = len(trace_line) + number_spaces    # will be adding 10 extra spaces
            new_trace_call.append(trace_line.rjust(added_space_length))
            index_new_trace_call = index_new_trace_call + 1
        return new_trace_call

# Old is_unindented_insertable() and python_auto_insert.py : checkout 6538f42
