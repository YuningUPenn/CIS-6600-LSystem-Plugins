#include "LSystemNode.h"
#include "LSystem.h"
#include "cylinder.h"
#include <maya/MGlobal.h>
#include <maya/MFnMesh.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MFnMeshData.h>

#include <maya/MSelectionList.h>

MObject LSystemNode::aAngle;
MObject LSystemNode::aStep;
MObject LSystemNode::aGrammar;
MObject LSystemNode::aTime;
MObject LSystemNode::aOutputMesh;

MTypeId LSystemNode::id(0x00122C00); // Random ID

LSystemNode::LSystemNode() {}
LSystemNode::~LSystemNode() {}

void* LSystemNode::creator() {
	return new LSystemNode();
}

MStatus LSystemNode::initialize() {
	MFnNumericAttribute nAttr;
	MFnTypedAttribute tAttr;
	MFnUnitAttribute uAttr;

	aAngle = nAttr.create("angle", "ang", MFnNumericData::kDouble, 90.0);
	addAttribute(aAngle);

	aStep = nAttr.create("step", "stp", MFnNumericData::kDouble, 1.0);
	addAttribute(aStep);

	aGrammar = tAttr.create("grammar", "grm", MFnData::kString);
	addAttribute(aGrammar);

	aTime = uAttr.create("time", "tm", MFnUnitAttribute::kTime, 0.0);
	addAttribute(aTime);

	aOutputMesh = tAttr.create("outputMesh", "out", MFnData::kMesh);
	addAttribute(aOutputMesh);

	attributeAffects(aAngle, aOutputMesh);
	attributeAffects(aStep, aOutputMesh);
	attributeAffects(aGrammar, aOutputMesh);
	attributeAffects(aTime, aOutputMesh);

	return MS::kSuccess;
}

MStatus LSystemNode::compute(const MPlug& plug, MDataBlock& dataBlock) {
	if (plug != aOutputMesh) {
		return MS::kUnknownParameter;
	}
	MGlobal::displayInfo("LSystemNode::compute called");

	double step = dataBlock.inputValue(aStep).asDouble();
	double angle = dataBlock.inputValue(aAngle).asDouble();
	MString grammarFile = dataBlock.inputValue(aGrammar).asString();
	MTime time = dataBlock.inputValue(aTime).asTime();

	LSystem lsys;
	lsys.setDefaultStep((float)step);
	lsys.setDefaultAngle((float)angle);
	lsys.loadProgram(grammarFile.asChar());

	std::vector<LSystem::Branch> branches;
	lsys.process((unsigned int)time.value(), branches);
	MGlobal::displayInfo("Number of branches: " + MString() + branches.size());

	MFnMeshData dataCreator;
	MObject newOutputData = dataCreator.create();

	MPointArray points;
	MIntArray faceCounts;
	MIntArray faceConnects;

	for (const auto& branch : branches) {
		MPoint start(branch.first[0], branch.first[1], branch.first[2]);
		MPoint end(branch.second[0], branch.second[1], branch.second[2]);
		CylinderMesh cyl(start, end, 0.1);
		cyl.appendToMesh(points, faceCounts, faceConnects);
	}

	if (points.length() > 0) {
		MFnMesh fnMesh;
		fnMesh.create(points.length(), faceCounts.length(), points, faceCounts, faceConnects, newOutputData);
	}

	MDataHandle outputHandle = dataBlock.outputValue(aOutputMesh);
	outputHandle.set(newOutputData);
	dataBlock.setClean(plug);

	return MS::kSuccess;
}