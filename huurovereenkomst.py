import classes

index = ('id', 'medewerkerid', 'klantid', 'polisnummer', 'start datum', 'Tijdsduur (dagen)', 'artikelnum', 'aantal')

medewerkerDB = classes.Database('./huurovereenkomstData.csv', index=index, separator='_$_')
interface = classes.TkinterInterface('Huurovereenkomst', index=index, database=medewerkerDB)

interface.runUI()