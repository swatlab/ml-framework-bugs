# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 15:19:31 2019

@author: kevin
"""

# https://docs.python.org/2/library/trace.html
# https://docs.python.org/3.0/library/trace.html

import argparse
import copy
import os
import re
import subprocess
import sys


def getFileContents(filepaths):
    """
    Open manually selected python files
    returns a 1d list, one element for each python file
    """
    file_contents = []
    for filepath in filepaths:
        file = open(filepath,"r") 
        file_content = file.read()
        file_contents.append(file_content)
        file.close()
    return file_contents

def splitFileContents(file_contents):
    """
    splits files content in lines
    returns a 2d list, one element for each python file, then one element for each line of file
    """
    file_contents_lines = []
    for file_content in file_contents:
        file_contents_lines.append(file_content.splitlines())
    return file_contents_lines

def is_function_def(test_str):
    """
    matches a def, an if, ... or a while in the test_str (one line of code)
    returns true if there is only one match
    """
    # the def regex is different to handle multi-line def 
    regex = r"(def \w+\(.*|if .+:|elif .+:|else.+:|try:|except \w+:|for .+:|while .+:)"
    function_matches = re.findall(regex, test_str, re.MULTILINE)
    return len(function_matches) == 1

def is_normal_line(test_str):
    """
    matches a def, an if, ... or a while in the test_str (one line of code)
    returns true if there is no match (the line is a normal code line)
    """
    # the def regex is different to handle multi-line def 
    regex = r"(def \w+\(.*|if .+:|elif .+:|else.+:|try:|except \w+:|for .+:|while .+:)"
    function_matches = re.findall(regex, test_str, re.MULTILINE)
    return len(function_matches) == 0

def is_empty_line(test_str):
    """
    matches a empty character or a comment in the test_str (one line of code)
    returns true if there is only one match
    """
    # the def regex is different to handle multi-line def 
    empty_line_regex = r"^\s*$|#"
    empty_line_match = re.findall(empty_line_regex, test_str, re.MULTILINE)
    return len(empty_line_match) == 1

def find_function_matches(test_str):
    """
    matches a def, an if, ... or a while in the test_str (one line of code)
    returns the litteral value found for printing
    """
    regex = r"(def \w+\(.*|if .+:|elif .+:|else.+:|try:|except \w+:|for .+:|while .+:)"
    function_matches = re.findall(regex, test_str, re.MULTILINE)
    return function_matches

# https://stackoverflow.com/a/13649013/9876427
def get_indentation_level(string):
    """
    returns the number of leading spaces in string (one line of code)
    """
    return len(string) - len(string.lstrip(" "))




def is_unindented_insertable(file_content_line, syntax_index):
    """
    Check if the file_content_line[syntax_index] line is an insertable line.
    
    an unindented line is insertable if the the code block is a running code (non-definition code).
    General rule : if the line after is also unindented (and a def or normal line), the line is insertable. The reason is that 
    it doesn't not break in a function def, for example. However, not all cases are covered.
    
    I tried to cover most cases in my code. I oversimplified unindented lines in four cases. 
    
    returns Ture if the line is insertable, else False
    """
    need_continue = True
    insertable = False
    print("scour unindented mode from", syntax_index + 1, len(file_content_line))
    syntax_index += 1
    while syntax_index < len(file_content_line) and need_continue:
        syntax_index += 1
        
        print("scour mode", syntax_index + 1, len(file_content_line))
        
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
            


def analyze_python_file(file_contents_lines, lines_numbers):
    # vars definitions
    are_insertable_lines = []
      
    # file_contents_lines : The text of each modified line
    # 2D list : fichier, lignes de code
    # est une liste de lignes de string (après splitlines)
    
    # for each changed file, get changed lines numbers
    for file_content_line in file_contents_lines:
        # for each changed line
        for line_number in lines_numbers:
            
            # indexes definition
            line_index = line_number # index for debugging. Is exact number of the line
            syntax_index = line_number - 1 # start point of analysis. Is line_number - 1 because of list access (start at 0)
            print("BEGIN ANALYSIS")
            print("syntax_index : ", syntax_index, "\n line changed : ", line_number, " - ", file_content_line[syntax_index])
            
            # first regex test, similar to greedy algorithm.            
            # if already matched, then changed line is a function def
            # TODO case 2 : insert trace call under function def
            
            # soit on parcourt vers le bas. soit c'est ligne non identée soit c'est rien. rien = ligne vide, comment ou fin de file
            if get_indentation_level(file_content_line[syntax_index]) == 0:
                if is_unindented_insertable(file_content_line, syntax_index):
                    are_insertable_lines.append(tuple((line_number, True)))
                    print("changed line is a unindented line")
                    print(are_insertable_lines)
                else:
                    print("insertion is impossible here")
            elif is_function_def(file_content_line[syntax_index]):
                are_insterable_lines.append(tuple((line_number, True)))
                print("changed line is a python function def")
            else:
                # TODO remove is_normal_line by should_continue or smt
                # reason why : we check if def line, it's not, check if normal line, it is, then we continue while loop
                # weird ?
                priority_indentation = get_indentation_level(file_content_line[syntax_index])
                has_found_def = False
                while 0 <= syntax_index and not has_found_def: # & syntax_index != in lines_numbers
                    
                    # go to previous lines (decreasing order of lines number) until a function definition is reached
                    line_index -= 1
                    syntax_index -= 1
    
                    if is_function_def(file_content_line[syntax_index]):
                        def_indentation = get_indentation_level(file_content_line[syntax_index])
                        print(def_indentation, priority_indentation, "at", line_index)
                        if def_indentation < priority_indentation:
                            print("FUNCTION DEF FOUND at line ", line_index, " :")
                            print(find_function_matches(file_content_line[syntax_index]))
                            are_insertable_lines.append(tuple((line_number, True)))
                            has_found_def = True
                    elif is_normal_line(file_content_line[syntax_index]) and not is_empty_line(file_content_line[syntax_index]):
                        # check tabulation
                        current_indentation = get_indentation_level(file_content_line[syntax_index])
                        if current_indentation < priority_indentation:
                            priority_indentation = current_indentation
                            print(priority_indentation, "at", line_index)
                            
                if has_found_def:
                    print("insertion is possible at these lines : ")
                    print(are_insertable_lines)
                    
                else:
                    print("insertion is impossible here")
                
def insertTraceCpp(traced_file_contents_lines, lines_numbers, trace_call_Cpp):
    """
    goes through the traced_file_contents_lines (copy of file_contents_lines) and add
    trace calls at the lines_numbers
    returns the inserted traced_file_contents_lines
    """
    for traced_file_content_line, line_number in zip(traced_file_contents_lines, lines_numbers):
        # adding of tracer.trace call on a inverted list to conserve the lines numbers (you add at the end so 
        # lines numbers aren't shifted)
        [traced_file_content_line.insert(n, trace_call_Cpp) for n in line_number[::-1]]
    return traced_file_contents_lines
                
# C : regex using void/int/bool/etc functionName() and {}

if __name__ == '__main__':
    filepaths = []
    lines_numbers = []
    filepaths.append("./test_dataloader.py")
    # lines_numbers is a 2D list.
    lines_numbers.append(373)
    lines_numbers.append(376)
    lines_numbers.append(1720)
    lines_numbers.append(381)
    file_contents = getFileContents(filepaths)
    trace_call_Cpp = "print('TRACE CALL HERE')"
    
    # file_contents_lines : le texte de chaque fichier modifié.
    # 2D list : fichier, lignes de code
    # est une liste de lignes de string (après splitlines)
    file_contents_lines = splitFileContents(file_contents)
    # TODO check if file is python file
    analyze_python_file(file_contents_lines, lines_numbers)
