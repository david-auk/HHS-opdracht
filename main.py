import classes

index = ('id', 'name', 'password')

myDatabase = classes.Database('data.csv', index=index, separator='_$_')
myDatabase.refreshData()