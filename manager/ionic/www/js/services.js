angular.module('services', [])

// Adavanced Settings Service
// change $http to $timeout for debug mode
.factory('advancedSettingsService', ['$http', '$q', 'host_url', function($http, $q, host_url) {
    var Service = {};
    console.log("http://" + host_url + "/config");

    Service.getAdvancedSettings = function(){
        var defer = $q.defer();

        // DO NOT ERASE
        //This is part that requests the data from the server. Below the commented out code is my mock of the data.
        $http({
            method: 'GET',
            url: "http://" + host_url + "/config",
            timeout: 3000
        }).then(function successCallback(response) {
            console.log(response);
            // this callback will be called asynchronously when the response is available
            defer.resolve([
                {name: "I_COEF", value: response.data["I_COEF"]},
                {name: "P_COEF", value: response.data["P_COEF"]},
                {name: "D_COEF", value: response.data["D_COEF"]},
                {name: "N_SAMPLES", value: response.data["N_SAMPLES"]},
                {name: "HUE_MIN", value: response.data["HUE_MIN"]},
                {name: "HUE_MAX", value: response.data["HUE_MAX"]},
                {name: "SAT_MIN", value: response.data["SAT_MIN"]},
                {name: "SAT_MAX", value: response.data["SAT_MAX"]},
                {name: "VAL_MIN", value: response.data["VAL_MIN"]},
                {name: "VAL_MAX", value: response.data["VAL_MAX"]},
                {name: "THRESHOLD_PERCENTILE", value: response.data["THRESHOLD_PERCENTILE"]},
                {name: "KERNEL_XY", value: response.data["KERNEL_XY"]}
            ]);
        }, function errorCallback(response) {
            // called asynchronously if an error occurs or server returns response with an error status.
            console.log(response);
            defer.resolve([
                {name: "I_COEF", value:1},
                {name: "P_COEF", value:4},
                {name: "D_COEF", value:0},
                {name: "N_SAMPLES", value:30},
                {name: "HUE_MIN", value:45},
                {name: "HUE_MAX", value:105},
                {name: "SAT_MIN", value:128},
                {name: "SAT_MAX", value:255},
                {name: "VAL_MIN", value:64},
                {name: "VAL_MAX", value:250},
                {name: "THRESHOLD_PERCENTILE", value:95},
                {name: "KERNEL_XY", value:3}
            ]);
        });

        return defer.promise;
    }
    return Service;
}])

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
