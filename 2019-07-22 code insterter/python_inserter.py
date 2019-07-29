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

def getVersionArguments():
    # to comment when script ready
    # TODO add Emilio improvement
    sys.argv.append('efc3d6b65')

    commit_number = sys.argv[1]
    commit_command = commit_number+'^..'+commit_number
    return commit_command
    
def commandFilepaths(commit_command):
    os.chdir("../..")
    os.chdir("pytorch")
    result_filenames = subprocess.run(['git', 'diff', "--name-only", commit_command], stdout=subprocess.PIPE)
    filenames = result_filenames.stdout.decode("utf-8")
    return filenames
    
def commandPatchfile(commit_command):
    resuly_patchfile = subprocess.run(['git', 'diff', commit_command], stdout=subprocess.PIPE)
    patchfile = result.stdout.decode("utf-8")
    return patchfile

""" 
Ouvre les fichiers à tracer et obtenir leur contenu textuel
Retourne une liste de string.
"""
def getFileContents(filepaths):
    file_contents = []
    for filepath in filepaths:
        file = open(filepath,"r") 
        file_content = file.read()
        file_contents.append(file_content)
        file.close()
    return file_contents

def splitFileContents(file_contents):
    file_contents_lines = []
    for file_content in file_contents:
        file_contents_lines.append(file_content.splitlines)
    return file_contents_lines

def findChangedLines(patchfile):
    regex = r"^@@ [-+](\d+)"
    matches = re.finditer(regex, patchfile, re.MULTILINE)
    line_numbers = []
    
    for matchNum, match in enumerate(matches, start=1):
        # print(int(match.group(1))) # debug which lines are modified
        line_numbers.append(int(match.group(1)))
    return line_numbers

if __name__ == '__main__':
    commit_command = getVersionArguments()
    filenames = commandFilepaths(commit_command)
    filepaths = filenames.splitlines()
    patchfile = commandPatchfile(commit_command)

    # fichiers à tracer
    file_contents = getFileContents(filepaths)
    file_contents_lines = splitFileContents(file_contents)
    
    # patch
    
    line_numbers = findChangedLines(patchfile)
    # WILL CHANGE DEPENDING OF LANGUAGE AND THE METHOD CALLED
    file_patch_lines_number = "SOURCE_CODE_TRACER.trace('patched function called');"
    
    # concatener lignes avec l'original
    # file_modified_content_lines = copy.deepcopy(file_content_lines)
    # for line_n in line_numbers:
    #     file_modified_content_lines.insert(line_n, file_patch_content_lines)
    
    # file_modified_content = ("\n".join(file_modified_content_lines))
    
    # # concatenation dans un nouveau fichier
    # new_file_path = "new_file.py"
    # new_file = open(new_file_path, "w")
    # new_file.write(file_modified_content)
    # print(new_file_path, " is written.")
    # new_file.close()

    
# rajouter lignes d'un file dans un autre file (à l'aide de diff)

# add trace.trace()
# file_patch_content_lines = file_patch_content.splitlines()

# TODO couper la où se trouvent les diff pour séparer par fichier 

# line_numbers = [1, 1, 1]
# another list for the patch file...


# TODO
# -insert for real (using the lines number)
# -portability
# -vectorial stuff ?

# TODO portability
# numero de commit
# chemins fichiers à inserer, patch, 
