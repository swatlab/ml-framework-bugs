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

def is_function_def(test_str, regex):
    function_matches = re.findall(regex, test_str, re.MULTILINE)
    return len(function_matches) == 1

def is_normal_line(test_str, regex):
    function_matches = re.findall(regex, test_str, re.MULTILINE)
    return len(function_matches) == 0

def find_matches(test_str, regex):
    matches = re.findall(regex, test_str, re.MULTILINE)
    return matches

def analyze_python_file(file_contents_lines, lines_numbers):
    # vars definitions
    are_insertable_lines = []
    regex = r"(def \w+\(.*\):|if __name__ == '__main__':|if __name__ == \"__main__\":)"
    empty_line_reg = r"^\s*$"
    unindented_line_reg = r"^\S.+"
    # empty_line_match = re.findall(empty_line_reg, test_str, re.MULTILINE)
    # unindented_line_match = re.findall(unindented_line_reg, test_str, re.MULTILINE)
      
    # file_contents_lines : le texte de chaque fichier modifié.
    # 2D list : fichier, lignes de code
    # est une liste de lignes de string (après splitlines)
    
    # for each changed file, get changed lines numbers
    for file_content_line in file_contents_lines:
        # for each changed line
        for line_number in lines_numbers:
            
            # TODO explain this
            line_index = line_number # index for debugging. Is exact number of the line
            syntax_index = line_number - 1 #start point of analysis. Is line_number - 1 because of list access (start at 0)
            print("BEGIN ANALYSIS")
            print("syntax_index : ", syntax_index, "\n line changed : ", line_number, " - ", file_content_line[syntax_index])
            
            # first regex test, similar to greedy algorithm
            test_str = file_content_line[syntax_index]
            function_matches = re.findall(regex, test_str, re.MULTILINE)
            
            # if already matched, then changed line is a function def
            # TODO case 2 : insert trace call under function def
            if is_function_def(file_content_line[syntax_index], regex):
                are_insterable_lines.append(tuple((line_number, True)))
                print("changed line is a python function def")
            else:
                # TODO remove is_normal_line by should_continue or smt
                # reason why : we check if def line, it's not, check if normal line, it is, then we continue while loop
                # weird ?
                while 0 <= syntax_index and is_normal_line(file_content_line[syntax_index], regex): # & syntax_index != in lines_numbers
                    # go to previous lines (decreasing order of lines number) until a function definition is reached
                    line_index -= 1
                    syntax_index -= 1
                    
                    # regex test
                    print("iter ", line_index)
    
                    if is_function_def(file_content_line[syntax_index], regex):
                        print("FUNCTION DEF FOUND at line ", line_index, " :")
                        print(find_matches(file_content_line[syntax_index], regex))
                        are_insertable_lines.append(tuple((line_number, True)))
                
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
