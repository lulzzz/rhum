angular.module("controllers", [])

// Basic Settings
.controller('DashCtrl', function($scope, $http, dashSettings, host_url) {
    $scope.Days = {name: "Days", value:1};
    $scope.getCSV = function () {
        window.open("http://" + host_url + "/logs/data-" + $scope.Days.value + ".csv");
        window.open("http://" + host_url + "/logs/data-" + $scope.Days.value + ".csv");
    }
    $scope.getJSON = function () {
        window.open("http://" + host_url + "/logs/data" + $scope.Days.value + ".json");
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
