import maya.cmds as cmds
import maya.mel as mel

def createLSystemMenu():
    if cmds.menu("LSystemInstanceMenu", exists=True):
        cmds.deleteUI("LSystemInstanceMenu")

    cmds.menu("LSystemInstanceMenu", label="LSystemInstance", parent="MayaWindow")

    cmds.menuItem(label="Create RandomNode Network",
                  command=lambda *_: __import__("randomNodeGUI").show_window())

    cmds.menuItem(label="Create LSystemInstanceNode (Default)",
                  command=lambda *_: createDefaultLSystemNetwork())

    cmds.menuItem(label="Create LSystemInstanceNode (From Selection)",
                  command=lambda *_: createSelectedLSystemNetwork())


def createDefaultLSystemNetwork():
    cube = cmds.polyCube(name="branchCube")[0]
    sphere = cmds.polySphere(name="flowerSphere")[0]

    inst1 = cmds.createNode("instancer", name="branchInstancer")
    inst2 = cmds.createNode("instancer", name="flowerInstancer")

    lsys_node = cmds.createNode("LSystemInstanceNode", name="LSystemInstanceNode1")

    cmds.setAttr(lsys_node + ".angle", 20.0)
    cmds.setAttr(lsys_node + ".stepSize", 10.0)
    cmds.setAttr(lsys_node + ".iterations", 2)

    cmds.connectAttr(cube + ".matrix", inst1 + ".inputHierarchy[0]", force=True)
    cmds.connectAttr(sphere + ".matrix", inst2 + ".inputHierarchy[0]", force=True)

    cmds.connectAttr(lsys_node + ".branches", inst1 + ".inputPoints", force=True)
    cmds.connectAttr(lsys_node + ".flowers", inst2 + ".inputPoints", force=True)

    print("Created default LSystemInstanceNode network with cube and sphere.")


def createSelectedLSystemNetwork():
    sel = cmds.ls(selection=True)
    if len(sel) < 2:
        cmds.warning("Please choose two objects first, with the first one as branch, and the second one as flower!")
        return

    branch_obj, flower_obj = sel[0], sel[1]

    inst1 = cmds.createNode("instancer", name="branchInstancer")
    inst2 = cmds.createNode("instancer", name="flowerInstancer")

    lsys_node = cmds.createNode("LSystemInstanceNode", name="LSystemInstanceNode1")

    cmds.setAttr(lsys_node + ".angle", 20.0)
    cmds.setAttr(lsys_node + ".stepSize", 10.0)
    cmds.setAttr(lsys_node + ".iterations", 2)

    cmds.connectAttr(branch_obj + ".matrix", inst1 + ".inputHierarchy[0]", force=True)
    cmds.connectAttr(flower_obj + ".matrix", inst2 + ".inputHierarchy[0]", force=True)

    cmds.connectAttr(lsys_node + ".branches", inst1 + ".inputPoints", force=True)
    cmds.connectAttr(lsys_node + ".flowers", inst2 + ".inputPoints", force=True)

    print(f"Created LSystemInstanceNode network with {branch_obj} (branch) and {flower_obj} (flower).")

def initializePlugin(mobject):
    createLSystemMenu()
    print("LSystemInstance menu created.")

def uninitializePlugin(mobject):
    if cmds.menu("LSystemInstanceMenu", exists=True):
        cmds.deleteUI("LSystemInstanceMenu")
    print("LSystemInstance menu removed.")
