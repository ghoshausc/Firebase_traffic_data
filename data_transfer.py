import csv
import mysql.connector

# Connect to the MySQL server
cnx = mysql.connector.connect(user='root', password='LittleMoana1110!', host='localhost', database='project')
cursor = cnx.cursor()


#the CREATE table query to be mentioned :
#CREATE TABLE data (`DR Number` varchar(500), `Date Occurred` date, `Area Name` varchar(500), `Victim Age` float, `Victim Sex` varchar(20), `Victim Descent` varchar(100), `Address` varchar(1000), `Location` varchar(200), PRIMARY KEY(`DR Number`));

cursor.execute('DROP table if exists data')
cnx.commit()
cursor.execute('CREATE TABLE data (`DR Number` varchar(500), `Date Occurred` date, `Area Name` varchar(500), `Victim Age` float, `Victim Sex` varchar(20), `Victim Descent` varchar(100), `Address` varchar(1000), `Location` varchar(200), PRIMARY KEY(`DR Number`))')
cnx.commit()

# Open the CSV file and read its data
with open('p_data.csv') as csvfile:
    csvreader = csv.reader(csvfile)
    header = next(csvreader)  # read the header row
    for row in csvreader:

        # Create the SQL INSERT statement
        # print(row,type(row))
        # print('Row 2 has : ',row)
        array = row[1].split('/')
        # print('Values has : ',values[:2])
        if int(array[0])<10:
            row[1] = '20' + array[-1] + '-' + '0' + array[0] + '-' + array[1]
        # print(row[1])
        # break
        values = ', '.join([f'"{val}"' for val in row])
        try:
            query = f"INSERT INTO data VALUES ({values});"
            # query = f"INSERT INTO data ({', '.join(header)}) VALUES ({values});"
            # print('Query ******** ',query)
            # Execute the SQL INSERT statement
            cursor.execute(query)
        except:
            continue
        
# Commit the changes to the database
cnx.commit()

# Close the database connection
cnx.close()
