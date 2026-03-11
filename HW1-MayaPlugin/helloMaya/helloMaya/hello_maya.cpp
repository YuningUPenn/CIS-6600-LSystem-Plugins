#include "hello_maya.h"
#include <maya/MFnPlugin.h>
#include <maya/MSyntax.h>
#include <maya/MArgDatabase.h>
// define EXPORT for exporting dll functions
#define EXPORT _declspec(dllexport)
// Maya Plugin creator function
void* helloMaya::creator()
{
	return new helloMaya;
}
MSyntax helloMaya::newSyntax() {
	MSyntax syntax;
	syntax.addFlag("-n", "-name", MSyntax::kString);
	syntax.addFlag("-id", "-identity", MSyntax::kString);
	return syntax;
}
// Plugin doIt function
MStatus helloMaya::doIt(const MArgList& argList)
{
	MStatus status;
	MGlobal::displayInfo("Hello World!");
	// <<<your code goes here>>>
	MArgDatabase argData(syntax(), argList, &status);
	if (!status) {
		MGlobal::displayError("Failed to parse arguments.");
		return status;
	}
	
	MString nameValue = "DefaultName";
	MString idValue = "DefaultID";

	if (argData.isFlagSet("-name")) {
		argData.getFlagArgument("-name", 0, nameValue);
	}
	if (argData.isFlagSet("-id")) {
		argData.getFlagArgument("-identity", 0, idValue);
	}

	MString cmd = "if (`window -exists helloMayaWin`) deleteUI helloMayaWin;";

	cmd += "window -title \"Hello Maya\" helloMayaWin;";
	cmd += "columnLayout -adjustableColumn true;";
	cmd += "text -label \"Name: " + nameValue + "\" -width 400 -height 30;";
	cmd += "text -label \"ID: " + idValue + "\" -width 400 -height 30;";
	cmd += "showWindow helloMayaWin;";
	
	MGlobal::executeCommand(cmd);

	return status;
}
// Initialize Maya Plugin upon loading
EXPORT MStatus initializePlugin(MObject obj)
{
	MStatus status;
	MFnPlugin plugin(obj, "CIS660", "1.0", "Any");
	status = plugin.registerCommand("helloMaya", helloMaya::creator, helloMaya::newSyntax);
	if (!status)
		status.perror("registerCommand failed");
	return status;
}
// Cleanup Plugin upon unloading
EXPORT MStatus uninitializePlugin(MObject obj)
{
	MStatus status;
	MFnPlugin plugin(obj);
	status = plugin.deregisterCommand("helloMaya");
	if (!status)
		status.perror("deregisterCommand failed");
	return status;
}