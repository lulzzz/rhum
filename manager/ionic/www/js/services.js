angular.module('services', [])

// Basic Settings Service
.factory('dashSettingsService', ['$http', '$q', 'host_url', function($http, $q, host_url) {
    var Service = {};

    Service.getDashSettings = function(){
        var defer = $q.defer();

        // DO NOT ERASE
        //This is part that requests the data from the server. Below the commented out code is my mock of the data.
        $http({
            method: 'GET',
            url: "http://" + host_url + "/config",
            timeout: 3000
        }).then(function successCallback(response) {
            console.log(response);
            // this callback will be called asynchronously
            // when the response is available
            defer.resolve([]);
        }, function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
            console.log(response);
            defer.resolve([]);
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
            method: "GET",
            url: "http://" + host_url + "/config",
            timeout: 3000
        }).then(function successCallback(response) {
            console.log(response);
            // this callback will be called asynchronously when the response is available
            defer.resolve([
                {name: "VERBOSE", value: response.data["VERBOSE"]}
            ]);
        }, function errorCallback(response) {
            // called asynchronously if an error occurs or server returns response with an error status.
            console.log(response);
            defer.resolve([
                {name: "VERBOSE", value: false}
            ]);
        });

        return defer.promise;
    }
    return Service;
}])
