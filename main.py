import classes

index = ('id', 'name', 'password')
myDatabase = classes.Database('data.csv', index=index, separator='_$_')
myDatabase.refreshData()

data = myDatabase.findData(all=True, mode='tuple')

interface = classes.TkinterInterface('Users', index=index, database=myDatabase)

interface.runUI()