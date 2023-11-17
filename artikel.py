import classes

index = ('id', 'naam', 'catagorie', 'prijs', 'voorraad', 'aanwezigheid', 'aanschafdatum')

artikelDB = classes.Database('./artikelData.csv', index=index, separator='_$_')
interface = classes.TkinterInterface('Artikels', index=index, database=artikelDB)

interface.runUI()