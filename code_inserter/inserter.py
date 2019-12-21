# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 14:06:21 2019

@author: kevin
"""

from analyzer_indentation import AnalyzerIndentation
from analyzer_syntax import AnalyzerSyntax
from diff_executor import DiffExecutor
from diff_processor import DiffProcessor
from file_opener import FileOpener
import argparse
import copy
import os
import re
import subprocess
import sys

"""
-------------------- code inserter --------------------
"""
class Inserter:
	def __init__(self):
		self.analyzerIndentation = AnalyzerIndentation()
		self.analyzerSyntax = AnalyzerSyntax()
		self.diffExecutor = DiffExecutor()
		self.diffProcessor = DiffProcessor()
		self.opener = FileOpener()

	def insertTrace(self, traced_file_contents_lines, lines_numbers, trace_call_Cpp):
		"""
		goes through the traced_file_contents_lines (copy of file_contents_lines) and add
		trace calls at the lines_numbers
		returns the inserted traced_file_contents_lines
		"""
		for traced_file_content_line, line_number in zip(traced_file_contents_lines, lines_numbers):
			# adding of tracer.trace call on a inverted list to conserve the lines numbers (by adding from the end,  
			# the lines numbers doesn't shift)
			[traced_file_content_line.insert(n, trace_call_Cpp) for n in line_number[::-1]]
		return traced_file_contents_lines

	def writeTracedFile(self, traced_file_contents_lines, filepaths, overwrite = False):
		"""
		write the traced files in new files
		"""
		for traced_file_content_line, filepath in zip(traced_file_contents_lines, filepaths):
			traced_file_content = ("\n".join(traced_file_content_line))
			
			filename, file_extension = os.path.splitext(filepath)
			
			# Concatenate in a new file
			new_file_path = filepath if overwrite else "{}_traced{}".format(filename, file_extension)
			new_file = open(new_file_path, "w")
			new_file.write(traced_file_content)
			print(new_file_path, " is written.")
			new_file.close()

	def printInsertedLinesNumbers(self, lines_numbers, traced_file_contents_line, trace_call_Cpp):
		print("Original file patched lines : \n", lines_numbers)
		indicesa = [i for i, x in enumerate(traced_file_contents_lines[0]) if x == trace_call_Cpp]
		indicesb = [i for i, x in enumerate(traced_file_contents_lines[1]) if x == trace_call_Cpp]
		print("Trace.trace() is inserted at these lines : \n" ,indicesa, indicesb)



	def insertTraces(self, commit_number, inserted_files_lines, files_contents_lines):
		
		
		# TODO find a way to use various models
		trace_call = ['model_name = "GaussianNB"',
		'print("TRACER WAS CALLED")',
		'with open("/home/kacham/Documents/tracelogs/tracelog_" + commit_number + "_" + model_name + ".txt", "a") as myfile:',
		'    myfile.write(model_name + " in  line  called \n")']
		
		for inserted_file in inserted_files_lines:
			for inserted_line in inserted_file:
				trace_call = self.analyzerIndentation.addIndentationLevel(inserted_line, trace_call)


if __name__ == '__main__':
	inserter = Inserter()

	# Get filepaths of files to trace
	# filepaths: [filepath_1, filepath_2, ..., filepath_n]
	commit_number, commit_command, filepaths = inserter.diffExecutor.diffFilepaths()

	# lines_numbers: [line_number_1, line_number_2, ..., line_number_n]
	lines_numbers = inserter.diffProcessor.diffLinesNumbers(commit_command)
	# TODO DEBUG seulement 37 a changé, pas les autres ... 
	# print(lines_numbers)
    
	# file_contents_lines: The entire text of each modified file, BUT is a 2D list
	# 				    obtained by splitlines on each element of file_contents
	# [[file_1_line_1, file_1_line_2, .. , file_1_line_n], 
	#  [file_2_line_1, file_2_line_2, .. , file_2_line_n],
	#  [file_m_line_1, file_m_line_2, .. , file_m_line_n]]
	files_contents_lines = inserter.opener.openFiles(filepaths)
    
	# inserted_files_lines: 2D array of lines_number that can be inserted
	# [[file_1_line_number_1, file_1_line_number_2, .. , file_1_line_number_n], 
	# [file_2_line_number_1, file_2_line_number_2, .. , file_2_line_number_n],
	# [file_m_line_number_1, file_m_line_number_2, .. , file_m_line_number_n]]
	inserted_files_lines = inserter.analyzerSyntax.analyze_syntax_python(lines_numbers, files_contents_lines)
    # #analyze_python_file(file_contents_lines, lines_numbers)
    
	inserter.insertTraces(commit_number, inserted_files_lines, files_contents_lines)
    # # insérer la trace et sauvegarder fichier tracé
    # traced_file_contents_lines = copy.deepcopy(file_contents_lines)
    # traced_file_contents_lines = inserter.insertTraceCpp(traced_file_contents_lines, lines_numbers, trace_call_Cpp)
    
    # inserter.writeTracedFile(traced_file_contents_lines, filepaths)
    
    # # test pour vérifier numéro des lignes tracées
    # inserter.printInsertedLinesNumbers(lines_numbers, traced_file_contents_lines, trace_call_Cpp)
    

# TODO
# -portability
# -vectorial stuff ?
# -langage de la trace insérée
