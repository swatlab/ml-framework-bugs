# -*- coding: utf-8 -*-

import argparse
import os
import subprocess

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
		[MAIN] Executes two class methods to obtain the filepaths of changed files.

		returns:
		  - commit_number: commit SHA
		  - commit_command: commit argument for git diff command
			--> example of command : git diff fe31832^..fe31832
		  - filepaths: paths of all the changed files at commit
			--> [filepath_1, filepath_2, ..., filepath_n]
		"""
		commit_number, commit_command = self.getAndFormatCommitNumber()
		filenames = self.executeChangedFilesPathsDiff(commit_command)
		filepaths = filenames.splitlines()
		return commit_number, commit_command, filepaths
