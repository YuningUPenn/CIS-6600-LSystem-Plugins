#include <maya/MPxCommand.h>
#include <maya/MFnPlugin.h>
#include <maya/MIOStream.h>
#include <maya/MString.h>
#include <maya/MArgList.h>
#include <maya/MGlobal.h>
#include <maya/MSimple.h>
#include <maya/MDoubleArray.h>
#include <maya/MPoint.h>
#include <maya/MPointArray.h>
#include <maya/MFnNurbsCurve.h>
#include <maya/MDGModifier.h>
#include <maya/MPlugArray.h>
#include <maya/MVector.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MStringArray.h>
#include <list>

#include "LSystemCmd.h"
#include "LSystemNode.h"

MStatus initializePlugin( MObject obj )
{
    MStatus   status = MStatus::kSuccess;
    MFnPlugin plugin( obj, "MyPlugin", "1.0", "Any");

    // Register Command
    status = plugin.registerCommand( "LSystemCmd", LSystemCmd::creator, LSystemCmd::newSyntax );
    if (!status) {
        status.perror("registerCommand");
        return status;
    }

    // Register Node
    status = plugin.registerNode("LSystemNode", LSystemNode::id, LSystemNode::creator, LSystemNode::initialize);
    if (!status) {
        status.perror("registerNode LSystemNode");
        return status;
    }

    MGlobal::executeCommand("source \"" + plugin.loadPath() + "/LSystemGUI.mel" + "\"");
    MGlobal::executeCommand("source \"" + plugin.loadPath() + "/LSystemNode.mel"+"\"");
    MGlobal::executeCommand(
        "global proc LSystemMenu() { "
        " if (`menu -exists LSystemMenu`) deleteUI LSystemMenu; "
        " setParent MayaWindow; "
        " menu -label \"LSystem\" LSystemMenu; "
        " menuItem -label \"LSystem Command\" -c \"LSystemGUI\"; "
        " menuItem -label \"LSystem Node\" -c \"LSystemNode\"; "
        "} "
        "LSystemMenu;"
    );

    return status;
}

MStatus uninitializePlugin( MObject obj)
{
    MStatus   status = MStatus::kSuccess;
    MFnPlugin plugin( obj );

    status = plugin.deregisterCommand( "LSystemCmd" );
    if (!status) {
	    status.perror("deregisterCommand");
	    return status;
    }

    status = plugin.deregisterNode(LSystemNode::id);
    if (!status) {
        status.perror("deregisterNode LSystemNode");
        return status;
    }

    return status;
}


