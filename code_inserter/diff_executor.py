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

class DiffExecutor:
	def getAndFormatCommitNumber(self):
		"""
		Parse commit number from the command line and format it
		like this "commit_number^..commit_number"
		
		returns :
			commit_command : commit number in the format "commit_number^..commit_number"
		"""
		
		parser = argparse.ArgumentParser(description='Commits')
		parser.add_argument('commits', metavar='C', type=str, nargs='+')
		args = parser.parse_args()

		commit_number = args.commits[0]
		commit_command = commit_number+'^..'+commit_number
		return commit_command
		
	def executeChangedFilesPathsDiff(self, commit_command):
		"""
		Moves into the framework local repo and return the names of files changed at the commit
		
		parameters : 
			commit_command : commit number in the format "commit_number^..commit_number"
							(example of command : git diff efc3d6b^..efc3d6b)

		returns :
			filenames : names of file changed at the commit
		
		"""
		os.chdir("../..")
		# TODO adapt path towards desired framework Github repo
		os.chdir("scikit-learn")
		result_filenames = subprocess.run(['git', 'diff', "--name-only", commit_command], stdout=subprocess.PIPE)
		filenames = result_filenames.stdout.decode("utf-8")
		return filenames

if __name__ == '__main__':
	differ = DiffExecutor()
	print("smt for now")
	commit_command = differ.getAndFormatCommitNumber()
	filenames = differ.executeChangedFilesPathsDiff(commit_command)
	
	print(filenames)
    

