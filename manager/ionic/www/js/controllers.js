angular.module("controllers", [])

// Basic Settings
.controller('DashCtrl', function($scope, $http, dashSettings, host_url) {
    $scope.Days = {name: "Days", value:1};
    $scope.getCSV = function () {
        setTimeout(function(){
            $http.post("regen/" + $scope.Days.value, {}).then(function (res) {});
        }, 5000);
        alert( "Manager received request to generate CSV! This operation may take a moment ...");
        window.location = "http://" + host_url + "/logs/data-" + $scope.Days.value + ".csv" + "?dummy=" + Math.floor(Math.random() * 10000);
    }
    $scope.getErrors = function () {
        window.location = "http://" + host_url + "/logs/errors.txt" + "?dummy=" + Math.floor(Math.random() * 10000);
    }
})

.controller('AboutCtrl', function($scope, $http, aboutSettings, host_url) {
    // No functions for About (yet)
});
