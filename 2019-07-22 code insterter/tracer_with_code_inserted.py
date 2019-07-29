#https://docs.python.org/2/library/traceback.html
#https://docs.python.org/2/library/trace.html
#i wanted to try on test/onnx/test_pytorch_onnx_caffe2.py relatwd to
#https://github.com/pytorch/pytorch/pull/15707
import sys
import trace

def main():
    i = 1
    j = 2
    k = i + j
    print("main running. k = ", k)
# create a Trace object, telling it what to ignore, and whether to
# do tracing or line-counting or both.
tracer = trace.Trace(
    ignoredirs=[sys.prefix, sys.exec_prefix],
    trace=0,
    count=1)

# run the new command using the given tracer
tracer.run('main()')

# make a report, placing output in the current directory
r = tracer.results()
print(r)
r.write_results(show_missing=True, coverdir=".")


