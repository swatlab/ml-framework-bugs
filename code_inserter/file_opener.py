# -*- coding: utf-8 -*-
import os, subprocess
class FileOpener:
	def __init__(self, git_dir):
		self.git_dir = git_dir

	def getFileContents(self, filepaths, git_revision):
		"""
		Opens all the changed files and obtain their text
		
		params:
		  - filepaths: paths of all the changed files at commit
			--> [filepath_1, filepath_2, ..., filepath_n]

		returns:
		  - files_contents: a 1D list of strings, obtained after reading entirely each file
			--> [file_1_content, file_2_content, .. , file_n_content]
		"""
		env_copy = os.environ.copy()
		env_copy['GIT_DIR'] = self.git_dir

		files_contents = []
		for filepath in filepaths:
			if self.git_dir:
				cmd = ['git', 'show', '{}:{}'.format(git_revision, filepath)]
				file_at_revision_cmd = subprocess.run(cmd, stdout=subprocess.PIPE, env=env_copy, check=True)
				content = file_at_revision_cmd.stdout.decode('utf-8')
				files_contents.append(content)
			else:
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

	def openFiles(self, filepaths, git_revision):
		"""
		[MAIN] Open the	changed files' content and put in files_contents_lines.
		getFileContents() gets each file's text in one string, then
		splitFileContents() splits each text in lines.
		
		params:
		  - filepaths: paths of all the changed files at commit
			--> [filepath_1, filepath_2, ..., filepath_n]
		
		returns:
		  - files_contents_lines: The entire text of each modified file, BUT is a 2D list
		 	obtained by splitlines on each element of file_contents
			--> [[file_1_line_1, file_1_line_2, .. , file_1_line_n], 
				[file_2_line_1, file_2_line_2, .. , file_2_line_n],
				[file_m_line_1, file_m_line_2, .. , file_m_line_n]]
		"""
		files_contents = self.getFileContents(filepaths, git_revision=git_revision)
		files_contents_lines = self.splitFileContents(files_contents)
		return files_contents_lines

