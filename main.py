#
# David Mendoza
# Analyzing CTA Daily Ridership, Fall 2021
#

import sqlite3
import matplotlib.pyplot as plt


##################################################################
#
# print_stats
#
# Given a connection to the CTA database, executes various
# SQL queries to retrieve and output basic stats.
#
def print_stats(dbConn):
    dbCursor = dbConn.cursor()

    print("General stats:")

    # basic count retrieval SQL queries
    dbCursor.execute("Select count(*) From Stations;")
    row = dbCursor.fetchone()
    print("  # of stations:", f"{row[0]:,}")

    dbCursor.execute("Select count(*) From Stops;")
    row = dbCursor.fetchone()
    print("  # of stops:", f"{row[0]:,}")

    dbCursor.execute("Select count(*) From Ridership;")
    row = dbCursor.fetchone()
    print("  # of ride entries:", f"{row[0]:,}")

    dbCursor.execute(  # date range
        "select min(date(Ride_Date)), max(date(Ride_Date)) from Ridership")
    row = dbCursor.fetchone()
    print("  date range:", row[0], "-", row[1])

    # total ridership
    dbCursor.execute("select sum(num_Riders) from Ridership")
    row = dbCursor.fetchone()
    total_riders = row[0]
    print("  Total ridership:", f"{row[0]:,}")

    # total riders from weekdays, Saturdays, and sunday/holidays
    dbCursor.execute(
        "select sum(num_Riders) from Ridership where Type_Of_Day = 'W';")
    row = dbCursor.fetchone()
    pct = round((row[0] / total_riders) * 100, 2)  # each column / total
    print("  Weekday ridership:", f"{row[0]:,}", "({}%)".format(pct))

    dbCursor.execute(
        "select sum(num_Riders) from Ridership where Type_Of_Day = 'A';")
    row = dbCursor.fetchone()
    pct = round((row[0] / total_riders) * 100, 2)
    print("  Saturday ridership:", f"{row[0]:,}", "({}%)".format(pct))

    dbCursor.execute(
        "select sum(num_Riders) from Ridership where Type_Of_Day = 'U';")
    row = dbCursor.fetchone()
    pct = round((row[0] / total_riders) * 100, 2)
    print("  Sunday/holiday ridership:", f"{row[0]:,}", "({}%)\n".format(pct))


#
# retrieve_stations
#
# retrieves station based on input search
#
def retrieve_stations(dbConn):
    print()
    name = input("Enter partial station name (wildcards _ and %): ")
    sql = "Select Station_ID, Station_Name from Stations where Station_Name like ? order by Station_Name asc"
    dbCursor = dbConn.cursor()
    rows = dbCursor.execute(sql, [name]).fetchall()
    if len(rows) == 0:  # no stations found:
        print("**No stations found...")
    else:
        for r in rows:
            print(r[0], ":", r[1])


#
# total_ridership
#
# cmd #2: outputs total ridership, and percentage of rides
def total_ridership(dbConn):
    dbCursor = dbConn.cursor()
    print("** ridership all stations **")
    sql = "select Station_Name, sum(Num_Riders) from Ridership inner join Stations on Ridership.Station_ID = Stations.Station_ID group by Station_Name order by Station_Name asc"
    rows = dbCursor.execute(sql).fetchall()
    total_riders = 0
    for r in rows:  # add up all riders
        total_riders = total_riders + r[1]

    rows = dbCursor.execute(sql).fetchall()
    for r in rows:  # each station's num Riders / total riders
        rounded_pct = round((r[1] / total_riders) * 100, 2)
        print(r[0], ":", "{:,}".format(r[1]), "({:.2f}%)".format(rounded_pct))


#
# top10_busiest
#
# cmd #3: outputs top 10 busiest stations
def top10_busiest(dbConn):
    print("** top-10 stations **")
    sql = "select Station_Name, sum(Num_Riders) from Ridership inner join Stations on Ridership.Station_ID = Stations.Station_ID group by Station_Name order by sum(Num_Riders) desc;"
    dbCursor = dbConn.cursor()
    rows = dbCursor.execute(sql).fetchall()
    total_riders = 0
    for r in rows:  # add up all riders
        total_riders = total_riders + r[1]

    sql10 = "select Station_Name, sum(Num_Riders) from Ridership inner join Stations on Ridership.Station_ID = Stations.Station_ID group by Station_Name order by sum(Num_Riders) desc limit 10;"
    rows = dbCursor.execute(sql10).fetchall()
    for r in rows:
        rounded_pct = round((r[1] / total_riders) * 100, 2)
        print(r[0], ":", "{:,}".format(r[1]), "({:.2f}%)".format(rounded_pct))


#
# least_busiest
#
# cmd #4: outputs 10 least busiest stations
def least_busiest(dbConn):
    print("** least-10 stations **")
    sql = "select Station_Name, sum(Num_Riders) from Ridership inner join Stations on Ridership.Station_ID = Stations.Station_ID group by Station_Name order by sum(Num_Riders);"
    dbCursor = dbConn.cursor()
    rows = dbCursor.execute(sql).fetchall()
    total_riders = 0
    for r in rows:  # add up all riders
        total_riders = total_riders + r[1]

    sql10 = "select Station_Name, sum(Num_Riders) from Ridership inner join Stations on Ridership.Station_ID = Stations.Station_ID group by Station_Name order by sum(Num_Riders) asc limit 10;"
    rows = dbCursor.execute(sql10).fetchall()
    for r in rows:
        rounded_pct = round((r[1] / total_riders) * 100, 2)
        print(r[0], ":", "{:,}".format(r[1]), "({:.2f}%)".format(rounded_pct))


#
# color_line
#
# cmd #5: outputs all stops that are part of inputted line
def color_line(dbConn):
    color = input("\nEnter a line color (e.g. Red or Yellow): ")
    dbCursor = dbConn.cursor()
    line_stations = dbCursor.execute(
        "select Stop_Name, direction, ADA from Lines inner join StopDetails on Lines.Line_ID = StopDetails.Line_ID inner join Stops on StopDetails.Stop_ID = Stops.Stop_ID where lower(color) = '"
        + color.lower() + "' order by Stop_Name asc;").fetchall()
    if len(line_stations) == 0:
        print("**No such line...")
    else:
        for l in line_stations:
            if l[2] == 1:
                access = "yes"
            elif l[2] == 0:
                access = "no"
            print(l[0], ": direction =", l[1],
                  "(accessible? {})".format(access))


#
# riders_by_month
#
# cmd #6: outputs total monthly ridership
def riders_by_month(dbConn):
    print("** ridership by month **")
    dbCursor = dbConn.cursor()
    sql = "select strftime('%m', Ride_Date) as Month, sum(num_Riders) from Ridership group by Month order by Month"
    monthNums = dbCursor.execute(sql).fetchall()
    x = []
    y = []

    for m in monthNums:  # allocate axes
        print(m[0], ":", "{:,}".format(m[1]))
        x.append(m[0])
        y.append(m[1])

    userInput = input("Plot? (y/n) ")
    if userInput == 'y':
        plt.clf()  # fresh plot
        plt.xlabel("month")  # x and y labels
        plt.ylabel("number of riders (x * 10^8)")
        plt.title("monthly ridership")
        plt.plot(x, y)
        plt.ion()
        plt.show()


#
# riders_by_year
#
# cmd #7: outputs total yearly ridership
def riders_by_year(dbConn):
    print("** ridership by year **")
    dbCursor = dbConn.cursor()
    sql = "select strftime('%Y', Ride_Date) as Year, sum(num_Riders) from Ridership group by year order by year asc"  # get years
    numYears = dbCursor.execute(sql).fetchall()
    x = []
    y = []

    for n in numYears:
        print(n[0], ":", "{:,}".format(n[1]))
        short_year = str(n[0])[2:]
        x.append(short_year)  # extracting last two digits of the year
        y.append(n[1])

    userInput = input("Plot? (y/n) ")
    if userInput == 'y':
        plt.clf()  # clear plot, fresh new plot
        plt.xlabel("year")
        plt.ylabel("number of riders (x * 10^8)")
        plt.title("yearly ridership")
        plt.plot(x, y)
        plt.ion()
        plt.show()


#
# searchStation
#
# helper function that returns none, 1, or multiple stations
def searchStation(dbConn, name):
    dbCursor = dbConn.cursor()
    sql = "Select Station_ID, Station_Name from Stations where Station_Name like '" + name + "' order by Station_Name asc"
    station = dbCursor.execute(sql).fetchall()
    return station


#
# print5Dates
#
# helper function that prints out first 5 and last 5 dates of the year
def print5Dates(dbConn, year, station):
    dbCursor = dbConn.cursor()
    dates = dbCursor.execute(
        "select date(Ride_Date), Num_Riders from Ridership where strftime('%Y', Ride_Date) = '"
        + year + "' and Station_ID = '" + str(station[0][0]) +
        "' group by Ride_Date order by Ride_Date asc;").fetchall()
    for i in range(0, 5):  # first 5 days of the year
        print(dates[i][0], dates[i][1])  # [i] is the day
    for i in range(-5, 0):  # last 5 days
        print(dates[i][0], dates[i][1])
    return dates


#
# first5last5
#
# cmd #8:
def first5last5(dbConn):
    yearInput = int(input("\nYear to compare against? "))
    if yearInput < 2001 or yearInput > 2021:
        return  # if year does not fall in data base range, quit
    year = str(yearInput)

    name1 = input("\nEnter station 1 (wildcards _ and %): ")
    station1 = searchStation(dbConn, name1)  # call search
    if len(station1) == 0:
        print("**No station found...")
        return
    elif len(station1) > 1:
        print("**Multiple stations found...")
        return

    name2 = input("\nEnter station 2 (wildcards _ and %): ")
    station2 = searchStation(dbConn, name2)
    if len(station2) == 0:
        print("**No station found...")
        return
    elif len(station2) > 1:
        print("**Multiple stations found...")
        return

    print("Station 1:", station1[0][0], station1[0][1])
    dates1 = print5Dates(dbConn, year, station1)

    x = []
    y1 = []
    dayCount = 0
    for d in dates1:
        dayCount = dayCount + 1  # used to get the x margin
        x.append(dayCount)  # automatically incremented by 50
        y1.append(d[1])  # station 1's num riders

    print("Station 2:", station2[0][0], station2[0][1])
    dates2 = print5Dates(dbConn, year, station2)

    y2 = []
    for d in dates2:
        y2.append(d[1])  # station 2 daily num riders
    userInput = input("\nPlot? (y/n) ")
    if userInput == 'y':
        plt.clf()
        plt.xlabel("day")
        plt.ylabel("number of riders")
        plt.title("riders each day of " + year)
        plt.plot(x, y1, y2)
        legend_drawn_flag = True  # legend key
        plt.legend([station1[0][1], station2[0][1]],
                   loc=0,
                   frameon=legend_drawn_flag)
        plt.ion()
        plt.show()


#
# line_plot
#
# cmd #9:
def line_plot(dbConn):
    dbCursor = dbConn.cursor()
    cta_lines = [
        "blue", "red", "green", "yellow", "pink", "brown", "purple",
        "purple-express", "orange"
    ]  # since analyzing CTA ridership, here is a list of all lines
    line_color = input("\nEnter a line color (e.g. Red or Yellow): ")
    color = line_color.lower()
    if cta_lines.count(color) == 0:  # color/line does not exist
        print("**No such line...")
        return
    else:  # get all stations from line
        stations = dbCursor.execute(
            """ select Station_Name, Latitude, Longitude from Lines join StopDetails on Lines.Line_ID = StopDetails.Line_ID join Stops on Stops.Stop_ID = StopDetails.Stop_ID join Stations on Stops.Station_ID = Stations.Station_ID where Color like ? group by Station_Name order by Station_Name ASC;""",
            [color]).fetchall()
        x = []
        y = []
        for s in stations:
            print(s[0], ": ({},".format(s[1]), "{})".format(s[2]))
            x.append(s[1])  # lat
            y.append(s[2])  # long

        userInput = input("\nPlot? (y/n) ")
        if userInput == 'y':
            plt.clf()
            image = plt.imread("chicago.png")
            xydims = [-87.9277, -87.5569, 41.7012,
                      42.0868]  # area covered by the map:
            plt.imshow(image, extent=xydims)

            plt.title(color + " line")
            #
            # color is the value input by user, we can use that to plot the
            # figure *except* we need to map Purple-Express to Purple:
            #
            if (line_color.lower() == "purple-express"):
                line_color = "Purple"  # color="#800080"

            for s in stations:
                plt.plot(s[2], s[1], "o", c=color)
            #
            # annotate each (x, y) coordinate with its station name:
            #
            for s in stations:
                plt.annotate(s[0], (s[2], s[1]))
            plt.xlim([-87.9277, -87.5569])
            plt.ylim([41.7012, 42.0868])
            plt.ion()
            plt.show()


##################################################################
#
# main
#
def main():
    print("** Welcome to CTA L analysis app **")
    print()

    dbConn = sqlite3.connect('CTA2_L_daily_ridership.db')

    print_stats(dbConn)

    cmd = input("\nPlease enter a command (1-9, x to exit): ")
    while cmd != 'x':
        if cmd == '1':
            retrieve_stations(dbConn)
        elif cmd == '2':
            total_ridership(dbConn)
        elif cmd == '3':
            top10_busiest(dbConn)
        elif cmd == '4':
            least_busiest(dbConn)
        elif cmd == '5':
            color_line(dbConn)
        elif cmd == '6':
            riders_by_month(dbConn)
        elif cmd == '7':
            riders_by_year(dbConn)
        elif cmd == '8':
            first5last5(dbConn)
        elif cmd == '9':
            line_plot(dbConn)
        else:
            print("**Error, unknown command, try again...")
        cmd = input("\nPlease enter a command (1-9, x to exit): ")


main()
#
# done
#
