# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 14:06:21 2019

@author: kevin
"""

#from python_inserter_copy import printsmt
import argparse
import copy
import os
import re
import subprocess
import sys

class FileAnalyzer:
	def removeEmptyElements(self, split_patchfile, file_contents_lines, lines_numbers):
		"""
		remove empty elements in the three lists
		"""
		split_patchfile = list(filter(None, split_patchfile))
		file_contents_lines = list(filter(None, file_contents_lines))
		lines_numbers = list(filter(None, lines_numbers))
		return split_patchfile, file_contents_lines, lines_numbers

	"""
	----------------------- code syntax analyzer ------------------------
	"""
	def analyze_python_file(self, file_contents_lines, lines_numbers):
		"""
		TODO replace with code in python_auto_inserter.py
		"""
		are_insertable_lines = []
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
