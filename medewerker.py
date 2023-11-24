import classes

index = ('id', 'voornaam', 'achternaam', 'functie', 'geboortedatum', 'gebruikersnaam', 'wachtwoord')

medewerkerDB = classes.Database('./data/medewerkerData.csv', index=index, separator='_$_')
interface = classes.TkinterInterface('Medewerker', index=index, database=medewerkerDB)

interface.runUI()