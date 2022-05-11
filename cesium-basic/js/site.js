var site = (function() {
    var viewer;
    var countryFilter = [];
    var missionTypeFilter = [];
    var config = {};
    var regimes = ['LEO','HEO','MEO','GEO'];
    var czmlString = '';
    dataSource = new Cesium.CzmlDataSource()

    var _readConfig = function() {
        $.ajax({
            url: './Data/config.json',
            async: false,
            success: function(data) {
                config = data;
            }
        });
    };

    var _initCesium = function() {
        viewer = new Cesium.Viewer('cesiumContainer', {
            animation: true,
            fullscreenButton: true,
            baseLayerPicker: false,
            geocoder: false,
            timeline: true,
            navigationHelpButton: false,
            navigationInstructionsInitiallyVisible: false,
            imageryProvider: new Cesium.TileMapServiceImageryProvider({
                url: './node_modules/cesium/Build/Cesium/Assets/Textures/NaturalEarthII'
                //url: './lib/cesium/Build/Cesium/Assets/Textures/NaturalEarthII'
            })
        });
        toggleOrbitPaths();
        toggleLabels();
        initFilterWindow();
    };

    var _generateSatellites = function() {

        console.log("In Generate Satellites")

        var propagateURL = new URL("http://"+config.computerName+"/Propagate");
        var satListURL = new URL("http://"+config.computerName+"/SatList");

        var request = new XMLHttpRequest();
        request.open("GET", propagateURL, true);

        request.onreadystatechange = function() {
            console.log("In State change function")
            if (request.readyState === 4) {
                
                czmlString = request.response;
                console.log(czmlString)
                console.log("Ready State 4a")

                dataSource.load(czmlString)
                
                viewer.dataSources.add(dataSource)
                console.log("Added czml as a datasource to viewer")
            }
        };
        request.send(null);
        
        var x = document.getElementById("filterMenu");
        x.style.display = "block";

        populateOrbitRegimes();
    };

    var toggleOrbitPaths = function() {
        var orbitCheckbox = document.getElementById("Show Orbits");
        var k;

        orbitCheckbox.onchange = function() {
            console.log("Orbit Check Box Debug")
            if (orbitCheckbox.checked) {
                for (k = 0; k < dataSource.entities._entities._array.length; k++) {
                    dataSource.entities._entities._array[k].path = {
                        width: 2,
                        leadTime: 45 * 60,
                        trailTime: 45 * 60,
                        material: {
                            polylineOutline: {
                                color: {
                                    rgba: [
                                        255, 215, 0, 255
                                    ]
                                },
                                outlineColor: {
                                    rgba: [
                                        0, 0, 0, 255
                                    ]
                                },
                                outlineWidth: 1
                            }
                        }
                    };
                }
            } else {
                for (k = 0; k < dataSource.entities._entities._array.length; k++) {
                    dataSource.entities._entities._array[k].path = {};
                }
            }
        };
    };

    var toggleLabels = function() {
        var labelCheckbox = document.getElementById("Show Labels");
        var k;
        labelCheckbox.onchange = function() {
            console.log("Labels Check Box")
            if (labelCheckbox.checked) {
                for (k = 0; k < dataSource.entities._entities._array.length; k++) {
                    dataSource.entities._entities._array[k]._label.show = true
                    dataSource.entities._entities._array[k]._label.style = Cesium.LabelStyle.FILL_AND_OUTLINE
                    dataSource.entities._entities._array[k]._label.outlineWidth = 2
                    dataSource.entities._entities._array[k]._label.verticalOrigin = Cesium.VerticalOrigin.BOTTOM
                }
            } else {
                for (k = 0; k < dataSource.entities._entities._array.length; k++) {
                    dataSource.entities._entities._array[k]._label.show = false
                }
            }
        };
    };

    var initFilterWindow = function() {
        var x = document.getElementById("filterMenu");
        x.style.display = "none";
    };

    var populateOrbitRegimes = function() {
        var i;

        var parentDiv = document.getElementById("OrbitRegime");
        console.log("populateOrbitRegimes");

        for (i = 0; i < regimes.length; i++) {
            var div = document.createElement("div");
            div.className = "nowrap";

            var input = document.createElement("input");
            input.id = regimes[i];
            input.name = regimes[i];
            input.className = "checkboxes";
            input.type = "checkbox";
            input.checked = true;

            var label = document.createElement("label");
            var labelNode = document.createTextNode(regimes[i] + " Sats");
            label.appendChild(labelNode);

            div.appendChild(input);
            div.appendChild(label);
            parentDiv.appendChild(div);

            createListener(input, regimes[i], "orbitType");
        }
    };

    var createListener = function(checkbox, parameter, type) {
        checkbox.onchange = function() {
            var entities = dataSource.entities._entities._array;
            var i = 0;
            if (checkbox.checked) {
                for (i = 0; i < entities.length; i++) {
                    if (type == "orbitType") {
                        check = entities[i]._properties._OrbitType;
                    } else if (type == "missionType") {
                        check = entities[i].missionType;
                    } else {
                        check = entities[i].country;
                    }

                    if (check == parameter) {
                        entities[i].show = true;
                    }
                }
            } else {
                for (i = 0; i < entities.length; i++) {
                    if (type == "orbitType") {
                        check = entities[i]._properties._OrbitType;
                    } else if (type == "missionType") {
                        check = entities[i].missionType;
                    } else {
                        check = entities[i].country;
                    }

                    if (check == parameter) {
                        entities[i].show = false;
                    }
                }
            }
        };
    };

    return {
        readConfig: _readConfig,
        initCesium: _initCesium,
        generateSatellites: _generateSatellites,
    };

})();