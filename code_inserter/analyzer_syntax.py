# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 14:06:21 2019

@author: kevin
"""

from file_opener import FileOpener
import argparse
import copy
import os
import re
import subprocess
import sys

class AnalyzerSyntax:

	"""
	----------------------- code syntax analyzer ------------------------
	"""
	def analyze_python_file(self, file_contents_lines, lines_numbers):
		"""
		TODO replace with code in python_auto_inserter.py
		"""
		self.are_insertable_lines = []
		# python : def keyword, if __name__ == '__main__': or if __name__ == "__main__":
		regex = r"(def \w+\(.*\):|if __name__ == '__main__':|if __name__ == \"__main__\":)"
		
		# TODO check if file is python file
		# for each changed file, get changed lines numbers
		for file_content_line in file_contents_lines:
			# for each changed lines group
			for line_number in lines_numbers:
				syntax_index = line_number
				test_str = file_content_line[syntax_index]
				matches = re.finditer(regex, test_str, re.MULTILINE)
				
				# go to previous lines (decreasing order of lines number) until a function definition is reached
				while syntax_index != 0 & len(matches) != 0: # & syntax_index != in lines_numbers 
					test_str = file_content_line[syntax_index]
					matches = re.finditer(regex, test_str, re.MULTILINE)

					for matchNum, match in enumerate(matches, start=1):
						for groupNum in range(0, len(match.groups())):
							groupNum = groupNum + 1
					
							
					line_number -= 1
	# C : regex using void/int/bool/etc functionName() and {}

# -*- coding: utf-8 -*-
"""
Created on Wed Aug 14 15:19:31 2019

@author: kevin
"""

# https://docs.python.org/2/library/trace.html
# https://docs.python.org/3.0/library/trace.html

def is_empty_line(test_str):
    """
    matches a empty character or a comment in the test_str (one line of code)
    returns true if there is only one match
    """
    # the def regex is different to handle multi-line def 
    empty_line_regex = r"^\s*$|#"
    empty_line_match = re.findall(empty_line_regex, test_str, re.MULTILINE)
    return len(empty_line_match) == 1

def is_class_start(test_str):
    """
    matches a def, an if, ... or a while in the test_str (one line of code)
    returns true if there is only one match
    """
    regex = r"(class .+:)"
    function_matches = re.findall(regex, test_str, re.MULTILINE)
    return len(function_matches) == 1

def is_python_block_start(test_str):
    """
    matches a def, an if, ... or a while in the test_str (one line of code)
    returns true if there is only one match
    """
    regex = r"(def \w+\(.*\):|if .+:|elif .+:|else.+:|try:|except \w+:|for .+:|while .+:|class .+:)"
    function_matches = re.findall(regex, test_str, re.MULTILINE)
    return len(function_matches) == 1

def is_multiline_start(test_str):
    """
    matches a def, an if, ... or a while in the test_str (one line of code)
    returns true if there is only one match
    """
    regex = r"(\[.*,$|\(.*,$|\{.*,$)"
    function_matches = re.findall(regex, test_str, re.MULTILINE)
    return len(function_matches) == 1

def is_multiline_middle(test_str):
    """
    matches a def, an if, ... or a while in the test_str (one line of code)
    returns true if there is only one match. CAUTION: be aware that this function
	catches also multiline starts
    """
    regex = r".*,$"
    function_matches = re.findall(regex, test_str, re.MULTILINE)
    return len(function_matches) == 1

def is_multiline_end(test_str):
    """
    matches a def, an if, ... or a while in the test_str (one line of code)
    returns true if there is only one match
    """
    regex = r"[^\[].*\]$|[^\(].*\)$|[^\{].*\}$|[^\[].*\]:$|[^\(].*\):$|[^\{].*\}:$"
    function_matches = re.findall(regex, test_str, re.MULTILINE)
    return len(function_matches) == 1

def is_docstring_line(test_str):
    """
    matches a docstring that start and end at the same line
    returns true if there is only one match
    """
    regex = r"(\"\"\".*\"\"\"|'''.*''')"
    function_matches = re.findall(regex, test_str, re.MULTILINE)
    return len(function_matches) == 1

def is_docstring_delimiter(test_str):
    """
    matches only one occurence of docstring delimiter
    returns true if there is only one match
    """
    regex = r"\"\"\"|'''"
    function_matches = re.findall(regex, test_str, re.MULTILINE)
    return len(function_matches) == 1

def is_comment_line(test_str):
    """
    matches a whitespace followed by a #
    returns true if there is only one match
    """
    regex = r"(^\s*#)"
    function_matches = re.findall(regex, test_str, re.MULTILINE)
    return len(function_matches) == 1

def is_decorator_line(test_str):
    """
    matches a whitespace followed by a @
    returns true if there is only one match
    """
    regex = r"(^\s*@)"
    function_matches = re.findall(regex, test_str, re.MULTILINE)
    return len(function_matches) == 1

def is_return_statement(test_str):
    """
    matches a whitespace followed by a @
    returns true if there is only one match
    """
    regex = r"(^\s*return)"
    function_matches = re.findall(regex, test_str, re.MULTILINE)
    return len(function_matches) == 1

def is_pass_statement(test_str):
    """
    matches a whitespace followed by a @
    returns true if there is only one match
    """
    regex = r"(^\s*pass)"
    function_matches = re.findall(regex, test_str, re.MULTILINE)
    return len(function_matches) == 1

def is_normal_line(test_str):
    """
    matches a def, an if, ... or a while in the test_str (one line of code)
    returns true if there is no match (the line is a normal code line)
    """
    # the def regex is different to handle multi-line def 
    regex = r"(def \w+\(.*|if .+:|elif .+:|else.+:|try:|except \w+:|for .+:|while .+:|class .+:)"
    function_matches = re.findall(regex, test_str, re.MULTILINE)
    return len(function_matches) == 0


def find_function_matches(test_str):
    """
    matches a def, an if, ... or a while in the test_str (one line of code)
    returns the litteral value found for printing
    """
    regex = r"(def \w+\(.*|if .+:|elif .+:|else.+:|try:|except \w+:|for .+:|while .+:|class .+:)"
    function_matches = re.findall(regex, test_str, re.MULTILINE)
    return function_matches

def printInsertableLines(insertable_lines):
	"""
	[FOR TESTING] Takes a 1D array of booleans. The array represents each line of the original
	code file.
	"""
	with open('insertable_lines.txt', 'w') as f:
		for item in insertable_lines:
			f.write("%s\n" % item)

def increment_numeric_index(numeric_index):
	return numeric_index + 1

def increment_real_index(real_index):
	return real_index + 1

def new_python_analyze_file(code_lines):
	"""
	Param: a 1D array of the files lines
	"""
	numeric_index = 0 # you count from 0 in python
	real_index = 1 # you count from 1 for line numbers
	max_numeric_index = len(code_lines)
	insertable_lines = [None] * len(code_lines)

	# Check all lines, starting from beginning
	while numeric_index < max_numeric_index:
		test_str = code_lines[numeric_index]
		
		if is_empty_line(test_str):
			insertable_lines[numeric_index] = True

		elif is_class_start(test_str):
			insertable_lines[numeric_index] = False
		
		elif is_python_block_start(test_str): 
			insertable_lines[numeric_index] = True

		elif is_multiline_start(test_str):
			# current line is the starting ( or [ or { 
			insertable_lines[numeric_index] = False

			# therefore, increment to next line
			# increment indexes
			numeric_index = increment_numeric_index(numeric_index)
			real_index = increment_real_index(real_index)
			test_str = code_lines[numeric_index]

			while is_multiline_middle(test_str) and numeric_index < max_numeric_index:
				insertable_lines[numeric_index] = False
				# therefore, go to next line
				# increment indexes
				numeric_index = increment_numeric_index(numeric_index)
				real_index = increment_real_index(real_index)
				test_str = code_lines[numeric_index]
			
			# at the end of the while, we reach the ending ) or ] or }, therefore we 
			# mark is a not insertable 
			test_str = code_lines[numeric_index]
			if is_multiline_end(test_str):
				insertable_lines[numeric_index] = True
			else: # not important but allows to safecheck is_multiline_end()
				insertable_lines[numeric_index] = False

		elif is_docstring_line(test_str):
			insertable_lines[numeric_index] = True
		
		# current line is the starting """. We iterate on next lines
		# until reaching the end of the ending """
		elif is_docstring_delimiter(test_str):
			# current line is the starting """ 
			insertable_lines[numeric_index] = False

			# therefore, increment to next line
			# increment indexes
			numeric_index = increment_numeric_index(numeric_index)
			real_index = increment_real_index(real_index)
			test_str = code_lines[numeric_index]

			while not is_docstring_delimiter(test_str) and numeric_index < max_numeric_index:
				insertable_lines[numeric_index] = False
				# therefore, go to next line
				# increment indexes
				numeric_index = increment_numeric_index(numeric_index)
				real_index = increment_real_index(real_index)
				test_str = code_lines[numeric_index]
			
			# at the end of the while, we reach the ending """, therefore we 
			# mark is a not insertable 
			test_str = code_lines[numeric_index]
			insertable_lines[numeric_index] = True

		elif is_comment_line(test_str):
			insertable_lines[numeric_index] = True

		elif is_decorator_line(test_str):
			insertable_lines[numeric_index] = False

		elif is_return_statement(test_str):
			insertable_lines[numeric_index] = False

		elif is_pass_statement(test_str):
			insertable_lines[numeric_index] = False

		# a functional code line
		else:
			insertable_lines[numeric_index] = True

		# end of checks for the current line
		# increment indexes
		numeric_index = increment_numeric_index(numeric_index)
		real_index = increment_real_index(real_index)

	printInsertableLines(insertable_lines)


	

if __name__ == '__main__':
	opener = FileOpener()
	filepaths = ["naive_bayes.py"]
	file_content = opener.getFileContents(filepaths) # 1D
	file_content_lines = opener.splitFileContents(file_content) # 2D
	new_python_analyze_file(file_content_lines[0])



def analyze_python_file(file_contents_lines, lines_numbers):
    """
    Scour the changed files to check if the trace call can be insered on the changed lines.
    
    Oversimplified cases :
    case 1: If the changed line is an unindented line, check is_unindented_insertable() four cases
                    
    case 2: If the changed line is a function def (see regexes above), the trace call can
            be inserted at the next line.
            In reality, it may be more complicated, because function def can be multi-lined ...
    
    case 3: If changed line is in non-definition code, scour the previous lines.
            The trace call would be inserted directly after the changed line,
            so the Python syntax shall be carefully respected by looking at the indentation
            stack (priority_indentation) of the previous lines.
    
    returns a (int; boolean) tuple list of (line_number; is_insertable)
    
    parameters:
        changed files' lines and changed lines number
    """
    
    
    # vars definitions
    are_insertable_lines = []
    
    # for each changed file, get changed lines numbers
    for file_content_line in file_contents_lines:
        # for each changed line number
        for line_number in lines_numbers:
            
            # indexes definition
            line_index = line_number # index for debugging. Is exact number of the line
            syntax_index = line_number - 1 # start point of analysis. Is line_number - 1 because of list access (start at 0)
            print("\n BEGIN ANALYSIS")
            print("line changed (", line_number, ") : ", file_content_line[syntax_index])
            
            # first regex test, similar to greedy algorithm.            
            # if already matched, then changed line is a function def
            
            # case 1: If the changed line is an unindented line
            if get_indentation_level(file_content_line[syntax_index]) == 0:
                if is_unindented_insertable(file_content_line, syntax_index):
                    are_insertable_lines.append(tuple((line_number, True)))
                    print("changed line is a insertable unindented line")
                else:
                    print("insertion is impossible here")
                    
            # case 2: If the changed line is a function def (see regexes above)
            # In reality, it may be more complicated, because function def can be multi-lined ...
            elif is_function_def(file_content_line[syntax_index]):
                are_insterable_lines.append(tuple((line_number, True)))
                print("changed line is a python function def")
              
            # case 3: check if changed line is in non-definition code
            # Scour the previous lines. The trace call would be inserted directly after the changed line,
            # so the Python syntax shall be carefully respected by looking at the indentation
            # stack (priority_indentation) of the previous lines.
            else:                
                # Saves the lowest identation level (lowest number of leading spaces)
                priority_indentation = get_indentation_level(file_content_line[syntax_index])
                has_found_def = False
                
                # loop until beginning of file or def found (see regex above)
                while 0 <= syntax_index and not has_found_def: # and syntax_index != in lines_numbers
                    
                    # go to previous lines (decreasing order of lines number) until a function definition is reached
                    line_index -= 1
                    syntax_index -= 1
    
                    # case 3.1: if previous line is a def and if the def line is correctly indented
                    if is_function_def(file_content_line[syntax_index]) and get_indentation_level(file_content_line[syntax_index]) < priority_indentation:
                        # the changed line is in a non-definition code block, and the line is insertable
                        print("higher function def found at line ", line_index, " :")
                        print(find_function_matches(file_content_line[syntax_index]))
                        are_insertable_lines.append(tuple((line_number, True)))
                        has_found_def = True
                        
                    # case 3.2: if previous line is a normal line and not an empty line
                    elif is_normal_line(file_content_line[syntax_index]) and not is_empty_line(file_content_line[syntax_index]):
                        # no concluant result. Check if Python indentation is respected
                        # and remember the lowest indentation level. Keep looking backwards
                        current_indentation = get_indentation_level(file_content_line[syntax_index])
                        if current_indentation < priority_indentation:
                            priority_indentation = current_indentation
                            
                if not has_found_def:
                    print("insertion is impossible here")
                    
    print(are_insertable_lines)
                
# C : regex using void/int/bool/etc functionName() and {}

