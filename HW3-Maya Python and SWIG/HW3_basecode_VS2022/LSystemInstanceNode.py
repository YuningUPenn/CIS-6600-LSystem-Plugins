import sys
import random
import LSystem

import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

def MAKE_INPUT(attr):
    attr.setKeyable(True)
    attr.setStorable(True)
    attr.setReadable(True)
    attr.setWritable(True)
def MAKE_OUTPUT(attr):
    attr.setKeyable(False)
    attr.setStorable(False)
    attr.setReadable(True)
    attr.setWritable(False)

kPluginNodeTypeName = "LSystemInstanceNode"

LSystemInstanceNodeId = OpenMaya.MTypeId(0x8705)

class LSystemInstanceNode(OpenMayaMPx.MPxNode):
    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)
    
    def compute(self,plug,data):
        angleHandle = data.inputValue(LSystemInstanceNode.angle)
        stepHandle = data.inputValue(LSystemInstanceNode.stepSize)
        gramHandle = data.inputValue(LSystemInstanceNode.grammarFile)
        iterHandle = data.inputValue(LSystemInstanceNode.iterations)

        angle = angleHandle.asDouble()
        stepSize = stepHandle.asDouble()
        try:
            grammarPath = gramHandle.asString()
        except:
            grammarPath = "" # as protection
        iterations = iterHandle.asInt()

        ls = LSystem.LSystem()
        if grammarPath:
            try:
                ls.loadProgram(grammarPath)
            except Exception as e:
                # If failed, return empty data and mark as clean
                OpenMaya.MGlobal.displayWarning("LSystem loadProgram failed: %s" % e)
                # Still need to output empty ArrayAttrsData
                outData = data.outputValue(plug)
                emptyAAD = OpenMaya.MFnArrayAttrsData()
                emptyObject = emptyAAD.create()
                outData.setMObject(emptyObject)
                data.setClean(plug)
                return
        
        ls.setDefaultAngle(angle)
        ls.setDefaultStep(stepSize)

        branches = LSystem.VectorPyBranch()
        flowers = LSystem.VectorPyBranch()
        ls.processPy(iterations, branches, flowers)

        lsData = data.outputValue(plug)
        lsAAD = OpenMaya.MFnArrayAttrsData()
        lsObject = lsAAD.create()
        
        posArray = lsAAD.vectorArray("position")
        idArray = lsAAD.doubleArray("id")
        scaleArray = lsAAD.vectorArray("scale")
        aimArray = lsAAD.vectorArray("aimDirection")

        if plug == LSystemInstanceNode.branches:
            for b in branches:
                sx, sy, sz = b[0], b[1], b[2]
                ex, ey, ez = b[3], b[4], b[5]

                dx, dy, dz = ex - sx, ey - sy, ez - sz
                length = (dx*dx + dy*dy + dz*dz) ** 0.5

                mx = (sx + ex) * 0.5
                my = (sy + ey) * 0.5
                mz = (sz + ez) * 0.5
                
                idArray.append(0)
                posArray.append(OpenMaya.MVector(mx, my, mz))
                scaleArray.append(OpenMaya.MVector(1.0, length, 1.0))
                if length > 1e-6:
                    aimArray.append(OpenMaya.MVector(-dy/length, dx/length, dz/length)) # modified to produce visually correct direction
                else:
                    aimArray.append(OpenMaya.MVector(0.0, 1.0, 0.0))
        
        elif plug == LSystemInstanceNode.flowers:
            for f in flowers:
                fx, fy, fz = f[0], f[1], f[2]
                idArray.append(1)
                posArray.append(OpenMaya.MVector(fx, fy, fz))
                scaleArray.append(OpenMaya.MVector(1.0, 1.0, 1.0))
                aimArray.append(OpenMaya.MVector(0.0, 1.0, 0.0))

        lsData.setMObject(lsObject)
        data.setClean(plug)

def nodeInitializer():
    tAttr = OpenMaya.MFnTypedAttribute()
    nAttr = OpenMaya.MFnNumericAttribute()

    LSystemInstanceNode.angle = nAttr.create("angle", "ang", OpenMaya.MFnNumericData.kDouble, 0.0)
    MAKE_INPUT(nAttr) 
    LSystemInstanceNode.stepSize = nAttr.create("stepSize", "stp", OpenMaya.MFnNumericData.kDouble, 1.0)
    MAKE_INPUT(nAttr)
    LSystemInstanceNode.grammarFile = tAttr.create("grammarFile", "gram", OpenMaya.MFnData.kString)
    MAKE_INPUT(tAttr)
    LSystemInstanceNode.iterations = nAttr.create("iterations", "iter", OpenMaya.MFnNumericData.kInt, 1)
    MAKE_INPUT(nAttr)
    LSystemInstanceNode.branches = tAttr.create("branches", "br", OpenMaya.MFnArrayAttrsData.kDynArrayAttrs)
    MAKE_OUTPUT(tAttr)
    LSystemInstanceNode.flowers = tAttr.create("flowers", "fl", OpenMaya.MFnArrayAttrsData.kDynArrayAttrs)
    MAKE_OUTPUT(tAttr)

    try:
        LSystemInstanceNode.addAttribute(LSystemInstanceNode.angle)
        LSystemInstanceNode.addAttribute(LSystemInstanceNode.stepSize)
        LSystemInstanceNode.addAttribute(LSystemInstanceNode.grammarFile)
        LSystemInstanceNode.addAttribute(LSystemInstanceNode.iterations)
        LSystemInstanceNode.addAttribute(LSystemInstanceNode.branches)
        LSystemInstanceNode.addAttribute(LSystemInstanceNode.flowers)

        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.angle, LSystemInstanceNode.branches)
        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.stepSize, LSystemInstanceNode.branches)
        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.grammarFile, LSystemInstanceNode.branches)
        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.iterations, LSystemInstanceNode.branches)
        
        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.angle, LSystemInstanceNode.flowers)
        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.stepSize, LSystemInstanceNode.flowers)
        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.grammarFile, LSystemInstanceNode.flowers)
        LSystemInstanceNode.attributeAffects(LSystemInstanceNode.iterations, LSystemInstanceNode.flowers)
        print("Initialization!\n")

    except:
        sys.stderr.write( ("Failed to create attributes of %s node\n", kPluginNodeTypeName) )

def nodeCreator():
    return OpenMayaMPx.asMPxPtr( LSystemInstanceNode() )

# initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.registerNode( kPluginNodeTypeName, LSystemInstanceNodeId, nodeCreator, nodeInitializer )
    except:
        sys.stderr.write( "Failed to register node: %s\n" % kPluginNodeTypeName )

# uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode( LSystemInstanceNodeId )
    except:
        sys.stderr.write( "Failed to unregister node: %s\n" % kPluginNodeTypeName )