import classes

index = ('id', 'voornaam', 'achternaam', 'straatnaam', 'huisnummer', 'postcode', 'woonplaats', 'geboortedatum')

klantDB = classes.Database('klantData.csv', index=index, separator='_$_')
interface = classes.TkinterInterface('Klanten', index=index, database=klantDB)

interface.runUI()