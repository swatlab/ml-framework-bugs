# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 14:06:21 2019

@author: kevin
"""

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
		self.analyzerSyntax = AnalyzerSyntax()
		self.diffExecutor = DiffExecutor()
		self.diffProcessor = DiffProcessor()
		self.opener = FileOpener()

	def insertTraceCpp(self, traced_file_contents_lines, lines_numbers, trace_call_Cpp):
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



if __name__ == '__main__':
    inserter = Inserter()
    commit_command = inserter.diffExecutor.getAndFormatCommitNumber()
    
    # Get files to trace
	# filenames: [filename_1, filename_2, ..., filename_n]
    filenames = inserter.diffExecutor.executeChangedFilesPathsDiff(commit_command)
    filepaths = filenames.splitlines()
    
    # file_contents: The entire text of each modified file. 
	#			   It is a 1D list of strings, obtained after reading entirely each file
    # 			   [file_1_content, file_2_content, .. , file_n_content]
    file_contents = inserter.opener.getFileContents(filepaths)
    
    # file_contents_lines: The entire text of each modified file, BUT is a 2D list
	# 				    obtained by splitlines on each element of file_contents
	# [[file_1_line_1, file_1_line_2, .. , file_1_line_n], 
	#  [file_2_line_1, file_2_line_2, .. , file_2_line_n],
	#  [file_m_line_1, file_m_line_2, .. , file_m_line_n]]
    file_contents_lines = inserter.opener.splitFileContents(file_contents)
    
    # obtenir patch -pour chaque fichier séparément-
    split_patchfile = inserter.diffProcessor.executePatchfileCommand(commit_command) # est une liste de strings (après split diff --git)
    print(split_patchfile)
    lines_numbers = inserter.diffProcessor.findChangedLinesPerFile(split_patchfile) # 2D list : fichier, lignes changées 
    trace_call_Cpp = "SOURCE_CODE_TRACER.trace('patched function called');" # DEVRA CHANGER EN FONCTION DU LANGAGE ET DE LA MÉTHODE APPELÉE
    
    # print(lines_numbers)
    # les éléments de première dimension de file_contents_lines doivent correspondre avec ceux
    # de split_patchfile.
    # retirer éléments vide pour conserver cohérence
    split_patchfile, file_contents_lines, lines_numbers = inserter.analyzerSyntax.removeEmptyElements(split_patchfile, file_contents_lines, lines_numbers)
    
    #analyze_python_file(file_contents_lines, lines_numbers)
    
    # insérer la trace et sauvegarder fichier tracé
    traced_file_contents_lines = copy.deepcopy(file_contents_lines)
    traced_file_contents_lines = inserter.insertTraceCpp(traced_file_contents_lines, lines_numbers, trace_call_Cpp)
    
    inserter.writeTracedFile(traced_file_contents_lines, filepaths)
    
    # # test pour vérifier numéro des lignes tracées
    # inserter.printInsertedLinesNumbers(lines_numbers, traced_file_contents_lines, trace_call_Cpp)
    

# TODO
# -portability
# -vectorial stuff ?
# -langage de la trace insérée
