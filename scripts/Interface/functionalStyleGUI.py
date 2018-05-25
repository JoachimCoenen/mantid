





'''
Default matplotlib interaction:
- move mouse over the plotting area. You can see
  the cursor position in the x and y coordinates
- while the mouse is over the figure, press keys
  'k' and 'l' to toggle the logarithmic x,y axes
'''
# This may be required if you are on a Mac and default to using OSX as
# your backend
from __future__ import print_function, absolute_import
import matplotlib
matplotlib.rcParams['backend'] = 'TkAgg'

import sys
import numpy as np
from matplotlib.backends.qt_compat import QtCore, QtWidgets
try:
	from matplotlib.backends.qt_compat import is_pyqt5
except ImportError:
	def is_pyqt5():
		from matplotlib.backends.qt_compat import QT_API
		return QT_API == u'PyQt5'

if is_pyqt5():
	from matplotlib.backends.backend_qt5agg import (
		FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
	from matplotlib.backends.backend_qt4agg import (
		FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure


class Stack:
	def __init__(self):
		self.__storage = []

	def isEmpty(self):
		return len(self.__storage) == 0

	def push(self,p):
		self.__storage.append(p)

	def pop(self):
		return self.__storage.pop()

	def replace(self, val):
		self.__storage[len(self.__storage) - 1] = val

	def peek(self):
		return self.__storage[len(self.__storage) - 1]

	def __len__(self):
		return len(self.__storage)

	def __iter__(self):
		return self.__storage.__iter__()

	def __reversed__(self):
		return self.__storage.__reversed__()




class GCS:
	"""GCS mean GUI Construction State"""
	def __init__(self, widget, counter):
		self.w = widget
		self.c = counter

class FunctionalStyleGUI():
			
	def __init__(self, host, OnGUI):
		self.host = host
		self.OnGUI = OnGUI
		self.isCurrentlyDrawing = False
		self.widgetStack = Stack()
		host.setLayout(QtWidgets.QGridLayout())
		self.widgetStack.push(GCS(host.layout(), 0))
		self.modifiedInput = (None, None) # tuple (widget, data)

		#self.buttonGroups = {} # dict {name : QButtonGroup}
		#self.oldButtonGroups = {} # dict {name : {set of buttons in this group}}


	def redrawGUI(self):
		if self.isCurrentlyDrawing:
			return
		try:
			self.isCurrentlyDrawing = True
			# prepare widgetStack:
			assert(len(self.widgetStack) == 1)
			self.widgetStack.peek().c = 0
			# draw GUI:
			print("###########################")
			print("###### redrawing GUI ######")
			self.OnGUI()
			assert(len(self.widgetStack) == 1)
		finally:
			self.isCurrentlyDrawing = False

	def OnInputModified(self, modifiedWidget, data = None):
		try:
			self.modifiedInput = (modifiedWidget, data)
			self.redrawGUI()
		finally:
			self.modifiedInput = (None, None)
		self.redrawGUI()

	def removeWidgets(self, fromPos = 0):
		while self.currentLayout().count() > fromPos:
			child = self.currentLayout().takeAt(0)
			self.currentLayout().removeItem(child)
			child.widget().setParent(None)

	def currentLayout(self):
		return self.widgetStack.peek().w

	def addkwArgsToItem(self, item, **kwargs):
		for propName, value in kwargs.items():
			name = propName 
			name = 'set' + name[0].upper() + name[1:len(name)]
			#if hasattr(item, name):
			getattr(item, name)(value)

	def addItem(self, ItemType, hasLabel = False, isLabel = False, **kwargs):
		gcs = self.widgetStack.peek()
		item = None
		isNew = False
		#print("[" + ", ".join(["({total}, {count})".format(total = elem.w.layout().count(), count = elem.c) for elem in self.widgetStack]) +"]")
		#print(gcs.w.layout().count(), gcs.c)

		if gcs.w.count() > gcs.c:
			item = gcs.w.itemAt(gcs.c).widget()
			if item == None:
				item = gcs.w.itemAt(gcs.c).layout()

			#print("testing item for type:", item, ItemType)
			if not isinstance(item, ItemType):
				print("removing Widgets after:", gcs.c)
				self.removeWidgets(fromPos=gcs.c)
				item = None
		if item == None:
			print("creating new item:", ItemType)
			item = ItemType()

			if isinstance(gcs.w, QtWidgets.QGridLayout):
				rindex = gcs.w.rowCount()
				cindex = 0
				cspan = 2	
				if hasLabel: 
					cindex = 1
					cspan = 1
					rindex -= 1
				if isLabel: 
					cspan = 1
				print(rindex, cindex, 1, cspan)
				if isinstance(item, QtWidgets.QWidget):
					gcs.w.addWidget(item, rindex, cindex, 1, cspan)
				elif isinstance(item, QtWidgets.QLayout):
						gcs.w.addLayout(item, rindex, cindex, 1, cspan)
			else:
				if isinstance(item, QtWidgets.QWidget):
					gcs.w.addWidget(item)
				elif isinstance(item, QtWidgets.QLayout):
						gcs.w.addLayout(item)
			isNew = True
		gcs.c += 1
		self.addkwArgsToItem(item, **kwargs)
		return item

	def addLabeledItem(self, ItemType, title = None, LabelType = QtWidgets.QLabel, tip = "", **kwargs):
		# returns a tuple (item, label)
		label = None
		if title != None:
			label = self.addItem(LabelType, isLabel = True, enabled = kwargs.get('enabled', True))
			label.setToolTip(tip)
			label.setText(title)

		item = self.addItem(ItemType, hasLabel = title != None, **kwargs)
		if hasattr(item, 'setToolTip'):
			item.setToolTip(tip)
		if label != None and isinstance(item, QtWidgets.QWidget):
			label.setBuddy(item)
		return (item, label)


	def pushLayout(self, LayoutType, title, LabelType = QtWidgets.QLabel, tip = "", **kwargs):
		items = self.addLabeledItem(LayoutType, title, LabelType, tip, **kwargs)
		layout = items[0]
		self.pushLayoutInstance(layout)
		return items

	def pushLayoutInstance(self, layoutInstance):
		self.widgetStack.push(GCS(layoutInstance, 0))
		print("push Layout, count = {0}".format(self.currentLayout().count()))

	def popLayout(self, LayoutType):
		assert(isinstance(self.currentLayout(), LayoutType))
		gcs = self.widgetStack.peek()
		self.removeWidgets(fromPos = gcs.c+1)
		print("pop Layout, newCount = {0}".format(gcs.c))
		self.widgetStack.pop()


	def verticalLayoutBegin(self, title = None, tip = "", **kwargs):
		self.pushLayout(QtWidgets.QGridLayout, title, tip=tip, **kwargs)
		# done

	def verticalLayoutEnd(self, preventStretch = False):
		layout = self.currentLayout()
		layout.setColumnStretch(layout.columnCount()-1, 1)
		# add spacer et the end, so widgets are aligned at the top:
		if preventStretch:
			spacer = self.addItem(QtWidgets.QWidget)
			layout.setRowStretch(layout.rowCount()-1, 1)
		self.popLayout(QtWidgets.QGridLayout)

	def horizontalLayoutBegin(self, title = None, tip = "", **kwargs):
		self.pushLayout(QtWidgets.QHBoxLayout, title, tip=tip, **kwargs)
		# done

	def horizontalLayoutCheckedBegin(self, isChecked, title = "", tip = "", **kwargs):
		items = self.pushLayout(QtWidgets.QHBoxLayout, title, LabelType=QtWidgets.QCheckBox, tip=tip, **kwargs)
		checkBox = items[1]
		if checkBox != self.modifiedInput[0] and checkBox.isChecked() != isChecked:
			checkBox.setChecked(isChecked)

		if QtCore.QObject.receivers(checkBox, checkBox.toggled) == 0 :
			checkBox.toggled.connect(lambda x: self.OnInputModified(checkBox))
		return checkBox.isChecked()
		# done

	def horizontalLayoutEnd(self, preventStretch = False):
		if preventStretch:
			spacer = self.addItem(QtWidgets.QWidget)
			spacer.sizePolicy().setHorizontalStretch(1)
		self.popLayout(QtWidgets.QHBoxLayout)
		# done

	def groupBoxBegin(self, title = "", **kwargs):
		groupBox = self.addItem(QtWidgets.QGroupBox, **kwargs)
		groupBox.setTitle(title)
		grid = groupBox.layout()
		if grid == None:
			grid = QtWidgets.QGridLayout()
			groupBox.setLayout(grid)
		self.pushLayoutInstance(grid)

	def groupBoxEnd(self, preventStretch = False):
		self.verticalLayoutEnd(preventStretch)
		#done

	def groupBoxHBegin(self, title = "", **kwargs):
		groupBox = self.addItem(QtWidgets.QGroupBox, **kwargs)
		groupBox.setTitle(title)
		grid = groupBox.layout()
		if grid == None:
			grid = QtWidgets.QHBoxLayout()
			groupBox.setLayout(grid)
		self.pushLayoutInstance(grid)
		
	def groupBoxHEnd(self, preventStretch = False):
		self.horizontalLayoutEnd(preventStretch)
		# done


	def button(self, text, tip = "", **kwargs):
		button = self.addLabeledItem(QtWidgets.QPushButton, None, tip=tip, **kwargs)[0]
		button.setToolTip(tip)
		button.setText(text)
		if QtCore.QObject.receivers(button, button.pressed) == 0 :
			button.pressed.connect(lambda: self.OnInputModified(button))
		return button.isDown()

	def label(self, text, tip = "", **kwargs):
		label = self.addLabeledItem(QtWidgets.QLabel, None, tip=tip, **kwargs)[0]
		label.setToolTip(tip)
		label.setText(text)

	def lineEdit(self, text, title = None, tip = "", **kwargs):
		lineEdit = self.addLabeledItem(QtWidgets.QLineEdit, title, tip=tip, **kwargs)[0]

		if lineEdit != self.modifiedInput[0] and lineEdit.text() != text:
			lineEdit.setText(text)
		
		if QtCore.QObject.receivers(lineEdit, lineEdit.textEdited) == 0 :
			lineEdit.textEdited.connect(lambda x: self.OnInputModified(lineEdit))
		return lineEdit.text()

	def spinBox(self, value, minVal = -float('inf'), maxVal = +float('inf'), step = 1, title = None, tip = "", **kwargs):
		spinBox = self.addLabeledItem(QtWidgets.QSpinBox, title, tip=tip, **kwargs)[0]

		spinBox.setRange(minVal, maxVal)
		spinBox.setSingleStep(step)
		if spinBox != self.modifiedInput[0] and spinBox.value() != value:
			spinBox.setValue(value)
		
		if QtCore.QObject.receivers(spinBox, spinBox.valueChanged) == 0 :
			spinBox.valueChanged.connect(lambda x: self.OnInputModified(spinBox))
		return spinBox.value()

	def doubleSpinBox(self, value, minVal = -float('inf'), maxVal = +float('inf'), step = 0.01, decimals = 3, title = None, tip = "", **kwargs):
		spinBox = self.addLabeledItem(QtWidgets.QDoubleSpinBox, title, tip=tip, **kwargs)[0]

		spinBox.setRange(minVal, maxVal)
		spinBox.setSingleStep(step)
		spinBox.setDecimals(decimals)
		if spinBox != self.modifiedInput[0] and spinBox.value() != value:
			spinBox.setValue(value)
		
		if QtCore.QObject.receivers(spinBox, spinBox.valueChanged) == 0 :
			spinBox.valueChanged.connect(lambda x: self.OnInputModified(spinBox))
		return spinBox.value()

	def slider(self, value, minVal, maxVal, title = None, tip = "", **kwargs):
		slider = self.addLabeledItem(QtWidgets.QSlider, title, tip=tip, **kwargs)[0]

		slider.setOrientation(QtCore.Qt.Horizontal)
		slider.setMinimum(minVal)
		slider.setMaximum(maxVal)
		if slider != self.modifiedInput[0] and slider.value() != value:
			slider.setValue(value)
		
		if QtCore.QObject.receivers(slider, slider.valueChanged) == 0 :
			slider.valueChanged.connect(lambda x: self.OnInputModified(slider))	
		return slider.value()

	def checkBox(self, isChecked, title, isExclusive = False, tip = "", **kwargs):
		checkBox = self.addLabeledItem(QtWidgets.QCheckBox, None, tip=tip, **kwargs)[0]
		checkBox.setToolTip(tip)
		checkBox.setText(title)

		checkBox.setAutoExclusive(isExclusive)
		if checkBox != self.modifiedInput[0] and checkBox.isChecked() != isChecked:
			checkBox.setChecked(isChecked)

		if QtCore.QObject.receivers(checkBox, checkBox.toggled) == 0 :
			checkBox.toggled.connect(lambda x: self.OnInputModified(checkBox))
		return checkBox.isChecked()

	def radioButtonGroup(self, value, radioButtons, title = None, tip = "", **kwargs):
		buttonGroup = QtWidgets.QButtonGroup()#self.addItem(QtWidgets.QButtonGroup)

		for button in buttonGroup.buttons():
			buttonGroup.removeButton(button)

		self.horizontalLayoutBegin(title=title, tip=tip, **kwargs)
		btnGrpLayout = self.currentLayout # used later for identifying, wether btnGroup has been changed by user
		for i in range(0, len(radioButtons)):
			btn = self.addLabeledItem(QtWidgets.QRadioButton, None, tip=tip)[0]
			buttonGroup.addButton(btn, i)
			btn.setText(radioButtons[i])
		self.horizontalLayoutEnd()
			
		buttonGroup.setExclusive(True)
		if btnGrpLayout != self.modifiedInput[0] and buttonGroup.checkedId() != value:
			buttonGroup.buttons()[value].setChecked(True)

		if QtCore.QObject.receivers(buttonGroup, buttonGroup.buttonToggled) == 0 :
			buttonGroup.buttonToggled.connect(lambda x: self.OnInputModified(btnGrpLayout, data=buttonGroup))
		return buttonGroup.checkedId()







