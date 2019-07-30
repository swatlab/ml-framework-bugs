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
        file_contents_lines.append(file_content.splitlines())
    return file_contents_lines

def commandPatchfile(commit_command):
    # TODO verifier que les paths
    result_patchfile = subprocess.run(['git', 'diff', commit_command], stdout=subprocess.PIPE)
    patchfile = result_patchfile.stdout.decode("utf-8")
    
    split_patchfile = splitPatchfile(patchfile)
    
    return split_patchfile

def splitPatchfile(patchfile):
    split_patchfile = patchfile.split('diff --git')
    return split_patchfile

def findChangedLines(split_patch):
    regex = r"^@@ [-+](\d+)"
    matches = re.finditer(regex, split_patch, re.MULTILINE)
    line_numbers = []
    
    for matchNum, match in enumerate(matches, start=1):
        # print(int(match.group(1))) # debug which lines are modified
        line_numbers.append(int(match.group(1)))
    return line_numbers

def findChangedLinesPerFile(split_patchfile):
    lines_numbers = []
    for split_patch in split_patchfile:
        lines_numbers.append(findChangedLines(split_patch))
    return lines_numbers

def removeEmptyElements(split_patchfile, file_contents_lines, lines_numbers):
    split_patchfile = list(filter(None, split_patchfile))
    file_contents_lines = list(filter(None, file_contents_lines))
    lines_numbers = list(filter(None, lines_numbers))
    return split_patchfile, file_contents_lines, lines_numbers

def insertTraceCpp(traced_file_contents_lines, lines_numbers, trace_call_Cpp):
    for traced_file_content_line, line_number in zip(traced_file_contents_lines, lines_numbers):
        # ajout de trace_call sur liste inversée pour conserver le numéro de ligne
        [traced_file_content_line.insert(n, trace_call_Cpp) for n in line_number[::-1]]
    return traced_file_contents_lines

def writeTracedFile(traced_file_contents_lines):
    # TODO
    # portability of new file name
    i = 1
    for traced_file_content_line in traced_file_contents_lines:
        traced_file_content = ("\n".join(traced_file_content_line))
        
        # concatenation dans un nouveau fichier
        new_file_path = "new_file"+str(i)+".py"
        new_file = open(new_file_path, "w")
        new_file.write(traced_file_content)
        print(new_file_path, " is written.")
        new_file.close()
        i += 1

def printInsertedLinesNumbers(lines_numbers, traced_file_contents_line, trace_call_Cpp):
    print("Original file patched lines : \n", lines_numbers)
    indicesa = [i for i, x in enumerate(traced_file_contents_lines[0]) if x == trace_call_Cpp]
    indicesb = [i for i, x in enumerate(traced_file_contents_lines[1]) if x == trace_call_Cpp]
    print("Trace.trace() is inserted at these lines : \n" ,indicesa, indicesb)

if __name__ == '__main__':
    commit_command = getVersionArguments()
    
    # obtenir contenu des fichiers à tracer
    filenames = commandFilepaths(commit_command)
    filepaths = filenames.splitlines()
    file_contents = getFileContents(filepaths) # est une liste de strings (après read fichier)
    file_contents_lines = splitFileContents(file_contents) # est une liste de lignes de string (après splitlines)
    
    # obtenir patch -pour chaque fichier séparément-
    split_patchfile = commandPatchfile(commit_command) # est une liste de strings (après split diff --git)
    lines_numbers = findChangedLinesPerFile(split_patchfile)
    trace_call_Cpp = "SOURCE_CODE_TRACER.trace('patched function called');" # WILL CHANGE DEPENDING OF LANGUAGE AND THE METHOD CALLED
    
    # les éléments de première dimension de file_contents_lines doivent correspondre avec ceux
    # de split_patchfile.
    # retirer éléments vide pour conserver cohérence
    split_patchfile, file_contents_lines, lines_numbers = removeEmptyElements(split_patchfile, file_contents_lines, lines_numbers)
    
    # insérer la trace et sauvegarder fichier tracé
    traced_file_contents_lines = copy.deepcopy(file_contents_lines)
    traced_file_contents_lines = insertTraceCpp(traced_file_contents_lines, lines_numbers, trace_call_Cpp)
    writeTracedFile(traced_file_contents_lines)
    
    # test pour vérifier numéro des lignes tracées
    printInsertedLinesNumbers(lines_numbers, traced_file_contents_lines, trace_call_Cpp)
    

# TODO
# -portability
# -vectorial stuff ?

# TODO portability
# numero de commit
    
# TODO
# update question sur stackO
