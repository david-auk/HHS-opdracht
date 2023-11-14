import classes

index = ('id', 'name', 'password', 'gepoetst')
myDatabase = classes.Database('data2.csv', index=index, separator='_$_')
myDatabase.refreshData()

interface = classes.TkinterInterface('Users', index=index, database=myDatabase)

interface.runUI()