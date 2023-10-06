import classes

myDatabase = classes.Database('data.csv', index=('id', 'name', 'password'), separator='_$_')
myDatabase.refreshData()


result = myDatabase.findData('name', 'Willem', mode='tuple')

print(result)

for id, name, password in result:
	myDatabase.chData(id, 'password', 'NewPass')

print(myDatabase.findData('name', 'Willem', mode='tuple'))

#myDatabase.addData((myDatabase.generateNewId(), 'Bassie', 'baspas'))
































#results = myDatabase.findData('name', 'David', format='tuple')

#print(results)
#for (name, id, password) in results:
#	print(name, password)

#results = myDatabase.findData('name', 'Willem', mode='tuple')
#print(results) # Output: [('PJaw2i0CCBX', 'Willem', 'MyPass123')]

#for id, name, password in results:
#	print(id, name) # Output: PJaw2i0CCBX Willem

#for (id, name, password) in myDatabase.findData('name', 'David', mode='tuple'):
#	print(id, name)
	#myDatabase.delData(id)

#print(myDatabase.findData('name', 'Willem'))