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

	# Old insert trace code : checkout 0450408

	def insertTraces(self, filepaths, commit_number, to_be_inserted_files_lines, files_contents_lines):
		# TODO find a way to use various models
		trace_call = ['model_name = "GaussianNB"',
		'print("TRACER WAS CALLED")',
		'with open("/home/kacham/Documents/tracelogs/tracelog_" + commit_number + "_" + model_name + ".txt", "a") as myfile:',
		'    myfile.write(model_name + " in  line  called \n")']
		
		for to_be_inserted_file, file_content in zip(to_be_inserted_files_lines, files_contents_lines):
			for to_be_inserted_line in to_be_inserted_file:
				if to_be_inserted_line != None: # that means : line can be inserted
					# add indentation level
					original_line = file_content[to_be_inserted_line]
					trace_call = self.analyzerIndentation.addIndentationLevel(original_line, trace_call)

					# insert trace call
					file_content.insert(to_be_inserted_line, trace_call)
		# Now files_contents_lines contains all inserted traces. 
		# Write the array elements in the files
		# for 
		# for filepath, inserted_file in zip(filepaths, to_be_inserted_files_lines):
		# 	file = open(filepath,"w")
			
		# 	for inserted_line in inserted_file:
		# 		original_line = files_contents_lines[inserted_line]
		# 		print("ON VA CRASHER", original_line)
		# 		trace_call = self.analyzerIndentation.addIndentationLevel(original_line, trace_call)

		# 	file.close()

if __name__ == '__main__':
	inserter = Inserter()

	# Get filepaths of files to trace
	# filepaths: [filepath_1, filepath_2, ..., filepath_n]
	commit_number, commit_command, filepaths = inserter.diffExecutor.diffFilepaths()

	# lines_numbers: 
	# --> [[file_1_line_number_1, file_1_line_number_2, .. , file_1_line_number_n], 
	# 	[file_2_line_number_1, file_2_line_number_2, .. , file_2_line_number_n],
	# 	[file_m_line_number_1, file_m_line_number_2, .. , file_m_line_number_n]]
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
	to_be_inserted_files_lines = inserter.analyzerSyntax.analyze_syntax_python(lines_numbers, files_contents_lines)
    # #analyze_python_file(file_contents_lines, lines_numbers)
    
	inserter.insertTraces(filepaths, commit_number, to_be_inserted_files_lines, files_contents_lines)
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
