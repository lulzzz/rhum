angular.module("controllers", [])

// Basic Settings
.controller('DashCtrl', function($scope, $http, dashSettings, host_url) {
    $scope.saveLog = function () {
        window.open("http://"+host_url+"/logs/log.txt");
    }
})

// Advanced Settings
.controller('advancedCtrl', function($scope, $http, advancedSettings, host_url) {
    $scope.saveLog = function () {
        window.open("http://"+host_url+"/logs/log.txt");
    }
})

.controller('AboutCtrl', function($scope, $http, aboutSettings, host_url) {
    $scope.VERBOSE = false;
    $scope.saveLog = function () {
        window.open("http://"+host_url+"/logs/log.txt");
    }
    $scope.setVerbose = function() {
        if ($scope.VERBOSE == true) {
            $scope.VERBOSE = false;
        } else {
            $scope.VERBOSE = true;
        }
    }
});
