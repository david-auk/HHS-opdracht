import random
import string
import tkinter
from tkinter import ttk

class Database(object):
	"""docstring for Database"""
	def __init__(self, filename, index, separator=','):
		self.filename = filename
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
			print("Data has not been loaded. Call refreshData() first.")
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
			dataFile.write(f'\n{self.separator.join(tuple(newDataFormatted.values()))}')

		self.refreshData()

	def chData(self, targetId, targetRow, newValue):
		# Because the data is accessesed directly. it must make shure that the data is loaded, findData() does this for you
		if self.data is None:
			print("Data has not been loaded. Call refreshData() first.")
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
			print("Data has not been loaded. Call refreshData() first.")
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

				# Remove trailing newline
				lines[-1] = lines[-1].rstrip()
				
				# Write the modified content back to the file
				with open(self.filename, 'w') as dataFile:
					dataFile.writelines(lines)

		if idFound:
			self.refreshData()
		else:
			raise Exception('ID not found')

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

		self.sheet = ttk.Treeview(self.window, columns=formattedIndex, show="headings", selectmode="extended", name="dataTreeview")

		for columnNum, column in enumerate(formattedIndex):
			self.sheet.heading(f"#{columnNum+1}", text=column)

		#self.sheet.heading(f"#{len(self.index)}", text="Last Column")

		self.sheet.pack()

		self.refreshSheetData()

		''' </ Loading the tree widget /> '''

	def refreshSheetData(self, findFilter='all'):
		self.sheet.delete(*self.sheet.get_children())

		if findFilter == 'all':
			data = self.database.findData(all=True, mode='tuple')
		else:
			filterColumn, filterValue = findFilter
			data = self.database.findData(targetColumn=filterColumn, targetValue=filterValue, mode='tuple')

		#for item in data:
		#	self.sheet.insert("", "end", values=item[:2])  # Insert row1 and row2 values
		#	self.sheet.insert(self.sheet.get_children()[-1], "end", values=item[2:])  # Insert data1 and data2 values as children of the previous row

		for item in data:
			self.sheet.insert("", "end", values=item)

		self.data = data

	def runUI(self):
		self.window.mainloop()