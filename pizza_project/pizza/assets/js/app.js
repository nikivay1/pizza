var app = angular.module('app', [
    'btford.modal',
    'angucomplete',
    'pascalprecht.translate'
]);

app
    .config(['$httpProvider', '$translateProvider', function($httpProvider, $translateProvider) {
        'use strict';
        $translateProvider
            .useSanitizeValueStrategy(null)
            .translations('ru', django.catalog)
            .preferredLanguage(current_language);
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    }])
    .constant('appSiteConfig', globalSettings)
    .directive('sliderSpecials', ['$timeout', function($timeout) {
        return {
            restrict: 'A',
            scope: {
                specials: '=',
                addToCart: '&'
            },
            templateUrl: 'slider_specials.html',
            link: function(scope, element) {
                if (!scope.results) {
                    scope.results = scope.specials;
                    $timeout(function () {
                        $(element[0]).slider();
                    }, 100);
                }
            }
        };
    }]);
