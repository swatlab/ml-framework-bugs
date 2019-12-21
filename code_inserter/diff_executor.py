# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 14:06:21 2019

@author: kevin
"""

import argparse
import copy
import os
import re
import subprocess
import sys

# PARAM: COMMIT ---> from console
FRAMEWORK_PATH = "scikit-learn"

class DiffExecutor:
	def getAndFormatCommitNumber(self):
		"""
		Parse commit number from the command line and format it
		like this "commit_number^..commit_number"
		
		returns:
			commit_command: commit number in the format "commit_number^..commit_number"
			--> example of command : git diff fe31832^..fe31832
		"""
		
		parser = argparse.ArgumentParser(description='Commits')
		parser.add_argument('commits', metavar='C', type=str, nargs='+')
		args = parser.parse_args()

		commit_number = args.commits[0]
		commit_command = commit_number+'^..'+commit_number
		return commit_number, commit_command
		
	def executeChangedFilesPathsDiff(self, commit_command):
		"""
		Moves into the framework local repo and return the names of files changed at the commit
		
		parameters : 
			commit_command: commit number in the format "commit_number^..commit_number"
			--> example of command : git diff fe31832^..fe31832

		returns :
			filenames: string of names of files changed at the commit.
					   Filenames are separated by newlines
		"""

		os.chdir("../..")
		# TODO adapt path towards desired framework Github repo
		os.chdir(FRAMEWORK_PATH)
		result_filenames = subprocess.run(['git', 'diff', "--name-only", commit_command], stdout=subprocess.PIPE)
		filenames = result_filenames.stdout.decode("utf-8")
		return filenames

	def diffFilepaths(self):
		"""
		Executes two members methods to obtain the filepaths of changed files

		returns: Paths of files changed at the commit
			--> [filepath_1, filepath_2, ..., filepath_n]
		"""
		commit_number, commit_command = self.getAndFormatCommitNumber()
		filenames = self.executeChangedFilesPathsDiff(commit_command)
		filepaths = filenames.splitlines()
		return commit_number, commit_command, filepaths
