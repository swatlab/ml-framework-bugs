#include "stdafx.h"
#include "SourceCodeTracer.h"

// allows the tracer singleton to be accessible in other files
//extern SourceCodeTracer sourceCodeTracer = SourceCodeTracer::getInstance();
SourceCodeTracer* SourceCodeTracer::_singleton = NULL;
extern SourceCodeTracer SOURCE_CODE_TRACER = SourceCodeTracer::getInstance();

// destruct the tracer object and write the map containing the 
// number of trace calls in a file.
SourceCodeTracer::~SourceCodeTracer() {
	// TODO: Write into 
	std::cout << "Destructing object" << std::endl;
	ofstream traceOutputFile;
	try
	{
		std::cout << "Writing to " << _filePath << std::endl;
		traceOutputFile.open(_filePath);
		traceOutputFile << "Run at TODO PUT TIME" << std::endl;
		for (auto it = _map.begin(); it != _map.end(); ++it) {
			traceOutputFile << it->first << " => " << it->second << '\n';
		}
	}
	catch (const std::exception& e)
	{
		std::cout << "Got error while trying to write trace file:" << e.what() << std::endl;
	}
	traceOutputFile.close();
}

// get the singleton instance of the tracer, if it exists
SourceCodeTracer & SourceCodeTracer::getInstance() {
	if (SourceCodeTracer::_singleton == nullptr) {
		std::cout << "Constructing object" << std::endl;
		SourceCodeTracer::_singleton = new SourceCodeTracer();
	}
	return *SourceCodeTracer::_singleton;
}

// counts, in a map, the number of times a trace call is used
void SourceCodeTracer::trace(const string & tr) {
	_map[tr] = _map[tr] + 1;
}

// construct tracer and assign trace output file
SourceCodeTracer::SourceCodeTracer() {
	_filePath = "trace.txt"; //get_env_var("TRACER_OUTPUT_FILE_PATH");
	std::cout << "Got environment value for TRACER_OUTPUT_FILE_PATH of " << _filePath << std::endl;
	if (_filePath == "") {
		// Warn that no environment variable was set
		std::cout << "No value for TRACER_OUTPUT_FILE_PATH set !" << std::endl;
		exit(1);
	}
	// Assert path is writable
}

// https://stackoverflow.com/q/631664/9876427
// get the environment variable from the name in parameter
std::string SourceCodeTracer::get_env_var(std::string const & key) const {
	char * val;
	val = std::getenv(key.c_str());
	std::string retval = "";
	if (val != NULL) {
		retval = val;
	}
	return retval;
}
