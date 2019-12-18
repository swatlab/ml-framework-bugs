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

class Opener:
	def getFileContents(filepaths):
		"""
		Opens the files to trace and obtain their text
		
		returns : a 1D list of text (each element is the text of each file)
		"""
		file_contents = []
		for filepath in filepaths:
			file = open(filepath,"r") 
			file_content = file.read()
			file_contents.append(file_content)
			file.close()
		return file_contents

	def splitFileContents(file_contents):
		"""
		Uses file_contents to split the file content into lines
		
		returns : a 2D list of the files string in line by line format
		"""
		file_contents_lines = []
		for file_content in file_contents:
			file_contents_lines.append(file_content.splitlines())
		return file_contents_lines

