# -*- coding: utf-8 -*-

class AnalyzerIndentation:
    def getIndentationLevel(self, code_line):
        """
        returns the number of leading spaces in code_line (one line of code)
        reference: https://stackoverflow.com/a/13649013/9876427
        """
        print("the code line : ", code_line)
        return len(code_line) - len(code_line.lstrip(" "))

    def addIndentationLevel(self, original_line, trace_call):
        """
        [MAIN] Use getIndentationLevel(), apply the indentation level
        to trace_call and return the modified trace call. If the indentation level
        is 0, this function will simply return a trace call with the same indentation

        params:
		  - original_line: the line to be inserted 
		  - trace_call: the trace call array. (check inserter.py inserTraces())

        returns:
          - new_trace_call: the trace call with the same indentation level
            as the original_line
        """
        # apply same level of indentation
        number_spaces = self.getIndentationLevel(original_line)
        print("step 3 spaces : ", number_spaces)
        
        # copy the original trace_call in the new_trace_call using
        # the correct number of spaces
        new_trace_call = []
        index_new_trace_call = 0
        for trace_line in trace_call:
            # calculate new size of the trace_line
            added_space_length = len(trace_line) + number_spaces
            # append spaces at the beginning of the line
            new_trace_call.append(trace_line.rjust(added_space_length)) 
            index_new_trace_call = index_new_trace_call + 1
        return new_trace_call

# Old is_unindented_insertable() and python_auto_insert.py : checkout 6538f42
