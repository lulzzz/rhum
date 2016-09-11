angular.module("controllers", [])

// Basic Settings
.controller('DashCtrl', function($scope, $http, dashSettings, host_url) {
    $scope.Days = {name: "Days", value:1};
    $scope.regenCSV = function () {
        $http.post("regen/" + $scope.Days.value, {}).then(function (res) {});
        alert( "Manager received request to generate CSV! This operation may take a moment.");
    }
    $scope.getCSV = function () {
        window.location = "http://" + host_url + "/logs/data-" + $scope.Days.value + ".csv";
    }
    $scope.getErrors = function () {
        window.location = "http://" + host_url + "/logs/errors.txt";
    }
})

.controller('AboutCtrl', function($scope, $http, aboutSettings, host_url) {
    // No functions for About (yet)
});
