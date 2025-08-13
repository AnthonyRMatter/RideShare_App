import mysql.connector
from helper import helper
mydb = mysql.connector.connect(host = "localhost",
        user = "root",
        password = "MedhatMcCarthy101",
        auth_plugin = 'mysql_native_password',
        database = "RideShare")
print(mydb)

#create cursor obj to interact with mySQL
mycursor = mydb.cursor()
#create the DB
mycursor.execute("CREATE SCHEMA Deathify;")
#show the databases that exist in my local mySQL
mycursor.execute("SHOW DATABASES")
# for x in mycursor:
#     print(x)

riderQuery = '''
CREATE TABLE rider(
    riderID INTEGER NOT NULL PRIMARY KEY);
'''
#mycursor.execute(riderQuery);

driverQuery = '''
CREATE TABLE driver(
    driverID INTEGER NOT NULL PRIMARY KEY,
    rating FLOAT,
    driveMode BOOLEAN);
'''
#mycursor.execute(driverQuery);

ridesQuery = '''
CREATE TABLE rides(
    rideID INTEGER NOT NULL PRIMARY KEY,
    drop_off VARCHAR(280),
    pick_up VARCHAR(280),
    driverID INTEGER NOT NULL,
    riderID INTEGER NOT NULL);
'''
#mycursor.execute(ridesQuery);

def Fetch(query):
    mycursor.reset()
    mycursor.execute(query)
    record = mycursor.fetchone()
    return record

def Execute(query):
    mycursor.reset()
    mycursor.execute(query)
    mydb.commit()

def MainMenu():
    choice = int(input('''
    Here one of options:
    1) Current User
    2) New User
    '''))
    caseType = "None"
    if(choice == 1):
        userID = int(input("Enter your ID: "))
        if(userID % 2 == 0):
            caseType = "Rider"
        elif(userID % 2 == 1):
            caseType = "Driver"
        else:
            print("UserID not found, create a new user")
        Checker(caseType,userID)
    elif(choice == 2):
        User()

def Checker(caseType,userID):
    if(caseType == "Driver"):
        while True:
            optionsDrive = driverOptions()
            if(optionsDrive == 1):
                # turn drive mode on: updates a flag on their file that they are able to drive
                modeQuery = '''
                UPDATE driver
                SET driveMode = '1'
                WHERE driverID = '%s';
                ''' % userID
                Execute(modeQuery)
                print("You can now drive")
            elif(optionsDrive == 2):
                # turn drive mode on: updates a flag on their file that they are able to drive
                modeQuery = '''
                UPDATE driver
                SET driveMode = '0'
                WHERE driverID = '%s';
                '''% userID
                Execute(modeQuery)
                print("You are not able drive now")   
            else:
                print("Exit")
                break
     
    elif(caseType == "Rider"):
        while True:
            option = riderOptions()
            if option == 1:
                FindDriver(userID) #Implement this function
            elif option == 2:
                rating = float(input("Please enter your desired rating from 1 - 5: "))
                RateMyDriver(userID,rating) #Implement this function
            elif option == 3:
                print("Exit")
                break

# The user should be able to give their ID and you will determine whether they are a driver
# or a user (cannot be both for simplicity)
def User():
    while True:
        user = int(input('''
        What is your user?
        1) Driver
        2) Rider
        '''))
        if(user == 1):
            query = '''
            SELECT COUNT(*)
            FROM driver
            '''
            Count = Fetch(query)[0]
            ID = (Count + 1) * 2
            print("This is your ID: " + str(ID))

            query = '''
            INSERT INTO driver (driverID, driveMode)
            Values ('%s','0')
            ''' % ID
            Execute(query)
            caseType = "Driver"
            Checker(caseType, ID)
            break
        elif(user == 2):
            query = '''
            SELECT COUNT(*)
            FROM rider
            '''
            Count = Fetch(query)[0]
            ID = (Count + 1) * 2
            print("This is your ID " + str(ID))

            query = '''
            INSERT INTO rider (riderID)
            Values ('%s')
            ''' % ID
            Execute(query)
            caseType = "Rider"
            Checker(caseType, ID)
            break
        else:
            print("Type either 1 or 2")

def riderOptions():
    print('''
    Select from the following menu options:\n
    1) Find Driver\n
    2) Rate My Driver\n
    3) Exit
    ''')
    return helper.get_choice([1,2,3])

def driverOptions():
    print('''
    Select from the following options:\n
    1) Turn DriveMode On
    2) Turn DriveMode Off
    3) Exit
    ''')
    return helper.get_choice([1,2,3])

def ActiveDriver(userID):
    # matches them with a driver that has their drive mode on activated
    findDriverQuery = '''
    SELECT driverID
    FROM driver
    WHERE driveMode = '1'
    LIMIT 1;
    '''
    activeDriver = Fetch(findDriverQuery)
    return activeDriver

def FindDriver(userID):
    driver = ActiveDriver(userID)
    drop_off = input("Enter in a drop off address: ")
    pick_up = input("Enter in a pick up address: ")
    driverID = driver[0]
    rideID = GetRideID()

    query = '''
    INSERT INTO rides (rideID, drop_off, pick_up, driverID, riderID)
    Values ('%s','%s','%s','%s','%s');
    ''' % (rideID, drop_off, pick_up, driverID, userID)

    Execute(query)


def GetRideID():
    query = '''
    SELECT COUNT(rideID)
    FROM rides
    '''
    RideCount = Fetch(query)[0]
    if(RideCount == 0):
        return 1
    else:
        return(RideCount + 1)

def RateMyDriver(userID, rating):

    query = '''
    SELECT COUNT(*)
    FROM rides
    WHERE riderID = '%s';
    ''' % userID

    RecordTotal = Fetch(query)[0]

    while True:
        if(RecordTotal != 0):
            lastRideQuery = '''
            SELECT driverID
            FROM rides
            WHERE riderID = '%s'
            ORDER BY rideID DESC
            LIMIT 1;
            '''% userID

            lastRide = Fetch(lastRideQuery)

            if(lastRide == None):
                print("No ride has been recorded")
            else:
                lastDriverID = lastRide[0]
                
                update = updateRating(rating)
                updateDriverRating = '''
                UPDATE driver
                SET rating = '%s'
                WHERE driverID = '%s';
                ''' % (update, lastDriverID)
                Execute(updateDriverRating)
                break
        else:
            print("You have no records at the moment")
            break

def updateRating(rating):

    currentRatingQuery = '''
    SELECT rating
    FROM driver
    ORDER BY driverID DESC
    LIMIT 1;
    '''
    current = Fetch(currentRatingQuery)

    if(current[0] == None):
        return (float(rating)/ 2.0)
    else:
        newRating = (Fetch(currentRatingQuery)[0] + float(rating)) / 2.0

    return newRating

MainMenu()

mydb.close()
