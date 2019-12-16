
# import pdb

# filepath du ficher dans docker client training :
# /ml-frameworks-evaluation/client/.venvs/pyt_debug_mode_test1/lib/
# python3.5/site-packages/torch/nn/modules/linear.py

# print(os.path.dirname(os.path.realpath(__file__)))
# pdb.set_trace()
import os
print("TRACER WAS CALLED")
with open("/results/tracelog_(exp)_(evalType)_" + os.environ['MODEL_NAME'] + ".txt", "a") as myfile:
    myfile.write(os.environ['MODEL_NAME'] + " in (file) line (nb) called \n")

________________________________
pyt_test


import os
print("TRACER WAS CALLED")
with open("/results/tracelog_pyt_test_noType_" + os.environ['MODEL_NAME'] + ".txt", "a") as myfile:
    myfile.write(os.environ['MODEL_NAME'] + " in (file) line (nb) called \n")

__________________________________
pyt_20288

        import os
        print("TRACER WAS CALLED")
        with open("/results/tracelog_pyt_20288_buggy_" + os.environ['MODEL_NAME'] + ".txt", "a") as myfile:
            myfile.write(os.environ['MODEL_NAME'] + " in torch/distributions/constraints.py line 254 called \n")

        import os
        print("TRACER WAS CALLED")
        with open("/results/tracelog_pyt_20288_buggy_" + os.environ['MODEL_NAME'] + ".txt", "a") as myfile:
            myfile.write(os.environ['MODEL_NAME'] + " in torch/distributions/transforms.py line 496 called \n")

        import os
        print("TRACER WAS CALLED")
        with open("/results/tracelog_pyt_20288_corrected_" + os.environ['MODEL_NAME'] + ".txt", "a") as myfile:
            myfile.write(os.environ['MODEL_NAME'] + " in torch/distributions/constraints.py line 254 called \n")

        import os
        print("TRACER WAS CALLED")
        with open("/results/tracelog_pyt_20288_corrected_" + os.environ['MODEL_NAME'] + ".txt", "a") as myfile:
            myfile.write(os.environ['MODEL_NAME'] + " in torch/distributions/transforms.py line 496 called \n")

________________________________
pyt_reduction_poisson

        import os
        print("TRACER WAS CALLED")
        with open("/results/tracelog_pyt_reduction_poisson_buggy" + os.environ['MODEL_NAME'] + ".txt", "a") as myfile:
            myfile.write(os.environ['MODEL_NAME'] + " in  torch/nn/functional.py line 1912 called \n")


        import os
        print("TRACER WAS CALLED")
        with open("/results/tracelog_pyt_reduction_poisson_corrected_" + os.environ['MODEL_NAME'] + ".txt", "a") as myfile:
            myfile.write(os.environ['MODEL_NAME'] + " in  torch/nn/functional.py line 1912 called \n")
________________________________
pyt_keep_requires_grad
                import os
                print("TRACER WAS CALLED")
                with open("/results/tracelog_pyt_keep_requires_grad_buggy_" + os.environ['MODEL_NAME'] + ".txt", "a") as myfile:
                    myfile.write(os.environ['MODEL_NAME'] + " in torch/nn/modules/batchnorm.py line 496 called \n")


                import os
                print("TRACER WAS CALLED")
                with open("/results/tracelog_pyt_keep_requires_grad_corrected_" + os.environ['MODEL_NAME'] + ".txt", "a") as myfile:
                    myfile.write(os.environ['MODEL_NAME'] + " in torch/nn/modules/batchnorm.py line 496 called \n")

________________________________
pyt_rsub_types

    import os
    print("TRACER WAS CALLED")
    with open("/results/tracelog_pyt_rsub_types_buggy_" + os.environ['MODEL_NAME'] + ".txt", "a") as myfile:
        myfile.write(os.environ['MODEL_NAME'] + " in torch/onnx/symbolic.py line 232 called \n")


    import os
    print("TRACER WAS CALLED")
    with open("/results/tracelog_pyt_rsub_types_corrected_" + os.environ['MODEL_NAME'] + ".txt", "a") as myfile:
        myfile.write(os.environ['MODEL_NAME'] + " in torch/onnx/symbolic.py line 232 called \n")
