from asyncore import read
import glob
import json
import re
import sys
import os

# assembly_path = r"C:\Users\kkonarkowski\Documents\docker\prop-docker\STKComponentsForDotNet2021r1\Assemblies"
assembly_path = r"./STKComponentsForDotNet2021r1/Assemblies"
sys.path.append(assembly_path)
sys.path

import clr
clr.AddReference("AGI.Foundation.Core")
clr.AddReference("AGI.Foundation.Cesium")
clr.AddReference("AGI.Foundation.Platforms")
clr.AddReference("AGI.Foundation.OrbitPropagation")

clr.AddReference('System.Drawing')
from System import DateTime
from System import Double
from System import String
from System.Drawing import Color
from System.IO import StringWriter
from System.IO import File
from System.IO import Path

from AGI.Foundation.Cesium import *
from AGI.Foundation.Cesium.Advanced import *
from AGI.Foundation.Propagators import Sgp4Propagator
from AGI.Foundation.Propagators import TwoLineElementSet
from AGI.Foundation.Celestial import CentralBodiesFacet
from AGI.Foundation import Licensing
from AGI.Foundation.Platforms import *
from AGI.Foundation.Geometry import AxesVehicleVelocityLocalHorizontal
from AGI.Foundation.Time import *

# Licensing.ActivateLicense("<License>" +
# "  <Field name='Name'>kkonarkowski</Field>" + 
# "  <Field name='Company'>AGI</Field>" +
# "  <Field name='AccountID'>26442</Field>" +
# "  <Field name='Source'>DevLics</Field>" +
# "  <Component name='Aircraft Propagation Library' />" +
# "  <Component name='Auto-Routing Library' />" +
# "  <Component name='Communications Library' />" +
# "  <Component name='Dynamic Geometry Library' />" +
# "  <Component name='Insight3D' />" +
# "  <Component name='Navigation Accuracy Library' />" +
# "  <Component name='Orbit Propagation Library' />" +
# "  <Component name='Radar Library' />" +
# "  <Component name='Route Design Library' />" +
# "  <Component name='Segment Propagation Library' />" +
# "  <Component name='Spatial Analysis Library' />" +
# "  <Component name='Terrain Analysis Library' />" +
# "  <Component name='Tracking Library' />" +
# "  <Component name='TIREM Library' />" +
# "  <Component name='Unifying Framework for Orchestration and Simulation' />" +
# "  <Component name='Moxie' />" +
# "  <Signature>GYkA7vA4PWe8vXjxzIeusdT+as4sF29RhmG+rWbSFAhPb6J0IJ21fZ1+ju++TvSQe4HUdUndWwVJux227Gp6SfCS3wmMM41odBla0qMJktvGSMKzem3ZdbtiRIMEdLthjg/UUhezqjO2bO8gGlINNhbdSCk5L4yr12+S21/rFAQ=</Signature>" +
# "</License>")

class Propagator:

    def __init__(self):
        self.tleFile = ''
        self.configFile = ''
        self.poiFile = ''
        self.satList = []
        self.useConfig = False
        self.outputFile = ''
        self.computerName = ''
        self.licenseFile = ''


    def _readConfig(self): 
        f = open('./Data/config.json')
        config = json.load(f)

        self.tleFile = config["tleFile"]
        self.outputFile = config["outputFile"]
        self.configFile = config["configFile"]
        self.poiFile = config["poiFile"]
        self.useConfig = False
        self.computerName = config["computerName"]
        self.licenseFile = config["licenseFile"]
        
        f.close()
        
        licenseFile_Open = open(self.licenseFile)
        licenseFile_Text = licenseFile_Open.read()
        print(licenseFile_Text)
        Licensing.ActivateLicense(licenseFile_Text)
        licenseFile_Open.close()

    def readTLEfile(self):
        
        self._readConfig()

        #print(self.tleFile)
        
        with open(self.tleFile) as f:
            tleData = f.readlines()
        # print(tleData)  
        return tleData

    def getSatList(self):
        
        tleData = self.readTLEfile()
        #print(int(len(tleData)/2))
        for x in range(int(len(tleData)/2)):
            
            line1 = tleData[2*x]
            line2 = tleData[2*x+1]
            curTLE = line1 + line2
            
            tle = TwoLineElementSet(curTLE)
            satName = tle.SatelliteNumber
            
            self.satList.append(satName)
        
        satListJSON = {"SatelliteList":self.satList}
        JSONstring = json.dumps(satListJSON)

        return JSONstring
        # return Propagator.satList

    def propagate(self):
        
        tleData = self.readTLEfile()
        satListJSON = self.getSatList()
        
        satListDic = json.loads(satListJSON)
        satList = satListDic["SatelliteList"]
        
        earth = CentralBodiesFacet.GetFromContext().Earth
        
        startTime = JulianDate(GregorianDate(DateTime.Now))
        stopTime = startTime.AddDays(1.0)
        interval = TimeInterval(startTime,stopTime)
        
        CzmlDoc = self.generateCZML(interval)
        satArray = []
        z = 0
        for x in range(int(len(tleData)/2)):
            
            line1 = tleData[2*x]
            line2 = tleData[2*x+1]
            curTLE = line1 + line2
            
            #print("this is TLE number", x+1)
            print(curTLE)
            #print("current Sat Name: ", satName)
            
            tle = TwoLineElementSet(curTLE)
            satName = tle.SatelliteNumber
            
            satPoint = Sgp4Propagator(tle).CreatePoint()
            satPoint_vel = satPoint.GetEvaluator().FirstDerivative
            satPoint_acc = satPoint.GetEvaluator().SecondDerivative

            orientationAxes = AxesVehicleVelocityLocalHorizontal(earth.FixedFrame, satPoint)
            curSat = Platform(satList[x],satPoint,orientationAxes)
            #print(Sgp4Propagator.ReferenceFrame())
            
            orbitType = self.getOrbitRegime(tle)
            print("Current orbit type: " + orbitType)
            
            cesiumOrbitType = ConstantCesiumProperty[String](orbitType)
            cesiumCustomProperty = CesiumCustomProperties()
            cesiumCustomProperty.AddCustomProperty[String]("OrbitType",cesiumOrbitType)
            cesiumOrbitTypePropertyExt = CesiumCustomPropertiesExtension(cesiumCustomProperty)
            
            curSat.Extensions.Add(cesiumOrbitTypePropertyExt)
            
            
            cesiumText = ConstantCesiumProperty[str](satName)
            cesiumFillColor = ConstantCesiumProperty[Color](Color.White)
            
            labelGraphics = LabelGraphics()
            labelGraphics.Text = cesiumText
            labelGraphics.Font = ConstantCesiumProperty[str]("15px sans-serif")
            labelGraphics.FillColor = cesiumFillColor
            labelGraphics.VerticalOrigin = ConstantCesiumProperty[CesiumVerticalOrigin]("Bottom")
            labelGraphics.Style = ConstantCesiumProperty[CesiumLabelStyle]("FillAndOutline")
            labelGraphics.OutlineWidth = ConstantCesiumProperty[Double](2.0)
            
            labelExtension = LabelGraphicsExtension(labelGraphics)
            
            curSat.Extensions.Add(labelExtension)

            color = ConstantCesiumProperty[Color](Color.White)
            #outlineWidth = ScalarCesiumProperty(1.0)
            #outlineColor = ConstantCesiumProperty[Color](Color.Black)

            #material = PolylineOutlineMaterialGraphics()
            material = SolidColorMaterialGraphics(ConstantCesiumProperty[Color](Color.White))
            #material.Color = color 
            #material.OutlineColor = outlineColor
            #material.OutlineWidth = outlineWidth
            
            pathGraphics = PathGraphics()
            #pathGraphics.Width = ScalarCesiumProperty(2.0)
            pathGraphics.LeadTime = ConstantCesiumProperty[Double](Duration.FromMinutes(0.0).TotalSeconds)
            pathGraphics.TrailTime = ConstantCesiumProperty[Double](Duration.FromMinutes(0.0).TotalSeconds)
            pathGraphics.Material = ConstantCesiumProperty[IPolylineMaterialGraphics](material)
            
            curSat.Extensions.Add(PathGraphicsExtension(pathGraphics))
            
            
            satArray.append(curSat)
            curSat = None
        
            
        for sat in satArray:
            CzmlDoc.ObjectsToWrite.Add(sat)
    
        return CzmlDoc
        print("Done Propagating Satellites")
    def generateCZML(self, interval):
        
        
        name = "TLE_Propagation"
        description = "CZML document containing propagated TLE data from all of the satellites contained in the input file."
        prettyFormatting = True
        requestedInterval = interval
        #print(interval)
        #print(interval.Start)
        clock = Clock()
        clock.Interval = interval 
        clock.CurrentTime = interval.Start
        
        CzmlDoc = CzmlDocument()
        CzmlDoc.Name = name
        CzmlDoc.Description = description
        CzmlDoc.PrettyFormatting = prettyFormatting
        CzmlDoc.RequestedInterval = requestedInterval
        CzmlDoc.Clock = clock
    
        print("Done generating the CZML Document")
        return CzmlDoc
        
    def getCZMLDoc(self):
    
        CzmlDoc = self.propagate()
    
        outputpath = self.outputFile
        writer_temp = File.CreateText(outputpath)
        CzmlDoc.WriteDocument(writer_temp)
        writer_temp.Close()
    
    
        #strwriter = StringWriter()
        #ouputStream = CesiumOutputStream(strwriter,False)
        
        #CzmlStream = CzmlDoc.WriteDocument(ouputStream)
        #CzmlData = strwriter.ToString()
        #strwriter.Close()
        
        print("Done Sending/Writing CZML string to Cesium")
        # return CzmlData
        return outputpath
    
    def getOrbitRegime(self,TLE):
    
        ecc = TLE.Eccentricity
        meanMotion = TLE.MeanMotion
        
        a = pow((8681663.653 / meanMotion),(2 / 3))
        
        hp = a * (1 - ecc) - 6371
        ha = a * (1 + ecc) - 6371
        
        if (ha < 2000):
            orbitType = 'LEO'
        elif (hp > (40164 - 6371) and ha < (44164 - 6371)):
            orbitType = 'GEO'
        elif (hp > 2000 and ha < (40164 - 6371)):
            orbitType = 'MEO'
        elif (hp < 2000 and ha > (40164 - 6371)):
            orbitType = 'GTO'
        else:
            orbitType = 'HEO'
            
        return orbitType
    
    # WIP
    # Adding feature to filter the TLE list to avoid duplicat TLEs and pick 
    # the one with the highest rev number (newest TLE)
    # WIP 
    def filterTLEList(self):
        
        tleData = self.readTLEfile()
        
        for x in range(int(len(tleData)/2)):
            # grab and split the second line of the TLE (SSC and rev)
            line1 = tleData[2*x]
            line2 = tleData[2*x+1]
            curTLE = line1 + line2
            print(curTLE)
            
            tle = TwoLineElementSet(curTLE)
            
            # indices = [i for i, x in enumerate(satNum) if x == z]

            # if len(indices) > 1:
            #     revInd = []
            #     revInds = indices(z)
            #     for aa in indices:
            #         print(aa)
            #         revInd.append(int(revNum[aa]))
                    
            #     maxRev = max(revInd)
            #     print(maxRev)
            #     print(revInd)
            #     keepInd = indices[revInd.index(maxRev)]
            #     dump = list(revInd)
            #     dump.pop()
            #     print(keepInd)
            #     print(revInd)
            #     #
        return 
    
        