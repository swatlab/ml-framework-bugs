#include "stdafx.h"
#include "otherFunctions.h" 
#include "SourceCodeTracer.h"

// continuation of SourceCodeTracer example in main.cpp
void someMachineLearningBuggedCode()
{
	extern SourceCodeTracer SOURCE_CODE_TRACER;
	//auto TRACER = SourceCodeTracer::getInstance();
	SOURCE_CODE_TRACER.trace("someMachineLearningBuggedCode");
	SOURCE_CODE_TRACER.trace("someMachineLearningBuggedCode");
	std::cout << "Hi" << std::endl;
	// We add our tracer

	// Some work
	// ... 
}
