# -*- coding: utf-8 -*-

import re
import subprocess
import os

class DiffProcessor:
	def __init__(self, git_dir):
		self.git_dir = git_dir

	def splitPatchfile(self, patchfile):
		"""
		[SUB-FUNCTION] of executePatchfileCommand()
		Separate the patchfile into patchfiles, one for each file changed.
		
		returns:
		  - split_patchfile: a 1D list of patchfiles (string)
			--> [patchfile_1, patchfile_2, ..., patchfile_n]
		"""
		split_patchfile = patchfile.split('diff --git')
		return split_patchfile

	def executePatchfileCommand(self, commit_command):
		"""
		Execute a git diff command to retrieve the commit patchfile, then use
		splitPatchfile to split the lines of patchfile. This function doesn't
		move into the framework repository because DiffExecutor already gets
		into he framework local repo. 
		
		parameters: 
		  - commit_command: commit argument for git diff command
			--> example of command : git diff fe31832^..fe31832
		
		returns:
		  - split_patchfile: a 1D list of patchfiles (string)
			--> [patchfile_1, patchfile_2, ..., patchfile_n]
		"""
		env_copy = os.environ.copy()
		env_copy['GIT_DIR'] = self.git_dir
		result_patchfile = subprocess.run(['git', 'diff', commit_command], stdout=subprocess.PIPE, env=env_copy)
		patchfile = result_patchfile.stdout.decode("utf-8")
		
		split_patchfile = self.splitPatchfile(patchfile)
		
		return split_patchfile
		
	def findChangedLines(self, split_patch):
		"""
		[SUB-FUNCTION] of findChangedLinesPerFile(). Parses the split_patch
		to obtain changed lines for each file
		
		returns:
		  - line_numbers: changed lines of 1 file 
			--> [line_number_1, line_number_2, ..., line_number_n]
		"""
		regex_hunk = r"@@ [-+](?P<mhunk>\d+),(?P<mlen>\d+)\s\+(?P<phunk>\d+),(?P<plen>\d+)"
		# Beginning and len of hunks of original file (minus) (m)
		mh_begins, mh_lens = [], []
		# Beginning and len of hunks of original file (plus) (p)
		ph_begins, ph_lens = [], []
		m_intra_hunk_offset, p_intra_hunk_offset = 0, 0
		m_offset, p_offset = 0, 0
		removals, adds = [], []
		# Skip 4 lines that contain:
		# diff --git a/file b/file
		# index <sha>..<sha> 100644
		# --- a/file
		# +++ b/file
		left_mod, right_mod = [], []
		for line in split_patch.splitlines(keepends=False)[4:]:
			mh = re.match(regex_hunk, line, re.MULTILINE)
			if mh is not None:
				g = mh.groupdict()
				mh_begins.append(g['mhunk']); mh_lens.append(g['mlen']); ph_begins.append(g['phunk']); ph_begins.append(g['plen'])
				m_offset, p_offset = g['mhunk'], g['phunk']
				m_intra_hunk_offset, p_intra_hunk_offset = 0, 0
			else:
				if line.startswith('+ '):
					ln = int(p_offset) + p_intra_hunk_offset
					adds.append(ln)
					left_mod.append(int(m_offset) + m_intra_hunk_offset)
					right_mod.append(int(p_offset) + p_intra_hunk_offset)
					p_intra_hunk_offset += 1
				elif line.startswith('- '):
					ln = int(m_offset) + m_intra_hunk_offset
					removals.append(ln)
					left_mod.append(int(m_offset) + m_intra_hunk_offset)
					right_mod.append(int(p_offset) + p_intra_hunk_offset)
					m_intra_hunk_offset += 1
				else:
					m_intra_hunk_offset += 1
					p_intra_hunk_offset += 1
		
		return left_mod, right_mod

	def findChangedLinesPerFile(self, split_patchfile):
		"""
		Scour the split_patchfile to find the changed lines (of one patchfile at time)
		
		returns:
		  - lines_numbers: changed lines of every file
			--> [[file_1_line_number_1, file_1_line_number_2, .. , file_1_line_number_n], 
				[file_2_line_number_1, file_2_line_number_2, .. , file_2_line_number_p],
				[file_m_line_number_1, file_m_line_number_2, .. , file_m_line_number_q]]
		"""
		lines_numbers = []
		for split_patch in split_patchfile:
			lines_numbers.append(self.findChangedLines(split_patch))
		return lines_numbers

	def diffLinesNumbers(self, commit_command):
		"""
		[MAIN] From the commit command in parameter, execute a git diff command, process
		the output of the command and return the changed lines numbers from the command.

		parameters: 
		  - commit_command: commit argument for git diff command
			--> example of command : git diff fe31832^..fe31832

		returns:
		  - lines_numbers: changed lines of every file
			--> [[file_1_line_number_1, file_1_line_number_2, .. , file_1_line_number_n], 
				[file_2_line_number_1, file_2_line_number_2, .. , file_2_line_number_p],
				[file_m_line_number_1, file_m_line_number_2, .. , file_m_line_number_q]]
		"""
		split_patchfile = self.executePatchfileCommand(commit_command)
		# remove empty elements caused by string.split()
		split_patchfile = list(filter(None, split_patchfile))
		lines_numbers = self.findChangedLinesPerFile(split_patchfile)
		return lines_numbers
