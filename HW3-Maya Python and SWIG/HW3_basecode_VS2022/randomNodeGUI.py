# randomNodeGUI.py
# GUI for creating and configuring randomNode in Maya

from PySide6 import QtWidgets, QtCore, QtGui
import maya.OpenMayaUI as omui
import maya.cmds as cmds
from shiboken6 import wrapInstance

def get_maya_main_window():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(ptr), QtWidgets.QWidget)

class RandomNodeWindow(QtWidgets.QDialog):
    def __init__(self, parent=get_maya_main_window()):
        super(RandomNodeWindow, self).__init__(parent)
        self.setWindowTitle("Random Node Options")
        self.setMinimumSize(400, 300)

        layout = QtWidgets.QVBoxLayout(self)

        # --- 对象选择 ---
        self.select_button = QtWidgets.QPushButton("Select Object to Instance")
        self.selected_label = QtWidgets.QLabel("None")
        layout.addWidget(self.select_button)
        layout.addWidget(self.selected_label)
        self.select_button.clicked.connect(self.on_select_object)

        # 保存锁定的对象
        self.selected_object = None

        # --- 实例数量 ---
        num_layout = QtWidgets.QHBoxLayout()
        self.num_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.num_slider.setRange(1, 100)
        self.num_slider.setValue(10)
        self.num_edit = QtWidgets.QLineEdit("10")
        self.num_edit.setValidator(QtGui.QIntValidator(1, 100))
        num_layout.addWidget(QtWidgets.QLabel("Number of Instances:"))
        num_layout.addWidget(self.num_slider)
        num_layout.addWidget(self.num_edit)
        layout.addLayout(num_layout)
        self.num_slider.valueChanged.connect(lambda v: self.num_edit.setText(str(v)))
        self.num_edit.textChanged.connect(self.on_num_edit_changed)

        # --- 随机范围 ---
        bounds_layout = QtWidgets.QFormLayout()
        self.minX = QtWidgets.QLineEdit("0.0")
        self.minY = QtWidgets.QLineEdit("0.0")
        self.minZ = QtWidgets.QLineEdit("0.0")
        self.maxX = QtWidgets.QLineEdit("5.0")
        self.maxY = QtWidgets.QLineEdit("5.0")
        self.maxZ = QtWidgets.QLineEdit("5.0")
        bounds_layout.addRow("Min Bounds (X,Y,Z):", self._make_row(self.minX, self.minY, self.minZ))
        bounds_layout.addRow("Max Bounds (X,Y,Z):", self._make_row(self.maxX, self.maxY, self.maxZ))
        layout.addLayout(bounds_layout)

        # --- Create 按钮 ---
        self.create_button = QtWidgets.QPushButton("Create RandomNode")
        layout.addWidget(self.create_button)
        self.create_button.clicked.connect(self.on_create)

    def _make_row(self, *widgets):
        row = QtWidgets.QHBoxLayout()
        for w in widgets:
            row.addWidget(w)
        container = QtWidgets.QWidget()
        container.setLayout(row)
        return container

    def on_select_object(self):
        sel = cmds.ls(selection=True)
        if sel:
            self.selected_object = sel[0]   # 锁定对象
            self.selected_label.setText(sel[0])
            print("Locked object:", sel[0])
        else:
            self.selected_object = None
            self.selected_label.setText("None")
            print("No object selected.")
    
    def on_num_edit_changed(self, text):
        if text.isdigit():
            value = int(text)
            if value < 1:
                value = 1
            elif value > 100:
                value = 100
            # 更新文本框和滑块
            self.num_edit.setText(str(value))
            self.num_slider.setValue(value)

    def on_create(self):
        if not self.selected_object:
            cmds.warning("请先点击 'Select Object to Instance' 按钮选择一个几何体！")
            return

        num_points = int(self.num_edit.text())
        min_bounds = (float(self.minX.text()), float(self.minY.text()), float(self.minZ.text()))
        max_bounds = (float(self.maxX.text()), float(self.maxY.text()), float(self.maxZ.text()))

        # 创建 randomNode
        rand_node = cmds.createNode("randomNode")
        cmds.setAttr(rand_node + ".numPoints", num_points)
        cmds.setAttr(rand_node + ".minBounds", *min_bounds)
        cmds.setAttr(rand_node + ".maxBounds", *max_bounds)

        # 创建 instancer
        instancer = cmds.createNode("instancer")

        # 连接几何体和 instancer
        cmds.connectAttr(self.selected_object + ".matrix", instancer + ".inputHierarchy[0]", force=True)
        cmds.connectAttr(rand_node + ".outPoints", instancer + ".inputPoints", force=True)

        print(f"Created randomNode: {rand_node}")
        print(f"Created instancer: {instancer}")
        print(f"Connected {self.selected_object} to instancer with random points.")

def show_window():
    win = RandomNodeWindow()
    win.show()
    return win
