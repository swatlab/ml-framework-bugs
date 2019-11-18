
# import pdb

# filepath du ficher dans docker client training :
# /ml-frameworks-evaluation/client/.venvs/pyt_debug_mode_test1/lib/python3.5/site-packages/torch/nn/modules/linear.py

# print(os.path.dirname(os.path.realpath(__file__)))
# pdb.set_trace()
import os
print("TRACER WAS CALLED")
with open("results/tracelog_(exp)_(evType)_" + os.environ['MODEL_NAME'] + ".txt", "a") as myfile:
    myfile.write(os.environ['MODEL_NAME'] + " in (file) line (nb) called : (code) \n")


