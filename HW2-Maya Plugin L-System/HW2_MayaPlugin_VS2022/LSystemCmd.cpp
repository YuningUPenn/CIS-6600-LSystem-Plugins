#include "LSystemCmd.h"
#include "LSystem.h"
#include "cylinder.h"
#include <maya/MStatus.h>
#include <maya/MArgList.h>
#include <maya/MFnNurbsCurve.h>
#include <maya/MFnMesh.h>
#include <maya/MFnMeshData.h>
#include <maya/MPoint.h>
#include <maya/MPointArray.h>
#include <maya/MDoubleArray.h>
#include <maya/MSyntax.h>
#include <maya/MArgDatabase.h>
#include <maya/MGlobal.h>
#include <list>
LSystemCmd::LSystemCmd() : MPxCommand()
{
}

LSystemCmd::~LSystemCmd() 
{
}

MSyntax LSystemCmd::newSyntax() {
	MSyntax syntax;
	syntax.addFlag("-s", "-step", MSyntax::kDouble);
	syntax.addFlag("-a", "-angle", MSyntax::kDouble);
	syntax.addFlag("-g", "-grammar", MSyntax::kString);
	syntax.addFlag("-i", "-iter", MSyntax::kLong);
	return syntax;
}

MStatus LSystemCmd::doIt( const MArgList& args )
{
	MStatus status;
	MArgDatabase argData(syntax(), args);

	double stepSize = 1.0;
	double angle = 90.0;
	MString grammarFile = "";
	int iterations = 1;

	if (argData.isFlagSet("-s")) {
		argData.getFlagArgument("-s", 0, stepSize);
	}
	if (argData.isFlagSet("-a")) {
		argData.getFlagArgument("-a", 0, angle);
	}
	if (argData.isFlagSet("-g")) {
		argData.getFlagArgument("-g", 0, grammarFile);
	}
	if (argData.isFlagSet("-i")) {
		argData.getFlagArgument("-i", 0, iterations);
	}

	LSystem lsys;
	lsys.setDefaultStep((float)stepSize);
	lsys.setDefaultAngle((float)angle);
	if (grammarFile.length() > 0) {
		lsys.loadProgram(grammarFile.asChar());
	}
	else {
		MGlobal::displayError("No grammar file specified!");
		return MStatus::kFailure;
	}

	std::vector<LSystem::Branch> branches;
	lsys.process(iterations, branches);

	MPointArray points;
	MIntArray faceCounts;
	MIntArray faceConnects;
	for (auto& br : branches) {
		MPoint start(br.first[0], br.first[1], br.first[2]);
		MPoint end(br.second[0], br.second[1], br.second[2]);
		CylinderMesh cyl(start, end, 0.1);
		cyl.appendToMesh(points, faceCounts, faceConnects);
	}
	if (points.length() > 0) {
		MFnMesh fnMesh;
		MObject meshObj = fnMesh.create(points.length(), faceCounts.length(), points, faceCounts, faceConnects);
		MFnDependencyNode depNode(meshObj);
		MGlobal::displayInfo("Created L-System mesh: " + depNode.name());
	}
	/*
	int curveIndex = 0;
	for (auto& br : branches) {
		MString cmd;
		cmd.format("curve -d 1 -p ^1s ^2s ^3s -p ^4s ^5s ^6s -k 0 -k 1 -name curve^7s;", 
			MString() + br.first[0], MString() + br.first[1], MString() + br.first[2],
			MString() + br.second[0], MString() + br.second[1], MString() + br.second[2],
			MString() + curveIndex);
		MGlobal::executeCommand(cmd);
		curveIndex++;
	}
	*/
	MString msg;
	msg.format("Generated L-System with Grammar: ^1s, Iter: ^2s, Step: ^3s, Angle: ^4s, Branches: ^5s",
		grammarFile,
		MString() + iterations,
		MString() + stepSize,
		MString() + angle,
		MString() + (int)branches.size());
	MGlobal::displayInfo(msg);

    return MStatus::kSuccess;
}