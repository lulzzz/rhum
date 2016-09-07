angular.module("controllers", [])

// Basic Settings
.controller('DashCtrl', function($scope, $http, dashSettings, host_url) {
    $scope.Days = {name: "Days", value:1};
    $scope.setRange = function () {
        $http.post("regen", {range : $scope.Days.value}).then(function (res) {
            alert( "Load was performed!");
        });
    }
    $scope.getCSV = function () {
        window.location = "http://" + host_url + "/logs/data-" + $scope.Days.value + ".csv";
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
        window.location = "http://" + host_url + "/logs/errors.txt";
    }
});
