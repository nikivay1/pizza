app
    .factory('catalogFactory', ['$http', '$location', function ($http, $location) {

        function getProducts(page) {
            var searchData = angular.extend($location.search(), {page: page || 1});
            return $http.get('/api/catalog/products?' + angular.element.param(searchData)).then(
                function (response) {
                    return response.data;
                }
            );
        }

        function getActionProducts() {
            return $http.get('/api/catalog/products/actions').then(
                function (response) {
                    return response.data;
                }
            );
        }

        return {
            getProducts: getProducts,
            getActionProducts: getActionProducts
        };
    }])
    .factory('cartFactory', ['$http', 'modalFactory', function ($http, modalFactory) {
        'use strict';

        function getTotalPrice(cart) {
            var total = 0, length = cart.items.length;
            for (var i = 0; i < length; i++) {
                total += cart.items[i].amount * cart.items[i].price.price;
            }
            return total;
        }

        function getItemPrice(item) {
            return item.price.price * item.amount;
        }

        function getTotalCount(cart) {
            var total = 0, length = cart.items.length;
            for (var i = 0; i < length; i++) {
                total += cart.items[i].amount;
            }
            return total;
        }

        function getCart() {
            return $http.get('/api/cart/').then(
                function (response) {
                    var cart = response.data;
                    if (cart.order) {
                        if (cart.order.address && cart.order.address.phone)
                            cart.order.address.phone = cart.order.address.phone.replace('+', '');
                    }
                    if (cart.order && cart.user) {
                        if (cart.order.address && cart.order.address.phone)
                            cart.order.address.phone = cart.order.address.phone.replace('+', '');
                        if (cart.order.address && !cart.order.address.phone)
                            cart.order.address.phone = cart.user.phone.replace('+', '');
                        if (cart.order.address && !cart.order.address.username)
                            cart.order.address.username = cart.user.first_name;
                    }
                    if (cart.empty_location) {
                        modalFactory.locationDialog.activate();
                    }
                    return response.data;
                }
            )
        }

        function updateAmountItem(itemId, amount) {
            return $http.put('/api/cart/item/' + itemId, {amount: amount}).then(
                function (response) {
                    return response.data;
                }
            );
        }

        function addProduct(priceId) {
            return $http.post('/api/cart/add', {price: priceId}).then(
                function (response) {
                    return response.data;
                }
            )
        }

        function removeProduct(itemId) {
            return $http.delete('/api/cart/item/' + itemId).then(function (response) {
                return response.data;
            });
        }

        function createOrder() {
            return $http.post('/api/cart/order').then(function (response) {
                return response.data;
            });
        }

        function cleanCartItems() {
            return $http.post('/api/cart/clean').then(function (response) {
                return response.data;
            });
        }

        function updateAddress(address) {
            return $http.put('/api/cart/order/address', address).then(function (response) {
                return response.data;
            });
        }

        function getPaymentLink(orderId) {
            return $http.get('/api/cart/order/' + orderId + '/link').then(
                function(response) {
                    return response.data;
                }
            )
        }

        return {
            getCart: getCart,
            getItemPrice: getItemPrice,
            getTotalPrice: getTotalPrice,
            getTotalCount: getTotalCount,
            updateAmountItem: updateAmountItem,
            addProduct: addProduct,
            removeProduct: removeProduct,
            createOrder: createOrder,
            updateAddress: updateAddress,
            cleanCartItems: cleanCartItems,
            getPaymentLink: getPaymentLink
        };
    }])
    .factory('authFactory', ['$http', function ($http) {
        'use strict';


        function getLocations () {
            return $http.get('/api/core/locations').then(function (response) {
                return response.data;
            });
        }
        function signIn(username, password) {
            return $http.post('/api/users/login', {username: '+' + username, password: password}).then(
                function (response) {
                    return response.data;
                }
            );
        }

        function register1fa(firstName, phone) {
            return $http.post('/api/users/signup', {first_name: firstName, phone: '+' + phone}).then(
                function (response) {
                    return response.data;
                }
            );
        }

        function register2fa(token, smsCode) {
            return $http.post('/api/users/signup/2fa', {token: token, code: smsCode}).then(
                function (response) {
                    return response.data;
                }
            );
        }

        function passwordRecover(phone) {
            return $http.post('/api/users/password/recover', {phone: '+' + phone}).then(
                function (response) {
                    return response.data;
                }
            );
        }

        return {
            signIn: signIn,
            register1fa: register1fa,
            register2fa: register2fa,
            passwordRecover: passwordRecover,
            getLocations: getLocations
        };
    }])
    .factory('modalFactory', ['btfModal', function (btfModal) {
        'use strict';

        var signInForm = btfModal({
            controller: 'signInCtrl',
            controllerAs: 'modal',
            templateUrl: 'signin.html',
            zIndex: 2001
        });
        var signUpForm = btfModal({
            controller: 'signUpCtrl',
            controllerAs: 'modal',
            templateUrl: 'register.html',
            zIndex: 2001
        });
        var recoverPasswordDialog = btfModal({
            controller: 'recoverPasswordCtl',
            controllerAs: 'modal',
            templateUrl: 'recover.html',
            zIndex: 2001
        });
        var deliveryDialog = btfModal({
            controller: 'deliveryCtrl',
            controllerAs: 'modal',
            templateUrl: 'delivery.html'
        });
        var contactDialog = btfModal({
            controller: 'contactCtrl',
            controllerAs: 'modal',
            templateUrl: 'contacts.html'
        });
        var cartDialog = btfModal({
            controller: 'cartCtrl',
            controllerAs: 'modal',
            templateUrl: 'index.html'
        });
        var locationDialog = btfModal({
            controller: 'modalLocationCtrl',
            controllerAs: 'modal',
            templateUrl: 'location.modal.html'
        });
        return {
            signInForm: signInForm,
            signUpForm: signUpForm,
            deliveryDialog: deliveryDialog,
            contactDialog: contactDialog,
            recoverPasswordDialog: recoverPasswordDialog,
            cartDialog: cartDialog,
            locationDialog: locationDialog
        };
    }])
    .factory('profileFactory', ['$http', function ($http) {
        'use strict';

        function loadProfile() {
            return $http.get('/api/users/profile').then(function (response) {
                return response.data;
            });
        }

        function updateProfile(data) {
            return $http.put('/api/users/profile', data).then(function (response) {
                return response.data;
            });
        }

        function passwordChange(data) {
            return $http.post('/api/users/password/change', data).then(
                function (response) {
                    return response.data;
                }
            );
        }

        return {
            loadProfile: loadProfile,
            updateProfile: updateProfile,
            passwordChange: passwordChange
        };
    }])
    .factory('dialogFactory', [function() {
        function successMessage(message) {
            alert(message);
        }

        function errorMessage(message) {
            alert(message);
        }

        function warningMessage(message) {
            alert(message);
        }

        return {
            success: successMessage,
            warning: warningMessage,
            error: errorMessage
        };
    }])
    .factory('actionsFactory', ['$http', function($http) {
        function getActions(limit, offset) {
            var data = {limit: limit, offset: offset};
            return $http.get('/api/core/actions?' + angular.element.param(data)).then(
                function(actionsResponse) {
                    return actionsResponse.data;
                }
            );
        }
        return {
            getActions: getActions
        }
    }]);
