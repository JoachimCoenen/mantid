





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

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt





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

	def __str__(self):
		return self.__storage.__str__()

class GCS:
	"""GCS mean GUI Construction State"""
	def __init__(self, widget, counter):
		self.w = widget
		self.c = counter
		self.rc = 0 # rowCount

class FunctionalStyleGUI():

	class DataTableModel(QtCore.QAbstractTableModel):
		def __init__(self, parent, headers = ()):
			QtCore.QAbstractTableModel.__init__(self, parent)
			self.tableData = []
			self.headers = headers

		def _numRows(self):
			"""
			:return: number of rows with data
			"""
			return len(self.tableData)

		def _getRow(self, row):
			"""
			:param row: int of the row to get 
			:return: data of the row
			"""
			return self.tableData[row] if row < self._numRows() else [""] * self.columnCount()

		def _isRowEmpty(self, row):
			"""
			checks if the row is empty
			:param row: int of the row to check
			:return: true if row is empty
			"""
			return all(not str(v).strip() for v in self._getRow(row))

		def _removeTrailingEmptyRows(self):
			"""
			remove all rows at the end of the table that are empty
			"""
			print("_removeTrailingEmptyRows")
			for row in reversed(range(self._numRows())):
				if self._isRowEmpty(row):
					del self.tableData[row]
				else:
					break

		def _removeEmptyRows(self):
			"""
			remove all empty rows 
			"""
			for row in reversed(range(self._numRows())):
				if self._isRowEmpty(row):
					del self.tableData[row]

		def _ensureHasRows(self, numRows):
			"""
			ensure the table has numRows
			:param numRows:  number of rows that should exist
			"""
			while self._numRows() < numRows:
				self.tableData.append([""] * self.columnCount())

		def _setCellText(self, row, col, text):
			"""
			set the text of a cell
			:param row: row of the cell
			:param col: column of the cell
			:param text: text for the cell
			"""
			self._ensureHasRows(row + 1)
			self.tableData[row][col] = str(text).strip()

		def _getCellText(self, row, col):
			"""
			get the text of a cell
			:param row: row of the cell
			:param col: column of the cell
			:return: text of the cell
			"""
			return str(self._getRow(row)[col]).strip()

		# reimplemented QAbstractTableModel methods

		selectCell = QtCore.pyqtSignal(QtCore.QModelIndex)

		def emptyCells(self, indexes):
			"""
			empty the cells with the indexes
			:param indexes: indexes of the cells to be emptied
			"""
			for index in indexes:
				row = index.row()
				col = index.column()

				self._setCellText(row, col, "")

			self._removeEmptyRows()
			self.beginResetModel()
			self.endResetModel()
			# indexes is never empty
			self.selectCell.emit(indexes[0])

		def rowCount(self, _=QtCore.QModelIndex()):
			"""
			number of rows
			:return: returns the number of rows
			"""
			# one additional row for new data
			return self._numRows() + 1

		def columnCount(self, _=QtCore.QModelIndex()):
			"""
			number of columns
			:return: number of columns
			"""
			return len(self.headers)

		def headerData(self, selection, orientation, role):
			"""
			header of the selection
			:param selection: selected cells
			:param orientation: orientation of selection
			:param role: role of the selection
			:return: header of the selection
			"""
			if Qt.Horizontal == orientation and Qt.DisplayRole == role:
				return self.headers[selection]
			return None

		def data(self, index, role):
			"""
			data of the cell
			:param index: index of the cell
			:param role: role of the cell
			:return: data of the cell
			"""
			if Qt.DisplayRole == role or Qt.EditRole == role:
				return self._getCellText(index.row(), index.column())
			return None

		def setData(self, index, text, _):
			"""
			set text in the cell
			:param index: index of the cell
			:param text: text for the cell
			:return: true if data is set
			"""
			print("## setData")
			row = index.row()
			col = index.column()

			self._setCellText(row, col, text)
			self._removeTrailingEmptyRows()

			self.beginResetModel()
			self.endResetModel()

			# move selection to the next column or row
			col = col + 1

			if col >= self.columnCount:
				row = row + 1
				col = 0

			row = min(row, self.rowCount() - 1)
			self.selectCell.emit(self.index(row, col))

			return True

		def flags(self, _):
			"""
			flags for the table
			:return: flags
			"""
			return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
			
	class DataTableView(QtWidgets.QTableView):
		"""
		View of the tables
		"""

		def keyPressEvent(self, QKeyEvent):
			"""
			reimplemented keyPressEvent for deleting cells and arrows in editing cells 
			:param QKeyEvent: 
			:return: 
			"""
			if self.state() == QtWidgets.QAbstractItemView.EditingState:
				index = self.currentIndex()
				if QKeyEvent.key() in [Qt.Key_Down, Qt.Key_Up]:
					self.setFocus()
					self.setCurrentIndex(self.model().index(index.row(), index.column()))
				else:
					QtWidgets.QTableView.keyPressEvent(self, QKeyEvent)
			if QKeyEvent.key() in [Qt.Key_Delete, Qt.Key_Backspace]:
				self.model().emptyCells(self.selectedIndexes())
			else:
				QtWidgets.QTableView.keyPressEvent(self, QKeyEvent)
	
	def __init__(self, host, OnGUI):
		self.host = host
		self.OnGUI = OnGUI
		self.isCurrentlyDrawing = False
		self.widgetStack = Stack()
		host.setLayout(QtWidgets.QGridLayout())
		self.widgetStack.push(GCS(host.layout(), 0))
		self.modifiedInput = (None, None) # tuple (widget, data)
		self._modifiedInputStack = Stack() # for handling recursive OnInputModified calls, don't remove!

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
			#print("###########################")
			print("###### redrawing GUI ######")
			self.OnGUI()
			assert(len(self.widgetStack) == 1)
		finally:
			self.isCurrentlyDrawing = False

	def OnInputModified(self, modifiedWidget, data = None):
		try:
			self._modifiedInputStack.push(self.modifiedInput)
			self.modifiedInput = (modifiedWidget, data)
			print("modifiedInput = {}".format(self.modifiedInput))
			self.redrawGUI()
		finally:
			self.modifiedInput = self._modifiedInputStack.pop()
		if self._modifiedInputStack.isEmpty():
			self.redrawGUI() # redraw again!

	def removeWidgets(self, layout, fromPos = 0):
		while layout.count() > fromPos:
			child = layout.takeAt(layout.count()-1)
			print("!!!! REMOVING Widgets after:", fromPos, child)

			layout.removeItem(child)
			if child.widget() != None:
				child.widget().deleteLater()
				child.widget().setParent(None)
			elif child.layout() != None:
				self.removeWidgets(child.layout(), 0)
				child.layout().deleteLater()
				child.layout().setParent(None)
			else:
				pass
				#child.spacerItem().setParent(None)

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

		if gcs.w.count() > gcs.c:
			item = gcs.w.itemAt(gcs.c).widget()
			if item == None:
				item = gcs.w.itemAt(gcs.c).layout()
			if not type(item) is ItemType:
				self.removeWidgets(self.currentLayout(), fromPos=gcs.c)
				item = None
		if item == None:
			print("creating new item:", ItemType)
			item = ItemType()

			if isinstance(gcs.w, QtWidgets.QGridLayout):
				rindex = gcs.rc
				print("####", "rowCount={}, hasLabel={}, isLabel={}".format(gcs.rc, hasLabel, isLabel))
				cindex = 1
				cspan = 2	
				if hasLabel: 
					cindex = 2
					cspan = 1
					rindex -= 1
				if isLabel: 
					cspan = 1
					item.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
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
		if isLabel: 
			item.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
		if isinstance(gcs.w, QtWidgets.QGridLayout):
			row, column, rowSpan, columnSpan = gcs.w.getItemPosition(gcs.c-1)
			gcs.rc = row + rowSpan
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
		if label != None and isinstance(item, QtWidgets.QWidget) and isinstance(label, QtWidgets.QLabel):
			label.setBuddy(item)
		return (item, label)


	def pushLayout(self, LayoutType, title, isIndented, LabelType = QtWidgets.QLabel, tip = "", **kwargs):
		items = self.addLabeledItem(QtWidgets.QWidget, title, LabelType, tip, **kwargs)
		widget = items[0]
		layout = widget.layout()
		if not type(layout) is LayoutType:
			if layout != None:
				self.removeWidgets(layout, 0)
				layout.deleteLater()
				layout.setParent(None)

			widget.setLayout(LayoutType())
			layout = widget.layout()
			layout.setContentsMargins(0, 0, 0, 0)

		#items = self.addLabeledItem(LayoutType, title, LabelType, tip, **kwargs)
		#layout = items[0]

		self.pushLayoutInstance(layout, isIndented)
		return items

	def pushLayoutInstance(self, layoutInstance, isIndented):
		self.widgetStack.push(GCS(layoutInstance, 0))
		indent = 30 if isIndented else 0

		gcs = self.widgetStack.peek()
		spacer = None
		if gcs.w.count() > 0:
			spacer = gcs.w.itemAt(0).spacerItem()
		if spacer == None:
			spacer = QtWidgets.QSpacerItem(indent, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
			if isinstance(gcs.w, QtWidgets.QGridLayout):
				gcs.w.addItem(spacer, 0, 0)
			else:
				gcs.w.addItem(spacer)
		gcs.c += 1
		spacer.changeSize(indent, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

		#print("push Layout, count = {0}".format(self.currentLayout().count()))

	def popLayout(self, LayoutType):
		assert(isinstance(self.currentLayout(), LayoutType))
		gcs = self.widgetStack.peek()
		self.removeWidgets(self.currentLayout(), fromPos = gcs.c+1)
		#print("pop Layout, newCount = {0}".format(gcs.c))
		self.widgetStack.pop()


	def verticalLayoutBegin(self, title = None, tip = "", isIndented = False, **kwargs):
		self.pushLayout(QtWidgets.QGridLayout, title, isIndented, tip=tip, **kwargs)
		# done

	def verticalLayoutEnd(self, preventVStretch = False, preventHStretch = False):
		layout = self.currentLayout()
		gcs = self.widgetStack.peek()
		# add spacer et the end, so widgets are left aligned:
		if preventHStretch:
			#add spacer to the right:
			spacer = None
			if gcs.w.count() > gcs.c:
				spacer = gcs.w.itemAt(gcs.c).widget()
				#print("testing item for type:", spacer, QtWidgets.QWidget)
				if not type(spacer) is QtWidgets.QWidget:
					print("removing Widgets after:", gcs.c)
					self.removeWidgets(self.currentLayout(), fromPos=gcs.c)
					spacer = None
			if spacer == None:
				print("creating new item:", QtWidgets.QWidget)
				spacer = QtWidgets.QWidget()
				gcs.w.addWidget(spacer, 0, 3, gcs.rc, 1)
			gcs.c += 1

		# always set column stretch, so that labels are not unnecessarily large:
		layout.setColumnStretch(layout.columnCount()-1, 1)
		# add spacer et the end, so widgets are aligned at the top:
		if preventVStretch:
			spacer = self.addItem(QtWidgets.QWidget)
			layout.setRowStretch(gcs.rc-1, 1)
		self.popLayout(QtWidgets.QGridLayout)

	def horizontalLayoutBegin(self, title = None, tip = "", **kwargs):
		self.pushLayout(QtWidgets.QHBoxLayout, title, isIndented=False, tip=tip, **kwargs)
		# done

	def horizontalLayoutCheckedBegin(self, isChecked, title = "", tip = "", **kwargs):
		items = self.pushLayout(QtWidgets.QHBoxLayout, title, isIndented=False, LabelType=QtWidgets.QCheckBox, tip=tip, **kwargs)
		checkBox = items[1]
		if checkBox != self.modifiedInput[0] and checkBox.isChecked() != isChecked:
			checkBox.setChecked(isChecked)

		if QtCore.QObject.receivers(checkBox, checkBox.toggled) == 0 :
			checkBox.toggled.connect(lambda x: self.OnInputModified(checkBox))
		return checkBox.isChecked()
		# done

	def horizontalLayoutEnd(self, preventHStretch = False):
		if preventHStretch:
			spacer = self.addItem(QtWidgets.QWidget)
			spacer.sizePolicy().setHorizontalStretch(5)
		self.popLayout(QtWidgets.QHBoxLayout)
		# done

	def groupBoxBegin(self, title = "", tip = "", **kwargs):
		groupBox = self.addItem(QtWidgets.QGroupBox, **kwargs)
		groupBox.setToolTip(tip)
		groupBox.setTitle(title)
		grid = groupBox.layout()
		if grid == None:
			grid = QtWidgets.QGridLayout()
			groupBox.setLayout(grid)
		self.pushLayoutInstance(grid, isIndented=False) # groupBoxes are already indented by the System Styles

	def groupBoxCheckedBegin(self, isChecked, title = "", tip = "", **kwargs):
		groupBox = self.addItem(QtWidgets.QGroupBox, **kwargs)
		if not groupBox.isCheckable():
			groupBox.setCheckable(True)
		groupBox.setToolTip(tip)
		groupBox.setTitle(title)
		grid = groupBox.layout()
		if grid == None:
			grid = QtWidgets.QGridLayout()
			groupBox.setLayout(grid)
		self.pushLayoutInstance(grid, isIndented=False) # groupBoxes are already indented by the System Styles
		
		if groupBox != self.modifiedInput[0] and groupBox.isChecked() != isChecked:
			groupBox.setChecked(isChecked)

		if QtCore.QObject.receivers(groupBox, groupBox.toggled) == 0 :
			groupBox.toggled.connect(lambda x: self.OnInputModified(groupBox, x))

		return groupBox.isChecked()


	def groupBoxEnd(self, preventVStretch = False, preventHStretch = False):
		#pass
		self.verticalLayoutEnd(preventVStretch, preventHStretch)
		#done

	def groupBoxHBegin(self, title = "", **kwargs):
		groupBox = self.addItem(QtWidgets.QGroupBox, **kwargs)
		groupBox.setTitle(title)
		grid = groupBox.layout()
		if grid == None:
			grid = QtWidgets.QHBoxLayout()
			groupBox.setLayout(grid)
		self.pushLayoutInstance(grid, isIndented=False) # groupBoxes are already indented by the System Styles
		
	def groupBoxHEnd(self, preventHStretch = False):
		self.horizontalLayoutEnd(preventHStretch)
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

	def folderPathEdit(self, path, title = None, tip = "", **kwargs):
		self.horizontalLayoutBegin(title, tip=tip, **kwargs)
		path = self.lineEdit(path, tip=tip, **kwargs)
		if self.button('Browse', tip=tip, **kwargs):
			newPath = str(QtWidgets.QFileDialog.getExistingDirectory(self.host, "Select Directory", path))
			path = newPath if newPath else path
		self.horizontalLayoutEnd()
		return path

	def openFilePathEdit(self, path, filter = "", title = None, tip = "", **kwargs):
		self.horizontalLayoutBegin(title, tip=tip, **kwargs)
		path = self.lineEdit(path, tip=tip, **kwargs)
		if self.button('Browse', tip=tip, **kwargs):
			newPath = str(QtWidgets.QFileDialog.getOpenFileNames(self.host, "Save File", filter, path))
			path = newPath if newPath else path
		self.horizontalLayoutEnd()
		return path

	def saveFilePathEdit(self, path, filter = "", title = None, tip = "", **kwargs):
		self.horizontalLayoutBegin(title, tip=tip, **kwargs)
		path = self.lineEdit(path, tip=tip, **kwargs)
		if self.button('Browse', tip=tip, **kwargs):
			newPath = str(QtWidgets.QFileDialog.getSaveFileName(self.host, "Save File", filter, path))
			path = newPath if newPath else path
		self.horizontalLayoutEnd()
		return path

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

	def comboBox(self, value, choices, title = None, tip = "", **kwargs):
		comboBox = self.addLabeledItem(QtWidgets.QComboBox, title, tip=tip, **kwargs)[0]

		allCurrentItems = [comboBox.itemText(i) for i in range(comboBox.count())]
		if allCurrentItems == choices:
			print("### comboBox all OK")
		else:
			comboBox.clear()
			comboBox.addItems(choices)
			print("### comboBox redone choices")

		if comboBox != self.modifiedInput[0] and comboBox.currentIndex() != value:
			comboBox.setCurrentIndex(value)
		
		if QtCore.QObject.receivers(comboBox, comboBox.currentIndexChanged[int]) == 0 :
			comboBox.currentIndexChanged[int].connect(lambda x: self.OnInputModified(comboBox))
		return comboBox.currentIndex()

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

	def checkBox(self, isChecked, title, tip = "", **kwargs):
		checkBox = self.addLabeledItem(QtWidgets.QCheckBox, None, tip=tip, **kwargs)[0]
		checkBox.setToolTip(tip)
		checkBox.setText(title)

		if checkBox != self.modifiedInput[0] and checkBox.isChecked() != isChecked:
			checkBox.setChecked(isChecked)

		if QtCore.QObject.receivers(checkBox, checkBox.toggled) == 0 :
			checkBox.toggled.connect(lambda x: self.OnInputModified(checkBox))

		return checkBox.isChecked()

	def radioButton(self, isChecked, title, tip = "", **kwargs):
		radioButton = self.addLabeledItem(QtWidgets.QRadioButton, None, tip=tip, **kwargs)[0]
		radioButton.setToolTip(tip)
		radioButton.setText(title)

		radioButton.setAutoExclusive(True)
		if radioButton != self.modifiedInput[0] and radioButton.isChecked() != isChecked:
			radioButton.setChecked(isChecked)

		if QtCore.QObject.receivers(radioButton, radioButton.toggled) == 0 :
			radioButton.toggled.connect(lambda x: self.OnInputModified(radioButton))

		return radioButton.isChecked()

	def radioButtonGroup(self, value, radioButtons, title = None, tip = "", **kwargs):
		buttonGroup = QtWidgets.QButtonGroup()#self.addItem(QtWidgets.QButtonGroup)

		for button in buttonGroup.buttons():
			buttonGroup.removeButton(button)

		self.horizontalLayoutBegin(title=title, tip=tip, **kwargs)
		btnGrpLayout = self.currentLayout() # used later for identifying, wether btnGroup has been changed by user
		for i in range(0, len(radioButtons)):
			btn = self.addLabeledItem(QtWidgets.QRadioButton, None, tip=tip)[0]
			buttonGroup.addButton(btn, i)
			btn.setText(radioButtons[i])
		self.horizontalLayoutEnd(preventHStretch = True)
			
		buttonGroup.setExclusive(True)
		print("value = {}, buttonGroup.checkedId() = {}".format(value, buttonGroup.checkedId()))
		if btnGrpLayout != self.modifiedInput[0] and buttonGroup.checkedId() != value:
			buttonGroup.buttons()[value].setChecked(True)

		if QtCore.QObject.receivers(buttonGroup, buttonGroup.buttonToggled[int, bool]) == 0 :
			# event gets fired twice (1x for button that turned on and 1x for button that turned off).
			# make sure only one event triggers a redrawing :
			buttonGroup.buttonToggled[int, bool].connect(lambda _, switchedOn: self.OnInputModified(btnGrpLayout, data=buttonGroup) if switchedOn else 0)
		return buttonGroup.checkedId()

	def dataTable(self, data, headers, title = None, tip = "", **kwargs):
		needsReset = False
		table = self.addLabeledItem(FunctionalStyleGUI.DataTableView, title, tip=tip, **kwargs)[0] 
		if table.model() == None:
			table.setModel(FunctionalStyleGUI.DataTableModel(table, headers))
			table.model().modelReset.connect(lambda : self.OnInputModified(table.model()))

		table.verticalHeader().setVisible(False);
		table.horizontalHeader().setStretchLastSection(True)
		table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
		table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

		if table.model().headers != headers:
			table.model().headers = headers
			needsReset = True
		if table.model() != self.modifiedInput[0] and  table.model().tableData != data:
			table.model().tableData = data
			needsReset = True

		if needsReset:
			table.model().beginResetModel() 
			table.model().endResetModel()
		return table.model().tableData





