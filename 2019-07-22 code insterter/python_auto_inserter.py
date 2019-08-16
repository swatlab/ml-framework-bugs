# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 15:19:31 2019

@author: kevin
"""

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

def analyze_python_file(file_contents_lines, lines_numbers):
    are_insertable_lines = []
    regex = r"(def \w+\(.*\):|if __name__ == '__main__':|if __name__ == \"__main__\":)"
    empty_line_reg = r"^\s*$"
    unindented_line_reg = r"^\S.+"
        
    # for each changed file, get changed lines numbers
    for file_content_line in file_contents_lines:
        # for each changed line
        for line_number in lines_numbers:
            
            line_index = line_number
            syntax_index = line_number - 1 #start point of analysis
            
            test_str = file_content_line[syntax_index]
            matches = re.findall(regex, test_str, re.MULTILINE)
            print("BEGIN ANALYSIS")
            print("syntax_index : ", syntax_index, "\n line changed : ", line_number, " - ", file_contents_lines[0][syntax_index])
            
            if len(matches) == 1:
                are_insterable_lines.append(tuple((line_number, True)))
                print("changed line is a python function def")
                # TODO case 2 : insert trace call under function def
            else:
                line_index = line_index - 1
                syntax_index -= 1
            # go to previous lines (decreasing order of lines number) until a function definition is reached
            while 0 <= syntax_index and len(matches) == 0: # & syntax_index != in lines_numbers 
                print(len(matches) == 0)
                test_str = file_content_line[syntax_index]
                matches = re.findall(regex, test_str, re.MULTILINE)
                print("iter ", line_index)

                if len(matches) == 1:
                    print("FUNCTION DEF FOUND")
                    print(matches)
                    are_insertable_lines.append(tuple((line_number, True)))
                else:
                    line_index -= 1
                    syntax_index -= 1
                
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
    lines_numbers.append(376)
    file_contents = getFileContents(filepaths)
    trace_call_Cpp = "print('TRACE CALL HERE')"
    
    # le texte de chaque fichier modifié.
    # 2D list : fichier, lignes de code
    # est une liste de lignes de string (après splitlines)
    file_contents_lines = splitFileContents(file_contents)
    # TODO check if file is python file
    analyze_python_file(file_contents_lines, lines_numbers)
