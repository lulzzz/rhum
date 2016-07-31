angular.module("controllers", [])

// Basic Settings
.controller('DashCtrl', function($scope, $http, dashSettings, host_url) {
    $scope.getCSV = function () {
        window.open("http://" + host_url + "/logs/data.csv");
    }
    $scope.getJSON = function () {
        window.open("http://" + host_url + "/logs/data.json");
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
});
