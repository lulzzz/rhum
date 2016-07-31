angular.module("controllers", [])

// Dash Tab
.controller('DashCtrl', function($scope, $http, dashSettings, host_url) {
    $scope.saveLog = function () {
        window.open("http://"+host_url+"/logs/log.txt");
    }
})

// About Tab
.controller('AboutCtrl', function($scope, $http, aboutSettings, host_url) {
    $scope.saveLog = function () {
        window.open("http://"+host_url+"/logs/log.txt");
    }
});
