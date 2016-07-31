angular.module('services', [])

// Basic Settings Service
.factory('dashSettingsService', ['$http', '$q', 'host_url', function($http, $q, host_url) {
    var Service = {};
    Service.getDashSettings = function(){
        var defer = $q.defer();
        $http({
            method: 'GET',
            url: "http://" + host_url + "/config",
            timeout: 3000
        }).then(function successCallback(response) {
            console.log(response);
        }, function errorCallback(response) {
            console.log(response);
        });
        return defer.promise;
    }
    return Service;
}])

// About Settings
.factory("aboutSettingsService", ["$http", "$q", "host_url", function($http, $q, host_url) {
    var Service = {};
    Service.getAboutSettings = function(){
        var defer = $q.defer();
        $http({
            method: 'GET',
            url: "http://" + host_url + "/config",
            timeout: 3000
        }).then(function successCallback(response) {
            console.log(response);
        }, function errorCallback(response) {
            console.log(response);
        });
        return defer.promise;
    }
    return Service;
}])
