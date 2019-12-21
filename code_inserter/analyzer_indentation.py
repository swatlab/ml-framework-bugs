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

        print(trace_call)
        for i in len(trace_call):
            trace_call[i] = added_spaces + trace_call[i]
        print(trace_call)
        return trace_call

        # open file to trace
        # insert trace at original_line's next line


def is_unindented_insertable(file_content_line, syntax_index):
    """
    Check if the file_content_line[syntax_index] line is an insertable line.
    
    an unindented line is insertable if the the code block is a runable code (non-definition code).
    General rule : if the line after is also unindented (and a def or normal line), the line is insertable. The reason is that 
    it doesn't not break in a function def, for example. However, not all cases are covered.
    
    I tried to cover most cases in my code. I oversimplified unindented lines in four cases. 
    
    returns Ture if the line is insertable, else False
    """
    need_continue = True
    insertable = False
    syntax_index += 1
    while syntax_index < len(file_content_line) and need_continue:
        syntax_index += 1
        
        print("scour mode at line", syntax_index + 1)
        
        # if a next line is unindented (normal or def) concluant result, True
        is_concluant_line = is_function_def(file_content_line[syntax_index]) or is_normal_line(file_content_line[syntax_index])
        
        # if the next line breaks the General rule
        if get_indentation_level(file_content_line[syntax_index]) != 0:
            need_continue = False
            insertable= False
        # if the next line respects the General rule
        elif get_indentation_level(file_content_line[syntax_index]) == 0 and is_concluant_line:
            print("ok, unindented code block")
            need_continue = False
            insertable= True
        # if empty line or comment, shall continue, because the result is not concluant
        elif is_empty_line(file_content_line[syntax_index]):
            need_continue = True
            insertable = False
        # a line at the end of a code line does never break the General rule. For instance, result is concluant
        elif syntax_index == len(file_content_line):
            need_continue = False
            insertable= True
    
    # check one last time. (needed because of syntax_index out of range ....... it's bad)
    # TODO avoid code duplication. 
    if syntax_index == len(file_content_line):
        need_continue = False
        insertable= True
    return insertable
  