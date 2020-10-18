# -*- coding: utf-8 -*-

import os
import subprocess
from pathlib import Path


# PARAM: COMMIT ---> from console
FRAMEWORK_PATH = "scikit-learn"

class DiffExecutor:
	def __init__(self, commits, git_dir):
		self.commits = commits
		self.git_dir = git_dir

	def getAndFormatCommitNumber(self):
		"""
		Parse commit number from the command line and format it
		like this "commit_number^..commit_number"
		
		returns:
			commit_command: commit number in the format "commit_number^..commit_number"
			--> example of command : git diff fe31832^..fe31832
		"""
		commit_number = self.commits[0]
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

		env_copy = os.environ.copy()
		env_copy['GIT_DIR'] = self.git_dir
		# TODO adapt path towards desired framework Github repo
		result_filenames = subprocess.run(['git', 'diff', "--name-only", commit_command], stdout=subprocess.PIPE, env=env_copy)
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
