angular.module('services', [])

// Basic Settings Service
.factory('dashSettingsService', ['$http', '$q', 'host_url', function($http, $q, host_url) {
    var Service = {};
    return Service;
}])

// About Settings
.factory("aboutSettingsService", ["$http", "$q", "host_url", function($http, $q, host_url) {
    var Service = {};
    return Service;
}])
