import sqlite3

db = sqlite3.connect('Persons')

cursor = db.cursor()
cursor.execute('''SELECT * FROM persons''')

#user1 = cursor.fetchone() #retrieve the first row
#print(user1)

for i in cursor:
    print(i)
