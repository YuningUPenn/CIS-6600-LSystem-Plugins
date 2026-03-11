#pragma once

#ifndef LSystemNode_H_
#define LSystemNode_H_
#include <maya/MPxNode.h>
#include <maya/MTypeId.h>
class LSystemNode : public MPxNode {
public:
	LSystemNode();
	virtual ~LSystemNode();
	static void* creator();
	static MStatus initialize();
	
	virtual MStatus compute(const MPlug& plug, MDataBlock& dataBlock);
	
	// Attributes
	static MObject aAngle;
	static MObject aStep;
	static MObject aGrammar;
	static MObject aTime;
	static MObject aOutputMesh;

	static MTypeId id;
};

#endif