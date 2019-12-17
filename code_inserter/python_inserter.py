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

"""
-------------------- code inserter --------------------
"""
def getVersionArguments():
    """
    Parse commit number in the command line and create the commit argument for other commands
    
    returns :
        commit_command : the commit argument for other commands
    """
    
    parser = argparse.ArgumentParser(description='Commits')
    parser.add_argument('commits', metavar='C', type=str, nargs='+')
    args = parser.parse_args()

    commit_number = args.commits[0]
    commit_command = commit_number+'^..'+commit_number
    return commit_command
    
def commandFilepaths(commit_command):
    """
    Moves into the framework local Github repo and return the names of files changed at the commit
    
    returns :
        filenames : names of file changed at the commit
    parameters : 
        commit_command : commit argument for git diff command (example of command : git diff efc3d6b65^..efc3d6b65)

    """
    os.chdir("../..")
    # TODO adapt path towards desired framework Github repo
    os.chdir("pytorch")
    result_filenames = subprocess.run(['git', 'diff', "--name-only", commit_command], stdout=subprocess.PIPE)
    filenames = result_filenames.stdout.decode("utf-8")
    return filenames
    

def getFileContents(filepaths):
    """
    Opens the files to trace and obtain their text
    
    returns : a 1d list of text (each element is the text of each file)
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

def commandPatchfile(commit_command):
    """
    Moves into the framework local Github repo and process the patchfile to obtain split_patchfile
    
    returns :
        the patchfile split in different elements (one for one file changed)
    parameters : 
        commit_command : commit argument for git diff command (example of command : git diff efc3d6b65^..efc3d6b65)

    """
    result_patchfile = subprocess.run(['git', 'diff', commit_command], stdout=subprocess.PIPE)
    patchfile = result_patchfile.stdout.decode("utf-8")
    
    split_patchfile = splitPatchfile(patchfile)
    
    return split_patchfile

def splitPatchfile(patchfile):
    """
    create a different patchfile for each file changed
    returns a 1d list of patchfiles
    """
    split_patchfile = patchfile.split('diff --git')
    return split_patchfile

def findChangedLines(split_patch):
    """
    parses the split_patch (of one file at time) to obtain changed lines for each file
    
    return changed lines for each file 
    """
    regex = r"^@@ [-+](\d+)"
    matches = re.finditer(regex, split_patch, re.MULTILINE)
    line_numbers = []
    
    for matchNum, match in enumerate(matches, start=1):
        # print(int(match.group(1))) # debug which lines are modified
        line_numbers.append(int(match.group(1)))
    return line_numbers

def findChangedLinesPerFile(split_patchfile):
    """
    Go through the split_patchfile and get find the changed lines (of one file at time)
    """
    lines_numbers = []
    for split_patch in split_patchfile:
        lines_numbers.append(findChangedLines(split_patch))
    return lines_numbers

def removeEmptyElements(split_patchfile, file_contents_lines, lines_numbers):
    """
    remove empty elements in the three lists
    """
    split_patchfile = list(filter(None, split_patchfile))
    file_contents_lines = list(filter(None, file_contents_lines))
    lines_numbers = list(filter(None, lines_numbers))
    return split_patchfile, file_contents_lines, lines_numbers

def insertTraceCpp(traced_file_contents_lines, lines_numbers, trace_call_Cpp):
    """
    goes through the traced_file_contents_lines (copy of file_contents_lines) and add
    trace calls at the lines_numbers
    returns the inserted traced_file_contents_lines
    """
    for traced_file_content_line, line_number in zip(traced_file_contents_lines, lines_numbers):
        # adding of tracer.trace call on a inverted list to conserve the lines numbers (you add at the end so 
        # lines numbers aren't shifted)
        [traced_file_content_line.insert(n, trace_call_Cpp) for n in line_number[::-1]]
    return traced_file_contents_lines

def writeTracedFile(traced_file_contents_lines, filepaths, overwrite = False):
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

def printInsertedLinesNumbers(lines_numbers, traced_file_contents_line, trace_call_Cpp):
    print("Original file patched lines : \n", lines_numbers)
    indicesa = [i for i, x in enumerate(traced_file_contents_lines[0]) if x == trace_call_Cpp]
    indicesb = [i for i, x in enumerate(traced_file_contents_lines[1]) if x == trace_call_Cpp]
    print("Trace.trace() is inserted at these lines : \n" ,indicesa, indicesb)



"""
----------------------- code syntax analyzer ------------------------
"""
def analyze_python_file(file_contents_lines, lines_numbers):
    """
    TODO replace with code in python_auto_inserter.py
    """
    are_insertable_lines = []
    # python : def keyword, if __name__ == '__main__': or if __name__ == "__main__":
    regex = r"(def \w+\(.*\):|if __name__ == '__main__':|if __name__ == \"__main__\":)"
    
    # TODO check if file is python file
    # for each changed file, get changed lines numbers
    for file_content_line in file_contents_lines:
        # for each changed lines group
        for line_number in lines_numbers:
            syntax_index = line_number
            test_str = file_content_line[syntax_index]
            matches = re.finditer(regex, test_str, re.MULTILINE)
            
            # go to previous lines (decreasing order of lines number) until a function definition is reached
            while syntax_index != 0 & len(matches) != 0: # & syntax_index != in lines_numbers 
                test_str = file_content_line[syntax_index]
                matches = re.finditer(regex, test_str, re.MULTILINE)

                for matchNum, match in enumerate(matches, start=1):
                    for groupNum in range(0, len(match.groups())):
                        groupNum = groupNum + 1
                
                        
                line_number -= 1
# C : regex using void/int/bool/etc functionName() and {}




if __name__ == '__main__':
    commit_command = getVersionArguments()
    
    # get files to trace obtenir fichiers à tracer
    filenames = commandFilepaths(commit_command)
    filepaths = filenames.splitlines()
    
    # le texte de chaque fichier modifié 
    # est une liste de strings (après read fichier)
    file_contents = getFileContents(filepaths)
    
    # le texte de chaque fichier modifié.
    # 2D list : fichier, lignes de code
    # est une liste de lignes de string (après splitlines)
    file_contents_lines = splitFileContents(file_contents)
    
    # obtenir patch -pour chaque fichier séparément-
    split_patchfile = commandPatchfile(commit_command) # est une liste de strings (après split diff --git)
    lines_numbers = findChangedLinesPerFile(split_patchfile) # 2D list : fichier, lignes changées 
    trace_call_Cpp = "SOURCE_CODE_TRACER.trace('patched function called');" # DEVRA CHANGER EN FONCTION DU LANGAGE ET DE LA MÉTHODE APPELÉE
    
    print(lines_numbers)
    # les éléments de première dimension de file_contents_lines doivent correspondre avec ceux
    # de split_patchfile.
    # retirer éléments vide pour conserver cohérence
    split_patchfile, file_contents_lines, lines_numbers = removeEmptyElements(split_patchfile, file_contents_lines, lines_numbers)
    
    #analyze_python_file(file_contents_lines, lines_numbers)
    
    # insérer la trace et sauvegarder fichier tracé
    traced_file_contents_lines = copy.deepcopy(file_contents_lines)
    traced_file_contents_lines = insertTraceCpp(traced_file_contents_lines, lines_numbers, trace_call_Cpp)
    
    writeTracedFile(traced_file_contents_lines, filepaths)
    
    # # test pour vérifier numéro des lignes tracées
    printInsertedLinesNumbers(lines_numbers, traced_file_contents_lines, trace_call_Cpp)
    

# TODO
# -portability
# -vectorial stuff ?
# -langage de la trace insérée
