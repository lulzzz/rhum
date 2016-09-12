angular.module("controllers", [])

// Basic Settings
.controller('DashCtrl', function($scope, $http, dashSettings, host_url) {
    $scope.Days = {name: "Days", value:1};
    $scope.regenCSV = function () {
        $http.post("regen/" + $scope.Days.value, {}).then(function (res) {});
        alert( "Generating CSV for the past " + $scope.Days.value + " day(s)! This operation may take a moment.");
    }
    $scope.getCSV = function () {
        window.location = "http://" + host_url + "/logs/data-" + $scope.Days.value + ".csv";
    }
    $scope.getErrors = function () {
        window.location = "http://" + host_url + "/logs/errors.txt";
    }
    $scope.cleanDB = function () {
        $http.post("clean/" + $scope.Days.value, {}).then(function (res) {});
        alert( "Deleting data older than " + $scope.Days.value + " day(s)!");
    }
})

.controller('AboutCtrl', function($scope, $http, aboutSettings, host_url) {
    // No functions for About (yet)
});
