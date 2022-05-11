# STK Components / Cesium Visuals Containers #
STK Components TLE Propagation w/ Cesium Visualization in disperate containers

> Unofficial STK Components and Cesium Visualization Containers

![Visuals](https://github.com/TrainedTrex/crispy-memory/blob/main/Visuals.PNG)

## Prerequirements ##

This requires you to download the STK Components .NET Libraries under Developer Tools from [AGI Downloads](https://support.agi.com/downloads/3/) and obtain a license by contacting [AGI Support](mailto:support@agi.com).

If you would like the change the port number of the STK Components Container (Python Container), You must update the config.json with the new port number. 

## Inputs ## 

All the inputs are found in the \Data_Folder\ Folder. The Config.json specifies the location of the input (TLE) file, output file, config file, computerName, and license file. 

| **Flag** | **Value** |
| :----- | :----- |
| tleFile | location of the TLE File in the container |
| outputFile | location of the .czml output file in the container |
| configFile | NOT CURRENTLY USED: Location of the configfile.txt in the container |
| useConfig | sets whether the configFile.txt will be used |
| computerName | name of the computer and port number that is running the propagation (python) container |
| licenseFile | location of the .lic license File in the container |

## Build both images ## 

You will want to replace the Agi.Foundation.lic.PLACEHOLDER file in '\prop-docker\' with your STK Compoents license. 

Next you will want to unzip and move the STK Components for .NET folder into the \prop-docker\ folder, so the folder structure looks like \prop-docker\STKComponentsForDotNet2021r1. 

### Example build commands ### 

> Make sure to CD into each container directory before each build command

```docker 
docker build --tag python-prop .

docker build --tag node-cesium .
```
## Run the container ##

to run the containers

| **Flag** | **Value** |
| :----- | :----- |
| -p, --publish | <localport>:8080 |
| --name | desired container name |
| -v, --volume | <LocalFileLocation>/tleViewer-docker/Data_Folder:app/Data  |
| -d, --detach | Detatch process from Command Prompt or PowerShell |

### Example Run Command ###

```docker 
docker run -d --name cesium -v C:\Users\<UserName>\Documents\docker\tleViewer-docker\Data_Folder:/app/Data --publish 8080:8080 node-cesium

docker run -d --name propagator -v C:\Users\<UserName>\Documents\docker\tleViewer-docker\Data_Folder:/app/Data --publish 5000:5000 python-prop
```

## Testing ## 

Now that the containers are running it can be tested by going to both the python API and the Cesium front end

Go to: http://localhost:5000/ 
> This is the Propagator's homepage

Go to: http://localhost:5000/Propagate
> This will kick off the container to propagate the List of

Go to: http://localhost:8080
> This will display the customer Cesium frontend and will populate with TLE Data

## END ##

