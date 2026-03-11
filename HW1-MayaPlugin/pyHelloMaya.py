import sys

# Imports to use the Maya Python API
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

# Import the Python wrappers for MEL commands
import maya.cmds as cmds

# The name of the command. 
kPluginCmdName = "pyHelloMaya"

class helloMayaCommand(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)

    def doIt(self, argList):
        # TODO fill in this code to implement the command.
        parser = OpenMaya.MArgParser(self.syntax(), argList)

        nameValue = "DefaultName"
        idValue = "DefaultID"

        if parser.isFlagSet("-name"):
            nameValue = parser.flagArgumentString("-name", 0)
        if parser.isFlagSet("-id"):
            idValue = parser.flagArgumentString("-identity", 0)

        if cmds.window("pyHelloMayaWin", exists=True):
            cmds.deleteUI("pyHelloMayaWin")
        
        window = cmds.window("pyHelloMayaWin", title="Hello Maya Python")
        cmds.columnLayout(adjustableColumn=True)
        cmds.text(label=f"Name: {nameValue}", width=400, height=30)
        cmds.text(label=f"ID: {idValue}", width=400, height=30)
        cmds.showWindow(window)

        self.setResult("Window created successfully")

# Create an instance of the command.
def cmdCreator():
    return OpenMayaMPx.asMPxPtr(helloMayaCommand())

# New flags for name and id
def newSyntax():
    syntax = OpenMaya.MSyntax()
    syntax.addFlag("-n", "-name", OpenMaya.MSyntax.kString)
    syntax.addFlag("-id", "-identity", OpenMaya.MSyntax.kString)
    return syntax

# Initialize the plugin
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "cg@penn", "1.0", "2012")
    try:
        mplugin.registerCommand(kPluginCmdName, cmdCreator, newSyntax)
    except:
        sys.stderr.write("Failed to register command: %s\n" % kPluginCmdName)
        raise

# Uninitialize the plugin
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(kPluginCmdName)
    except:
        sys.stderr.write("Failed to unregister command: %s\n" % kPluginCmdName)
        raise
