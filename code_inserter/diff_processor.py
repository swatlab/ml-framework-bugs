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
		
		returns:
		  - split_patchfile: a 1D list of patchfiles (string)
			--> [patchfile_1, patchfile_2, ..., patchfile_n]
		"""
		split_patchfile = patchfile.split('diff --git')
		return split_patchfile

	def executePatchfileCommand(self, commit_command):
		"""
		Execute a git diff command to retrieve the commit patchfile, then use
		splitPatchfile to split the lines of patchfile. This function doesn't
		move into the framework repository because DiffExecutor already gets
		into he framework local repo. 
		
		parameters: 
		  - commit_command : commit argument for git diff command
			--> example of command : git diff fe31832^..fe31832
		
		returns:
		  - split_patchfile: a 1D list of patchfiles (string)
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
		
		returns:
		  - line_numbers: changed lines of 1 file 
			--> [line_number_1, line_number_2, ..., line_number_n]
		"""
		regex = r"^@@ [-+](\d+)"
		matches = re.finditer(regex, split_patch, re.MULTILINE)
		line_numbers = []
		
		for matchNum, match in enumerate(matches, start=1):
			number = int(match.group(1))

			# adjust number, because line indexes are line number - 1
			# don't adjust 0, because will end up -1
			if number != 0:
				number = int(match.group(1)) - 1

			line_numbers.append(number)
		return line_numbers

	def findChangedLinesPerFile(self, split_patchfile):
		"""
		Scour the split_patchfile to find the changed lines (of one patchfile at time)
		
		returns:
		  - lines_numbers: changed lines of every file
		--> [[file_1_line_number_1, file_1_line_number_2, .. , file_1_line_number_n], 
			[file_2_line_number_1, file_2_line_number_2, .. , file_2_line_number_p],
			[file_m_line_number_1, file_m_line_number_2, .. , file_m_line_number_q]]
		"""
		lines_numbers = []
		for split_patch in split_patchfile:
			lines_numbers.append(self.findChangedLines(split_patch))
		return lines_numbers

	def diffLinesNumbers(self, commit_command):
		"""
		[MAIN] From the commit command in parameter, execute a git diff command, process
		the output of the command and return the changed lines numbers from the command.

		parameters: 
		  - commit_command : commit argument for git diff command
			--> example of command : git diff fe31832^..fe31832

		returns:
		  - lines_numbers: changed lines of every file
		--> [[file_1_line_number_1, file_1_line_number_2, .. , file_1_line_number_n], 
			[file_2_line_number_1, file_2_line_number_2, .. , file_2_line_number_p],
			[file_m_line_number_1, file_m_line_number_2, .. , file_m_line_number_q]]
		"""
		split_patchfile = self.executePatchfileCommand(commit_command)
		# remove empty elements caused by string.split()
		split_patchfile = list(filter(None, split_patchfile))
		lines_numbers = self.findChangedLinesPerFile(split_patchfile)
		return lines_numbers
