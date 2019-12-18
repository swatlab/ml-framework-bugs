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

class DiffAnalysisDoer:
	def executePatchfileCommand(self, commit_command):
		"""
		Moves into the framework local Github repo, create commit patchfile and
		use splitPatchfile to split the lines of patchfile
		
		parameters : 
			commit_command : commit argument for git diff command (example of command : git diff efc3d6b65^..efc3d6b65)
		
		returns :
			the patchfile split in different elements (one for one file changed)
		"""
		result_patchfile = subprocess.run(['git', 'diff', commit_command], stdout=subprocess.PIPE)
		patchfile = result_patchfile.stdout.decode("utf-8")
		
		split_patchfile = self.splitPatchfile(patchfile)
		
		return split_patchfile

	def splitPatchfile(self, patchfile):
		"""
		separate the patchfile in one patchfile for each file changed
		returns a 1D list of patchfiles
		"""
		split_patchfile = patchfile.split('diff --git')
		return split_patchfile

	def findChangedLinesPerFile(self, split_patchfile):
		"""
		Go through the split_patchfile and get find the changed lines (of one file at time)
		"""
		lines_numbers = []
		for split_patch in split_patchfile:
			lines_numbers.append(self.findChangedLines(split_patch))
		return lines_numbers
		
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

if __name__ == '__main__':
	differ = Diffdoer()
	print("smt for now")
	commit_command = differ.getAndFormatCommitNumber()
	filenames = differ.executeChangedFilesPathsDiff(commit_command)
	
	print(filenames)
    

