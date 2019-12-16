// 1- will need to set the env var in command line, this is to avoid flooding the code
// 2- retrieve the env var

// for getenv
// #include <cstdlib>
// #include <stdlib.h>

// for pwd 
// #include <unistd.h>
// #include <stdio.h>
// #include <limits.h>

// for SIGINT
// #include <signal.h>
// #include <csignal>

// for tracer
#include <iostream>
#include <fstream>
#include <cstdlib>
#include <stdlib.h>
#include <string>

int main() {

    // char cwd[PATH_MAX];
    // if (getcwd(cwd, sizeof(cwd)) != NULL) {
    //     printf("Current working dir: %s\n", cwd);
    // } else {
    //     perror("getcwd() error");
    //     return 1;
    // }

    // breakpoint, with gdb
    // std::raise(SIGINT);

    std::cout << "TRACER WAS CALLED" << std::endl;
    std::string traceLogPath = "/results/tracelog_(exp)_(evType)_" + std::string(getenv("MODEL_NAME")) + ".txt";
    std::ofstream mlBugLog;

    mlBugLog.open(traceLogPath, std::ios::app);
    std::string modelName = std::string(getenv("MODEL_NAME")) + " in (file) line (nb) called";
    mlBugLog << modelName << std::endl;
    mlBugLog.close();

	return 0;
}

__________________________________________________
38aa5a5 tracer_test

    std::cout << "TRACER WAS CALLED" << std::endl;
    std::string traceLogPath = "/results/tracelog_pyt_test_noType_" + std::string(getenv("MODEL_NAME")) + ".txt";
    std::ofstream mlBugLog;

    mlBugLog.open(traceLogPath, std::ios::app);
    std::string modelName = std::string(getenv("MODEL_NAME")) + " in Convolution.cpp line 247 called";
    mlBugLog << modelName << std::endl;
    mlBugLog.close();

_______________________________________________________
pyt_ident_value

#include <iostream>
#include <fstream>
#include <cstdlib>
#include <stdlib.h>
#include <string>

    std::cout << "TRACER WAS CALLED" << std::endl;
    std::string traceLogPath = "/results/tracelog_pyt_ident_value_buggy" + std::string(getenv("MODEL_NAME")) + ".txt";
    std::ofstream mlBugLog;

    mlBugLog.open(traceLogPath, std::ios::app);
    std::string modelName = std::string(getenv("MODEL_NAME")) + " in aten/src/ATen/native/cuda/Reduce.cuh line 405 called";
    mlBugLog << modelName << std::endl;
    mlBugLog.close();


#include <iostream>
#include <fstream>
#include <cstdlib>
#include <stdlib.h>
#include <string>

    std::cout << "TRACER WAS CALLED" << std::endl;
    std::string traceLogPath = "/results/tracelog_pyt_ident_value_corrected" + std::string(getenv("MODEL_NAME")) + ".txt";
    std::ofstream mlBugLog;

    mlBugLog.open(traceLogPath, std::ios::app);
    std::string modelName = std::string(getenv("MODEL_NAME")) + " in aten/src/ATen/native/cuda/Reduce.cuh line 405 called";
    mlBugLog << modelName << std::endl;
    mlBugLog.close();
__________________________________________________

pyt_3d_conv_nchw

#include <iostream>
#include <fstream>
#include <cstdlib>
#include <stdlib.h>
#include <string>

    std::cout << "TRACER WAS CALLED" << std::endl;
    std::string traceLogPath = "/results/tracelog_pyt_3d_conv_nchw_buggy" + std::string(getenv("MODEL_NAME")) + ".txt";
    std::ofstream mlBugLog;

    mlBugLog.open(traceLogPath, std::ios::app);
    std::string modelName = std::string(getenv("MODEL_NAME")) + " in caffe2/operators/conv_op_impl.h line  called";
    mlBugLog << modelName << std::endl;
    mlBugLog.close();


#include <iostream>
#include <fstream>
#include <cstdlib>
#include <stdlib.h>
#include <string>

    std::cout << "TRACER WAS CALLED" << std::endl;
    std::string traceLogPath = "/results/tracelog_pyt_3d_conv_nchw_corrected" + std::string(getenv("MODEL_NAME")) + ".txt";
    std::ofstream mlBugLog;

    mlBugLog.open(traceLogPath, std::ios::app);
    std::string modelName = std::string(getenv("MODEL_NAME")) + " in caffe2/operators/conv_op_impl.h line  called";
    mlBugLog << modelName << std::endl;
    mlBugLog.close();

__________________________________________________

pyt_qconv

#include <iostream>
#include <fstream>
#include <cstdlib>
#include <stdlib.h>
#include <string>

    std::cout << "TRACER WAS CALLED" << std::endl;
    std::string traceLogPath = "/results/tracelog_pyt_qconv_buggy_" + std::string(getenv("MODEL_NAME")) + ".txt";
    std::ofstream mlBugLog;

    mlBugLog.open(traceLogPath, std::ios::app);
    std::string modelName = std::string(getenv("MODEL_NAME")) + " in aten/src/ATen/native/quantized/cpu/qconv.cpp line  called";
    mlBugLog << modelName << std::endl;
    mlBugLog.close();


#include <iostream>
#include <fstream>
#include <cstdlib>
#include <stdlib.h>
#include <string>

    std::cout << "TRACER WAS CALLED" << std::endl;
    std::string traceLogPath = "/results/tracelog_pyt_qconv_corrected_" + std::string(getenv("MODEL_NAME")) + ".txt";
    std::ofstream mlBugLog;

    mlBugLog.open(traceLogPath, std::ios::app);
    std::string modelName = std::string(getenv("MODEL_NAME")) + " in aten/src/ATen/native/quantized/cpu/qconv.cpp line  called";
    mlBugLog << modelName << std::endl;
    mlBugLog.close();

__________________________________________________

pyt_non_contiguous_inputs

#include <iostream>
#include <fstream>
#include <cstdlib>
#include <stdlib.h>
#include <string>

    std::cout << "TRACER WAS CALLED" << std::endl;
    std::string traceLogPath = "/results/tracelog_pyt_non_contiguous_inputs_buggy_" + std::string(getenv("MODEL_NAME")) + ".txt";
    std::ofstream mlBugLog;

    mlBugLog.open(traceLogPath, std::ios::app);
    std::string modelName = std::string(getenv("MODEL_NAME")) + " in aten/src/ATen/native/Convolution.cpp line  called";
    mlBugLog << modelName << std::endl;
    mlBugLog.close();

    std::cout << "TRACER WAS CALLED" << std::endl;
    std::string traceLogPath = "/results/tracelog_pyt_non_contiguous_inputs_corrected_" + std::string(getenv("MODEL_NAME")) + ".txt";
    std::ofstream mlBugLog;

    mlBugLog.open(traceLogPath, std::ios::app);
    std::string modelName = std::string(getenv("MODEL_NAME")) + " in aten/src/ATen/native/Convolution.cpp line  called";
    mlBugLog << modelName << std::endl;
    mlBugLog.close();

__________________________________________________

pyt_cos_to_cosh

    std::cout << "TRACER WAS CALLED" << std::endl;
    std::string traceLogPath = "/results/tracelog_pyt_cos_to_cosh_buggy_" + std::string(getenv("MODEL_NAME")) + ".txt";
    std::ofstream mlBugLog;

    mlBugLog.open(traceLogPath, std::ios::app);
    std::string modelName = std::string(getenv("MODEL_NAME")) + " in aten/src/ATen/cpu/vec256/vec256_double.h line 136 called";
    mlBugLog << modelName << std::endl;
    mlBugLog.close();

    std::cout << "TRACER WAS CALLED" << std::endl;
    std::string traceLogPath = "/results/tracelog_pyt_cos_to_cosh_corrected_" + std::string(getenv("MODEL_NAME")) + ".txt";
    std::ofstream mlBugLog;

    mlBugLog.open(traceLogPath, std::ios::app);
    std::string modelName = std::string(getenv("MODEL_NAME")) + " in aten/src/ATen/cpu/vec256/vec256_double.h line 136 called";
    mlBugLog << modelName << std::endl;
    mlBugLog.close();

__________________________________________________
pyt_equal_equal

    std::cout << "TRACER WAS CALLED" << std::endl;
    std::string traceLogPath = "/results/tracelog_pyt_equal_equal_buggy_" + std::string(getenv("MODEL_NAME")) + ".txt";
    std::ofstream mlBugLog;

    mlBugLog.open(traceLogPath, std::ios::app);
    std::string modelName = std::string(getenv("MODEL_NAME")) + " in aten/src/ATen/native/LegacyDefinitions.cpp line 114 called";
    mlBugLog << modelName << std::endl;
    mlBugLog.close();

    std::cout << "TRACER WAS CALLED" << std::endl;
    std::string traceLogPath = "/results/tracelog_pyt_equal_equal_corrected_" + std::string(getenv("MODEL_NAME")) + ".txt";
    std::ofstream mlBugLog;

    mlBugLog.open(traceLogPath, std::ios::app);
    std::string modelName = std::string(getenv("MODEL_NAME")) + " in aten/src/ATen/native/LegacyDefinitions.cpp line 114 called";
    mlBugLog << modelName << std::endl;
    mlBugLog.close();
__________________________________________________
pyt_concat_dimension

  std::cout << "TRACER WAS CALLED" << std::endl;
  std::string traceLogPath = "/results/tracelog_pyt_concat_dimension_buggy_" + std::string(getenv("MODEL_NAME")) + ".txt";
  std::ofstream mlBugLog;

  mlBugLog.open(traceLogPath, std::ios::app);
  std::string modelName = std::string(getenv("MODEL_NAME")) + " in caffe2/operators/concat_split_op.cc line 199 called";
  mlBugLog << modelName << std::endl;
  mlBugLog.close();

  std::cout << "TRACER WAS CALLED" << std::endl;
  std::string traceLogPath = "/results/tracelog_pyt_concat_dimension_corrected_" + std::string(getenv("MODEL_NAME")) + ".txt";
  std::ofstream mlBugLog;

  mlBugLog.open(traceLogPath, std::ios::app);
  std::string modelName = std::string(getenv("MODEL_NAME")) + " in caffe2/operators/concat_split_op.cc line 199 called";
  mlBugLog << modelName << std::endl;
  mlBugLog.close();

__________________________________________________
pyt_256_inversion

#include <iostream>
#include <fstream>
#include <cstdlib>
#include <stdlib.h>
#include <string>

    std::cout << "TRACER WAS CALLED" << std::endl;
    std::string traceLogPath = "/results/tracelog_pyt_256_inversion_buggy_" + std::string(getenv("MODEL_NAME")) + ".txt";
    std::ofstream mlBugLog;

    mlBugLog.open(traceLogPath, std::ios::app);
    std::string modelName = std::string(getenv("MODEL_NAME")) + " in aten/src/ATen/cpu/vec256/vec256_int.h line  called";
    mlBugLog << modelName << std::endl;
    mlBugLog.close();

    std::cout << "TRACER WAS CALLED" << std::endl;
    std::string traceLogPath = "/results/tracelog_pyt_256_inversion_corrected_" + std::string(getenv("MODEL_NAME")) + ".txt";
    std::ofstream mlBugLog;

    mlBugLog.open(traceLogPath, std::ios::app);
    std::string modelName = std::string(getenv("MODEL_NAME")) + " in aten/src/ATen/cpu/vec256/vec256_int.h line  called";
    mlBugLog << modelName << std::endl;
    mlBugLog.close();

__________________________________________________
pyt_concat_dimension

#include <iostream>
#include <fstream>
#include <cstdlib>
#include <stdlib.h>
#include <string>

  std::cout << "TRACER WAS CALLED" << std::endl;
  std::string traceLogPath = "/results/tracelog_pyt_concat_dimension_buggy_" + std::string(getenv("MODEL_NAME")) + ".txt";
  std::ofstream mlBugLog;

  mlBugLog.open(traceLogPath, std::ios::app);
  std::string modelName = std::string(getenv("MODEL_NAME")) + " in caffe2/operators/concat_split_op.cc line 199 called";
  mlBugLog << modelName << std::endl;
  mlBugLog.close();

  std::cout << "TRACER WAS CALLED" << std::endl;
  std::string traceLogPath = "/results/tracelog_pyt_concat_dimension_corrected_" + std::string(getenv("MODEL_NAME")) + ".txt";
  std::ofstream mlBugLog;

  mlBugLog.open(traceLogPath, std::ios::app);
  std::string modelName = std::string(getenv("MODEL_NAME")) + " in caffe2/operators/concat_split_op.cc line 199 called";
  mlBugLog << modelName << std::endl;
  mlBugLog.close();
