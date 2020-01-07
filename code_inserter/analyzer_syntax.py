# -*- coding: utf-8 -*-

# https://docs.python.org/2/library/trace.html
# https://docs.python.org/3.0/library/trace.html

import re

class AnalyzerSyntax:
    def is_empty_line(self, test_str):
        """
        matches an empty
        returns true if there is only one match
        """
        empty_line_regex = r"^\s*$"
        empty_line_match = re.findall(empty_line_regex, test_str, re.MULTILINE)
        return len(empty_line_match) == 1

    def is_class_start(self, test_str):
        """
        matches a class def keyword
        returns true if there is only one match
        """
        regex = r"(class .+:)"
        function_matches = re.findall(regex, test_str, re.MULTILINE)
        return len(function_matches) == 1

    def is_python_block_start(self, test_str):
        """
        matches a def, an if, etc. in the test_str
        returns true if there is only one match
        """
        regex = r"(def \w+\(.*\):|if .+:|elif .+:|else.+:|try:|except \w+:|for .+:|while .+:|class .+:)"
        function_matches = re.findall(regex, test_str, re.MULTILINE)
        return len(function_matches) == 1

    def is_multiline_start(self, test_str):
        """
        matches the beginning of multiline code statement
        example : my_list = [el1, el2, el3, <--
                              el4, el5, el6,
                              el7, el8, el9]
        returns true if there is only one match
        """
        regex = r"(\[.*,$|\(.*,$|\{.*,$)"
        function_matches = re.findall(regex, test_str, re.MULTILINE)
        return len(function_matches) == 1

    def is_multiline_middle(self, test_str):
        """
        matches the beginning of multiline code statement
        example : my_list = [el1, el2, el3,
                              el4, el5, el6, <--
                              el7, el8, el9]
        catches also multiline starts
        """
        regex = r".*,$"
        function_matches = re.findall(regex, test_str, re.MULTILINE)
        return len(function_matches) == 1

    def is_multiline_end(self, test_str):
        """
        matches the beginning of multiline code statement
        example : my_array = [el1, el2, el3,
                              el4, el5, el6,
                              el7, el8, el9] <--
        returns true if there is only one match
        """
        regex = r"[^\[].*\]$|[^\(].*\)$|[^\{].*\}$|[^\[].*\]:$|[^\(].*\):$|[^\{].*\}:$"
        function_matches = re.findall(regex, test_str, re.MULTILINE)
        return len(function_matches) == 1

    def is_docstring_line(self, test_str):
        """
        matches a docstring that start and end at the same line
        returns true if there is only one match
        """
        regex = r"(\"\"\".*\"\"\"|'''.*''')"
        function_matches = re.findall(regex, test_str, re.MULTILINE)
        return len(function_matches) == 1

    def is_docstring_delimiter(self, test_str):
        """
        matches only one occurence of docstring delimiter
        returns true if there is only one match
        """
        regex = r"\"\"\"|'''"
        function_matches = re.findall(regex, test_str, re.MULTILINE)
        return len(function_matches) == 1

    def is_comment_line(self, test_str):
        """
        matches a whitespace followed by a #
        returns true if there is only one match
        """
        regex = r"(^\s*#)"
        function_matches = re.findall(regex, test_str, re.MULTILINE)
        return len(function_matches) == 1

    def is_decorator_line(self, test_str):
        """
        matches a whitespace followed by a @
        returns true if there is only one match
        """
        regex = r"(^\s*@)"
        function_matches = re.findall(regex, test_str, re.MULTILINE)
        return len(function_matches) == 1

    def is_return_statement(self, test_str):
        """
        matches a whitespace followed by a @
        returns true if there is only one match
        """
        regex = r"(^\s*return)"
        function_matches = re.findall(regex, test_str, re.MULTILINE)
        return len(function_matches) == 1

    def is_pass_statement(self, test_str):
        """
        matches a whitespace followed by a @
        returns true if there is only one match
        """
        regex = r"(^\s*pass)"
        function_matches = re.findall(regex, test_str, re.MULTILINE)
        return len(function_matches) == 1

    def is_normal_line(self, test_str):
        """
        matches a def, an if, ... or a while in the test_str (one line of code)
        returns true if there is no match (the line is a normal code line)
        """
        regex = r"(def \w+\(.*|if .+:|elif .+:|else.+:|try:|except \w+:|for .+:|while .+:|class .+:)"
        function_matches = re.findall(regex, test_str, re.MULTILINE)
        return len(function_matches) == 0

    def find_function_matches(self, test_str):
        """
        matches a def, an if, ... or a while in the test_str (one line of code)
        returns the litteral value found for printing
        """
        regex = r"(def \w+\(.*|if .+:|elif .+:|else.+:|try:|except \w+:|for .+:|while .+:|class .+:)"
        function_matches = re.findall(regex, test_str, re.MULTILINE)
        return function_matches

    def printInsertableLines(self, insertable_lines):
        """
        [FOR TESTING] Takes a 1D array of booleans. The array represents each line of the original
        code file.
        """
        # TODO don`t overwrite if the function is called multiple times
        with open('insertable_lines.txt', 'w') as f:
            for item in insertable_lines:
                f.write("%s\n" % item)

    def print_to_be_inserted_validity(self, lines_numbers, to_be_inserted_files_lines):
        """
        [FOR DEBUG] check if lines_numbers and to_be are same dimensions
        """
        print("lines_numbers and to_be_inserted_files_lines")
        print(len(lines_numbers), len(to_be_inserted_files_lines))
        for l, t in zip(lines_numbers, to_be_inserted_files_lines):
            print(len(l), len(t))

    def increment_numeric_index(self, numeric_index):
        return numeric_index + 1

    def analyze_python(self, code_lines):
        """
        Checks every line of a file file_content_lines (1D array, because
        it is the second dimension of files_contents_lines) and 
        create a same sized 1D list. A line in insertable_lines
        indicates if the corresponding line in file_content_lines
        can have a trace call at the next line (real line + 1)

        params:
          - code_lines: a 1D array of the files lines
            --> [file_line_1, file_line_2, .. , file_line_n]

        returns:
          - insertable_lines: a 1D array that indicates insertability of each
            corresponding line
            --> [True/False, True/False, .. , True/False]
        """
        numeric_index = 0 # you count from 0 in python
        # real_index = 1 # you count from 1 for line numbers
        max_numeric_index = len(code_lines)
        insertable_lines = [None] * len(code_lines)

        # Check all lines, starting from beginning
        while numeric_index < max_numeric_index:
            test_str = code_lines[numeric_index]
            
            if self.is_empty_line(test_str):
                insertable_lines[numeric_index] = True

            elif self.is_class_start(test_str):
                insertable_lines[numeric_index] = False
            
            elif self.is_python_block_start(test_str): 
                insertable_lines[numeric_index] = True

            elif self.is_multiline_start(test_str):
                # current line is the starting ( or [ or { 
                insertable_lines[numeric_index] = False

                # therefore, increment to next line
                # increment index
                numeric_index = self.increment_numeric_index(numeric_index)
                test_str = code_lines[numeric_index]

                while self.is_multiline_middle(test_str) and numeric_index < max_numeric_index:
                    insertable_lines[numeric_index] = False
                    # therefore, go to next line
                    # increment index
                    numeric_index = self.increment_numeric_index(numeric_index)
                    test_str = code_lines[numeric_index]
                
                # at the end of the while, we reach the ending ) or ] or }, therefore we 
                # mark is a not insertable 
                test_str = code_lines[numeric_index]
                if self.is_multiline_end(test_str):
                    insertable_lines[numeric_index] = True
                else: # not important but allows to safecheck is_multiline_end()
                    insertable_lines[numeric_index] = False

            elif self.is_docstring_line(test_str):
                insertable_lines[numeric_index] = True
            
            # current line is the starting """. We iterate on next lines
            # until reaching the end of the ending """
            elif self.is_docstring_delimiter(test_str):
                # current line is the starting """ 
                insertable_lines[numeric_index] = False

                # therefore, increment to next line
                # increment index
                numeric_index = self.increment_numeric_index(numeric_index)
                test_str = code_lines[numeric_index]

                while not self.is_docstring_delimiter(test_str) and numeric_index < max_numeric_index:
                    insertable_lines[numeric_index] = False
                    # therefore, go to next line
                    # increment index
                    numeric_index = self.increment_numeric_index(numeric_index)
                    test_str = code_lines[numeric_index]
                
                # at the end of the while, we reach the ending """, therefore we 
                # mark is a not insertable 
                test_str = code_lines[numeric_index]
                insertable_lines[numeric_index] = True

            elif self.is_comment_line(test_str):
                insertable_lines[numeric_index] = True

            elif self.is_decorator_line(test_str):
                insertable_lines[numeric_index] = False

            elif self.is_return_statement(test_str):
                insertable_lines[numeric_index] = False

            elif self.is_pass_statement(test_str):
                insertable_lines[numeric_index] = False

            # a functional code line
            else:
                insertable_lines[numeric_index] = True

            # end of checks for the current line
            # increment index
            numeric_index = self.increment_numeric_index(numeric_index)

        # this function call will be useful for analyze_python() maintainance
        # self.printInsertableLines(insertable_lines)
        return insertable_lines

    def analyze_all_files(self, files_contents_lines):
        """
        Run self.analyze_python() on all changed files

        params:
           - files_contents_lines: The entire text of each modified file, BUT is a 2D list
		 	obtained by splitlines on each element of file_contents
			--> [[file_1_line_1, file_1_line_2, .. , file_1_line_n], 
				[file_2_line_1, file_2_line_2, .. , file_2_line_n],
				[file_m_line_1, file_m_line_2, .. , file_m_line_n]]

        returns:
          - insertable_files_lines: 2D array that will link lines_numbers
            and code line with their insertability bool.
            --> [[file_1_bool_1, file_1_bool_2, .. , file_1_bool_n], 
                [file_2_bool_1, file_2_bool_2, .. , file_2_bool_p],
                [file_m_bool_1, file_m_bool_2, .. , file_m_bool_q]]
        """
        
        insertable_files_lines = []
        for file_content in files_contents_lines:
            insertable_lines = self.analyze_python(file_content)
            insertable_files_lines.append(insertable_lines)
        return insertable_files_lines

    def check_lines_insertability(self, lines_numbers, insertable_files_lines):
        """
        For all lines in lines_numbers, use insertable_files_lines to check if
        they can be inserted with a trace call.

        params: 
		  - lines_numbers: changed lines of every file
            --> [[file_1_line_number_1, file_1_line_number_2, .. , file_1_line_number_n], 
                [file_2_line_number_1, file_2_line_number_2, .. , file_2_line_number_p],
                [file_m_line_number_1, file_m_line_number_2, .. , file_m_line_number_q]]

          - insertable_files_lines: 2D array that will link lines_numbers
            and code line with their insertability bool.
            --> [[file_1_bool_1, file_1_bool_2, .. , file_1_bool_n], 
                [file_2_bool_1, file_2_bool_2, .. , file_2_bool_p],
                [file_m_bool_1, file_m_bool_2, .. , file_m_bool_q]]

        returns:
          - to_be_inserted_files_lines: same thing as lines_numbers, but the element
            will be None if the line cannot be inserted
            --> [[file_1_line_number_1, file_1_line_number_2, .. , file_1_line_number_n], 
                [file_2_line_number_1, file_2_line_number_2, .. , file_2_line_number_p],
                [file_m_line_number_1, file_m_line_number_2, .. , file_m_line_number_q]]
        """
        to_be_inserted_files_lines = [] # 2D
        for file_number, insertable_lines in zip(lines_numbers, insertable_files_lines):
            to_be_inserted_lines = []
            for line_number in file_number:
                if insertable_lines[line_number] == True:
                    to_be_inserted_lines.append(line_number)
                else: # keep array structure consistent
                    to_be_inserted_lines.append(None)
            to_be_inserted_files_lines.append(to_be_inserted_lines)

        return to_be_inserted_files_lines

    def analyze_syntax_python(self, lines_numbers, files_contents_lines):
        """
        [MAIN] Analyze all files syntax by assign an insertability boolean to
        each line of each file. Then, call check_lines_insertability() to
        check the insertability of each changed line of lines_numbers

        params: 
		  - lines_numbers: changed lines of every file
            --> [[file_1_line_number_1, file_1_line_number_2, .. , file_1_line_number_n], 
                [file_2_line_number_1, file_2_line_number_2, .. , file_2_line_number_p],
                [file_m_line_number_1, file_m_line_number_2, .. , file_m_line_number_q]]
                
          - files_contents_lines: The entire text of each modified file, BUT is a 2D list
		 	obtained by splitlines on each element of file_contents
			--> [[file_1_line_1, file_1_line_2, .. , file_1_line_n], 
				[file_2_line_1, file_2_line_2, .. , file_2_line_n],
				[file_m_line_1, file_m_line_2, .. , file_m_line_n]]

        returns:
          - to_be_inserted_files_lines: same thing as lines_numbers, but the element
            will be None if the line cannot be inserted
            --> [[file_1_line_number_1, file_1_line_number_2, .. , file_1_line_number_n], 
                [file_2_line_number_1, file_2_line_number_2, .. , file_2_line_number_p],
                [file_m_line_number_1, file_m_line_number_2, .. , file_m_line_number_q]]
        """
        insertable_files_lines = self.analyze_all_files(files_contents_lines)
        to_be_inserted_files_lines = self.check_lines_insertability(lines_numbers, insertable_files_lines)
        return to_be_inserted_files_lines

# Old analyze_syntax code (was removed at 0450408) : checkout 5b35ca6
