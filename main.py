#   Student: Divya Shah, dshah86, 655844407
#   Program 1: CTA Database App
#   Course: CS 341, Spring 2024
#   System: MacOS using PyCharm with SQL
# References: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.xticks.html, https://w3schools.com/python/matplotlib_plotting.asp, https://matplotlib.org/stable/users/explain/quick_start.html
# Cont. https://www.freecodecamp.org/news/connect-python-with-sql/, https://www.simplilearn.com/tutorials/sql-tutorial/sql-with-python
#TA: Krishna, Salvador, Navdeep

import sqlite3
import matplotlib.pyplot as plt
##################################################################
#
# print_stats
#
# Given a connection to the CTA database, executes various
# SQL queries to retrieve and output basic stats.
#

#This fucntion is printed at the start when the program is run without any input, it prints 5 stats, the stastions, the stops, number of ride entires and data range and finally total ridership
def print_stats(dbConn):
    dbCursor = dbConn.cursor()

    print("General Statistics:")
    # Number of stations
    dbCursor.execute("SELECT COUNT(*) FROM Stations;")
    numStations = dbCursor.fetchone()[0]
    print("  # of stations:", f"{numStations:,}")

    # Number of stops
    dbCursor.execute("SELECT COUNT(*) FROM Stops;")
    numStops = dbCursor.fetchone()[0]
    print("  # of stops:", f"{numStops:,}")

    # Number of ride entries
    dbCursor.execute("SELECT COUNT(*) FROM Ridership;")
    numEntries = dbCursor.fetchone()[0]
    print("  # of ride entries:", f"{numEntries:,}")

    # Data range
    dbCursor.execute("SELECT MIN(Ride_Date), MAX(Ride_Date) FROM Ridership;")
    minDate, maxDate = dbCursor.fetchone()
    minData = minDate.split()[0]
    maxData = maxDate.split()[0]
    print("  date range:", minData, "-", maxData)

    # Total ridership
    dbCursor.execute("SELECT SUM(Num_Riders) FROM Ridership;")
    ridership = dbCursor.fetchone()[0]
    print("  Total ridership:", f"{ridership:,}")

#This fucnction is used when the User wants to run command 1, it is called in main and it asks the user for an input which is the station name,
# based on the snippit it produces the station and if there is no station it says no station found.
def commandOne(dbConn):
    print()
    userInput = input("Enter partial station name (wildcards _ and %): ").strip()
    #print()
    dbCursor = dbConn.cursor()

    dbCursor.execute("SELECT Station_ID, Station_Name FROM Stations WHERE Station_Name LIKE ? ORDER BY Station_Name ASC;", (userInput,))
    matchingStations = dbCursor.fetchall()

    if matchingStations:
        for station_id, station_name in matchingStations:
            print(f"{station_id} : {station_name}")
    else:
        print("**No stations found...")

#This function is used when the User wants to run command 2, it is called in main and it asks the user for an input of a station name,
#Based on that it uses SQL queries that are similar to our HW ones to find the perctange of riders on weekdays, saturadays and sundays/hoildays,
# if the station has no riders then it says no data found and same if the station name was not found.
def commandTwo(dbConn):
    print()
    userInput2 = input("Enter the name of the station you would like to analyze: ").strip()
    dbCursor = dbConn.cursor()

    dbCursor.execute("SELECT Station_ID FROM Stations WHERE Station_Name = ?;", (userInput2,))
    stationID = dbCursor.fetchone()

    if stationID:
        stationID = stationID[0]

        # SQL querie similar to HW one to find ridership for weekdays, Saturdays, and Sundays/holidays
        dbCursor.execute("SELECT SUM(Num_Riders) FROM Ridership WHERE Station_ID = ? AND Type_of_Day = 'W';", (stationID,))
        weekdayCount = dbCursor.fetchone()[0]

        dbCursor.execute("SELECT SUM(Num_Riders) FROM Ridership WHERE Station_ID = ? AND Type_of_Day = 'A';", (stationID,))
        saturadayCount = dbCursor.fetchone()[0]

        dbCursor.execute("SELECT SUM(Num_Riders) FROM Ridership WHERE Station_ID = ? AND Type_of_Day = 'U';", (stationID,))
        sundayCount = dbCursor.fetchone()[0]

        dbCursor.execute("SELECT SUM(Num_Riders) FROM Ridership WHERE Station_ID = ?;", (stationID,))
        totalCount = dbCursor.fetchone()[0]

        if totalCount:
            weekdayPercent = (weekdayCount / totalCount) * 100
            satPercent = (saturadayCount / totalCount) * 100
            sunPercent = (sundayCount / totalCount) * 100
            print(f"Percentage of ridership for the {userInput2} station: ")
            print(f"  Weekday ridership: {weekdayCount:,} ({weekdayPercent:.2f}%)")
            print(f"  Saturday ridership: {saturadayCount:,} ({satPercent:.2f}%)")
            print(f"  Sunday/holiday ridership: {sundayCount:,} ({sunPercent:.2f}%)")
            print(f"  Total ridership: {totalCount:,}")
        else:
            print("**No data found...")
    else:
        print("**No data found...")

#This function is used when the user wants to check command 3, there is no other input that this fucntion takes
#Everytime this function is called it outputs the total riderships on the weekdays for each station and the perctange of riders per the total.
def commandThree(dbConn):
    dbCursor = dbConn.cursor()

    #SQL quere to find the total count for each station
    dbCursor.execute("""
        SELECT S.Station_Name, SUM(R.Num_Riders) AS Total_Ridership
        FROM Ridership R
        JOIN Stations S ON R.Station_ID = S.Station_ID
        WHERE R.Type_of_Day = 'W'
        GROUP BY S.Station_Name
        ORDER BY Total_Ridership DESC;
    """)

    weekdayRiders = dbCursor.fetchall()
    totalRidership = sum(row[1] for row in weekdayRiders)
    print("Ridership on Weekdays for Each Station")

    for station, ridership in weekdayRiders:
        riderPercent = (ridership / totalRidership) * 100
        print(f"{station} : {ridership:,} ({riderPercent:.2f}%)")


#This fucntion is called when the user wants to check command 4, this function is called in main with the while loop
#This function asks the user for a line color first and if that is a corret color then it asks the user for a direction, if there is a line with that color and diresction it will print all the stops and if they are/are not handicap accessible
#If either the line color or direction don't match then 1 of 2 messages will be printed and promt the user to restart with a command.
def commandFour(dbConn):
    print()
    dbCursor = dbConn.cursor()
    userInputColor = input("Enter a line color (e.g. Red or Yellow): ").lower()

    dbCursor.execute("SELECT Line_ID FROM Lines WHERE Color = ? COLLATE NOCASE;", (userInputColor,))
    line = dbCursor.fetchone()

    if line:
        userInputDirection = input("Enter a direction (N/S/W/E): ").upper()
        dbCursor.execute("""
            SELECT DISTINCT S.Stop_Name, S.Direction, S.ADA
            FROM Stops S
            JOIN StopDetails SD ON S.Stop_ID = SD.Stop_ID
            JOIN Lines L ON SD.Line_ID = L.Line_ID
            WHERE L.Color = ? COLLATE NOCASE AND S.Direction = ?
            ORDER BY S.Stop_Name ASC;
        """, (userInputColor, userInputDirection))

        stops = dbCursor.fetchall()
        if stops:
            for stop in stops:
                handicapStatus = "handicap accessible" if stop[2] else "not handicap accessible"
                print(f"{stop[0]} : direction = {stop[1]} ({handicapStatus})")
        else:
            print("**That line does not run in the direction chosen... ")
    else:
        print("**No such line... ")

#This function is used when the user calls command 5 in main, there is no other input to this funciton.
#When called it will print the number of stops for each color and direction in ascedning order and with the percentages
def commandFive(dbConn):
    #print("Hello")
    dbCursor = dbConn.cursor()
    counter = "SELECT COUNT(*) FROM STOPS"
    dbCursor.execute(counter)
    total = dbCursor.fetchone()

    dbCursor.execute("""
        SELECT Lines.Color, Stops.Direction, COUNT(Stops.Stop_ID) AS Num_Stops
        FROM Stops
        INNER JOIN StopDetails ON Stops.Stop_ID = StopDetails.Stop_ID
        INNER JOIN Lines ON StopDetails.Line_ID = Lines.Line_ID
        GROUP BY Lines.Color, Stops.Direction
        ORDER BY Lines.Color ASC, Stops.Direction ASC;
    """)

    colorStops = dbCursor.fetchall()
    if colorStops:
        totalStops = sum(row[2] for row in colorStops)
        print("Number of Stops For Each Color By Direction")
        for row in colorStops:
            color = row[0]
            direction = row[1]
            numStops = row[2]
            percentStops = (numStops / total[0]) * 100
            print(f"{color} going {direction} : {numStops} ({percentStops:.2f}%)")
    else:
        print("**No data found...")

#This function is called when the user calls command 6, there is an input to this fucntion which is a station name
#Given the station name it will output the total ridership for that year, also is using the same funcitoalilty at command 1
#The user also has the option to plot a graph after the data is printed, if yes is selected then a line graph will apear that shows the data.
def commandSix(dbConn): #Produce the correct output and graph, autograder shows incorrect
    print()
    userInput6 = input("Enter a station name (wildcards _ and %): ")
    dbCursor = dbConn.cursor()

    dbCursor.execute("SELECT Station_Name FROM Stations WHERE Station_Name LIKE ?;", (userInput6,))
    matchStation = dbCursor.fetchall()

    if not matchStation:
        print("**No station found...")
    elif len(matchStation) > 1:
        print("**Multiple stations found...")
    else:
        stationName = matchStation[0][0]
        dbCursor.execute("""
            SELECT strftime('%Y', Ride_Date) AS Year, SUM(Num_Riders) AS Total_Ridership
            FROM Ridership
            WHERE Station_ID = (
                SELECT Station_ID FROM Stations WHERE Station_Name LIKE ?
            )
            GROUP BY Year
            ORDER BY Year ASC;
        """, (userInput6,))

        yearlyCount = dbCursor.fetchall()
        print(f"Yearly Ridership at {stationName}")
        for year, ridership in yearlyCount:
            print(f"{year} : {ridership:,}")

        #This is the plot asecpt of the function, this is where Matpoltlib is used and the data from above is graphed
        plot6 = input("Plot? (y/n) ").lower()
        if plot6 == 'y':
            years = [int(year) for year, _ in yearlyCount]
            ridership = [ridership for _, ridership in yearlyCount]

            plt.figure(figsize=(10, 6))
            plt.plot(years, ridership, color='b', linestyle='-')
            plt.title(f"Yearly Ridership at {stationName} Station")
            plt.xlabel("Year")
            plt.ylabel("Number of Ridership")
            plt.xticks(range(2001, 2022))
            plt.grid(True)
            plt.show()

#This function is called when the user calls command 7, there is an input to this fucntion which is a station name and year
#Given the station name and year it will output the total ridership for that year by month, also is using the same funcitoalilty at command 1
#The user also has the option to plot a graph after the data is printed, if yes is selected then a line graph will apear that shows the data.
def commandSeven(dbConn):
    print()
    userInput7 = input("Enter a station name (wildcards _ and %): ")
    dbCursor = dbConn.cursor()

    dbCursor.execute("SELECT Station_Name FROM Stations WHERE Station_Name LIKE ?;", (userInput7,))
    matchStations = dbCursor.fetchall()

    if len(matchStations) == 0:
        print("**No station found...")
        return
    elif len(matchStations) > 1:
        print("**Multiple stations found...")
        return

    stationName = matchStations[0][0]
    yearInput = input("Enter a year: ")

    #SQL quere for this function that finds the station data for the year/month given.
    dbCursor.execute("""
        SELECT strftime('%m/%Y', Ride_Date) AS Month, SUM(Num_Riders) AS Total_Ridership
        FROM Ridership
        WHERE Station_ID IN (
            SELECT Station_ID FROM Stations WHERE Station_Name LIKE ?
        ) AND strftime('%Y', Ride_Date) = ?
        GROUP BY Month
        ORDER BY Month ASC;
    """, (userInput7, yearInput))

    monthly_ridership = dbCursor.fetchall()
    print(f"Monthly Ridership at {stationName} for {yearInput}")
    for month, ridership in monthly_ridership:
        print(f"{month} : {ridership:,}")

    plot7 = input("Plot? (y/n) ").strip().lower()
    if plot7 == 'y':
        months = [month.split('/')[0] for month, _ in monthly_ridership]
        ridership = [ridership for _, ridership in monthly_ridership]

        plt.figure(figsize=(10, 6))
        plt.plot(months, ridership, color='b', linestyle='-')
        plt.title(f"Monthly Ridership at {stationName} Station ({yearInput})")
        plt.xlabel("Month")
        plt.ylabel("Number of Ridership")
        plt.grid(True)
        plt.show()

#This fucntion is called in main when the user entieres command 8, this fucntion asks the uesr for 2 stations and a year and outputs the ridership for each day.
#We cut off the days at 5 from the start so the frist 5 days and 5 from the back so the last 5 days for each station, the user will also have the option to plot the data
#If the user enters a station that has multiple stations or no station depending on the name then there are statments to take care of that and the user will be promted to enter a new command and start over
#This fucntion also uses part of function 1 where the user can enter SQL wildcards (_ and %) for each station name, same as 1,6,7.
#This fucntion also has 2 helper functions, 1 to print the data in the specfifed order based on the pdf and 1 for plotting.
def commandEight(dbConn):
    print()
    year = input("Year to compare against? ")
    print()
    station1Name = input("Enter station 1 (wildcards _ and %): ")

    dbCursor = dbConn.cursor()
    dbCursor.execute("SELECT Station_ID, Station_Name FROM Stations WHERE Station_Name LIKE ?;", (station1Name,))
    station1 = dbCursor.fetchone()

    if station1 is None:
        print("**No station found...")
        return

    oneId = station1[0]
    dataName1 = station1[1]

    checkStation1 = dbCursor.execute("SELECT COUNT(*) FROM Stations WHERE Station_Name LIKE ?;", (station1Name,)).fetchone()[0] > 1
    if checkStation1:
        print("**Multiple stations found...")
        return

    print()
    station2Name = input("Enter station 2 (wildcards _ and %): ")

    dbCursor.execute("SELECT Station_ID, Station_Name FROM Stations WHERE Station_Name LIKE ?;", (station2Name,))
    station2 = dbCursor.fetchone()

    if station2 is None:
        print("**No station found...")
        return

    twoId = station2[0]
    dataName2 = station2[1]

    checkStation2 = dbCursor.execute("SELECT COUNT(*) FROM Stations WHERE Station_Name LIKE ?;", (station2Name,)).fetchone()[0] > 1
    if checkStation2:
        print("**Multiple stations found...")
        return

    # SQL queries to find the data there are 2 different ones for each station which helps with the plotting, gotten from lecture slides
    sql1 = f"""
        SELECT Ride_Date, SUM(Num_Riders)
        FROM Ridership
        WHERE strftime('%Y', Ride_Date) = ? AND Station_ID = ?
        GROUP BY Ride_Date
        ORDER BY Ride_Date;
    """
    sql2 = f"""
        SELECT Ride_Date, SUM(Num_Riders)
        FROM Ridership
        WHERE strftime('%Y', Ride_Date) = ? AND Station_ID = ?
        GROUP BY Ride_Date
        ORDER BY Ride_Date;
    """

    #Following code is for the data from above and for the plotting, the vector aspect is found through lecture slides.
    dbCursor.execute(sql1, (year, oneId))
    data1 = dbCursor.fetchall()

    dbCursor.execute(sql2, (year, twoId))
    data2 = dbCursor.fetchall()

    y1 = [row[1] for row in data1]
    y2 = [row[1] for row in data2]

    #Helper for printing
    print(f"Station 1: {oneId} {dataName1}")
    printDataFunction(data1[:5])
    printDataFunction(data1[-5:])
    print(f"Station 2: {twoId} {dataName2}")
    printDataFunction(data2[:5])
    printDataFunction(data2[-5:])

    print()
    plot8 = input("Plot? (y/n) ").lower()
    if plot8 == 'y':
        #helper for plotting
        plotFunctionCommand8(y1, y2, dataName1, dataName2, year)

#Command 8 helper fucntion thats prints the data point in the correct format
def printDataFunction(data):
    for row in data:
        ride_date = row[0].split()[0]
        print(f"{ride_date} {row[1]}")

#Command 8 helper function that is used for plotting, when the user selects yes to plot it jumps to this fucnction and then plots.
def plotFunctionCommand8(y1, y2, name1, name2, year):
    plt.figure(figsize=(10, 6))
    plt.plot(y1, color='blue', label=name1)
    plt.plot(y2, color='orange', label=name2)
    plt.title(f"Ridership Each Day of {year}")
    plt.xlabel("Day")
    plt.ylabel("Number of Riders")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

#This fucntion is called in main when the user enteris command 9, this fucntion asks the user for latitude and longitude, there are failure checks in place depnding on the data range
# Using the given data point it will find the stations withina mile raidus, there is also an option to plot. The plot uses the chicago.png which is in my folder for program 1.
def commandNine(dbConn):

    print()
    latitude = float(input("Enter a latitude: "))
    if not (40 <= latitude <= 43):
        print("**Latitude entered is out of bounds...")
        return

    longitude = float(input("Enter a longitude: "))
    if not (-88 <= longitude <= -87):
        print("**Longitude entered is out of bounds...")
        return

    latitudeRange = (round(latitude - (1 / 69), 3), round(latitude + (1 / 69), 3))
    longitudeRange = (round(longitude - (1 / 51), 3), round(longitude + (1 / 51), 3))

    dbCursor = dbConn.cursor()
    dbCursor.execute("""
        SELECT DISTINCT Stations.Station_Name, Stops.Latitude, Stops.Longitude 
        FROM Stops 
        JOIN Stations ON Stops.Station_ID = Stations.Station_ID
        WHERE Stops.Latitude BETWEEN ? AND ? AND Stops.Longitude BETWEEN ? AND ?
        ORDER BY Stations.Station_Name
    """, (latitudeRange[0], latitudeRange[1], longitudeRange[0], longitudeRange[1]))

    stations = dbCursor.fetchall()

    if stations:
        print()
        print("List of Stations Within a Mile")
        for station in stations:
            print(f"{station[0]} : ({station[1]}, {station[2]})")
    else:
        print("**No stations found...")
        return

    print()
    plot_input = input("Plot? (y/n) ")
    if plot_input.lower() == 'y':
        image = plt.imread("chicago.png")
        plt.imshow(image, extent=[-87.9277, -87.5569, 41.7012, 42.0868])

        for station in stations:
            plt.plot(station[2], station[1], 'o', color='blue')
            plt.annotate(station[0], (station[2], station[1]))

        plt.title("Stations Near You")
        plt.xlim([-87.9277, -87.5569])
        plt.ylim([41.7012, 42.0868])
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.tight_layout()
        plt.show()

##################################################################
#
# main
#
# Main program
#This is my main, only thing in here is teh while loop which keesp track of the user command inputs, based on the command it jumps to the spefic fucntion.
print('** Welcome to CTA L analysis app **')
print()

dbConn = sqlite3.connect('CTA2_L_daily_ridership.db')
print_stats(dbConn)
print()

# Command loop
while True:
    command = input("Please enter a command (1-9, x to exit): ").strip()
    #print()
    if command == 'x':
        dbConn.close()
        break
    elif command == '1':
        commandOne(dbConn)
        # print()
    elif command == '2':
        commandTwo(dbConn)
        #print()
    elif command == '3':
        commandThree(dbConn)
        # print()
    elif command == '4':
        commandFour(dbConn)
        # print()
    elif command == '5':
        commandFive(dbConn)
        # print()
    elif command == '6':
        commandSix(dbConn)
        # print()
    elif command == '7':
        commandSeven(dbConn)
        # print()
    elif command == '8':
        commandEight(dbConn)
        # print()
    elif command == '9':
        commandNine(dbConn)
        # print()
    else:
        print("**Error, unknown command, try again...")
        # print()
    print()
#
# done
#
