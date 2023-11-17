import random
import string
import os.path
import tkinter
from tkinter import ttk

class Database(object):
	"""docstring for Database"""
	def __init__(self, filename, index, separator=','):
		self.filename = filename

		if not os.path.isfile(self.filename):
			raise Exception(f'File {self.filename} doesnt exist or cant be found.')

		self.index = index
		self.data = None

		self.separator = separator

	def refreshData(self):

		data = {}

		with open(self.filename, mode='r') as dataFile:
			for rowNum, rowData in enumerate(dataFile):		
				
				rowNum += 1 # SQL like index

				data[rowNum] = {}

				rowDataList = rowData.replace('\n', '').split(self.separator)
				
				if len(self.index) != len(rowDataList):
					raise Exception(f"Index and data for row {rowNum} dont have the same length")

				for valueNum, key in enumerate(self.index):
					data[rowNum][key] = rowDataList[valueNum]

		self.data = data

	def findData(self, targetColumn=None, targetValue=None, mode='dictionary', all=False):
		if self.data is None:
			raise Exception("Data has not been loaded. Call refreshData() first.")
			return None

		if all == True:
			if mode == 'dictionary':
				return [self.data[row] for row in self.data]
			elif mode == 'tuple':
				return [tuple(self.data[row].values()) for row in self.data]
			else:
				raise Exception('Mode not recognized')
		else:
			if targetColumn == None or targetValue == None:
				raise Exception('Invalid arguments')

		returnList = []

		for row in self.data:
			
			if self.data[row][targetColumn] == targetValue:
				
				if mode == 'dictionary':
					returnList.append(self.data[row])
				elif mode == 'tuple':
					returnList.append(tuple(self.data[row].values()))
				else:
					raise Exception('Mode not recognized')

		return returnList

	def generateNewId(self, length=11):
		characters = string.ascii_letters + string.digits

		newIdFound = False
		while not newIdFound:
			possibleId = ''.join(random.choice(characters) for _ in range(length))
			if not self.findData('id', str(possibleId)):
				newIdFound = True
				newId = possibleId

		return newId

	def addData(self, newData):
		
		# Checking if the provided data has the same amount of fields (is indext the same)
		if len(self.index) != len(newData):
			raise Exception('Index and the new data dont have the same length')
		
		if type(newData) == dict:
			newDataFormatted = {key: newData[key] for key in self.index}
		elif type(newData) == tuple:
			newDataFormatted = dict(zip(self.index, newData))

		# Checking if the ID is unique
		if self.findData('id', str(newDataFormatted['id'])):
			raise Exception(f"id \"{newDataFormatted['id']}\" already in use in {self.filename}")

		# Writing to the data file

		with open(self.filename, mode='a') as dataFile:
			if not bool(self.data): # If the file is empty
				dataFile.write(f'{self.separator.join(tuple(newDataFormatted.values()))}') # Place at firstline
			else:
				dataFile.write(f'\n{self.separator.join(tuple(newDataFormatted.values()))}') # Place at last line (with a newline before for formatting)

		self.refreshData()

	def chData(self, targetId, targetRow, newValue):
		# Because the data is accessesed directly. it must make shure that the data is loaded, findData() does this for you
		if self.data is None:
			raise Exception("Data has not been loaded. Call refreshData() first.")
			return None

		idFound = False
		for row in self.data:
			value = self.data[row]
			
			if value['id'] == targetId:
				rowToChange = row
				idFound = True

				with open(self.filename, 'r') as dataFile:
					lines = dataFile.readlines()

				# Remove the line at the specified line number (index - 1)
				self.data[rowToChange][targetRow] = newValue
				
				# Remove the line at the specified line number (index - 1)
				lines[rowToChange - 1] = f'{self.separator.join(tuple(self.data[rowToChange].values()))}\n'
				
				# Remove trailing newline
				lines[-1] = lines[-1].rstrip()

				# Write the modified content back to the file
				with open(self.filename, 'w') as dataFile:
					dataFile.writelines(lines)

		if idFound:
			self.refreshData()
		else:
			raise Exception('ID not found')

	def delData(self, targetId):
		
		# Because the data is accessesed directly. it must make shure that the data is loaded, findData() does this for you
		if self.data is None:
			raise Exception("Data has not been loaded. Call refreshData() first.")
			return None

		idFound = False
		for row in self.data:
			value = self.data[row]
			
			if value['id'] == targetId:
				rowToDelete = row
				idFound = True

				with open(self.filename, 'r') as dataFile:
					lines = dataFile.readlines()

				# Remove the line at the specified line number (index - 1)
				del lines[rowToDelete - 1]

				if bool(lines): # If it isn't the last line
					# Remove trailing newline
					lines[-1] = lines[-1].rstrip()
				
				# Write the modified content back to the file
				with open(self.filename, 'w') as dataFile:
					dataFile.writelines(lines)

		if idFound:
			self.refreshData()
		else:
			raise Exception('ID not found')

class BetterTreeview(ttk.Treeview):
	def __init__(self, master, index, database, padySpacing, **kw):
		super().__init__(master, **kw)

		self.master = master

		self.index = index
		self.database = database

		self.treeTableSize = len(index) * 200 + 5

		self.padySpacing = padySpacing

		self.columnFilterdIndex = None
		self.columnFilterdTypeIndex = 0 # 0: None, 1: Alphabetical/numeral, 2: reversed.

		self.findFilter = None

		self.bind("<ButtonRelease-1>", self.onSingleLeftClick)
		self.bind("<ButtonRelease-2>", self.onRightClick)
		self.bind("<Double-1>", self.onDoubleClick)

		self.refreshSheetData()

	def onSingleLeftClick(self, event):
		regionClicked = self.identify_region(x=event.x, y=event.y)
		
		if regionClicked not in ("heading"):
			return

		# Getting clicked Header info
		headingClicked = self.identify_column(x=event.x)
		headingClickedIndex = int(headingClicked[1:]) - 1

		# The column header that will be filterd
		oldColumnFilterdIndex = self.columnFilterdIndex
		self.columnFilterdIndex = headingClickedIndex
		
		# Check if a new header is clicked whilst filtering
		if oldColumnFilterdIndex != self.columnFilterdIndex and self.columnFilterdTypeIndex != 0:
			
			# Cleaning up old filter arrows
			for column in self["columns"]:
				self.heading(column, text=f'{column}')

			# Resetting the modes ensuring a clean start
			self.columnFilterdTypeIndex = 0

		# Cycling modes per click
		self.columnFilterdTypeIndex += 1

		# Resetting cycle
		if self.columnFilterdTypeIndex == 3:
			self.columnFilterdTypeIndex = 0

		# Setting the header filter indicator
		if self.columnFilterdTypeIndex == 0:

			# Clear sort indicators from all columns
			for column in self["columns"]:
				self.heading(column, text=f'{column}')

		else:
			if self.columnFilterdTypeIndex == 1:
				char = '▼'
			elif self.columnFilterdTypeIndex == 2:
				char = '▲'
			
			# Set a triangle indicator next to the selected column's header
			headerName = self["columns"][headingClickedIndex]
			self.heading(headerName, text=f'{headerName} {char}')

		# Sorting/resetting
		self.refreshSheetData(findFilter=self.findFilter)

	def onRightClick(self, event):

		# Identifying the region clicked 
		regionClicked = self.identify_region(x=event.x, y=event.y)

		# Blocking unwanted region clicks, We're only intrested in cels (values) and trees
		if regionClicked not in ("cell"):
			return

		selectedRows = self.selection()
		rightClickedRow = self.identify_row(event.y)

		if not rightClickedRow in selectedRows:
			self.selection_set(rightClickedRow)	
			self.focus(rightClickedRow)
			selectedRows = (rightClickedRow,)

		selectedRowsAmount = len(self.selection())

		def refreshButton(self):
			self.refreshRawData()
			self.refreshSheetData(findFilter=self.findFilter)

		def deleteButton(self, selectedRows):
			# Gets the values of the tree using the column and selected iid
			for row in selectedRows:
				selectedValues = self.item(row)['values']
				entryDbID = dict(zip(self.index, tuple(selectedValues)))['id']

				self.database.delData(entryDbID)

			self.refreshRawData()
			self.refreshSheetData(findFilter=self.findFilter)
			self.showMessage(message=f"{self.database.filename.split('/')[-1]} Updated", colour='green', time=3000)

		rightMouseMenu = tkinter.Menu(self.master, tearoff=False)
		rightMouseMenu.add_command(label="Refresh", command=lambda: refreshButton(self))
		if selectedRowsAmount == 1:
			rightMouseMenu.add_command(label="Delete Row", command=lambda: deleteButton(self, selectedRows))
		else:
			rightMouseMenu.add_command(label=f"Delete Rows ({selectedRowsAmount})", command=lambda: deleteButton(self, selectedRows))

		# Configuring the pixel penalty for a resized window
		if self.master.winfo_width() < self.treeTableSize:
			xAxisTableScreenWidthTax = 8
		else:
			xAxisTableScreenWidthTax = int((self.master.winfo_width() - self.treeTableSize) / 2)

		self.update_idletasks()
		rightMouseMenu.tk_popup(x=event.x + xAxisTableScreenWidthTax + 5, y=event.y + self.padySpacing+10)

	def onDoubleClick(self, event):
		
		# Identifying the region clicked 
		regionClicked = self.identify_region(x=event.x, y=event.y)

		# Blocking unwanted region clicks, We're only intrested in cels (values) and trees
		if regionClicked not in ("tree", "cell"):
			return

		# For example the first row will be #0, then #1, ect.
		column = self.identify_column(x=event.x)
		columnIndex = int(column[1:]) - 1 # The index of this column to its corosponding value

		# For example 001
		selected_iid = self.focus() # Y value

		# Gets the values of the tree using the column and selected iid
		selectedValues = self.item(selected_iid)['values']
		selectedValue = selectedValues[columnIndex]

		# This will get the column border of the double clicked cell or tree
		columnBox = self.bbox(selected_iid, column)

		# This will create a new widget event
		entryEditWidget = ttk.Entry(self.master, width=columnBox[2])
	
		# Saving the values so they can be reused in the onEnterPressed() function to adress the cell
		entryEditWidget.editing_column_index = columnIndex
		entryEditWidget.editing_item_iid = selected_iid

		# This puts the existing data in the text field
		entryEditWidget.insert(0, selectedValue)
		entryEditWidget.select_range(0, tkinter.END)
		
		# Sets the focus on this widget
		entryEditWidget.focus()

		# This is responcible for user action handling
		entryEditWidget.bind("<FocusOut>", self.onFocusOut)
		entryEditWidget.bind("<Return>", self.onEnterPressed)
		entryEditWidget.bind("<Escape>", self.onEscapeOut)

		# Configuring the pixel penalty for a resized window

		if self.master.winfo_width() < self.treeTableSize:
			xAxisTableScreenWidthTax = 8
		else:
			xAxisTableScreenWidthTax = (self.master.winfo_width() - self.treeTableSize) / 2

		# Sets the borders of the text widget
		#entryEditWidget.place(x=columnBox[0]+xAxisTableScreenWidthTax, y=columnBox[1]-5, w=columnBox[2]+5, h=columnBox[3]+10)
		entryEditWidget.place(x=columnBox[0] + xAxisTableScreenWidthTax - 7, y=columnBox[1] - 1 + self.padySpacing, w=columnBox[2], h=columnBox[3]+6)

	def onEnterPressed(self, event):

		# Gets the newly returned value
		newValue = event.widget.get()

		# Collects data saved in variables fron the onDoubleClick() function
		selected_iid = event.widget.editing_item_iid # Such as I002
		columnIndex = event.widget.editing_column_index	# Such as 0

		# Gets all the unedited values
		currentValues = self.item(selected_iid)['values']

		# Gets the column thats been selected
		changedColumn = self.index[columnIndex]

		# Gets the id from the edited entry
		entryDbID = dict(zip(self.index, tuple(currentValues)))['id']

		# Updates the file
		self.database.chData(entryDbID, targetRow=changedColumn, newValue=newValue)

		# Updates the tree
		self.refreshSheetData(findFilter=self.findFilter)

		# Cleanes up the edit widget
		event.widget.destroy()

		# Giving message
		self.showMessage(message=f"{self.database.filename.split('/')[-1]} Updated", colour='green', time=3000)

	def refreshRawData(self):
		self.database.refreshData()

	def refreshSheetData(self, findFilter=None):
		
		# Deletes the existing data
		self.delete(*self.get_children())

		# Gets new data using the database class
		if findFilter == None:
			data = self.database.findData(all=True, mode='tuple')
		else:
			filterColumn, filterValue = findFilter
			data = self.database.findData(targetColumn=filterColumn, targetValue=filterValue, mode='tuple')

		sortingValues = {
			0: None,    # No sort at all (None for reverse means no sorting)
			1: False,   # Standard sort
			2: True     # Reversed sort
		}

		sortType = sortingValues[self.columnFilterdTypeIndex]

		# Sorting the data
		if sortType != None:
			data = sorted(data, key=lambda item: item[self.columnFilterdIndex], reverse=sortType)

		# Inputs raw data into tree
		for item in data:
			self.insert("", "end", values=item)

	def updateFilter(self, findFilter):
		self.findFilter = findFilter

	def showMessage(self, message, colour, time):
		label = tkinter.Label(self.master, text=f"ⓘ {message}", background=colour, foreground="white")
		label.pack(pady=10)
		label.after(time, label.destroy)

	def onFocusOut(self, event):

		# Destroys the event if the focus is lost (clicked away)
		event.widget.destroy()

	def onEscapeOut(self, event):

		# Destroys the event if escaped
		event.widget.destroy()

class BetterButtonActions(object):
	def __init__(self, master, index, treeView, database):

		self.master = master
		self.treeView = treeView
		self.database = database
		self.index = index

		# Open menus
		self.userMenuOpen = False

		self.findFilter = None
		self.findColumn = None
		self.findValue = None

		self.clearFilterButton = False

	def refresh(self):
		self.treeView.refreshRawData()
		self.treeView.refreshSheetData(findFilter=self.findFilter)

	def find(self):

		if self.userMenuOpen:
			self.showMessage(message='Close the Field', colour='red', time=3000)
			return

		if self.clearFilterButton:
			self.clearFilterButton.destroy()

		mainContainer = tkinter.Frame(self.master, highlightbackground="gray", highlightthickness=2)
		mainContainer.pack(pady=20)

		# Create a tkinter StringVar to hold the selected dropdown option
		selected_option = tkinter.StringVar(self.master)

		if self.findColumn == None:
			selected_option.set(self.index[0])  # Set the default option
		else:
			selected_option.set(self.findColumn)


		# Create a label and dropdown menu for the first input
		option_label = tkinter.Label(self.master, text="Find all Data where:")
		option_label.grid(in_=mainContainer,column=0, row=0)
		option_dropdown = tkinter.OptionMenu(self.master, selected_option, *self.index)
		option_dropdown.grid(in_=mainContainer,column=1, row=0)

		# Create a label and text input for the second input
		text_label = tkinter.Label(self.master, text="Has Value:")
		text_label.grid(in_=mainContainer,column=3, row=0)
		text_entry = tkinter.Entry(self.master, width=10)

		if self.findValue:
			text_entry.insert(0, self.findValue)

		text_entry.grid(in_=mainContainer,column=1, row=1)
		text_entry.focus()

		# Function to close the window and return the selected values
		def submit(event):
			findColumn = selected_option.get()
			self.findColumn = selected_option.get()
			self.findValue = text_entry.get()
			mainContainer.destroy()  # Close the window

			if self.findValue:
				self.findFilter = (self.findColumn, self.findValue)
				self.treeView.updateFilter(findFilter=self.findFilter)
				self.treeView.refreshSheetData(findFilter=self.findFilter)
				self.clearFilterButton = tkinter.Button(self.master, text="Clear Filters", padx=5, pady=5, command=clearFilter)
				self.clearFilterButton.pack(pady=10)
				text_entry.destroy()
			else:
				self.findFilter = None
				
			self.userMenuOpen = False

		def clearFilter():
			
			self.findFilter = None
			self.findValue = None
			#self.findColumn = None

			self.treeView.updateFilter(findFilter=self.findFilter)
			self.treeView.refreshSheetData(findFilter=self.findFilter)

			self.clearFilterButton.destroy()			

		find_button = tkinter.Button(self.master, text="Find", command=lambda: submit(None))
		text_entry.bind("<Return>", submit)
		find_button.grid(in_=mainContainer, row=2, column=1, columnspan=1)

		self.userMenuOpen = True

	def add(self): # posible rightclick? (on nothing)

		if self.userMenuOpen:
			self.showMessage(message='Close the Field', colour='red', time=3000)
			return

		mainContainer = tkinter.Frame(self.master, highlightbackground="gray", highlightthickness=2)
		mainContainer.pack(padx=10, pady=10)

		def submit(entry_widgets):

			values = []

			for entry in entry_widgets:

				entryValue = entry.get()
				if entryValue == '':

					self.showMessage("Fill all Fields", colour='red', time=3000)
					return
					
				else:
					values.append(entryValue)

			values = tuple(values)

			self.database.addData(newData=values)
			self.treeView.refreshSheetData(findFilter=self.findFilter)

			self.showMessage(message=f"{self.database.filename.split('/')[-1]} Updated", colour='green', time=3000)

			mainContainer.destroy()
			self.userMenuOpen = False

		def cancel():
			mainContainer.destroy()
			self.userMenuOpen = False

		entry_widgets = []

		for field in self.index:
			label = tkinter.Label(mainContainer, text=field.capitalize())
			label.pack(in_=mainContainer)

			entry = tkinter.Entry(mainContainer)

			if field == 'id':
				entry.insert(0, self.database.generateNewId())
				entry.select_range(0, tkinter.END)

			entry.pack()

			entry_widgets.append(entry)

		submitButton = tkinter.Button(mainContainer, text="Submit", command=lambda: submit(entry_widgets))
		submitButton.pack(pady=10)

		cancelButton = tkinter.Button(mainContainer, text="Cancel", command=cancel)
		cancelButton.pack(pady=10)

		self.userMenuOpen = True

	def showMessage(self, message, colour, time):
		
		label = tkinter.Label(self.master, text=f"ⓘ {message}", background=colour, foreground="white")
		label.pack(pady=10)
		label.after(time, label.destroy)

class TkinterInterface(object):
	
	def __init__(self, databaseTitle, index, database):

		self.databaseTitle = databaseTitle
		
		self.index = index
		formattedIndex = tuple(item.capitalize() for item in self.index)

		self.window = tkinter.Tk()
		self.window.title(databaseTitle)
		SCREEN_WIDTH = self.window.winfo_screenwidth()
		SCREEN_HEIGHT = self.window.winfo_screenheight()
		self.window.geometry(f"{round(SCREEN_WIDTH/1.5)}x{round(SCREEN_HEIGHT/2)}")

		# Database innit
		self.database = database
		self.database.refreshData()

		''' < Loading the tree widget > '''

		# Configure frame
		padySpacing = 20
		treeFrame = tkinter.Frame(self.window, highlightbackground="gray", highlightthickness=2)
		treeFrame.pack(pady=padySpacing)

		# Configure scroll wheel
		treeScroll = tkinter.Scrollbar(treeFrame)
		treeScroll.pack(side='right', fill='y')

		self.sheet = BetterTreeview(master=self.window, index=self.index, database=self.database, columns=formattedIndex, padySpacing=padySpacing, show="headings", selectmode="extended", name="dataTreeview", yscrollcommand=treeScroll.set)

		for columnNum, column in enumerate(formattedIndex):
			self.sheet.heading(f"#{columnNum+1}", text=column)

		self.sheet.pack(in_=treeFrame)

		# Making the scroll bar movable by drag
		treeScroll.config(command=self.sheet.yview)

		''' </ Loading the tree widget /> '''

		''' < Loading the button widget(s) > '''

		buttonFunctions = BetterButtonActions(master=self.window, index=self.index, treeView=self.sheet, database=self.database)

		buttonContainer = tkinter.LabelFrame(self.window)
		buttonContainer.pack()

		refreshButton = tkinter.Button(self.window, text='↻', padx=10, pady=10, command=buttonFunctions.refresh)
		refreshButton.grid(in_=buttonContainer, column=0, row=0)

		findButton = tkinter.Button(self.window, text='Search', padx=10, pady=10, command=buttonFunctions.find)
		findButton.grid(in_=buttonContainer, column=1, row=0)

		spacing = tkinter.Label(self.window, text = '')
		spacing.grid(in_=buttonContainer, column=2, row=0)

		additionButton = tkinter.Button(self.window, text='+', padx=10, pady=10, command=buttonFunctions.add)
		additionButton.grid(in_=buttonContainer, column=3, row=0)
		

	def runUI(self):
		self.window.mainloop()