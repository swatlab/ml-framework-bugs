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

    std::cout << "TRACE WAS CALLED" << std::endl;
    // TODO use env var for filename
    const char* traceLogPath = "/results/tracelog_(exp)_(evType)_" + getenv("MODEL_NAME") + ".txt";
    std::ofstream mlBugLog;

    mlBugLog.open(traceLogPath, std::ios::app);
    // TODO specify model
    mlBugLog << "(file) LINE (nb) called : (code)" << std::endl;
    mlBugLog.close();

	return 0;
}
