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
    file_contents = []
    for filepath in filepaths:
        file = open(filepath,"r") 
        file_content = file.read()
        file_contents.append(file_content)
        file.close()
    return file_contents

def splitFileContents(file_contents):
    file_contents_lines = []
    for file_content in file_contents:
        file_contents_lines.append(file_content.splitlines())
    return file_contents_lines

# later for other regexes
    # empty_line_reg = r"^\s*$"
    # unindented_line_reg = r"^\S.+"
    # empty_line_match = re.findall(empty_line_reg, test_str, re.MULTILINE)
    # unindented_line_match = re.findall(unindented_line_reg, test_str, re.MULTILINE)

def is_function_def(test_str):
    regex = r"(def \w+\(.*|if __name__ == '__main__':|if __name__ == \"__main__\":)"
    function_matches = re.findall(regex, test_str, re.MULTILINE)
    return len(function_matches) == 1

def is_normal_line(test_str):
    regex = r"(def \w+\(.*|if __name__ == '__main__':|if __name__ == \"__main__\":)"
    function_matches = re.findall(regex, test_str, re.MULTILINE)
    return len(function_matches) == 0

def is_empty_line(test_str):
    empty_line_regex = r"^\s*$"
    empty_line_match = re.findall(empty_line_regex, test_str, re.MULTILINE)
    return len(empty_line_match) == 1

def find_function_matches(test_str):
    regex = r"(def \w+\(.*|if __name__ == '__main__':|if __name__ == \"__main__\":)"
    function_matches = re.findall(regex, test_str, re.MULTILINE)
    return function_matches

# https://stackoverflow.com/a/13649013/9876427
def get_indentation_level(string):
    return len(string) - len(string.lstrip(" "))

def analyze_python_file(file_contents_lines, lines_numbers):
    # vars definitions
    are_insertable_lines = []
      
    # file_contents_lines : le texte de chaque fichier modifié.
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
            if is_function_def(file_content_line[syntax_index]):
                are_insterable_lines.append(tuple((line_number, True)))
                print("changed line is a python function def")
            else:
                # TODO remove is_normal_line by should_continue or smt
                # reason why : we check if def line, it's not, check if normal line, it is, then we continue while loop
                # weird ?
                priority_indentation = get_indentation_level(file_content_line[syntax_index])
                has_found_def = False
                while 520 <= syntax_index and not has_found_def: # & syntax_index != in lines_numbers
                    
                    # go to previous lines (decreasing order of lines number) until a function definition is reached
                    line_index -= 1
                    syntax_index -= 1
                    
                    # regex test
                    print("iter ", line_index)
                    
    
                    if is_function_def(file_content_line[syntax_index]):
                        def_indentation = get_indentation_level(file_content_line[syntax_index])
                        print(def_indentation, priority_indentation)
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
                            print(priority_indentation)
                
def insertTraceCpp(traced_file_contents_lines, lines_numbers, trace_call_Cpp):
    for traced_file_content_line, line_number in zip(traced_file_contents_lines, lines_numbers):
        # ajout de trace_call sur liste inversée pour conserver le numéro de ligne
        [traced_file_content_line.insert(n, trace_call_Cpp) for n in line_number[::-1]]
    return traced_file_contents_lines
                
# C : regex using void/int/bool/etc functionName() and {}

if __name__ == '__main__':
    filepaths = []
    lines_numbers = []
    filepaths.append("./test_dataloader.py")
    # lines_numbers : 2D list ?
    lines_numbers.append(579)
    file_contents = getFileContents(filepaths)
    trace_call_Cpp = "print('TRACE CALL HERE')"
    
    # file_contents_lines : le texte de chaque fichier modifié.
    # 2D list : fichier, lignes de code
    # est une liste de lignes de string (après splitlines)
    file_contents_lines = splitFileContents(file_contents)
    # TODO check if file is python file
    analyze_python_file(file_contents_lines, lines_numbers)
