import math
from re import LOCALE
import tkinter as tk
from tkinter import *
from tkinter import Listbox
from tkinter.ttk import Combobox
from tkinter import messagebox
from tkinter import simpledialog

window = Tk()
screenWidth = int(window.winfo_screenwidth())
screenHeight = int(window.winfo_screenheight())
canv = Canvas(window, width = screenWidth, height = screenHeight, bg = "#7dd0b6")
canv.pack()

class Buoy():

    def __init__(self):
        __buoyNum = 0
        __location = ""
        __waveHeight = 0
        __airTemp = 0
        __waterTemp = 0
        __humidity=0
        __rainfall=0
        __pastAirPressure = 0
        __currentAirPressure = 0
        __windDir = ""
        __windSpeed = 0
        __batteryHealth = 0

        self.statNamesTuple = ("buoyNum", "location", "waveHeight", "airTemp", "waterTemp", "humidity", "rainfall(mm)", "pastAirPressure", "currentAirPressure", "windDir", "windSpeed", "batteryHealth")

    def __getRawData_FromFile(self, fileName):
        rawData = []
        try:
            fileReader = open(fileName, 'r')
            rawData = fileReader.readlines()
            for line in rawData:
                line.rstrip() #rstrip() removes empty space characters from the end of the file, including newline characters
        except:
            raise Exception("The file you are trying to read from is invalid.")

        return rawData

    def __readStatsFromFile(self, fileName):
        rawData = self.__getRawData_FromFile(fileName)
        statNames = self.statNamesTuple

        correctFile = True
        idx = 0
        dataItems = {}

        while idx < len(rawData) and idx < len(statNames) and correctFile is True:
            name = statNames[idx]
            dataString = rawData[idx]
            #print("name {}, dataString {}".format(name, dataString)) #Debugging output statement
            if dataString.startswith(name) == False:
                correctFile = False
            else:
                end = len(dataString) -1 #Every line ends with a newline character which must be removed
                start = len(name)+1
                data = dataString[start:end]
                #print(data) #Debugging output statement
                dataItems.setdefault(name, data)

            idx += 1

        if correctFile == False:
            raise Exception("You are either reading from the wrong file or the file has been altered.")

        return dataItems

    def getLocationComponents(self, strLocation):
        location = []
        charIdx = 0
        while charIdx< len(strLocation):
            char = strLocation[charIdx]
            if char == ",":
                location = [strLocation[0:charIdx],strLocation[charIdx:] ]
            charIdx += 1

        if location == []:
            raise Exception("The location data has been tampered with.")

        return location

    def assignValuesToStats(self, fileName):
        #This has the precondition of the file being valid and the data matching exactly.
        #We can ensure this is the case if dataItems is not an empty list.
        dataItems = self.__readStatsFromFile(fileName)
        #print(dataItems) #debugging output statemet
        try:
            self.__buoyNum = int(dataItems.get("buoyNum"))
            self.__location = self.getLocationComponents(dataItems.get("location"))
            self.__waveHeight = float(dataItems.get("waveHeight"))
            self.__airTemp = float(dataItems.get("airTemp"))
            self.__waterTemp = float(dataItems.get("waterTemp"))
            self.__humidity = float(dataItems.get("humidity"))
            self.__rainfall = float(dataItems.get("rainfall(mm)"))
            self.__pastAirPressure = float(dataItems.get("pastAirPressure"))
            self.__currentAirPressure = float(dataItems.get("currentAirPressure"))
            self.__windDir = dataItems.get("windDir")
            self.__windSpeed = float(dataItems.get("windSpeed"))
            self.__batteryHealth = int(dataItems.get("batteryHealth"))
        except:
            raise Exception("There was an error assigning values.")

    def getMeasurement(self, statName):
        stat = 0
        if statName == "buoyNum":
            stat = self.getBuoyNum()
        elif statName == "location":
            stat = self.getLocation()
        elif statName == "waveHeight":
            stat = self.getWaveHeight()
        elif statName == "airTemp":
            stat = self.getAirTemp()
        elif statName == "waterTemp":
            stat = self.getWaterTemp()
        elif statName == "humidity":
            stat = self.getHumidity()
        elif statName == "rainfall(mm)":
            stat = self.getRainfall()
        elif statName == "pastAirPressure":
            stat = self.getPastAirPressure()
        elif statName == "currentAirPressure":
            stat = self.getCurrentAirPressure()
        elif statName == "windDir":
            stat = self.getWindDir()
        elif statName == "windSpeed":
            stat = self.getWindSpeed()
        elif statName == "batteryHealth":
            stat = self.getBatteryHealth()
        else:
            #The name of a stat is given that doesn't match the expected data
            raise Exception("An improper statistic name has been given.")

        return stat
        
    def getBuoyNum(self):
        return self.__buoyNum

    def getLocation(self):
        return self.__location

    def getWaveHeight(self):
        return self.__waveHeight

    def getAirTemp(self):
        return self.__airTemp

    def getWaterTemp(self):
        return self.__waterTemp

    def getHumidity(self):
        return self.__humidity

    def getRainfall(self):
        return self.__rainfall

    def getPastAirPressure(self):
        return self.__pastAirPressure

    def getCurrentAirPressure(self):
        return self.__currentAirPressure

    def getWindDir(self):
        return self.__windDir

    def getWindSpeed(self):
        return self.__windSpeed

    def getBatteryHealth(self):
        return self.__batteryHealth

class ReadFromBuoys():
    def __init__(self, season):
        self.season = season

        fileDetails = self.getFileDetails_FromSeason(season)
        pastFile = fileDetails[0]
        currentFiles = fileDetails[1]

        self.pastAverage = self.readPastData(pastFile)
        self.currentBuoysList = self.getListCurrentBuoys(currentFiles)
        currentBuoysList = self.currentBuoysList
        self.currentDataDict = self.getDictCurrentData(currentBuoysList)

    def getNumBuoys(self):
        numBuoys = 5
        return numBuoys

    def getFileDetails_FromSeason(self, season):
        pastDataLocation = "PastData/"
        currentDataLocation = "CurrentData/"
        pastFileName = pastDataLocation + season + "/" + "BuoyData24.txt"
        #retrieves files with the name: "PastData/<season>/BuoyData24.txt"
        #E.g. "PastData/DrySeason/BuoyData24.txt"
        currentFileNameStart = season + "/" + "Buoy"
        currentFileNameEnd = "_Data.txt"

        buoyIdx = 1
        numBuoys = self.getNumBuoys()
        currentFileNames = []

        while buoyIdx <= numBuoys:
            #retrieves files with the name: "CurrentData/<season>/Buoy<buoyIdx>_Data.txt"
            #E.g. "CurrentData/DrySeason/Buoy1_Data.txt"
            fileName = currentDataLocation + currentFileNameStart + str(buoyIdx) + currentFileNameEnd
            currentFileNames.append(fileName)
            buoyIdx += 1

        return (pastFileName, currentFileNames)

    def readPastData(self, fileName):
        #read from txt file for past data
        #The location of the 'buoy' for the past data is the exact latitude and longitude of Saibai Island
        pastAverage = Buoy()
        pastAverage.assignValuesToStats(fileName)
        return pastAverage

    def getListCurrentBuoys(self, fileNamesList):
        #get current data from txt file and store it as list of Buoy classes
        currentBuoys = [] #dummy data

        if len(fileNamesList) > 0:
            for fileName in fileNamesList:
                #print(fileName) #debugging output statement
                buoy = Buoy()
                buoy.assignValuesToStats(fileName)
                currentBuoys.append(buoy)
        else:
            raise Exception("There was an error reading the data.")

        return currentBuoys

    def getDictCurrentData(self, currentBuoysList):
        currentData = {}
        statNamesTuple = Buoy().statNamesTuple
        for statName in statNamesTuple:
            currentData.setdefault(statName, [])
        
        i = 0
        while i < len(statNamesTuple):
            statName = statNamesTuple[i]
            statsList = currentData.get(statName)

            for buoy in currentBuoysList:
                statsList.append(buoy.getMeasurement(statName))

            currentData.setdefault(statName, statsList)

            i += 1

        return currentData

class BuoyWeatherProcessor():

    def __init__(self):
        
        self.__pastData = []
        self.__currentBuoysList = []
        self.__currentData = {}

    def instantiateValues(self, season):

        if season == "Wet Season":
            season = "WetSeason"
        else:
            season = "DrySeason"

        BuoyData = ReadFromBuoys(season)
        
        self.__pastData = BuoyData.pastAverage
        self.__currentBuoysList = BuoyData.currentBuoysList
        self.__currentData = BuoyData.currentDataDict

    def getPastData(self):
        return self.__pastData
    
    def getCurrentData(self):
        return self.__currentData

    def getBuoysList(self):
        return self.__currentBuoysList

    def getIndividualBuoy(self, buoyNum):
        buoyNum -= 1
        buoy = self.__currentBuoysList[buoyNum]
        return buoy

    def calculateMean(self, data):
        sumData = 0
        for dataPoint in data:
            sumData += dataPoint

        return (sumData / len(data))

    def getMeanSquared(self, mean):
        meanSqrd = mean * mean
        return meanSqrd

    def calculateMean_SquaredValues(self, data):
        sumSquared = 0
        squaredDataVals = []
        for dataPoint in data:
            squaredDataVals.append(dataPoint * dataPoint)

        meanSqrdVals = self.calculateMean(squaredDataVals)
        return meanSqrdVals

    def calculateVariance(self, meanSqrd, meanSqrdVals):
        var_x = meanSqrdVals - meanSqrd
        #This uses the formula Var(x) = E(x^2) - E(x)^2
        return var_x

    def getStdDeviation_FromData(self, data):
        #This uses the formula that S^2 = Var(x), where S is the standard deviation and Var(x) is the variance.
        
        avg = self.calculateMean(data)
        avgSqrd = self.getMeanSquared(avg)
        meanSqrdVals = self.calculateMean_SquaredValues(data)
        var_x = self.calculateVariance(avgSqrd, meanSqrdVals)

        stdDeviation = math.sqrt(var_x)
        return stdDeviation

    def getStdDeviation_Data_AND_Mean(self, data, avg):
        #This uses the formula that S^2 = Var(x), where S is the standard deviation and Var(x) is the variance.
        
        avgSqrd = self.getMeanSquared(avg)
        meanSqrdVals = self.calculateMean_SquaredValues(data)
        var_x = self.calculateVariance(avgSqrd, meanSqrdVals)

        stdDeviation = math.sqrt(var_x)
        return stdDeviation

    def determineZScore(self, dataPoint, mean, stdDeviation):
        #This uses the formula that Z = (x - E(x)) / S, where E(x) is the mean, x is the data point being analysed, and S is the standard deviation. 
        z_score = (dataPoint - mean) / stdDeviation
        return z_score

    def calculateMedian(self, data):
        data.sort()
        
        medianIdx = 0
        median = data[0]
        length = len(data)
        partition = int(length / 2)
        
        if length % 2 == 0:
            
            lower_n = partition - 1
            higher_n = partition
            median = (data[lower_n] + data[higher_n] )/ 2
            medianIdx = (lower_n + higher_n) / 2
        else:
            median = data[partition]
            medianIdx = partition
        
        return median, medianIdx

    def alterMedianIdx(self, medianIdx):
        intIdx = int(medianIdx)
        
        if medianIdx > intIdx: #We know because of how the median is calculated above, if it is not an integer it will have a decimal value of 0.5.
            medianIdx = intIdx + 1

        return medianIdx

    def calculateQ1(self, Q2_idx, data):
        Q2_idx = self.alterMedianIdx(Q2_idx)
        Q1_data = self.calculateMedian(data[:Q2_idx])
        return Q1_data[0]

    def calculateQ3(self, Q2_idx, data):
        Q2_idx = self.alterMedianIdx(Q2_idx)
        if len(data) % 2 == 1:
            Q2_idx += 1
        Q3_data = self.calculateMedian(data[Q2_idx:])
        return Q3_data[0]

    def calculateIQR(self, Q1, Q3):
        return Q3 - Q1

    def determineHazardExtent(self, dataPoint, Q1, Q3, IQR):
        #If it is more than 1.3 over the IQR it is a potential hazard
        #DataPoint is single piece of data, either integer or floating point
        #Q3 + 1.5 * IQR and Q1 - 1.5 * IQR
        const = 1.5
        hazard = False
        higherQ3 = False

        highHazardExtent = (dataPoint - Q3) / IQR
        lowHazardExtent = (dataPoint - Q1) / IQR
        hazardExtent = 0

        if highHazardExtent >= const:
            hazardExtent = highHazardExtent
            hazard = True
            higherQ3 = True
        elif lowHazardExtent >= const:
            hazardExtent = lowHazardExtent
            hazard = True

        return (hazard, hazardExtent, higherQ3)

class StormDetermination():
    
    def __init__(self, buoy):
        self.airTemp = buoy.getAirTemp()
        self.humidity = buoy.getHumidity()
        self.windSpeed = buoy.getWindSpeed()
        self.windDir = buoy.getWindDir()
        self.pastAirPressure = buoy.getPastAirPressure()
        self.currentAirPressure = buoy.getCurrentAirPressure()

    def determineDewPoint(self, airTemp, humidity):
        #Use the formula to calculate dew point. Here we assume that the relative humidity is the same as the given humidity.
        #Given that our estimation for storm probability is relative, we use the shortcut formula:
        #Tdew = T - (100 - RH) / 5
        dewPoint =  airTemp - (100 - humidity) / 5

        return dewPoint

    def getLiftedIndex(self, seaLvlTemp, dewPoint):
        #The lifted index is a measure of the variability of weather. To calculate it we compare the temperature and
        #dew point at sea level, to that of a higher altitude.Given the fact that we are measuring temperature values 
        #at sea level, we do not need to make any adjustments.
         
        #Here we do not have a measurement from a higher altitude, and so we must calculate the lifted index by estimating
        #values for a higher altitude. We do this by calculating the LCL, or lifting condensation level, and then using
        #the LCL to get a higher temperature value.
        const = 125
        lcl = (seaLvlTemp - dewPoint) * const #The LCL is in metres. We must change it to be in km.

        malr = 6 #This is an estimate for the moist adiabatic lapse rate, the rate (in degrees/km) at which air cools as it rises above the LCL.
        maxAlt = 5.5 #The temperature of the air parcel at approximately 5.5km needs to be determined.
        lcl/= 1000
        t500 = -10 #This is the estimated temperature at 5500m above sea level
        deltaT = (maxAlt - lcl) * malr#measure the change in temperature above the LCL
        parcelTemp = seaLvlTemp - deltaT 

        liftedIndex = t500 - parcelTemp
        return liftedIndex

    def calculatePressureTendency(self, pastAirPressure, currentAirPressure):
        #Given that Saibai Island needs regular data, the time difference is restricted to 3 hours between air pressure measurements being sent.
        #Use formula: pt = (p2 - p1) / (t2 - t1)
        pressureTendency = currentAirPressure - pastAirPressure
        return pressureTendency

    def calculateWindSheer(self, groundWindSpeed):
        #Wind sheer is the change in wind speed with height. Strong wind sheer can indicate a storm approaching. To simplify calculations we are only insterested in
        #vertical wind sheer, which is calculated as (Vhigh - Vlow) / deltaZ, where deltaZ is the change in height. However, given we do not have a wind measurement 
        #from above the buoy, we must estimate wind sheer, through the formula V(z) = V0 * (z / z0) ^ alpha, where alpha is a constant between 0.10 and 0.20.
        
        referenceHeight = 1.5 #reference height 1.5 above sea level
        elevation = 500 #we can determine the wind speed at height 500m above sea level
        alpha = 0.15 #This value is empirically determined, and sits between 0.1 and 0.2.
        elevatedWindSpeed = groundWindSpeed * math.pow( (elevation / referenceHeight), alpha)
        windSheer = (elevatedWindSpeed - groundWindSpeed) / elevation
        
        return windSheer

    def determineStormLikelihood(self, dewPoint, liftedIndex, pressureTendency, windShear):
        #Here we combine measurements of dew point, lifted index, pressure tendency, and wind shear to heuristically determine the relative probability of a storm.
        stormLikelihood = ""
        if dewPoint > 70 and liftedIndex < -6.7 and pressureTendency > 2 and windShear > 20:
            stormLikelihood = "high"
        elif dewPoint > 60 and liftedIndex < -3.3 and pressureTendency > 1 or windShear > 10:
            stormLikelihood = "moderate"
        else: 
            stormLikelihood = "low"
        
        return stormLikelihood

    def checkStormHazard(self):
        airTemp = self.airTemp
        humidity = self.humidity
        pastAirPressure = self.pastAirPressure
        currentAirPressure = self.currentAirPressure
        windSpeed = self.windSpeed

        dewPoint = self.determineDewPoint(airTemp, humidity)
        liftedIndex = self.getLiftedIndex(airTemp, dewPoint)
        pressureTendency = self.calculatePressureTendency(pastAirPressure, currentAirPressure)
        windShear = self.calculateWindSheer(windSpeed)
        stormLikelihood = self.determineStormLikelihood(dewPoint, liftedIndex, pressureTendency, windShear)

        return stormLikelihood

class KingTideDetermination():

    def __init__(self, currentMeasurements, prevMeasurements, tideDeviation, windDeviation):
        self.seasonalTideHeight = prevMeasurements.getWaveHeight()
        self.measuredTideHeight = currentMeasurements.getWaveHeight()
        self.tideDeviation = tideDeviation
        self.windDir = currentMeasurements.getWindDir()
        self.windSpeed = currentMeasurements.getWindSpeed()
        self.windDeviation = windDeviation
        self.seasonalWindSpeed = prevMeasurements.getWindSpeed()
        self.location = currentMeasurements.getLocation()

        self.SaibaiLocation = ("-9.3999984*S","142.6833306*E")

    def getLatitudeAndLongitude(self, location):
        degSouth = location[0]
        degEast = location[1]

        locationVals = []
        locationVals.append(float( degSouth[0: (len(degSouth) - 2)] ))
        locationVals.append(float( degEast[1: (len(degEast) - 2)] ))

        return locationVals

    def getDiffLatitude(self, buoyLat, saibaiLat):
        return buoyLat - saibaiLat

    def getDiffLongitude(self, buoyLong, saibaiLong):
        return buoyLong - saibaiLong

    def checkNorthSouth(self, diffLatitude):
        val = "N"
        if diffLatitude > 0:
            val = "S"  

        return val

    def checkEastWest(self, diffLongitude):
        val = "E"
        if diffLongitude < 0:
            val = "W"

        return val

    def generalDirection(self, diffLatitude, diffLongitude):
        #Here we determine if the direction from the buoy to the island is North, South, East, or West.
        #The value for direction will be very generic because wind direction is impacted by changes in
        #topography, and, given that some buoys are close to PNG and other islands, it will be hard to
        #calculate the wind direction approaching Saibai from these buoys without more complex modelling.
        generalDirection = ""
        generalDirection = self.checkNorthSouth(diffLatitude) + self.checkEastWest(diffLongitude)

        return generalDirection

    def checkCharInString(self, charToFind, string):
        charInside = False
        for char in string:
            if char == charToFind:
                charInside = True
        return charInside

    def checkWindDirection(self, windDir, directionToIsland):
        pointingToIsland = False

        if directionToIsland == windDir:
            pointingToIsland = True
        else:
            if directionToIsland.startswith("N"):
                pointingToIsland = self.checkCharInString("N", windDir)
            else:
                pointingToIsland = self.checkCharInString("S", windDir)

        return pointingToIsland

    def checkHighTide(self, tideHeight, pastTideHeight, tideDeviation):
        highTide = False
        processor = BuoyWeatherProcessor()
        zScore = processor.determineZScore(tideHeight, pastTideHeight, tideDeviation)
        if zScore > 1:
            highTide = True
        return highTide

    def checkHighWind(self, windSpeed, pastWindSpeed, windDeviation):
        highSpeed = False
        processor = BuoyWeatherProcessor()
        zScore = processor.determineZScore(windSpeed, pastWindSpeed, windDeviation)
        if zScore > 0.5:
            highSpeed = True
        return highSpeed

    def checkWindOnShore(self, buoyLocation, windDir, windSpeed, pastWindSpeed, windDeviation):
        windOnShore = False
        saibaiLocation = self.SaibaiLocation
        
        saibaiLocationVals = self.getLatitudeAndLongitude(saibaiLocation)
        buoyLocationVals = self.getLatitudeAndLongitude(buoyLocation)

        diffLatitude = self.getDiffLatitude(buoyLocationVals[0], saibaiLocationVals[1])
        diffLongitude = self.getDiffLongitude(buoyLocationVals[0], saibaiLocationVals[1])
        directionToIsland = self.generalDirection(diffLatitude, diffLongitude)

        pointingToIsland = self.checkWindDirection(windDir, directionToIsland)
        highSpeed = self.checkHighWind(windSpeed, pastWindSpeed, windDeviation)

        if pointingToIsland is True and highSpeed is True:
            windOnShore = True

        return windOnShore

    def checkTidalHazard(self):
        hazardLikelihood = ""
        windDir = self.windDir
        windSpeed = self.windSpeed
        seasonalWindSpeed = self.seasonalWindSpeed
        windDeviation = self.windDeviation
        tideDeviation = self.tideDeviation
        buoyLocation = self.location
        seasonalTideHeight = self.seasonalTideHeight
        measuredTideHeight = self.measuredTideHeight

        windOnShore = self.checkWindOnShore(buoyLocation, windDir, windSpeed, seasonalWindSpeed, windDeviation)
        highTides = self.checkHighTide(measuredTideHeight, seasonalTideHeight, tideDeviation)

        if highTides is True and windOnShore is True:
            hazardLikelihood = "high"
        elif highTides is True or windOnShore is True:
            hazardLikelihood = "moderate"
        else:
            hazardLikelihood = "low"

        return hazardLikelihood

class UserInterface():
    def __init__(self, Main):
        global screenWidth
        global screenHeight
        
        eightWidth = int(screenWidth * 0.125)
        quarterWidth = 2 * eightWidth
        halfWidth = 2 * quarterWidth

        sixteenHeight = int(screenHeight * 0.0625)
        eightHeight = 2 * sixteenHeight
        quarterHeight = 2 * eightHeight
        halfHeight = 2 * quarterHeight

        listbox = self.getListBox("Hazard Information \n")
        listbox.place(x = halfWidth, y = eightHeight)

        seasons = ("Wet Season","Dry Season")
        seasonDropDown = self.createDropDown(0, seasons)
        seasonDropDown.place(x = quarterWidth, y = sixteenHeight)

        btnPastData = self.createButton("Get Previous Hazard Data")
        btnPastData.configure(command = lambda: self.handleButtonOnClick(Main, listbox, False, seasonDropDown.get()))
        btnPastData.place(x = quarterWidth, y = quarterHeight)

        btnCurrentData = self.createButton("Get Current Hazard Data")
        btnCurrentData.configure(command = lambda: self.handleButtonOnClick(Main, listbox, True, seasonDropDown.get()))
        btnCurrentData.place(x = quarterWidth, y = eightHeight)

        btnClearData = self.createButton("Clear Data")
        btnClearData.configure(command = lambda: self.clearListBox(listbox))
        btnClearData.place(x = quarterWidth, y = halfHeight - sixteenHeight )

        defaultLanguageIdx = 0
        languageOptions = ("English", "Torres Strait Pidgin", "Kalaw Kawaw Ya")
        languageDropDown = self.createDropDown(defaultLanguageIdx, languageOptions)
        languageDropDown.place(x = quarterWidth, y = quarterHeight + eightHeight)

    def getListBox(self, title):
        listbox = Listbox(window, width = 50, height = 20) 
        idx = 1
        listbox.insert(idx, title)
        return listbox

    def createButton(self, title):
        btn = Button(window, text = title, bg = "#75BFEC", height = 2)
        return btn

    def createDropDown(self, defaultIdx, options):
        dropDown = Combobox(window, values = options, state = "readonly")
        dropDown.current(defaultIdx)

        return dropDown

    def createLabel(self, lblText):
        lbl = Label(window, text = lblText, bg = "lightblue", height = 2)
        return lbl

    def handleButtonOnClick(self, Main, listbox, current, seasonChosen):
        Main.instantiateValues(seasonChosen)

        if current is True:
            self.currentDataWindow(Main, listbox)
        else:
            self.displayPastData(Main, listbox)

    def currentDataWindow(self, Main, listbox):
        startPos = 400
        endPos = 630
        dataWindow = canv.create_rectangle(startPos, startPos, endPos, endPos, fill = "#75BFEC")
        
        lblDataWindow = self.createLabel("Data Entry Options")
        lblDataWindow.place(x = startPos + 20, y = startPos + 20)

        lblSeasonInfo = self.createLabel("We are in the wet season")
        lblSeasonInfo.configure(bg = "#75BFEC")
        lblSeasonInfo.place(x = startPos + 50, y = startPos + 60)

        btnCloseWindow = self.createButton("X")
        btnCloseWindow.place(x = endPos - 20, y = startPos + 10)

        dataOptions = ("View individual buoy data", "View individual measurement", "Get hazard assessment")
        optionsDropDown = self.createDropDown(0, dataOptions)
        optionsDropDown.configure(width = 26)
        optionsDropDown.place(x = startPos + 50, y = startPos + 100)

        btnShowData = self.createButton("Show Current Data")
        btnShowData.configure(command = lambda: self.showData_AND_CloseWindow(optionsDropDown.get(), Main, listbox, windowItems, {"startPos":startPos, "endPos":endPos}))
        btnShowData.place(x = startPos + 50, y = startPos + 170)

        windowItems = [dataWindow, lblSeasonInfo, btnCloseWindow, lblDataWindow, optionsDropDown, btnShowData]
        btnCloseWindow.configure(command = lambda: self.destroyDataWindow(windowItems))

    def destroyDataWindow(self, windowItems):
        for item in windowItems:
            if type(item) == int:
                canv.delete(item)
            else:
                item.destroy()
        window.update()

    def showData_AND_CloseWindow(self, choice, Main, listbox, windowItems, windowCoords):
        dataToShow = ""

        pastData = Main.getPastData()
        buoyMeasurements = pastData.statNamesTuple

        hazardOptions = ("Storm Surge", "Tidal Flooding")

        if choice == "View individual buoy data":
            minValue = 1
            maxValue = 5
            
            buoyChosen = self.getValidChoice("Enter a buoy number from 1 to 5.", minValue, maxValue)
            self.currentData_IndividualBuoy(Main, listbox, buoyChosen)

        elif choice == "View individual measurement":
            msg = ""

            idx = 0
            count = 1
            length = len(buoyMeasurements) - 1
            while idx <  length:
                msg += "Enter " + str(count) + " for " + buoyMeasurements[idx] + "\n"
                idx += 1
                count = idx + 1

            msg += "Enter " + str(count) + " for " + buoyMeasurements[idx]

            minValue = 1
            maxValue = length + 2
            
            numChosen = self.getValidChoice(msg, minValue, maxValue)
            measurementChosen = buoyMeasurements[numChosen - 1]
            self.currentData_SpecificMeasurement(Main, listbox, measurementChosen)
        else:
            minValue = 1
            maxValue = 2
            hazards = ("Storm Surge", "Tidal Flood")
            hazardNum = self.getValidChoice("Enter 1 to get Storm Surge data. Enter 2 to get Tidal Flooding data.", minValue, maxValue)
            
            hazardChosen = hazards[hazardNum - 1]
            self.hazardWarning(Main, listbox, hazardChosen)

    def promptValidNumber(self, minValue, maxValue):
        messagebox.showerror(title = "Invalid Value Entered", message = "Please enter a number from {} to {}.".format(minValue, maxValue))

    def getValidChoice(self, textToDisplay, minValue, maxValue):
        valid = False
        numInputted = 0

        while valid is False:
            inputStr = simpledialog.askstring("", textToDisplay)
            try:
                numInputted = int(inputStr)
                if numInputted < minValue or numInputted > maxValue:
                    valid = False
                    self.promptValidNumber(minValue, maxValue)
                else:
                    valid = True
            except:
                valid = False
                self.promptValidNumber(minValue, maxValue)

        return numInputted

    def currentData_IndividualBuoy(self, Main, listbox, buoyNum):
        self.clearListBox(listbox)

        buoy = Main.getIndividualBuoy(buoyNum)
        statNames = buoy.statNamesTuple
        
        output = "Current data for buoy " + str(buoyNum) + "."
        pos = 1
        listbox.insert(pos, output)
        pos += 1
        output = ""
        listbox.insert(pos, output)
        pos += 1

        for name in statNames:
            unit = self.getUnit(name)
            output = name + ": " + str(buoy.getMeasurement(name)) + " " + unit
            listbox.insert(pos, output)
            pos += 1

        window.update()

    def currentData_SpecificMeasurement(self, Main, listbox, measurementChosen):
        self.clearListBox(listbox)

        output = "Current data for " + measurementChosen + "."
        pos = 1
        listbox.insert(pos, output)
        pos += 1
        output = ""
        listbox.insert(pos, output)

        currentData = Main.getCurrentData()
        dataGathered = currentData.get(measurementChosen)
        unit = self.getUnit(measurementChosen)

        buoyNum = 0
        for dataItem in dataGathered:
            pos += 1
            output = "Buoy " + str(buoyNum + 1) + ": " + str(dataItem) + " " + unit
            listbox.insert(pos, output)
            buoyNum += 1

        pos += 1
        output = ""
        listbox.insert(pos, output)
        pos += 1
        medianVals = Main.calculateMedian(dataGathered)
        median = medianVals[0]
        output = "Median value = " + str(median) + " " + unit
        listbox.insert(pos, output)

        window.update()

    def displayStormHazard(self, Main):
        hazardLvl = "low"
        buoysList = Main.getBuoysList()

        buoyIdx = 0
        while buoyIdx < len(buoysList) and hazardLvl == "low":
            buoy = buoysList[buoyIdx]
            storm = StormDetermination(buoy)
            hazardLvl = storm.checkStormHazard()

            buoyIdx += 1

        return hazardLvl

    def displayTidalHazard(self, Main):
        hazardLvl = "low"

        prevData = Main.getPastData()
        currentData = Main.getCurrentData()
        buoysList = Main.getBuoysList()

        tideData = currentData.get("waveHeight")
        windData = currentData.get("windSpeed")
        tideDeviation = Main.getStdDeviation_FromData(tideData)
        windDeviation = Main.getStdDeviation_FromData(windData)

        buoyIdx = 0
        while buoyIdx < len(buoysList) and hazardLvl == "low":
            buoy = buoysList[buoyIdx]
            kingTide = KingTideDetermination(buoy, prevData, tideDeviation, windDeviation)
            hazardLvl = kingTide.checkTidalHazard()
            
            buoyIdx += 1    

        return hazardLvl

    def hazardWarning(self, Main, listbox, hazardChosen):
        self.clearListBox(listbox)

        output = "Hazard Warning \n"
        pos = 1
        listbox.insert(pos, output)
        output = ""
        pos += 1
        listbox.insert(pos, output)

        hazardLvl = "" 

        if hazardChosen == "Storm Surge":
            hazardLvl = self.displayStormHazard(Main)
        else:
            hazardLvl = self.displayTidalHazard(Main)

        output = "Probability of " + hazardChosen + ": " + hazardLvl
        pos += 1
        listbox.insert(pos, output)

    def getUnit(self, measurementName):
        #If a piece of data doesn't have a unit, an empty string is returned
        unit = ""
        unitsDict = {"buoyNum":"", "location": "", "waveHeight":"m", "airTemp":"*C", "waterTemp":"*C", "humidity":"%", "rainfall(mm)":"mm", "pastAirPressure":"hpa", "currentAirPressure":"hpa", "windDir":"", "windSpeed":"km/h", "batteryHealth":"%"}
        unit = unitsDict.get(measurementName)
        return unit

    def displayPastData(self, Main, listbox):
        self.clearListBox(listbox)

        pastData = Main.getPastData()
        statNames = pastData.statNamesTuple

        output = "Previous Year's Data"
        pos = 1
        listbox.insert(pos, output)
        pos = 2
        listbox.insert(pos, "")

        for name in statNames:
            pos += 1
            output = name + ": " + str(pastData.getMeasurement(name)) + " " + self.getUnit(name)
            listbox.insert(pos, output)

        window.update()

    def clearListBox(self, listbox):
        listbox.delete(0, END)
        return listbox

if __name__ == '__main__':
    Main = BuoyWeatherProcessor()
    UserInterface(Main)

window.geometry(str(screenWidth) + "x" + str(screenHeight) + "+0+0")
window.configure(bg = "#7dd0b6")
window.title('Net Ninjas')
window.mainloop()
