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

class DiffProcessor:
	def splitPatchfile(self, patchfile):
		"""
		[SUB-FUNCTION] of executePatchfileCommand()
		Separate the patchfile into patchfiles, one for each file changed.
		
		returns: a 1D list of patchfiles (string)
			--> [patchfile_1, patchfile_2, ..., patchfile_n]
		"""
		split_patchfile = patchfile.split('diff --git')
		return split_patchfile

	def executePatchfileCommand(self, commit_command):
		"""
		With DiffExecutor, we are already into the framework local repo. 
		Retrieves commit patchfile and
		use splitPatchfile to split the lines of patchfile
		
		parameters: 
			commit_command : commit argument for git diff command
			--> example of command : git diff fe31832^..fe31832
		
		returns: a 1D list of patchfiles (string)
			--> [patchfile_1, patchfile_2, ..., patchfile_n]
		"""
		result_patchfile = subprocess.run(['git', 'diff', commit_command], stdout=subprocess.PIPE)
		patchfile = result_patchfile.stdout.decode("utf-8")
		
		split_patchfile = self.splitPatchfile(patchfile)
		
		return split_patchfile
		
	def findChangedLines(self, split_patch):
		"""
		[SUB-FUNCTION] of findChangedLinesPerFile(). Parses the split_patch
		to obtain changed lines for each file
		
		returns: changed lines for each file 
			--> [line_number_1, line_number_2, ..., line_number_n]
		"""
		regex = r"^@@ [-+](\d+)"
		matches = re.finditer(regex, split_patch, re.MULTILINE)
		line_numbers = []
		
		for matchNum, match in enumerate(matches, start=1):
			# print(int(match.group(1))) # debug which lines are modified
			number = int(match.group(1)) - 1
			line_numbers.append(number)
		return line_numbers

	def findChangedLinesPerFile(self, split_patchfile):
		"""
		Scour the split_patchfile to find the changed lines (of one patchfile at time)
		
		returns: changed lines of every file
		--> [[file_1_line_number_1, file_1_line_number_2, .. , file_1_line_number_n], 
			[file_2_line_number_1, file_2_line_number_2, .. , file_2_line_number_n],
			[file_m_line_number_1, file_m_line_number_2, .. , file_m_line_number_n]]
		"""
		lines_numbers = []
		for split_patch in split_patchfile:
			lines_numbers.append(self.findChangedLines(split_patch))
		return lines_numbers

	def diffLinesNumbers(self, commit_command):
		split_patchfile = self.executePatchfileCommand(commit_command)
		split_patchfile = list(filter(None, split_patchfile))
		lines_numbers = self.findChangedLinesPerFile(split_patchfile)
		lines_numbers = list(filter(None, lines_numbers))
		return lines_numbers
