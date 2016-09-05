angular.module("controllers", [])

// Basic Settings
.controller('DashCtrl', function($scope, $http, dashSettings, host_url) {
    // set up all the sliders with the data grabbed from the server
    for(var i = 0; i < dashSettings.length; i++){
        console.log("dashSettings[" + i +"] = "+ dashSettings[i].name);
        if(dashSettings[i].name == "Days"){
            $scope.Days = {name: dashSettings[i].name, value:dashSettings[i].value};
        }
    }
    $scope.getCSV = function () {
        window.open("http://" + host_url + "/logs/data-" + $scope.Days.value + ".csv");
    }
    $scope.getJSON = function () {
        window.open("http://" + host_url + "/logs/data" + $scope.Days.value + ".json");
    }
})

.controller('AboutCtrl', function($scope, $http, aboutSettings, host_url) {
    $scope.VERBOSE = false;
    $scope.setVerbose = function() {
        if ($scope.VERBOSE == true) {
            $scope.VERBOSE = false;
        } else {
            $scope.VERBOSE = true;
        }
    }
    $scope.getErrors = function () {
        window.open("http://" + host_url + "/logs/errors.txt");
    }
});
