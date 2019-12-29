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

class FileOpener:
	def getFileContents(self, filepaths):
		"""
		Opens all the changed files and obtain their text
		
		returns:
		  - files_contents: a 1D list of strings, obtained after reading entirely each file
			--> [file_1_content, file_2_content, .. , file_n_content]
		"""
		files_contents = []
		for filepath in filepaths:
			file = open(filepath,"r") 
			file_content = file.read()
			files_contents.append(file_content)
			file.close()
		return files_contents

	def splitFileContents(self, files_contents):
		"""
		Uses file_contents to split the file content into lines
		
		returns:
		  - files_contents_lines: The entire text of each modified file, BUT is a 2D list
		 	obtained by splitlines on each element of file_contents
			--> [[file_1_line_1, file_1_line_2, .. , file_1_line_n], 
				[file_2_line_1, file_2_line_2, .. , file_2_line_n],
				[file_m_line_1, file_m_line_2, .. , file_m_line_n]]
		"""
		files_contents_lines = []
		for file_content in files_contents:
			files_contents_lines.append(file_content.splitlines())
		return files_contents_lines

	def openFiles(self, filepaths):
		"""
		[MAIN] Open the	changed files' content and put in files_contents_lines.
		getFileContents() gets each file's text in one string, then
		splitFileContents() splits each text in lines.
		
		params:
		  - filepaths: paths of all the changed files
		
		returns:
		  - files_contents_lines: The entire text of each modified file, BUT is a 2D list
		 	obtained by splitlines on each element of file_contents
			--> [[file_1_line_1, file_1_line_2, .. , file_1_line_n], 
				[file_2_line_1, file_2_line_2, .. , file_2_line_n],
				[file_m_line_1, file_m_line_2, .. , file_m_line_n]]
		"""
		files_contents = self.getFileContents(filepaths)
		files_contents_lines = self.splitFileContents(files_contents)
		return files_contents_lines

