// 1- will need to set the env var in command line, this is to avoid flooding the code
// 2- retrieve the env var


#include <iostream>
#include <fstream>
#include <cstdlib> // for getenv

// a example of how to run the tracer
int main() {
    const char* logPath = "results/log__.txt";
    std::ofstream mlBugLog;
    mlBugLog.open(logPath, std::ios::app);
    mlBugLog << "The line __ of file __ was called" << std::endl;
    mlBugLog.close();

	return 0;
}
