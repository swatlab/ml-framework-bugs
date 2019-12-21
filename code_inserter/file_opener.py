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

class FileOpener:
	def getFileContents(self, filepaths):
		"""
		Opens the changed files and obtain their text
		
		returns : a 1D list of strings, obtained after reading entirely each file
		--> [file_1_content, file_2_content, .. , file_n_content]
		"""
		file_contents = []
		for filepath in filepaths:
			file = open(filepath,"r") 
			file_content = file.read()
			file_contents.append(file_content)
			file.close()
		return file_contents

	def splitFileContents(self, file_contents):
		"""
		Uses file_contents to split the file content into lines
		
		returns : The entire text of each modified file, BUT is a 2D list
		 			obtained by splitlines on each element of file_contents
		--> [[file_1_line_1, file_1_line_2, .. , file_1_line_n], 
			[file_2_line_1, file_2_line_2, .. , file_2_line_n],
			[file_m_line_1, file_m_line_2, .. , file_m_line_n]]
		"""
		file_contents_lines = []
		for file_content in file_contents:
			file_contents_lines.append(file_content.splitlines())
		return file_contents_lines

	def openFiles(self, filepaths):
		file_contents = self.getFileContents(filepaths)
		file_contents_lines = self.splitFileContents(file_contents)
		return file_contents_lines

