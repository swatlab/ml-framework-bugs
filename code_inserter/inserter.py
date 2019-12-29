# -*- coding: utf-8 -*-
"""
The main file of the code_inserter. The main function executes
all of the modules' main functions

Execute code:
	python inserter.py commit_number
	example: py inserter.py 9e5819a
"""

from analyzer_indentation import AnalyzerIndentation
from analyzer_syntax import AnalyzerSyntax
from diff_executor import DiffExecutor
from diff_processor import DiffProcessor
from file_opener import FileOpener
import copy

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

	def overwriteTracedFiles(self, traced_files_contents_lines, filepaths):
		"""
		Overwrite the framework's original code with the trace-inserted code.

		params: 
		  - traced_files_contents_lines: trace-inserted code
		  - filepaths: paths of to be 'trace-inserted' files
		"""
		for traced_file_content, filepath in zip(traced_files_contents_lines, filepaths):
			# copy file_content array in a string
			new_file_content = "\n".join(traced_file_content)
			
			# empty the file. Reference: https://stackoverflow.com/a/30604077/9876427 
			with open(filepath, 'w'): pass

			# write over it
			with open(filepath, "w") as text_file:
				text_file.write("{0}".format(new_file_content))

	def insertTraces(self, filepaths, commit_number, to_be_inserted_files_lines, files_contents_lines):
		"""
		[MAIN] Use the to_be_inserted_files_lines to insert trace_call in the files_contents_lines
		(from end of file_content to beginning of file_content)
		and then overwrite the original code with overwriteTracedFiles()

		params:
		  - filepaths: paths of all the changed files 
		  - commit_number: commit SHA
		  - to_be_inserted_files_lines: same thing as lines_numbers.
			The line number will be normal if the line can be inserted, else None
			--> [[file_1_line_number_1, file_1_line_number_2, .. , file_1_line_number_n], 
				[file_2_line_number_1, file_2_line_number_2, .. , file_2_line_number_p],
				[file_m_line_number_1, file_m_line_number_2, .. , file_m_line_number_q]]

		  - files_contents_lines: The entire text of each modified file, BUT is a 2D list
			obtained by splitlines on each element of file_contents
			--> [[file_1_line_1, file_1_line_2, .. , file_1_line_n], 
				[file_2_line_1, file_2_line_2, .. , file_2_line_n],
				[file_m_line_1, file_m_line_2, .. , file_m_line_n]]
		"""
		
		# Iterate through files-line in to_be_inserted_files_lines,
		# check if line is insertable
		# if yes, insert trace in files_contents_lines
		traced_files_contents_lines = copy.deepcopy(files_contents_lines)
		index = 0
		for to_be_inserted_file, file_content in zip(to_be_inserted_files_lines, files_contents_lines):
			for to_be_inserted_line in reversed(to_be_inserted_file): 
				print("\nstep 1 filepath :", filepaths[index])
				print("step 2 to be inserted line : ", to_be_inserted_line)
				if to_be_inserted_line != None: # that means : line can be inserted
					# add indentation level
					original_line = file_content[to_be_inserted_line]

					# TODO find a way to change the model_name, commit_number, 
					trace_call = ['model_name = "GaussianNB"',
					'print("TRACER WAS CALLED")',
					'with open("/home/kacham/Documents/tracelogs/tracelog_" + commit_number + "_" + model_name + ".txt", "a") as myfile:',
					'    myfile.write(model_name + " in  line  called \n")'.encode("unicode_escape").decode("utf-8")]
					# TODO add the filename and line number in the myfile.write on the line above ^

					trace_call_spaced = self.analyzerIndentation.addIndentationLevel(original_line, trace_call)

					# insert trace call
					#print(" INDEX ", index, " \n", file_content)
					trace_index = 0
					for trace in trace_call_spaced: 
						traced_files_contents_lines[index].insert(to_be_inserted_line + 1 + trace_index, trace)
						trace_index = trace_index + 1
			index = index + 1

		# Now files_contents_lines contains all inserted traces. 
		# Write each element of traced_files_contents_lines in the framework code's files
		self.overwriteTracedFiles(traced_files_contents_lines, filepaths)

if __name__ == '__main__':
	inserter = Inserter()

	# Get filepaths of files to trace. Obtain commit_number and commit_command for future uses
	commit_number, commit_command, filepaths = inserter.diffExecutor.diffFilepaths()
	# filepaths: 
	# 		[filepath_1, filepath_2, ..., filepath_n]

	# Use git diff to obtain the numbers of lines changed
	lines_numbers = inserter.diffProcessor.diffLinesNumbers(commit_command)
	# lines_numbers: 
	# -->	[[file_1_line_number_1, file_1_line_number_2, .. , file_1_line_number_n], 
	# 		[file_2_line_number_1, file_2_line_number_2, .. , file_2_line_number_n],
	# 		[file_m_line_number_1, file_m_line_number_2, .. , file_m_line_number_n]]

	# Get the text of changed files in array format
	files_contents_lines = inserter.opener.openFiles(filepaths)    
	# file_contents_lines: The entire text of each modified file, BUT is a 2D list
	# 				    obtained by splitlines on each element of file_contents
	# 		[[file_1_line_1, file_1_line_2, .. , file_1_line_n], 
	#  		 [file_2_line_1, file_2_line_2, .. , file_2_line_n],
	#  		 [file_m_line_1, file_m_line_2, .. , file_m_line_n]]

	# Check syntax of the changed files. If the changed lines (lines_numbers) can be inserted,
	# the line number will be present in to_be_inserted_files_lines, else will be None
	to_be_inserted_files_lines = inserter.analyzerSyntax.analyze_syntax_python(lines_numbers, files_contents_lines)    
	# inserted_files_lines: 2D array of lines_number that can be inserted
	# 		[[file_1_line_number_1, file_1_line_number_2, .. , file_1_line_number_n], 
	# 		 [file_2_line_number_1, file_2_line_number_2, .. , file_2_line_number_n],
	# 		 [file_m_line_number_1, file_m_line_number_2, .. , file_m_line_number_n]]
    
	# Insert traces after making the syntax check
	inserter.insertTraces(filepaths, commit_number, to_be_inserted_files_lines, files_contents_lines)
