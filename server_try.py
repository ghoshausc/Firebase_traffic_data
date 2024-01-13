# More details at: 
#     https://flask.palletsprojects.com/en/2.2.x/

#to open mysql from command prompt, first type cd /, then usr/local/mysql/bin/mysql -u root -p, enter password : LittleMoana1110!

from flask import Flask, jsonify, request
import mysql.connector
import json
import random
from mysql.connector import errorcode

# my MySQL connection details
db_config = {         #please change these values based on your MySQL details.
    'user': 'root',
    'password': 'LittleMoana1110!',
    'host': 'localhost',
    'database': 'project'
}

import json
from datetime import date


import json

app = Flask(__name__)


@app.route('/', defaults={'myPath': ''})
@app.route('/<path:myPath>', methods=['PUT'])
def catch_all_put(myPath):
    
    #configuring the database connection first.
    # Fetch data from MySQL database
    print("Inside PUT...")
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()
    
    # print("********** Request path is : ", request.full_path)
    
    print("********** Data is : ",request.get_data().decode('utf-8'))
    
    #for PUT as per the structure of my database, the valid command would be curl -X PUT 'http://localhost:8000/data.json' -d '{"DR Number":"AN34","Date Occurred":"2021-12-23","Area Name" :"Kudghat","Victim Age" : 34.09,"Victim Sex" : "F","Victim Descent" : "Bengali","Address" : "386A BP Road","Location": "(9,10)"}'
    
    #no orderBy or anything would be present because I don't have any nested node/child under the columns DR Number, Date Occurred. So will check if request.path + "?" == request.full_path
    #the ID column will be there in the URL like curl -X PUT -d '{"name":"John", "age":30, "city":"Los Angeles"}' 'https://<your-firebase-project>.firebaseio.com/data/3.json'

    #need to fetch the value of the primary key
    
    #splitting the path by a "/"
    mydict = dict()
    
    path = request.path
    key = ""
    
    #checking if PUT is in format curl -X PUT -d '{"103" : {"name":"John", "age":30, "city":"Los Angeles"}}' 'https://<your-firebase-project>.firebaseio.com/data.json}'. Plase note 103 has to be within double quotes and not '103'.
    
    array = path.split('/')[-1]
    print("Array is :",array)
    
    try:      #this means the key is specifid in data itself like curl -X PUT -d '{"103" : {"name":"John", "age":30, "city":"Los Angeles"}' 'https://<your-firebase-project>.firebaseio.com/data.json}'
        
        #need to get the key first
        if array == 'data.json':
            mydict = json.loads(request.get_data().decode('utf-8'))
            key = list(mydict.keys())[0]   #key fetched!

            print("Key is : ",key)
            # print("Mydict is : ",mydict)

            mydict = json.loads(request.get_data().decode('utf-8'))[key]
            print("Mydict when key in data is : ",mydict,type(mydict))

        else:         #in format curl -X PUT -d '{"name":"John", "age":30, "city":"Los Angeles"}' 'https://<your-firebase-project>.firebaseio.com/data/3.json}'

            key = path.split("/")[-1].replace(".json","")

            print("Key is : ",key)

            if not isinstance(key,str):
                key = key + ""

            mydict = json.loads(request.get_data().decode('utf-8'))
            print("Mydict when key not in data is : ",mydict,type(mydict))

        #first check if all keys(column names) are there in the database.
        sql_query = 'INSERT INTO data (`Dr Number`,' 

        #first the columns
        for each in list(mydict.keys()):
            # if ' ' in each:
            sql_query = sql_query + '`' + each + '`' + ","

        sql_query = sql_query[:-1]   #to remove the last ","
        sql_query = sql_query + ")" + " values (" + '"' + key + '"' + ","

        # print("insert sql query : ",sql_query)

        #now collecting values
        for each in list(mydict.keys()):

            print(mydict[each],type(mydict[each]))

            if mydict[each] == "":   #empty string
                sql_query = sql_query + "NULL,"
            elif isinstance(mydict[each],float) or isinstance(mydict[each],int):
                sql_query = sql_query + str(mydict[each]) + ","
            else:
                sql_query = sql_query + '"' + mydict[each] + '"' + ","

        sql_query = sql_query[:-1]   #to remove the last ","
        sql_query = sql_query + ")"

        sql_query = sql_query + ";"
        print("SQL query is : ",sql_query)   

        #now inserting this to the database
        cursor.execute(sql_query)
        db.commit()

        #creating the response object
        resp = {"database": request.url_root,
                "path": request.path,
                "full path": request.full_path,
                "data": request.get_data(),
                "data": request.get_data().decode('utf-8')}

    except json.JSONDecodeError as e:
        print(" except wrong format specified...")
        
        mydict = {"error" : "Invalid data; couldn't parse JSON object, array, or value. Perhaps you're using invalid characters in your key names."}
        
    except mysql.connector.Error as e:
        
        if e.errno == errorcode.ER_DUP_ENTRY:
        # Record already exists so now just update!
            #creating the update query
            
            #right from PATCH!
            
            print("************* Duplicate entry!")
            mydict = json.loads(request.get_data().decode('utf-8'))
            # print("Mydict is : ",mydict,type(mydict))
            
            #checking type if format is {key:{}} or just {key : }
            all_keys = list(mydict.keys())
            
            dr_number = all_keys[0]
            
            if '"' not in dr_number:
                dr_number = '"' + dr_number + '"'
            
            if isinstance(mydict[all_keys[0]],dict):
                mydict = mydict[all_keys[0]]
                                
            #create the UPDATE query
            update_sql_query = "UPDATE data set "
            intermediate_query = ""
            key = '"' + key + '"'

            for key,value in mydict.items():
                # if '"' not in key:
                #     key = '"' + key + '"'
                
                if isinstance(value,str) and '"' not in value:
                    value = '"' + value + '"'
                    
                print(key,"*********",value)

                if "Date Occurred" in key and value == '""':   #empty string passed as value
                    intermediate_query = intermediate_query + "`" + key + "`" + "=" + "NULL" + ","

                elif "Victim Age" not in key:     
                    intermediate_query = intermediate_query + "`" + key + "`" + "=" + value + ","

                else:    #these will be float values, not string
                    print("***************** Inside VICTIM AGE ELSE ********************",value)
                    if value and isinstance(value,int):
                        intermediate_query = intermediate_query + "`" + key + "`" + "=" + str(value) + ","
                    else:
                        intermediate_query = intermediate_query + "`" + key + "`" + "=" + "NULL" + ","

            intermediate_query = intermediate_query[:-1]
            update_sql_query = update_sql_query + intermediate_query + " where `DR Number` = " + dr_number + ";"
            print("Update SQL query is : ",update_sql_query)

            #updating on database
            cursor.execute(update_sql_query)
            db.commit()
            data = mydict
            
            
        else:   #other kinds of exceptions like maybe wring column name specified!
             print("Normal Exception!")
        
    except (ValueError, TypeError) as e:
        print("Normal Exception!")
#     return mydict
#     #check if number of rows increased in database
    
    
#     #PUT can also be used to update a record if the key actually exists in the database.
#     if '"' not in key:
#         key = '"' + key + '"'
        
#     put_update_query = "SELECT * from data where `DR Number` = " + key
#     cursor.execute(put_update_query) 
#     record = cursor.fetchall()
    
#     if record and len(record)!=0:   #record exists! so now update
#         #write later
#         pass
    
    resp = {"database": request.url_root,
            "path": request.path,
            "full path": request.full_path,
            "data": mydict}      #perfect! Firebase returns null when PUT fails. Otherwise will print the JSON string .
    
    return jsonify(resp['data'])

#now to delete

@app.route('/', defaults={'myPath': ''})
@app.route('/<path:myPath>', methods=['DELETE'])
def catch_all_delete(myPath):
    
    print("Inside DELETE..")
    #configuring the database connection first.
    # Fetch data from MySQL database
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()
    path = request.path
    full_path = request.full_path
    
    #fetch the value specified in path
    key_in_path = path.split("/")[-1]    #we cannot use orderBy/equalTo with DELETE, the valid DELETE command is : curl -X DELETE 'http://localhost:8000/data/"ANI34".json' where ANI34 is the key, as per my data this is the value of column DR Number.
    
    key_in_path = key_in_path.replace(".json","")
    
    if '"' not in key_in_path:
        key_in_path = '"' + key_in_path + '"'
    
    if not isinstance(key_in_path,str):
        key_in_path = '"' + key_in_path + '"'
        
    print("key in path is : ",key_in_path)
    #check number of rows in table
    cursor.execute("select COUNT(*) from data")
    data_before = cursor.fetchall()
    # print("Row count before: ",data)
        
    sql_delete_query = "DELETE from data where `DR Number`=" + key_in_path
    print("Column name and value specified : ",sql_delete_query)
    
    cursor.execute(sql_delete_query)
    data = cursor.fetchall()
    db.commit()
    
    #check number of rows after deletion in table
    cursor.execute("select COUNT(*) from data")
    data_after = cursor.fetchall()
    
    data = {"Status":"200"}
    
    if data_after<data_before:
        #print what Firebase prints when deletion successful
        print('Successful..')
    else:
        print("Error")   #check what Firebase prints when deletion is unsuccessful
        data = {"Status":"Error"}
    
    
    resp = {"database": request.url_root,
            "path": request.path,
            "full path": request.full_path,
            "data": data}      #perfect! Firebase returns null when DELETE doesn't work because no such record exists!
    
    return jsonify(resp['data'])


@app.route('/', defaults={'myPath': ''})
@app.route('/<path:myPath>', methods=['PATCH'])
def catch_all_patch(myPath):
    
    print("Inside PATCH..")
    #configuring the database connection first.
    # Fetch data from MySQL database
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()
    path = request.path
    full_path = request.full_path
    data = dict()
    
    #fetch the value specified in path
    key_in_path = path.split("/")[-1]    
    
    key_in_path = key_in_path.replace(".json","")

    
    if not isinstance(key_in_path,str):
        key_in_path = key_in_path + ""
        
    if '"' not in key_in_path:
        key_in_path = '"' + key_in_path + '"'
        
    try:
        mydict = json.loads(request.get_data().decode('utf-8'))
        print("Mydict is : ",mydict,type(mydict))


        #create the UPDATE query
        update_sql_query = "UPDATE data set "
        intermediate_query = ""

        for key,value in mydict.items():
            print(key,"*********",value)
            key = key.replace("%20"," ")

            if key!="Victim Age":     
                intermediate_query = intermediate_query + "`" + key + "`" + "=" + '"' + value + '"' + ","
            else:    #careful, these will be date/float values, not string, Date format : YYYY-MM-DD
                intermediate_query = intermediate_query + "`" + key + "`" + "=" + str(value) + ","

        intermediate_query = intermediate_query[:-1]
        update_sql_query = update_sql_query + intermediate_query + " where `DR Number` = " + key_in_path  + ";"
        print("Update SQL query is : ",update_sql_query)

        #updating on database
        cursor.execute(update_sql_query)
        db.commit()
        data = mydict
        
    except :
        data = {"error" : "Invalid data; couldn't parse JSON object. Are you sending a JSON object with valid key names?"}

    resp = {"database": request.url_root,
            "path": request.path,
            "full path": request.full_path,
            "data": data}      #perfect! Firebase returns null when DELETE doesn't work because no such record exists!
    
    return jsonify(resp['data'])


@app.route('/', defaults={'myPath': ''})
@app.route('/<path:myPath>', methods=['POST'])
def catch_all_post(myPath):
    
    print("Inside POST..")
    #configuring the database connection first.
    # Fetch data from MySQL database
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()
    path = request.path
    full_path = request.full_path
    data = dict()
    
    #sane as PUT
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()
    
    # print("********** Request path is : ", request.full_path)
    
    print("********** Data is : ",request.get_data().decode('utf-8'))
    
    #splitting the path by a "/"
    
    path = request.path
    mydict = dict()
    key = ""
    
    #First checking if the key is specified with the data
    
    key = "ANI" + str(random.randint(10,99))

    print("Key is : ",key)
    
    if request.path + "?" == request.full_path:    #no issues, valid PUT
    
        try:
            #to be inserted to database now
            mydict = json.loads(request.get_data().decode('utf-8'))
            print("Mydict is : ",mydict,type(mydict))

            #first check if all keys(column names) are there in the database.
            sql_query = 'INSERT INTO data (`Dr Number`,' 

            #first the columns
            for each in list(mydict.keys()):
                # if ' ' in each:
                sql_query = sql_query + '`' + each + '`' + ","

            sql_query = sql_query[:-1]   #to remove the last ","
            sql_query = sql_query + ")" + " values (" + '"' + key + '"' + ","


            #now collecting values
            for each in list(mydict.keys()):

                print(mydict[each],type(mydict[each]))
                if isinstance(mydict[each],float) or isinstance(mydict[each],int):
                    sql_query = sql_query + str(mydict[each]) + ","
                else:
                    sql_query = sql_query + '"' + mydict[each] + '"' + ","

            sql_query = sql_query[:-1]   #to remove the last ","
            sql_query = sql_query + ")"

            sql_query = sql_query + ";"
            print("SQL query is : ",sql_query)   

            # return None

            #now inserting this to the database
            try:
                cursor.execute(sql_query)
                db.commit()
                data = {"name":key}

                #creating the response object
                resp = {"database": request.url_root,
                        "path": request.path,
                        "full path": request.full_path,
                        "data": request.get_data(),
                        "data": request.get_data().decode('utf-8')}

            except:   #for the last try(SQL problem)!
                print("SQL error")  
            
        ####### there will be conditions when some data might have more colummns that that in database. Try to include support for that(Already done!). 
        
        except:
            data = {"error" : "Invalid data; couldn't parse JSON object, array, or value. Perhaps you're using invalid characters in your key names."}
    else:   #problem based on my JSON structure.
        
        # print("Wrong format specified...")
        data = {"error" : "Invalid data; couldn't parse JSON object, array, or value. Perhaps you're using invalid characters in your key names."}

    # print(type(jsonify(resp['data'])))
    
    # print(jsonify(resp['data']))
    
    resp = {"database": request.url_root,
            "path": request.path,
            "full path": request.full_path,
            "data": data}     
    
    return jsonify(resp['data']) 


@app.route('/', defaults={'myPath': '/'})
@app.route('/<path:myPath>', methods=['GET'])
def catch_all_get(myPath):
    # Fetch data from MySQL database
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()
    full_path = request.full_path
    path = request.path
    print('Pathh is : ',request.path)
    print('Full path is : ',full_path, type(full_path))
    full_path_copy = full_path
    sql_query = ""
    
    #Splitting both path and full_path by '/', if length is just 1 fine with the query below, else check if '?' present, if not error!
    json_data = ""
    path_array = path.split('/')
    full_path_array = full_path.split('/')
    print(len(path_array),len(full_path_array))
    
    
    #fetching the column names
    query = "SELECT * FROM data"
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]   #getting the column names from the database.
    data = cursor.fetchall()
    
    
    if path + "?" == full_path:         #No  query specified parameter..!
        
        print("No  query specified parameter..!")  #equivalent to select * from users
        
        #can have as simple as curl -X GET 'http://localhost:8000/data.json' or something like curl -X GET 'http://localhost:8000/data/nam.json', a specific column name, split by '/' and check if last position has only data.json
        
        
        array = path.split('/')
        if array[-1] == 'data.json':    #similar to curl -X GET 'http://localhost:8000/data.json'
        
            query = "SELECT * FROM data"   #CURL command : curl -X GET 'http://localhost:8000/data.json'
            cursor.execute(query)
            data = cursor.fetchall()
            db.close()
            print("Data is : ",data[1])

            for i,each in enumerate(data):
                each = list(each)
                data[i] = each
                print('Each is :',each)

                for index,each1 in enumerate(each):
                    if each1 and not isinstance(each1,str) and not isinstance(each1,float):
                        date_str = each1.strftime("%Y-%m-%d")
                        each[index] = date_str

                data[i] = each

            json_data = json.dumps(data)
            print("JSON data looks like : ",json_data)

            # Build response
            resp = {"database": request.url_root,
                    "path": request.path,
                    "full path": request.full_path,
                    "data": json_data}

            print("Length is : ",len(resp["data"]),type(resp['data']))
        
        else:    # a column name specified
            
            col = array[-1].replace(".json","").replace("%20"," ")
            
            try:   #possible SQL error!
                query = "SELECT `" + col + "` FROM data"   #CURL command : curl -X GET 'http://localhost:8000/data.json'
                cursor.execute(query)
                data = cursor.fetchall()
                db.close()
                # print("Data is : ",data[1])

                for i,each in enumerate(data):
                    each = list(each)
                    data[i] = each
                    # print('Each is :',each)

                    for index,each1 in enumerate(each):
                        if each1 and not isinstance(each1,str) and not isinstance(each1,float):
                            date_str = each1.strftime("%Y-%m-%d")
                            each[index] = date_str

                    data[i] = each

                json_data = json.dumps(data)
                print("JSON data looks like : ",data)

                # Build response
                # resp = {"database": request.url_root,
                #         "path": request.path,
                #         "full path": request.full_path,
                #         "data": json_data}

                # print("Length is : ",len(resp["data"]),type(resp['data']))

                myset = list()
                newstring = '{'

                for each in data:
                    if each and each[0]:
                        myset.append(str(each[0]) + ':' + '')
                        newstring = newstring + '"' + str(each[0]) + '"' + '\n'

                # print("Myset is : ",myset)
                return newstring
            
            except:
                return "null"

        # return None

    # if 'orderBy' in full_path or 'limitToFirst' in full_path or 'limitToLast' in full_path or 'startAt' in full_path or 'endAt' in full_path or 'print=pretty' in full_path: 
        
    else:     
        print("********* Inside else ************")
        
        if 'orderBy' in full_path or 'limitToFirst' in full_path or 'limitToLast' in full_path or 'equalTo' in full_path or 'startAt' in full_path or 'endAt' in full_path or 'print=pretty' in full_path:
            #we have sopme query parameters specifed.
            
            #fetching the columns from the database table.
            
            # query = "SELECT * FROM data"
            # cursor.execute(query)
            # columns = [column[0] for column in cursor.description]   #getting the column names from the database.
            # data = cursor.fetchall()
            # db.close()
            
            #steps : split by ?, check the last index of the left part.
            array_of_2_parts = full_path.split('?')
            left_part = array_of_2_parts[0]
            right_part = array_of_2_parts[-1]
            column_name = ""
            
            for each in columns:
                if each in left_part:
                    #this means a column name has been specified in the query. Get this column name to fetch the data
                    column_name = each
            
            print("Column name : ",column_name)
            if column_name!='':       #has to be printPretty for a valid query like curl -X GET 'http://local..../data/name.json?print=pretty'
                
                
                # if 'print=pretty' in right_part:
                #valid query, return the whole data from the table in JSON format
                sql_query = 'SELECT `' + column_name + '` from data;'   #equivalent to curl -X GET 'https://firebase_database_url/data/name.json?print=pretty' 

                cursor.execute(sql_query)
                data = cursor.fetchall()
                # db.close()
                # print("Date is : ",data[0][1])

                myset = list()
                newstring = '{'

                for each in data:
                    if each and each[0]:
                        myset.append(str(each[0]) + ':' + '')
                        newstring = newstring + '"' + str(each[0]) + '"' + '\n'

                # print("Myset is : ",myset)
                return newstring

                # Build response
                # resp = {"database": request.url_root,
                #         "path": request.path,
                #         "full path": request.full_path,
                #         "data": json_data}

                    # print("Length is : ",len(resp["data"]),type(resp['data']))

                    # return jsonify(resp['data'])
                    
                    
            else:   #coluymn name is empty string, so now check for orderBy,limitToFirst,limitToLast,equalTo,startAt,endAt
                
                #********** Firebase query looks like curl -X GET 'http>//local...../data.json?ordrBy="DR%20Number&startAt=4'
                sql_query = ""
                
                #All possible combinations
                
                
                            
                
                
                if 'orderBy' in full_path and 'limitToFirst' in full_path:
                    #write code
                    orderBystr = right_part.split('&')[0]
                    limitTostr = right_part.split('&')[-1]
                    
                    #extract column name for orderBy and number for limitToFirst
                    
                    print("Values are : ",orderBystr,limitTostr)
                    
                    column_name = orderBystr.split('orderBy=')[-1]
                    limit_value = limitTostr.split('limitToFirst=')[-1]
                    
                    print('Column name and limit value is : ',column_name, limit_value,type(column_name),type(limit_value))
                    
                    #writing the equivalent query
                    #SELECT * FROM <table_name> ORDER BY name ASC LIMIT 5;
                    column_name = column_name.replace('%20',' ')
                    column_name = column_name.replace('"','')
                    
                    try:    #for any possible SQL error
                        # if column_name!='Location':
                        sql_query = 'SELECT * from data ORDER BY ' + '`' + column_name + '`' + ' ASC LIMIT ' + limit_value

                        print("SQL query constructed is : ",sql_query)

                        #now fetching results from database.
                        cursor.execute(sql_query)
                        data = cursor.fetchall()

                        print("Date is : ",data[0][1])

                        for i,each in enumerate(data):
                            each = list(each)
                            data[i] = each
                            for index,each1 in enumerate(each):
                                if each1 and not isinstance(each1,str) and not isinstance(each1,float):
                                    date_str = each1.strftime("%Y-%m-%d")
                                    each[index] = date_str
                            data[i] = each

                        json_data = json.dumps(data)
                        
                    except:   #SQL error
                        data = {"error" : "Invalid data; couldn't parse JSON object, array, or value. Perhaps you're using invalid characters in your key names."}
                        
                        return "null"    
                    
                elif 'orderBy' in full_path and 'limitToLast' in full_path:
                    #write code
                    orderBystr = right_part.split('&')[0]
                    limitTostr = right_part.split('&')[-1]
                    
                    #extract column name for orderBy and number for limitToFirst
                    
                    print("Values are : ",orderBystr,limitTostr)
                    
                    column_name = orderBystr.split('orderBy=')[-1]
                    limit_value = limitTostr.split('limitToLast=')[-1]
                    
                    print('Column name and limit value is : ',column_name, limit_value,type(column_name),type(limit_value))
                    
                    #writing the equivalent query
                    #SELECT * FROM <table_name> ORDER BY name ASC LIMIT 5;
                    column_name = column_name.replace('%20',' ')
                    column_name = column_name.replace('"','')
                    
                    try:   #checking for any possible error
                        sql_query = 'SELECT * from data ORDER BY ' + '`' + column_name + '`' + ' DESC LIMIT ' + limit_value

                        print("SQL query constructed is : ",sql_query)

                        # print('Got columns : ',columns)
                        #now fetching results from database.
                        cursor.execute(sql_query)
                        data = cursor.fetchall()

                        print("Date is : ",data[0][1])

                        for i,each in enumerate(data):
                            each = list(each)
                            data[i] = each
                            for index,each1 in enumerate(each):
                                if each1 and not isinstance(each1,str) and not isinstance(each1,float):
                                    date_str = each1.strftime("%Y-%m-%d")
                                    each[index] = date_str
                            data[i] = each

                        json_data = json.dumps(data)
                    except:    #SQL error
                        return "null"
                    
                elif 'orderBy' in full_path and 'startAt' in full_path and 'endAt' not in full_path:
                    #write code
                    orderBystr = right_part.split('&')[0]
                    startAtstr = right_part.split('&')[-1]
                    
                    #extract column name for orderBy and number for startAt
                    
                    print("Values are : ",orderBystr,startAtstr)
                    
                    column_name = orderBystr.split('orderBy=')[-1]
                    startAt_value = startAtstr.split('startAt=')[-1]
                    
                    print('Column name and startAt value is : ',column_name, startAt_value,type(column_name),type(startAt_value))
                    
                    #writing the equivalent query
                    
                    #SELECT * FROM <table_name> WHERE score >= <START_VALUE> ORDER BY score ASC;

                    column_name = column_name.replace('%20',' ')
                    column_name = column_name.replace('"','')
                    
                    try:
                        sql_query = 'SELECT * from data WHERE ' + '`' + column_name + '`' + ">=" + startAt_value + ' ORDER BY ' + '`' + column_name + '`' + ' ASC;'

                        print("SQL query constructed is : ",sql_query)

                        # print('Got columns : ',columns)
                        #now fetching results from database.
                        cursor.execute(sql_query)
                        data = cursor.fetchall()
                        db.close()

                        # print("Date is : ",data[0][1])

                        for i,each in enumerate(data):
                            each = list(each)
                            data[i] = each
                            for index,each1 in enumerate(each):
                                if each1 and not isinstance(each1,str) and not isinstance(each1,float):
                                    date_str = each1.strftime("%Y-%m-%d")
                                    each[index] = date_str
                            data[i] = each

                        json_data = json.dumps(data)
                    except:
                        return "null"
                        
                elif 'orderBy' in full_path and 'endAt' in full_path and 'startAt' not in full_path:
                    #write code
                    
                    orderBystr = right_part.split('&')[0]
                    endAtstr = right_part.split('&')[-1]
                    
                    #extract column name for orderBy and number for startAt
                    
                    print("Values are : ",orderBystr,endAtstr)
                    
                    column_name = orderBystr.split('orderBy=')[-1]
                    endAt_value = endAtstr.split('endAt=')[-1]
                    
                    print('Column name and ndAt value is : ',column_name, endAt_value,type(column_name),type(endAt_value))
                    
                    #writing the equivalent query
                    
                    #SELECT * FROM <table_name> WHERE score <= <START_VALUE> ORDER BY score ASC;

                    column_name = column_name.replace('%20',' ')
                    column_name = column_name.replace('"','')
                    
                    if column_name!='Location':
                        sql_query = 'SELECT * from data WHERE ' + '`' + column_name + '`' + "<=" + endAt_value + ' ORDER BY ' + '`' + column_name + '`' + ' ASC;'

                        print("SQL query constructed is : ",sql_query)

                        # print('Got columns : ',columns)
                        #now fetching results from database.
                        cursor.execute(sql_query)
                        data = cursor.fetchall()
                        db.close()

                        # print("Date is : ",data[0][1])

                        for i,each in enumerate(data):
                            each = list(each)
                            data[i] = each
                            for index,each1 in enumerate(each):
                                if each1 and not isinstance(each1,str) and not isinstance(each1,float):
                                    date_str = each1.strftime("%Y-%m-%d")
                                    each[index] = date_str
                            data[i] = each

                        json_data = json.dumps(data)
                        
                elif 'orderBy' in full_path and 'startAt' in full_path and 'endAt' in full_path:
                    #write code
                    # print('Right part is : ',right_part)
                    orderBystr = right_part.split('&')[0]
                    startAtstr = right_part.split('&')[1]
                    endAtstr = right_part.split('&')[2]
                    
                    #extract column name for orderBy and number for startAt
                    
                    # print("Values are : ",orderBystr,startAtstr,endAtstr)
                    
                    column_name = orderBystr.split('orderBy=')[-1]
                    startAt_value = startAtstr.split('startAt=')[-1]
                    endAt_value = endAtstr.split('endAt=')[-1]
                    
                    print('Column name and ndAt value is : ',column_name, startAt_value, endAt_value,type(column_name),type(endAt_value),type(startAt_value))
                    
                    #writing the equivalent SQL query
                    
                    #SELECT * FROM <table_name> WHERE score >= <START_VALUE> AND score <= <END_VALUE> ORDER BY score ASC;

                    column_name = column_name.replace('%20',' ')
                    column_name = column_name.replace('"','')
                    
                    try:
                        sql_query = 'SELECT * from data WHERE ' + '`' + column_name + '`' + ">=" + startAt_value + ' AND ' + '`' + column_name + '`' + "<=" + endAt_value + ' ORDER BY ' + '`' + column_name + '`' + 'ASC;'

                        print("SQL query constructed is : ",sql_query)

                        # print('Got columns : ',columns)
                        #now fetching results from database.
                        cursor.execute(sql_query)
                        data = cursor.fetchall()
                        db.close()

                        # print("Date is : ",data[0][1])

                        for i,each in enumerate(data):
                            each = list(each)
                            data[i] = each
                            for index,each1 in enumerate(each):
                                if each1 and not isinstance(each1,str) and not isinstance(each1,float):
                                    date_str = each1.strftime("%Y-%m-%d")
                                    each[index] = date_str
                            data[i] = each

                        json_data = json.dumps(data)
                        
                    except:
                        return "null"
                    
                elif 'orderBy' in full_path and 'equalTo' in full_path:
                    #write code
                    orderBystr = right_part.split('&')[0]
                    equalTostr = right_part.split('&')[-1]
                    
                    #extract column name for orderBy and number for startAt
                    
                    print("Values are : ",orderBystr,equalTostr)
                    
                    column_name = orderBystr.split('orderBy=')[-1]
                    equalTo_value = equalTostr.split('equalTo=')[-1]
                    
                    print('Column name and equalTo value is : ',column_name, equalTostr,type(column_name),type(equalTo_value))
                    
                    #writing the equivalent query
                    
                    #SELECT * FROM <table_name> WHERE column_name = 'John';

                    column_name = column_name.replace('%20',' ')
                    column_name = column_name.replace('"','')
                    equalTo_value = equalTo_value.replace('%20',' ')
                    # equalTo_value = equalTo_value.replace('"','')
                    
                    
                    try:
                        sql_query = 'SELECT * from data WHERE ' + '`' + column_name + '`' + "=" + equalTo_value + ';'

                        print("SQL query constructed is : ",sql_query)

                        # print('Got columns : ',columns)
                        #now fetching results from database.
                        cursor.execute(sql_query)
                        data = cursor.fetchall()
                        db.close()

                        # print("Date is : ",data[0][1])

                        for i,each in enumerate(data):
                            each = list(each)
                            data[i] = each
                            for index,each1 in enumerate(each):
                                if not isinstance(each1,str) and not isinstance(each1,float):
                                    date_str = each1.strftime("%Y-%m-%d")
                                    each[index] = date_str
                            data[i] = each

                        json_data = json.dumps(data)
                        
                    except:
                        return "null"
        else:   
            data = {"error" : "Invalid data; couldn't parse JSON object, array, or value. Perhaps you're using invalid characters in your key names."}      #no orderBy or any query string specified hence invalid.
            
            return data
    db.close()
    
    print("SQL query : ",sql_query)
    #now formatting JSON data
    dict_of_JSON_data = dict()
    i = 1
    
    # print("Data is : ",data[:2])
    final_string = ""
    final_string_1 = ""
    
    print("Before response! ")
    if data:
        for each in data:
            # print("Each is : ",each)
            newdict = dict()
            for i in range(1,len(columns)):
                # print("Column and i are : ",columns[i],i)
                newdict[columns[i]] = each[i]
                i = i + 1
            dict_of_JSON_data[each[0]] = newdict
            # for key,value in newdict:
            final_string = final_string + json.dumps(newdict) + "\n\n"
    
    # print("Column name : ",column_name)
    # mydict = dict(sorted(dict_of_JSON_data.items(), key=lambda x: x[1]['Area Name']))
    
#     print(dict_of_JSON_data)
    
    # for key,v in dict_of_JSON_data.items():
    #     final_string_1 += key + "\n" + "  "
    #     for k,v1 in v.items():
    #         final_string_1 += k + " : " + v1 + "\n"
    
#     final_string = json.dumps(dict_of_JSON_data)
#     mydict = dict_of_JSON_data.copy()
    
    # Build response
    # resp = {"database": request.url_root,
    #         "path": request.path,
    #         "full path": request.full_path,
    #         "data": dict_of_JSON_data}
    
    return final_string


    #analyze the full path, 
    #copy the full path somewhere, replace the 'http://localhost:8000/' part by blank ''string.
    #now replace .json by '' blank string
    #now split the string by '/'
    #if length is 1 that means its equivalent to SQL query 'select * from table'.
    #if length is >1, then you check the values from 1, position 1 should be column name like users/name.json. This reponds to SQL query 'select name from table'
    
    #for lengths>1, position 2 should be a specific value mentioned under that column name like 'users/name/anindita.json'. Refer to noted for understanding the difference a child node and its value. In my database table, I don't have a child node 'anindita' under 'name' so this should return '404 not Found'.'
    
    #Also if someone wants to see the data of the user with name 'anindita', the Firebase equivalent CURL command will be : curl -X GET 'https://your-firebase-database-url/data.json?orderBy="name"&equalTo="anindita"' which referes to SQL query : select * from users where name='anindita'; In this specific case, using orderBy="name" makes sure that the results are ordered by the name attribute of each object in the data node. This is necessary because the equalTo parameter is filtering the results based on the value of the name attribute, so the results need to be ordered by the same attribute.

    # If you don't specify an orderBy parameter, the Firebase Realtime Database will return the results in an unspecified order, and the equalTo parameter may not work as expected. So, it's always a good practice to use orderBy in combination with equalTo when filtering data in Firebase Realtime Database using the REST API.
    

app.run(port=8000, debug=True)
app.run(debug=True)
