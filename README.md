# HHS-opdracht

### Initializing a new Database:

make sure every database has an ID, as it is essential for this class to function properly

```python
myDatabase = Database('data.csv', index=('id', 'name', 'password'), separator='_$_')
```

`data.csv` should look like this:

```
1o3NYZIh8Kd_$_David_$_YoullNeverGuess
```

To initialise the data, you can use `refreshData()` function, llike so:
```python
myDatabase.refreshData()
```

### Adding Data:

##### ID's

This class requires that all databases have ID's, make sure every entry's ID is unique. If you want a unique ID for that database you can use the `generateNewId()` function:

```python
uniqueId = myDatabase.generateNewId()
```

which will provide you with a new unique ID.

##### Data

There are two ways to store data to the Datafile using the addData() function

1. Using a Tuple:  
   
   Pros: **Quick**, **Easy**
   
   Cons: **Must follow format of Index** (when the index is e.g:
   `index=('id', 'name', 'password')` this order must be followed in the tuple). (in big project this can be a hassle to change once the index is reordered)

```python
myDatabase.addData((myDatabase.generateNewId(), 'Willem', 'MyPass123'))
```

2. Using a Dictionary:
   
   Pros: **The order of the index is automatically followed**
   
   Cons: **Takes longer to input**

```python
myDatabase.addData({'name': 'Willem', 'id': myDatabase.generateNewId(), 'password': 'MyPass123'})
```

### Finding Data:

To find data you can use the `findData()` function that returns a filtered version your data.

The function takes two arguments: `targetColumn` and `targetValue`. In my example i want to find all data where the column **name** has the value **Willem**

There are two ways to get data in different modes using `findData()`:

1. Using the dictionary mode (default):
   Pros: **Modular**, **organized**
   
   Cons: **Can be tedious at times**

```python
results = myDatabase.findData('name', 'Willem')
print(results) # Output: [{'id': 'PJaw2i0CCBX', 'name': 'Willem', 'password': 'MyPass123'}]

for result in results:
	print(result) # Output: {'id': 'PJaw2i0CCBX', 'name': 'Willem', 'password': 'MyPass123'}
	print(result['id'], result['name']) # Output: PJaw2i0CCBX Willem
```

2. Using the tuple mode:
   Pros: **Quick**, **Readable**
   Cons: **Not modular**

```python
results = myDatabase.findData('name', 'Willem', mode='tuple')
print(results) # Output: [('PJaw2i0CCBX', 'Willem', 'MyPass123')]

for id, name, passowrd in results:
	print(id, name) # Output: PJaw2i0CCBX Willem
```

(it comes down to preference)

### Changing Data:

### Deleting Data: