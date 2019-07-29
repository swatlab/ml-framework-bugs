# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 14:06:21 2019

@author: kevin
"""

import copy
import os
import re
import subprocess
import sys

# to comment when script ready
# TODO add Emilio improvement
sys.argv.append('efc3d6b65')

# obtenir la patch
commit_number = sys.argv[1]
commit_command = commit_number+'^..'+commit_number

os.chdir("../..")
os.chdir("pytorch")
result_filenames = subprocess.run(['git', 'diff', "--name-only", commit_command], stdout=subprocess.PIPE)
filenames = result_filenames.stdout.decode("utf-8")
filepaths = filenames.splitlines()
result = subprocess.run(['git', 'diff', commit_command], stdout=subprocess.PIPE)
test_str = result.stdout.decode("utf-8")

file_contents = []

# ouvrir fichier à  py
for filepath in filepaths:
    file = open(filepath,"r") 
    file_content = file.read()
    file_contents.append(file_content)
    file.close()

# file_patch = open("tracer.py","r")
# file_patch_content = file_patch.read()
# file_patch.close()


# regex trouver numero lignes changees.
regex = r"^@@ [-+](\d+)"
matches = re.finditer(regex, test_str, re.MULTILINE)
line_numbers = []

for matchNum, match in enumerate(matches, start=1):
    
    #print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
    
    print(line_numbers.append(int(match.group(1))))
    #print ("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))

# rajouter lignes d'un file dans un autre file (à l'aide de diff)

# split texte en lignes
file_content_lines = file_content.splitlines()
# add trace.trace()
# file_patch_content_lines = file_patch_content.splitlines()
# WILL CHANGE DEPENDING OF LANGUAGE AND THE METHOD CALLED
file_patch_lines_number = "SOURCE_CODE_TRACER.trace('patched function called');"
# TODO couper la où se trouvent les diff pour séparer par fichier 

# line_numbers = [1, 1, 1]
# another list for the patch file...

# concatener lignes avec l'original
file_modified_content_lines = copy.deepcopy(file_content_lines)
for line_n in line_numbers:
    file_modified_content_lines.insert(line_n, file_patch_content_lines)

file_modified_content = ("\n".join(file_modified_content_lines))

# concatenation dans un nouveau fichier
new_file_path = "new_file.py"
new_file = open(new_file_path, "w")
new_file.write(file_modified_content)
print(new_file_path, " is written.")
new_file.close()

# TODO :
# -insert for real (using the lines number)
# -portability
# -vectorial stuff ?

# TODO portability
# numero de commit
# chemins fichiers à inserer, patch, 
