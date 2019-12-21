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
		Moves into the framework local Github repo, 
		retrieves commit patchfile and
		use splitPatchfile to split the lines of patchfile
		
		parameters : 
			commit_command : commit argument for git diff command
			--> example of command : git diff fe31832^..fe31832
		
		returns :
			the patchfile split in different elements (one for one file changed)
		"""
		result_patchfile = subprocess.run(['git', 'diff', commit_command], stdout=subprocess.PIPE)
		patchfile = result_patchfile.stdout.decode("utf-8")
		
		split_patchfile = self.splitPatchfile(patchfile)
		
		return split_patchfile
		
	def findChangedLines(self, split_patch):
		"""
		[SUB-FUNCTION] of findChangedLinesPerFile(). Parses the split_patch
		(of one file at time) to obtain changed lines for each file
		
		return changed lines for each file 
		"""
		regex = r"^@@ [-+](\d+)"
		matches = re.finditer(regex, split_patch, re.MULTILINE)
		line_numbers = []
		
		for matchNum, match in enumerate(matches, start=1):
			# print(int(match.group(1))) # debug which lines are modified
			line_numbers.append(int(match.group(1)))
		return line_numbers

	def findChangedLinesPerFile(self, split_patchfile):
		"""
		Go through the split_patchfile and get find the changed lines (of one file at time)
		"""
		lines_numbers = []
		for split_patch in split_patchfile:
			lines_numbers.append(self.findChangedLines(split_patch))
		return lines_numbers

	def diffLinesNumbers(self, commit_command):
		split_patchfile = self.executePatchfileCommand(commit_command)
		lines_numbers = self.findChangedLinesPerFile(split_patchfile)
		return lines_numbers
