
from __future__ import print_function, absolute_import

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
import itertools
import six
import re
if not 'unicode' in __builtins__:
	unicode = str

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

class WithBlock(object):
	"""docstring for WithBlock"""
	def __init__(self):
		super(WithBlock, self).__init__()
	
	def __enter__(self):
		pass

	def __exit__(self, exc_type, exc_value, traceback):
		pass

	def surroundWithBlock(self, outer):
		return self.surround(outer.__enter__, outer.__exit__)
		#done

	def surroundWith(self, enter, exit = None):
		class BoundBlock(WithBlock):
			"""docstring for BoundBlock"""
			def __init__(self, inner, outer__enter, outer__exit = None):
				super(BoundBlock, self).__init__()
				self.inner = inner
				self.outer__enter = outer__enter
				self.outer__exit = outer__exit
			
			def __enter__(self):
				result = self.outer__enter()
				self.inner.__enter__()
				return result

			def __exit__(self, exc_type, exc_value, traceback):
				hasHandeledException = self.inner.__exit__(exc_type, exc_value, traceback)
				if self.outer__exit != None:
					if hasHandeledException:
						self.outer__exit(None, None, None)
						return True
					else:
						return self.outer__exit(exc_type, exc_value, traceback)
				else:
					return hasHandeledException
		
		return BoundBlock(self, enter, exit)

class Layout(WithBlock):
	def __init__(self, qLayout, gui):
		super(Layout, self).__init__()
		self._qLayout = qLayout
		self._gui = gui
		self.indentLevel = 0
		self._index = 0

	def resetIndex(self):
		self._index = 0
		self.indentLevel = 0

	def __enter__(self):
		self._gui.pushLayout(self)

	def __exit__(self, exc_type, exc_value, traceback):
		self._gui.popLayout(self)
		self.removeWidgets(self._qLayout, fromPos = self._index)
		return False

	def getItem(self, index = None):
		index = self._index if index == None else index

		if self._qLayout.count() <= index:
			return None
		else:
			item = self._qLayout.itemAt(index)
			if item.widget() != None:
				return item.widget()
			elif item.layout() != None:
				return item.layout()
			elif item.spacerItem() != None:
				return item.spacerItem()
			return None

	def _addItem(self, ItemType, initArgs = {}, args = ()):
		item = self.getItem()	

		hasToAddItem = False
		if  isinstance(ItemType, QtWidgets.QWidget):
			if not item == ItemType:
				self.removeWidgets(self._qLayout, fromPos=self._index)
				item = ItemType
				hasToAddItem = True
		else:
			if type(item) is not ItemType:
				self.removeWidgets(self._qLayout, fromPos=self._index)
				print("creating new item:", ItemType)
				item = ItemType(*initArgs)
				hasToAddItem = True		

		if hasToAddItem:
			if isinstance(item, QtWidgets.QWidget):
				#print("adding Widget, args={}".format(type(item)))
				self._qLayout.addWidget(item, *args)
			elif isinstance(item, QtWidgets.QLayout):
				#print("adding Layout, args={}".format(args))
				self._qLayout.addLayout(item, *args)
			elif isinstance(item, QtWidgets.QSpacerItem):
				self._qLayout.addItem(item, *args)
			else:
				raise Exception('cannot add item {}'.format((item)))
		self._index += 1
		return item

	def removeWidgets(self, qLayout, fromPos = 0):
		while qLayout.count() > fromPos:
			child = qLayout.takeAt(qLayout.count()-1)
			print("!!!! REMOVING Widgets after:", fromPos, child)

			qLayout.removeItem(child)
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

class Splitter(Layout):
	QLayoutType = QtWidgets.QSplitter
	def __init__(self, qSplitter, gui):
		super(Splitter, self).__init__(qSplitter, gui)
		#done

	def resetIndex(self):
		self._index = 0
		self.indentLevel = 0

	def getItem(self, index = None):
		index = self._index if index == None else index

		if self._qLayout.count() <= index:
			return None
		else:
			return self._qLayout.widget(index)

	def _addItem(self, ItemType, initArgs = {}, args = ()):
		item = self.getItem()

		itemToAdd = None
		if  isinstance(ItemType, QtWidgets.QWidget):
			if not item == ItemType:
				self.removeWidgets(self._qLayout, fromPos=self._index)
				item = ItemType
				itemToAdd = item
		elif type(item) is QtWidgets.QWidget and type(item.layout()) is ItemType:
			item = item.layout()
		else:
			if type(item) is not ItemType:
				self.removeWidgets(self._qLayout, fromPos=self._index)
				print("creating new item:", ItemType)
				item = ItemType(*initArgs)
				if isinstance(item, QtWidgets.QSpacerItem):
					raise Exception('QSpacerItem cannot be added to a Splitter directly!')
				elif isinstance(item, QtWidgets.QLayout):
					itemToAdd = QtWidgets.QWidget()
					itemToAdd.setLayout(item)
				else:
					itemToAdd = item

		if itemToAdd:
			#print("adding Widget, args={}".format(type(item)))
			self._qLayout.addWidget(itemToAdd)

		self._index += 1
		return item

	def addItem(self, ItemType, initArgs = {}, fullSize = False):
		item = self._addItem(ItemType, initArgs)
		return item

	def removeWidgets(self, qLayout, fromPos = 0):
		if not isinstance(qLayout, QtWidgets.QSplitter):
			return super(Splitter, self).removeWidgets(qLayout, fromPos)

		while qLayout.count() > fromPos:
			widget = qLayout.widget(qLayout.count()-1)
			print("!!!! REMOVING Widgets after:", fromPos, widget)
			widget.deleteLater()
			widget.setParent(None)

class DoubleColumnLayout(Layout):
	QLayoutType = QtWidgets.QGridLayout

	def __init__(self, qLayout, gui, preventVStretch, preventHStretch):
		super(DoubleColumnLayout, self).__init__(qLayout, gui)
		self._preventVStretch = preventVStretch
		self._preventHStretch = preventHStretch
		self.resetIndex()

		self._qLayout.setVerticalSpacing(1)


	def __exit__(self, exc_type, exc_value, traceback):
		super(DoubleColumnLayout, self).__exit__(exc_type, exc_value, traceback)
		if self._preventHStretch:
			#add spacer to the right:
			spacer = self._addItem(QtWidgets.QWidget, 0, 1)

		# always set column stretch, so that labels are not unnecessarily large:
		self._qLayout.setColumnStretch(self._qLayout.columnCount()-1, 1)
		# add spacer et the end, so widgets are aligned at the top:
		if self._preventVStretch:
			spacer = self.addItem(QtWidgets.QWidget, fullSize=True)
			self._qLayout.setRowStretch(self._row-1, 1)
		return False

	def resetIndex(self):
		super(DoubleColumnLayout, self).resetIndex()
		self._row = 0
		self._column = 0

	def _addItem(self, ItemType, row, column, rowSpan = 1, columnSpan = 1, initArgs = {}):
		if self._qLayout.getItemPosition(self._index) != (row, column, rowSpan, columnSpan):
			#print("{} != {}".format(self._qLayout.getItemPosition(self._index), (row, column, rowSpan, columnSpan)))
			self.removeWidgets(self._qLayout, self._index)

		return super(DoubleColumnLayout, self)._addItem(ItemType, args=(row, column, rowSpan, columnSpan), initArgs=initArgs)
		#done

	def addItem(self, ItemType, initArgs = {}, fullSize = False):
		columnSpan = 2 if fullSize else 1
		if fullSize and self._column > 0:
			self.carriageReturn()

		item = self._addItem(ItemType, self._row, self._column, 1, columnSpan, initArgs)
		self._column += columnSpan
		if self._column > 1:
			self.carriageReturn()
		return item

	def canIndentItem(self, fullSize):
		return self._column == 0 or fullSize and self._column > 0
		#done

	def carriageReturn(self):
		self._row += 1
		self._column = 0

class DoubleRowLayout(Layout):
	QLayoutType = QtWidgets.QGridLayout

	def __init__(self, qLayout, gui):
		super(DoubleRowLayout, self).__init__(qLayout, gui)
		self.resetIndex()

	def resetIndex(self):
		super(DoubleRowLayout, self).resetIndex()
		self._row = 0
		self._column = 0

	def _addItem(self, ItemType, row, column, rowSpan = 1, columnSpan = 1, initArgs = {}):
		return super(DoubleRowLayout, self)._addItem(ItemType, args=(row, column, rowSpan, columnSpan), initArgs=initArgs)
		#done

	def addItem(self, ItemType, initArgs = {}, fullSize = False):
		rowSpan = 1
		if fullSize and self._row > 0:
			self.carriageReturn()
			rowSpan = 2
		item = self._addItem(ItemType, self._row, self._column, rowSpan, 1, initArgs)
		self._row += rowSpan
		if self._row > 1:
			self.carriageReturn()
		return item

	def canIndentItem(self, fullSize):
		return self._row == 1 and not fullSize
		#done

	def carriageReturn(self):
		self._row = 0
		self._column += 1

class SingleRowLayout(Layout):
	QLayoutType = QtWidgets.QHBoxLayout

	def __init__(self, qLayout, gui):
		super(SingleRowLayout, self).__init__(qLayout, gui)
		self.resetIndex()

	def _addItem(self, ItemType, initArgs = {}):
		return super(SingleRowLayout, self)._addItem(ItemType, args=(), initArgs=initArgs)
		#done

	def addItem(self, ItemType, initArgs = {}, fullSize = False):
		item = self._addItem(ItemType, initArgs)
		return item

	def canIndentItem(self, fullSize):
		return False
		#done
		
class FunctionalStyleGUI:

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

		qLayout = DoubleColumnLayout.QLayoutType()
		self.widgetStack.push(DoubleColumnLayout(qLayout, self, False, False))

		if host.layout() != None:
			host.layout().addLayout(qLayout)
			#self.currentLayout().removeWidgets(host.layout(), 0)
			#host.layout().deleteLater()
			#host.layout().setParent(None)
		host.setLayout(qLayout)

		self.modifiedInput = (None, None) # tuple (widget, data)
		self._modifiedInputStack = Stack() # for handling recursive OnInputModified calls, don't remove!
		self.anim1 = None

	def redrawGUI(self):
		if self.isCurrentlyDrawing:
			return
		try:
			self.isCurrentlyDrawing = True
			# prepare widgetStack:
			assert(len(self.widgetStack) == 1)
			self.widgetStack.peek().resetIndex()
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
			if not self.isCurrentlyDrawing:
				print("modifiedInput = {}".format(self.modifiedInput))
			self.redrawGUI()
		finally:
			self.modifiedInput = self._modifiedInputStack.pop()
		if self._modifiedInputStack.isEmpty():
			self.redrawGUI() # redraw again!

	def currentLayout(self):
		return self.widgetStack.peek()
		#done

	def addkwArgsToItem(self, item, **kwargs):
		for propName, value in kwargs.items():
			name = propName 
			name = 'set' + name[0].upper() + name[1:len(name)]
			#if hasattr(item, name):
			getattr(item, name)(value)

	def addItem(self, ItemType, fullSize, isIndented, initArgs = {}, **kwargs):
		indentLevel = self.currentLayout().indentLevel
		indentLevel += 1 if isIndented else 0
		shouldIndent = indentLevel > 0 and self.currentLayout().canIndentItem(fullSize)

		item = None
		if shouldIndent:
			with self.hLayout(fullSize):
				self.addSpacer(17 * indentLevel, QtWidgets.QSizePolicy.Fixed)
				item = self.currentLayout().addItem(ItemType, initArgs=initArgs, fullSize=fullSize)
		else:
			item = self.currentLayout().addItem(ItemType, initArgs=initArgs, fullSize=fullSize)

		layout = self.currentLayout()
		qLayout = layout._qLayout
		if hasattr(qLayout, 'setRowMinimumHeight'):
			row, _, _, _ = qLayout.getItemPosition(layout._index-1)
			if not isinstance(item, QtWidgets.QLabel) and isinstance(item, QtWidgets.QWidget):
				qLayout.setRowMinimumHeight(row, 27)
			else:
				qLayout.setRowMinimumHeight(row, 0)

		self.addkwArgsToItem(item, **kwargs)

		return item

	def addLabeledItem(self, ItemType, label, fullSize, isIndented, initArgs = {}, **kwargs):
		if label != None:
			self.label(label, fullSize, isIndented, enabled = kwargs.get('enabled', True), toolTip=kwargs.get('toolTip', ''))
		return self.addItem(ItemType, fullSize, isIndented, initArgs, **kwargs)

	def addLayout(self, LayoutType, label, isIndented, LabelType = QtWidgets.QLabel, tip = "", **kwargs):
		items = self.addLabeledItem(QtWidgets.QWidget, title, LabelType, tip, **kwargs)
		widget = items
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

	def pushLayout(self, layoutInstance):
		#print('pushLayout', layoutInstance)
		self.widgetStack.push(layoutInstance)
		#indent = 30 if isIndented else 0

	def popLayout(self, layoutInstance):
		assert(self.currentLayout() == layoutInstance)
		#print("pop Layout, {0}".format(layoutInstance))
		self.widgetStack.pop()

	def indentation(self):
		"""
		Creates an indented block. has to be used in an `with` statement (`with gui.indentation():`).
		Everything within the with statement will be indented.
		"""
		class Indentation(WithBlock):
			"""docstring for Indentation"""
			def __init__(self, gui):
				super(Indentation, self).__init__()
				self._gui = gui
			def __enter__(self):
				self._gui.currentLayout().indentLevel += 1
			def __exit__(self, exc_type, exc_value, traceback):
				self._gui.currentLayout().indentLevel -= 1
				return False
		return Indentation(self)
		
	def vLayout(self, fullSize = True, isIndented = False, preventVStretch = False, preventHStretch = False, tip = "", **kwargs):
		"""
		Creates a vertical layout. has to be used in an `with` statement (`with gui.vLayout():`).
		Everything within the with statement will be inside the vertical layout.
		"""
		qLayout = self.addItem(DoubleColumnLayout.QLayoutType, fullSize, isIndented, **kwargs)
		return DoubleColumnLayout(qLayout, self, preventVStretch, preventHStretch)

	def vLayoutLabeled(self, label, fullSize = False, isIndented = False, preventVStretch = False, preventHStretch = False, tip = "", enabled = True, **kwargs):
		"""
		Creates a horizontal layout. has to be used in an `with` statement (`with gui.hLayout():`).
		Everything within the with statement will be inside the horizontal layout.
		"""
		self.label(label, fullSize, isIndented, enabled)
		return self.vLayout(fullSize, isIndented, preventHStretch, **kwargs)

	def hLayout(self, fullSize = True, isIndented = False, preventHStretch = False, tip = "", **kwargs):
		"""
		Creates a horizontal layout. has to be used in an `with` statement (`with gui.hLayout():`).
		Everything within the with statement will be inside the horizontal layout.
		"""
		qLayout = None
		if isIndented:
			qLayout = self.addItem(SingleRowLayout.QLayoutType, fullSize, isIndented)
		else:
			qLayout = self.currentLayout().addItem(SingleRowLayout.QLayoutType, (), fullSize)
		self.addkwArgsToItem(qLayout, **kwargs)
		return SingleRowLayout(qLayout, self)

	def hLayoutLabeled(self, label, fullSize = False, isIndented = False, preventHStretch = False, tip = "", enabled = True, **kwargs):
		"""
		Creates a horizontal layout. has to be used in an `with` statement (`with gui.hLayout():`).
		Everything within the with statement will be inside the horizontal layout.
		"""
		self.label(label, fullSize, isIndented, enabled)
		return self.hLayout(fullSize, isIndented, preventHStretch, **kwargs)

	def hLayout2(self, fullSize = True, isIndented = False, preventHStretch = False, tip = "", **kwargs):
		"""
		Creates a horizontal layout. has to be used in an `with` statement (`with gui.hLayout():`).
		Everything within the with statement will be inside the horizontal layout.
		"""
		qLayout = None
		if isIndented:
			qLayout = self.addItem(DoubleRowLayout.QLayoutType, fullSize, isIndented)
		else:
			qLayout = self.currentLayout().addItem(DoubleRowLayout.QLayoutType, (), fullSize)
		self.addkwArgsToItem(qLayout, **kwargs)
		return DoubleRowLayout(qLayout, self)

	def hLayoutChecked(self, isChecked, label = None, fullSize = False, isIndented = False, preventHStretch = False, tip = "", **kwargs):
		"""
		Creates a horizontal layout with a checkBox. has to be used in an `with` statement (`with gui.hLayoutChecked(boolValue) as boolValue:`).
		The state of the checkbox can be retrieved via `boolValue = hlayout.value`
		Everything within the with statement will be inside the horizontal layout.
		"""
		isChecked = self.checkBox(isChecked, label, tip, fullSize, enabled = kwargs.get('enabled', True))
		qLayout = self.addItem(SingleRowLayout.QLayoutType, fullSize, isIndented, **kwargs)
		
		return SingleRowLayout(qLayout, self).surroundWith(enter=lambda: isChecked)
		
	def groupBox(self, title, isIndented = False, preventVStretch = False, preventHStretch = False, enabled=True, **kwargs):
		"""
		Creates a vertical layout. has to be used in an `with` statement (`with gui.verticalLayout():`).
		Everything within the with statement will be inside the vertical layout.
		"""
		self.title(title, isIndented=isIndented, enabled=enabled, **kwargs)
		return self.indentation()

	def groupBoxChecked(self, isChecked, title = None, isCheckable = True, isIndented = False, preventVStretch = False, preventHStretch = False, enabled=True, **kwargs):
		"""
		Creates a vertical layout. has to be used in an `with` statement (`with gui.verticalLayout():`).
		Everything within the with statement will be inside the vertical layout.
		"""
		return self.indentation().surroundWith(lambda: self.checkBox(isChecked, title, "", True, isIndented, enabled, styleSheet="font-weight: bold;\n", **kwargs))

	def scrollBox(self, fullSize = True, isIndented = False, preventVStretch = False, preventHStretch = False, **kwargs):
		"""
		Creates a vertical layout. has to be used in an `with` statement (`with gui.verticalLayout():`).
		Everything within the with statement will be inside the vertical layout.
		"""
		scrollBox = self.addItem(QtWidgets.QScrollArea, fullSize, isIndented, widgetResizable=True, **kwargs)
		widget = scrollBox.widget()
		if widget == None:
			widget = QtWidgets.QWidget()
			scrollBox.setWidget(widget)

		qLayout = widget.layout()
		if qLayout == None:
			qLayout = DoubleColumnLayout.QLayoutType()
			widget.setLayout(qLayout)

		return DoubleColumnLayout(qLayout, self, preventVStretch, preventHStretch)

	def tabWidget(self, tip = "", fullSize = True, isIndented = False, **kwargs):
		"""
		Creates a vertical layout. has to be used in an `with` statement (`with gui.verticalLayout():`).
		Everything within the with statement will be inside the vertical layout.
		"""
		class TabControl:
			def __init__(self, tabWidget, gui):
				self._gui = gui
				self._tabWidget = tabWidget
				self._index = 0
			def __enter__(self):
				return self
			def __exit__(self, exc_type, exc_value, traceback):
				tabWidget = self._tabWidget
				while tabWidget.count() > self._index:
					tabWidget.removeTab(tabWidget.count()-1)
				return False

			def addTab(self, label, preventVStretch = False, preventHStretch = False):
				tabWidget = self._tabWidget
				if tabWidget.count() <= self._index:
					widget = QtWidgets.QWidget()
					qLayout = DoubleColumnLayout.QLayoutType()
					widget.setLayout(qLayout)
					tabWidget.addTab(widget, label)
					print("adding Tab", tabWidget.count())
				tabWidget.setTabText(self._index, label)
				qLayout = tabWidget.widget(self._index).layout()
				self._index +=1
				return DoubleColumnLayout(qLayout, self._gui, preventVStretch, preventHStretch)
		
		tabWidget = self.addItem(QtWidgets.QTabWidget, fullSize, isIndented, toolTip=tip, minimumHeight=0, **kwargs)
		return TabControl(tabWidget, self)

	def splitter(self, **kwargs):
		qLayout = self.addItem(Splitter.QLayoutType, True, False, **kwargs)
		return Splitter(qLayout, self)

	def addSpacer(self, size, sizePolicy):
		spacer = self.currentLayout().addItem(QtWidgets.QSpacerItem, initArgs=(0, 0), fullSize=True)
		needsInvalidation = False

		layout = self.currentLayout()
		if isinstance(layout, DoubleColumnLayout):
			needsInvalidation = needsInvalidation or spacer.sizeHint().height() != size
			needsInvalidation = needsInvalidation or spacer.sizePolicy().verticalPolicy() != sizePolicy
			spacer.changeSize(0, size, vPolicy = sizePolicy)
		elif isinstance(layout, SingleRowLayout) or isinstance(layout, DoubleRowLayout):
			needsInvalidation = needsInvalidation or spacer.sizeHint().width() != size
			needsInvalidation = needsInvalidation or spacer.sizePolicy().horizontalPolicy() != sizePolicy
			spacer.changeSize(size, 0, hPolicy = sizePolicy)
		if needsInvalidation:
			spacer.invalidate()

	def button(self, text, fullSize = False, isIndented = False, enabled=True, **kwargs):
		button = self.addItem(QtWidgets.QPushButton, fullSize, isIndented, text=text, enabled=enabled, **kwargs)
		if QtCore.QObject.receivers(button, button.pressed) == 0 :
			button.pressed.connect(lambda: self.OnInputModified(button))
		return button.isDown()

	def label(self, text, fullSize = False, isIndented = False, enabled=True, **kwargs):
		label = self.addItem(QtWidgets.QLabel, fullSize, isIndented, text=text, enabled=enabled, **kwargs)
		if type(self.currentLayout()._qLayout) is not QtWidgets.QGridLayout:
			sp = label.sizePolicy()
			sp.setHorizontalPolicy(QtWidgets.QSizePolicy.Minimum)
			label.setSizePolicy(sp)

	def title(self, text, fullSize = True, isIndented = False, enabled=True, **kwargs):
		self.addSpacer(10, QtWidgets.QSizePolicy.Fixed)
		self.label(text, fullSize, isIndented, enabled, styleSheet="font-weight: bold;", **kwargs)

	helpBoxStyles = {'hint', 'info', 'warning', 'error'}
	def helpBox(self, text, style = 'hint', fullSize = True, isIndented = False, enabled=True):
		''' displays a full width Help Box'''
		assert(style in self.helpBoxStyles)
		styleSheet = 'font-size: 10pt; font-style: italic; '
		styleSheet += 'color: rgb(255, 0, 0); ' if style in {'error'} else ''
		styleSheet += 'color: rgb(127, 127, 0); ' if style in {'warning'} else ''
		if text:
			self.label(text, fullSize, isIndented, enabled, styleSheet=styleSheet)
		#'font: italic 10pt "Bitstream Charter";'

	def helpBoxRight(self, text, style = 'hint', isIndented = False, enabled=True):
		''' displays a Help Box under the last drawn gui element'''
		if text:
			self.addItem(QtWidgets.QWidget, False, isIndented)
			self.helpBox(text, style, False, isIndented, enabled)
		#'font: italic 10pt "Bitstream Charter";'

	def lineEdit(self, text, label = None, fullSize = False, isIndented = False, tip = "", enabled=True, **kwargs):
		lineEdit = self.addLabeledItem(QtWidgets.QLineEdit, label, fullSize, isIndented, enabled=enabled, **kwargs)

		if lineEdit != self.modifiedInput[0] and lineEdit.text() != text:
			lineEdit.setText(text)
		
		if QtCore.QObject.receivers(lineEdit, lineEdit.textEdited) == 0 :
			lineEdit.textEdited.connect(lambda x: self.OnInputModified(lineEdit))
		print('lineEdit: %d' % lineEdit.height())
		return lineEdit.text()

	def folderPathEdit(self, path, label, tip = '', fullSize = False, isIndented = False, enabled=True):
		self.label(label, fullSize, isIndented, enabled)
		with self.hLayout(fullSize, isIndented):
			path = self.lineEdit(path, enabled=enabled)
			if self.button('Browse', enabled=enabled):
				newPath = str(QtWidgets.QFileDialog.getExistingDirectory(self.host, "Select Directory", path))
				path = newPath if newPath else path
		return path

	def openFilePathEdit(self, path, filter = "", label = None, tip = '', fullSize = False, isIndented = False, enabled=True, **kwargs):
		self.label(label, fullSize, isIndented, enabled)
		with self.hLayout(fullSize, isIndented):
			path = self.lineEdit(path, enabled=enabled)
			if self.button('Browse', enabled=enabled):
				newPath = str(QtWidgets.QFileDialog.getOpenFileNames(self.host, "Save File", path, filter)[0])
				path = newPath if newPath else path
		return path

	def saveFilePathEdit(self, path, filter = "", label = None, tip = '', fullSize = False, isIndented = False, enabled=True, **kwargs):
		self.label(label, fullSize, isIndented, enabled)
		with self.hLayout(fullSize, isIndented):
			path = self.lineEdit(path, enabled=enabled)
			if self.button('Browse', enabled=enabled):
				newPath = str(QtWidgets.QFileDialog.getSaveFileName(self.host, "Save File", path, filter)[0])
				path = newPath if newPath else path
		return path

	def spinBox(self, value, minVal = -0, maxVal = +99, step = 1, label = None, fullSize = False, isIndented = False, enabled=True, **kwargs):
		spinBox = self.addLabeledItem(QtWidgets.QSpinBox, label, fullSize, isIndented, enabled=enabled, singleStep=step, minimum=minVal, maximum=maxVal, **kwargs)

		#spinBox.setRange(minVal, maxVal)
		if spinBox != self.modifiedInput[0] and spinBox.value() != value:
			spinBox.setValue(value)
		
		if QtCore.QObject.receivers(spinBox, spinBox.valueChanged) == 0 :
			spinBox.valueChanged.connect(lambda x: self.OnInputModified(spinBox))
		return spinBox.value()

	def doubleSpinBox(self, value, minVal = -float('inf'), maxVal = +float('inf'), step = 0.01, decimals = 3, label = None, tip = "", fullSize = False, isIndented = False, enabled=True, **kwargs):
		spinBox = self.addLabeledItem(QtWidgets.QDoubleSpinBox, label, fullSize, isIndented, enabled=enabled, singleStep=step, minimum=minVal, maximum=maxVal, decimals=decimals, **kwargs)

		#spinBox.setRange(minVal, maxVal)
		if spinBox != self.modifiedInput[0] and spinBox.value() != value:
			spinBox.setValue(value)
		
		if QtCore.QObject.receivers(spinBox, spinBox.valueChanged) == 0 :
			spinBox.valueChanged.connect(lambda x: self.OnInputModified(spinBox))
		return spinBox.value()

	def comboBox(self, value, choices, label = None, tip = "", fullSize = False, isIndented = False, enabled=True, **kwargs):
		comboBox = self.addLabeledItem(QtWidgets.QComboBox, label, fullSize, isIndented, enabled=enabled, **kwargs)

		allCurrentItems = [comboBox.itemText(i) for i in range(comboBox.count())]
		if allCurrentItems != list(choices):
			comboBox.clear()
			comboBox.addItems(choices)

		valueIsStr = type(value) is str or type(value) is unicode
		setCurrentValue = comboBox.setCurrentText if valueIsStr else comboBox.setCurrentIndex
		getCurrentValue = comboBox.currentText if valueIsStr else comboBox.currentIndex

		if comboBox != self.modifiedInput[0] and getCurrentValue() != value:
			setCurrentValue(value)
		
		if QtCore.QObject.receivers(comboBox, comboBox.currentIndexChanged[int]) == 0 :
			comboBox.currentIndexChanged[int].connect(lambda x: self.OnInputModified(comboBox))
		print('comboBox: %d' % comboBox.height())
		return getCurrentValue()

	def slider(self, value, minVal, maxVal, label = None, tip = "", fullSize = False, isIndented = False, enabled=True, **kwargs):
		print("Adding Slider")
		slider = self.addLabeledItem(QtWidgets.QSlider, label, fullSize, isIndented, enabled=enabled, orientation=QtCore.Qt.Horizontal, minimum=minVal, maximum=maxVal, **kwargs)

		if slider != self.modifiedInput[0] and slider.value() != value:
			slider.setValue(value)
		
		if QtCore.QObject.receivers(slider, slider.valueChanged) == 0 :
			slider.valueChanged.connect(lambda x: self.OnInputModified(slider))	
		return slider.value()

	def checkBox(self, isChecked, label, tip = "", fullSize = True, isIndented = False, enabled=True, **kwargs):
		checkBox = self.addItem(QtWidgets.QCheckBox, fullSize, isIndented, enabled=enabled, text=label, **kwargs)

		if checkBox != self.modifiedInput[0] and checkBox.isChecked() != isChecked:
			checkBox.setChecked(isChecked)

		if QtCore.QObject.receivers(checkBox, checkBox.toggled) == 0 :
			checkBox.toggled.connect(lambda x: self.OnInputModified(checkBox))

		return checkBox.isChecked()

	def radioButton(self, isChecked, label, tip = "", fullSize = True, isIndented = False, enabled=True, **kwargs):
		radioButton = self.addItem(QtWidgets.QRadioButton, fullSize, isIndented, enabled=enabled, text=label, **kwargs)

		radioButton.setAutoExclusive(True)
		if radioButton != self.modifiedInput[0] and radioButton.isChecked() != isChecked:
			radioButton.setChecked(isChecked)

		if QtCore.QObject.receivers(radioButton, radioButton.toggled) == 0 :
			radioButton.toggled.connect(lambda x: self.OnInputModified(radioButton))

		return radioButton.isChecked()

	def radioButtonGroup(self, value, radioButtons, label = None, tip = "", fullSize = False, isIndented = False, enabled=True, **kwargs):
		buttonGroup = QtWidgets.QButtonGroup()#self.addItem(QtWidgets.QButtonGroup)

		with self.hLayoutLabeled(label, fullSize, isIndented, preventHStretch = True, **kwargs):
			btnGrpLayout = self.currentLayout() # used later for identifying, wether btnGroup has been changed by user
			for i in range(0, len(radioButtons)):
				btn = self.addItem(QtWidgets.QRadioButton, fullSize, isIndented, enabled=enabled, text=radioButtons[i])
				buttonGroup.addButton(btn, i)
			
		buttonGroup.setExclusive(True)
		print("value = {}, buttonGroup.checkedId() = {}".format(value, buttonGroup.checkedId()))
		if btnGrpLayout != self.modifiedInput[0] and buttonGroup.checkedId() != value:
			buttonGroup.buttons()[value].setChecked(True)

		if QtCore.QObject.receivers(buttonGroup, buttonGroup.buttonToggled[int, bool]) == 0 :
			# event gets fired twice (1x for button that turned on and 1x for button that turned off).
			# make sure only one event triggers a redrawing :
			buttonGroup.buttonToggled[int, bool].connect(lambda _, switchedOn: self.OnInputModified(btnGrpLayout, data=buttonGroup) if switchedOn else 0)
		return buttonGroup.checkedId()

	def dataTable(self, data, headers, label = None, tip = "", fullSize = True, isIndented = False, enabled=True, **kwargs):
		needsReset = False
		table = self.addLabeledItem(FunctionalStyleGUI.DataTableView, label, fullSize, isIndented, enabled=enabled, **kwargs)
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

	def progressBar(self, progressSignal, minVal = 0, maxVal = 100, label = None, tip = "", fullSize = False, isIndented = False, enabled=True, **kwargs):
		progressBar = self.addLabeledItem(QtWidgets.QProgressBar, label, fullSize, isIndented, enabled=enabled, orientation=QtCore.Qt.Horizontal, minimum=minVal, maximum=maxVal, **kwargs)

		try:
			progressSignal.disconnect(progressBar.setValue)
		except Exception as e:
			if str(e)[0:19] != "disconnect() failed":
				raise e
		progressSignal.connect(progressBar.setValue, type=QtCore.Qt.UniqueConnection)

	def vector(self, values, labeles, widgetPainter, label = None, fullSize = False, isIndented = False, tip = "", enabled=True, **kwargs):
		allLabeles = itertools.chain(labeles, itertools.repeat(None))
		with self.hLayoutLabeled(label, fullSize, isIndented, tip=tip, enabled=enabled):
			result = map(lambda (v, l): widgetPainter(v, label=l, tip=tip, enabled=enabled, **kwargs), zip(values, allLabeles))
			return result

	def customWidget(self, widgetInstance, label = None, tip = "", fullSize = False, isIndented = False, enabled=True, **kwargs):
		self.addLabeledItem(widgetInstance, label, fullSize, isIndented, **kwargs)
		#done
	# line 919

	# Mantid specific:
	def validate_runs(self, runs):
		# Ranges are:
		# |- simple scalars : "17"
		# |- simple ranges : "5:15" or "5-15", but not reversed eg:"15-5"
		# |- sstepped ranges: "5:15:2" or "5-15:2" meaning "5, 7, 9, 11, 13, 15"
		#
		# Ranges can be seperated by a comma+space (eg. "3, 5"). Just a comma (eg. "3,5")is not sufficent!
		if not runs:
			return ''

		errorStr = ''
		reResult = re.findall(r'(^X|(?:^X)?[-:, ]+)(?:$|([^-:, \n]+)(?:([-:])([^-:, \n]*)(?:([:])([^-:, \n]*))?)?)', "X" + runs)
		for r in reResult:
			# Group 1 = start-of-String, or ", " mandatory
			# Group 2 = start value				 mandatory
			# Group 3 = range separator (- or :)
			# Group 4 = end value
			# Group 5 = step separator (:)
			# Group 6 = step value
			group1, start, rangeSepar, end, stepSepar, step = r
			#Group 1
			if not group1:
				errorStr = 'invalid Input!'
			elif group1[0] == 'X' and len(group1) > 1:
				errorStr = "missing number before '%s'" % group1
			elif group1 == ',':
				errorStr = 'comma (,) needs to be followed by a space'
			elif re.match(r', {2,}$', group1):
				errorStr = 'too many spaces after comma (,)'
			elif group1 not in {', ', 'X'}:
				errorStr = "unknown characters found '%s'" % group1
			elif not start.isdigit():
				errorStr = "expected number after comma" if not start else \
						   "'%s' is not a positiv integer" % start
			elif rangeSepar and not end.isdigit():
				errorStr = "expected number after '%s'" % rangeSepar if not end else \
						   "'%s' is not a positiv integer" % end
			elif end and int(end) <= int(start):
				errorStr = "start of range cannot be larger than end of range: '%s%s%s'" % (start,rangeSepar, end)
			elif stepSepar and not step.isdigit():
				errorStr = "expected number after '%s'" % stepSepar if not step else \
						   "'%s' is not a positiv integer" % step

			if errorStr:
				break
		return errorStr

	def runsEdit(self, runs, label = None, fullSize = False, isIndented = False, tip = "", enabled=True, **kwargs):
		runs = self.lineEdit(runs, label, fullSize, isIndented, tip, enabled, **kwargs)
		errorStr = self.validate_runs(runs)
		return (runs, errorStr)

