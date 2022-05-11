# TLE Propagator Containers Setup

# CD to directory of folder
$ cd C:\Users\<USERNAME>\Documents\tleViewer-docker\prop-docker\

# Build Image

docker build --tag python-prop .

# Run Container using image that was just built
$ docker run -dit --name propagator -v C:\Users\<USERNAME>\Documents\tleViewer-docker\TLE_Folder:/app/Data --publish 5000:5000 python-prop
	
# Run options
	- dit: disconnected (can use powershell while container is running)
	- v: sets up Bind moutn between host machine folder and container (used so you can update the TLE file and look at the czml)
	- publish: publish port so you can see output

# GO to: http://localhost:5000/
	- you should see the words "This is the Propagators homepage" 
# Go to: http://localhost:5000/SatList
	- you should see the list of satellites from the TLE file as a JSON
# Go to: http://localhost:5000/Propagate
	- Should see the container directory that the czml file is being returned to. 
	- Also is being returned to the mapped host machine dir specified in the docker run command
	- Open the CZML file and see that all the satellites are in there, CZML is in human readable format. 