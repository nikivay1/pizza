app
    .controller('baseProductListCtrl', ['$rootScope', '$scope', 'cartFactory',
        function ($rootScope, $scope, cartFactory) {

            $scope.productListUrl = 'products.html';

            /**
             * Получение главной цены
             *
             * @param product
             * @returns {*}
             */
            function getActivePrice(product) {
                if (product.activePrice) {
                    return product.activePrice;
                }
                product.activePrice = product.prices[0];
                return product.activePrice;
            }

            /**
             * Выбор цены по нажатию на элемент
             *
             * @param product
             * @param price
             */
            function setActivePrice(product, price) {
                product.activePrice = price;
            }

            /**
             * @description
             * Добавление товара в корзину покупок.
             *
             * @param priceID
             */
            function addProductToCart(priceID) {
                cartFactory.addProduct(priceID).then(function (response) {
                    $rootScope.reloadCart();
                });
            }

            $scope.addProductToCart = addProductToCart;
            $scope.getActivePrice = getActivePrice;
            $scope.setActivePrice = setActivePrice;
        }])
    .controller('deliveryCtrl', ['$sce', '$scope', 'appSiteConfig', 'modalFactory', function ($sce, $scope, appSiteConfig, modalFactory) {
        $scope.config = appSiteConfig;
        $scope.closeDialog = modalFactory.deliveryDialog.deactivate;
        $scope.trustSrc = function(src) {
            return $sce.trustAsResourceUrl(src);
        }
    }])
    .controller('contactCtrl', ['$scope', 'appSiteConfig', 'modalFactory', function ($scope, appSiteConfig, modalFactory) {
        $scope.config = appSiteConfig;
        $scope.closeDialog = modalFactory.contactDialog.deactivate;
    }])
    .controller('baseCtrl', ['$scope', '$rootScope', '$location', 'modalFactory', 'cartFactory', function ($scope, $rootScope, $location, modalFactory, cartFactory) {
        function init() {
            loadCart();
        }

        function loadCart() {
            return cartFactory.getCart().then(function (cartResponse) {
                $rootScope.cart = cartResponse;
                return cartResponse;
            });
        }

        function openSignInDialog() {
            modalFactory.recoverPasswordDialog.deactivate();
            modalFactory.signUpForm.deactivate();
            modalFactory.signInForm.activate();
        }

        function openSignUpDialog() {
            modalFactory.signInForm.deactivate('no');
            modalFactory.recoverPasswordDialog.deactivate('yes');
            modalFactory.signUpForm.activate().then(function(result){
            });
        }

        function openDeliveryDialog() {
            modalFactory.deliveryDialog.activate();
        }

        function openContactsDialog() {
            modalFactory.contactDialog.activate();
        }

        function openCartDialog() {
            modalFactory.cartDialog.activate();
        }

        function profileClickHandler() {
            if ($rootScope.cart.user) {
                location.href = '/profile';
            }
            else {
                openSignUpDialog();
            }
        }

        function getTotalCartCount() {
            if ($rootScope.cart)
                return cartFactory.getTotalCount($rootScope.cart);
            return 0;
        }

        $rootScope.reloadCart = loadCart;
        $scope.openCartDialog = openCartDialog;
        $scope.openSignInDialog = openSignInDialog;
        $scope.openSignUpDialog = openSignUpDialog;
        $scope.openDeliveryDialog = openDeliveryDialog;
        $scope.openContactsDialog = openContactsDialog;
        $scope.profileClickHandler = profileClickHandler;
        $scope.getTotalCartCount = getTotalCartCount;

        init();
    }])
    .controller('productListCtrl', ['$controller', '$scope', '$rootScope', '$location', 'catalogFactory', 'cartFactory', function ($controller, $scope, $rootScope, $location, catalogFactory, cartFactory) {

        angular.extend(this, $controller('baseProductListCtrl', {$scope: $scope}));

        $scope.products = [];
        $scope.loading = true;
        $scope.actionProducts = [];
        $scope.currentPage = 0;
        $scope.hasNext = false;
        $scope.searchData = {
            category: []
        };

        function init() {
            catalogFactory.getActionProducts().then(function (products) {
                $scope.actionProducts = products;
            });
        }

        function setSearch(data) {
            var newData = angular.copy(data);
            newData.category = data.category.join(',');
            $location.search(newData);
        }

        function getSearch() {
            var data = $location.search();
            if (data && data.category)
                $scope.searchData.category = data.category.split(',');
        }

        function toggleCategory(category, fl) {
            var categories = $scope.searchData.category.filter(function (elem) {
                return elem != category.toString();
            });
            if (fl)
                categories.push(category);
            $scope.searchData.category = categories;
            setSearch($scope.searchData);
        }

        function setActiveCategory(category) {
            toggleCategory(category, !isActiveCategory(category));
        }

        function nextPage() {
            $scope.currentPage += 1;
            $scope.loading = true;
            catalogFactory.getProducts($scope.currentPage).then(function (productsResponse) {
                var oldIds = $scope.products.map(function (elem) {
                    return elem.id;
                }),
                    products = productsResponse.results.filter(function (elem) {
                        return oldIds.indexOf(elem.id) == -1;
                    });
                $scope.products = Array.prototype.concat($scope.products, products);
                $scope.loading = false;
                $scope.hasNext = !!productsResponse.next;
            });
        }

        $rootScope.$on('$locationChangeStart', function () {
            getSearch();
            $scope.loading = true;
            $scope.currentPage = 1;
            catalogFactory.getProducts().then(function (products) {
                $scope.products = products.results;
                $scope.loading = false;
                $scope.hasNext = !!products.next;
            });
        });

        function isActiveCategory(category) {
            return $scope.searchData.category.indexOf(category.toString()) != -1;
        }

        $scope.setActiveCategory = setActiveCategory;
        $scope.isActiveCategory = isActiveCategory;
        $scope.nextPage = nextPage;

        init();
    }])
    .controller('cartCtrl', ['$rootScope', '$scope', '$interval', 'cartFactory', 'modalFactory', 'appSiteConfig',
        function ($rootScope, $scope, $interval, cartFactory, modalFactory, appSiteConfig) {
        'use strict';

        if (!appSiteConfig.delivery_is_available) {
            alert(gettext("Delivery don't work now"));
        }

        if (appSiteConfig.min_order_sum > getTotalPrice()) {
            alert(gettext("Min order price is") + ' ' + appSiteConfig.min_order_sum.toString() + ' ' + gettext('rub'));
        }

        $scope.loading = true;

        var CART_STATES = {
            'new': 'new',
            'cart': 'cart',
            'order': 'order',
            'wait': 'wait'
        };

        $scope.currentStep = CART_STATES.new;


        var STATE_TEMPLATES = {
            'new': {},
            'cart': {file: 'cart', addition: false},
            'order': {file: 'order', addition: true},
            'wait': {file: 'wait', addition: false}
        };

        var STATE_CLASSES = {
            'cart': 'commerce',
            'order': 'cart-forms',
            'wait': 'cart-success'
        };

        function getCurrentClass() {
            return STATE_CLASSES[$scope.currentStep];
        }

        function getCurrentTemplate() {
            if (STATE_TEMPLATES[$scope.currentStep].file) {
                return STATE_TEMPLATES[$scope.currentStep].file + '.html';
            }
            return '';
        }

        function getAdditionCurrentTemplate() {
            if (STATE_TEMPLATES[$scope.currentStep].addition) {
                return STATE_TEMPLATES[$scope.currentStep].file + '.addition.html';
            }
            return '';
        }

        function updateItemAmount(item, delta) {
            if ((item.amount + delta) > 0) {
                cartFactory.updateAmountItem(item.id, item.amount + delta).then(function (response) {
                    item.amount = response.amount;
                });
            }
            else {
                if (confirm('Remove item?')) {
                    removeProductFromCart(item);
                }
            }
        }

        function getItemPrice(item) {
            return cartFactory.getItemPrice(item);
        }

        function getTotalPrice() {
            return cartFactory.getTotalPrice($rootScope.cart);
        }

        function removeProductFromCart(item) {
            var index = $rootScope.cart.items.indexOf(item);
            cartFactory.removeProduct(item.id).then(function () {
                $rootScope.cart.items.splice(index, 1);
            });
        }


        function goStep(state) {
            $scope.currentStep = state;
        }

        function createOrder() {
            if ($rootScope.cart.order) {
                if (appSiteConfig.min_order_sum > getTotalPrice()) {
                    alert(gettext("Min order price is") + ' ' + appSiteConfig.min_order_sum.toString() + ' ' + gettext('rub'));
                    return;
                }
                return goStep(CART_STATES.order);
            }
            cartFactory.createOrder().then(function (response) {
                $rootScope.cart.order = response;
                goStep(CART_STATES.order);
            }, function (response) {
                switch (response.status) {
                    case 400:
                        alert(gettext("Error creating order") + ": " + response.data.detail);
                        break;
                    default:
                        alert(gettext("Error creating order") + ": " + response.responseText);
                        break;
                }
            });
        }

        function updateAddress() {
            if ($scope.blocked) {
                return;
            }
            var data = angular.extend({}, $rootScope.cart.order.address, {
                payment_type: $rootScope.cart.order.payment_type,
                phone: '+' + $rootScope.cart.order.address.phone
            });
            $scope.blocked = true;
            cartFactory.updateAddress(data).then(
                function (responseUrl) {
                    location.href = responseUrl;
                },
                function (response) {
                    var fieldMap = {
                        house: gettext('house'),
                        street: gettext('street'),
                        phone: gettext('phone'),
                        username: gettext('first name')
                    }, showRows = [];
                    switch (response.status) {
                        case 403:
                            alert(response.data.detail);
                            break;
                        case 400:
                            alert(response.data.detail);
                            break;
                        default:
                            for (var i in response.data) {
                                showRows.push(
                                    [fieldMap[i].toUpperCase(), response.data[i].join('; ')].join(" : ")
                                );
                            }
                            showRows = showRows.join('\n\n');
                            alert(showRows || gettext("Error address saving"));
                            break;
                    }
                    $scope.blocked = false;
                }
            );
        }

        function setDeliveryType(deliveryType) {
            $rootScope.cart.order.address.delivery_type = deliveryType;
        }

        function setAddressType(addressType) {
            $rootScope.cart.order.address.address_type = addressType;
        }

        function setPaymentType(paymentType) {
            $rootScope.cart.order.payment_type = paymentType;
        }

        $scope.stadions = [
            "Олимпийский Стадион «Фишт»",
            "Ледяной куб",
            "Большой"
        ];

        function isVisibleAddress() {
            return $rootScope.cart.order.address.delivery_type == 'DELIVERY' && $rootScope.cart.order.address.address_type == 'ADDRESS';
        }

        function isVisibleArena() {
            return $rootScope.cart.order.address.delivery_type == 'DELIVERY' && $rootScope.cart.order.address.address_type == 'ARENA';
        }

        function init() {

            for (var i = 1; i < 100; i++) {
                $scope.numbers.push(i);
            }
            $scope.loading = true;
            $rootScope.reloadCart().then(function(data) {
                $scope.currentStep = CART_STATES.cart;
                $scope.loading = false;
                $scope.blocked = false;
            });
        }

        function openSignUpDialog() {
            modalFactory.signInForm.deactivate();
            modalFactory.recoverPasswordDialog.deactivate();
            modalFactory.signUpForm.activate().then(function(result){
                alert(result);
            });
        }

        /**
         * @description
         * Добавление товара в корзину покупок.
         *
         * @param priceID
         */
        function addProductToCart(priceID) {
            cartFactory.addProduct(priceID).then(function (response) {
                $rootScope.reloadCart();
            });
        }

        //variables
        $scope.STATES = CART_STATES;
        $scope.numbers = [];
        $scope.phonePattern = /^(\d+-)?\d{9,20}$/;
        $scope.blocked = true;

        // methods
        $scope.closeDialog = modalFactory.cartDialog.deactivate;
        $scope.addProductToCart = addProductToCart;
        $scope.openSignUpDialog = openSignUpDialog;
        $scope.updateItemAmount = updateItemAmount;
        $scope.isVisibleAddress = isVisibleAddress;
        $scope.isVisibleArena = isVisibleArena;
        $scope.updateAddress = updateAddress;
        $scope.removeProductFromCart = removeProductFromCart;
        $scope.setDeliveryType = setDeliveryType;
        $scope.setAddressType = setAddressType;
        $scope.setPaymentType = setPaymentType;
        $scope.getCurrentTemplate = getCurrentTemplate;
        $scope.getAdditionCurrentTemplate = getAdditionCurrentTemplate;
        $scope.getCurrentClass = getCurrentClass;
        $scope.getTotalPrice = getTotalPrice;
        $scope.getItemPrice = getItemPrice;
        $scope.createOrder = createOrder;
        $scope.goStep = goStep;

        init();
    }
    ])
    .controller('signInCtrl', ['$scope', '$rootScope', 'modalFactory', 'authFactory', function ($scope, $rootScope, modalFactory, authFactory) {
        function signIn() {
            authFactory.signIn($scope.username, $scope.password).then(
                function (userData) {
                    $rootScope.reloadCart();
                    $scope.closeDialog();
                },
                function (response) {
                    switch (response.status) {
                        case 400:
                            alert(gettext("Invalid username/password, try again"));
                            break;
                        case 401:
                            alert(gettext("Invalid username/password, try again"));
                            break;
                        case 500:
                            alert(gettext("Internal server error"));
                            break;
                    }
                }
            )
        }

        function showRecoverDialog() {
            $scope.closeDialog();
            modalFactory.recoverPasswordDialog.activate();
        }

        $scope.closeDialog = modalFactory.signInForm.deactivate;
        $scope.username = '';
        $scope.password = '';
        $scope.showRecoverDialog = showRecoverDialog;
        $scope.signIn = signIn;
    }])
    .controller('recoverPasswordCtl', ['$scope', '$rootScope', 'modalFactory', 'authFactory', function ($scope, $rootScope, modalFactory, authFactory) {
        'use strict';

        function passwordRecover() {
            authFactory.passwordRecover($scope.phone).then(
                function (recoverResponse) {
                    $scope.token = recoverResponse.token;
                    alert(gettext("The password will be sent to You by sms") + ".");
                    $scope.closeDialog();
                    modalFactory.signInForm.activate();
                },
                function (response) {
                    switch (response.status){
                        case 401:
                            alert(gettext("Phone was not found"));
                            break;
                        case 400:
                            alert(gettext("Incorrect sent data"));
                            break;
                        case 429:
                            alert(gettext("Too frequent requests"));
                            break;
                        default:
                            alert(gettext("Internal server error"));
                    }
                }
            );
        }

        $scope.phone = '';
        $scope.closeDialog = modalFactory.recoverPasswordDialog.deactivate;
        $scope.passwordRecover = passwordRecover;
    }])
    .controller('signUpCtrl', ['$scope', '$rootScope', 'modalFactory', 'authFactory', function ($scope, $rootScope, modalFactory, authFactory) {
        'use strict';

        function signUp1fa() {
            authFactory.register1fa($scope.firstName, $scope.phone).then(
                function (response) {
                    $scope.token = response.token;
                    $scope.factor = 2;
                },
                function (response) {
                    switch (response.status) {
                        case 400:
                            alert(gettext("Invalid username/password, try again"));
                            break;
                        case 403:
                            alert(gettext("This number is already registered"));
                            break;
                        case 401:
                            alert(gettext("Invalid username/password, try again"));
                            break;
                        case 500:
                            alert(gettext("Internal server error"));
                            break;
                    }
                }
            );
        }


        function openSignInDialog() {
            modalFactory.recoverPasswordDialog.deactivate();
            modalFactory.signUpForm.deactivate();
            modalFactory.signInForm.activate();
        }

        function signUp2fa() {
            authFactory.register2fa($scope.token, $scope.smsCode).then(
                function (userData) {
                    $scope.user = userData;
                    $rootScope.reloadCart();
                    $scope.closeDialog(true);
                },
                function (response) {
                    switch (response.status) {
                        case 400:
                            alert(gettext("Invalid username/password, try again"));
                            break;
                        case 401:
                            alert(gettext("Invalid username/password, try again"));
                            break;
                        case 500:
                            alert(gettext("Internal server error"));
                            break;
                    }
                }
            );
        }

        function closeDialog(reason) {
            modalFactory.signUpForm.deactivate(reason);
        }

        $scope.openSignInDialog = openSignInDialog;
        $scope.closeDialog = closeDialog;
        $scope.firstName = '';
        $scope.phone = '';
        $scope.factor = 1;
        $scope.smsCode = '';
        $scope.signUp1fa = signUp1fa;
        $scope.signUp2fa = signUp2fa;
    }])
    .controller('profileCtrl', ['$rootScope', '$scope', 'profileFactory', 'authFactory', 'cartFactory', 'dialogFactory', function ($rootScope, $scope, profileFactory, authFactory, cartFactory, dialogFactory) {
        'use strict';

        function init() {
            $scope.loading = true;
            profileFactory.loadProfile().then(function (profileResponse) {
                $scope.profileData = profileResponse;
                $scope.loading = false;
                $scope.blocked = false;
            }, function () {
                $scope.loading = false;
                $scope.blocked = false;
                alert(gettext("Error loading profile"));
            });
        }

        function changeProfile() {
            var data = {
                first_name: $scope.profileData.first_name,
                phone: $scope.profileData.phone,
                email: $scope.profileData.email
            };

            if ($scope.passwordData.password1.trim() != $scope.passwordData.password2.trim()) {
                alert(gettext("Passwords didn't match"));
                return;
            }
            else{
                if (($scope.passwordData.password1.trim() && !$scope.passwordData.oldPassword.trim()) ||
                    (!$scope.passwordData.password1.trim() && $scope.passwordData.oldPassword.trim())) {
                    alert("Введите пароль");
                    return;
                }
                if ($scope.passwordData.password1.trim()) {
                    data = angular.merge(data, {
                        old_password: $scope.passwordData.oldPassword.trim(),
                        password1: $scope.passwordData.password1.trim(),
                        password2: $scope.passwordData.password2.trim()
                    });
                }
            }

            profileFactory.updateProfile(data).then(
                function(profileResponse){
                    switchChangeMode(false);
                    $scope.passwordData = {oldPassword: '', password1: '', password2: ''};
                    alert(gettext("Profile was updated"));
                },
                function () {
                    alert(gettext("Error saving profile"));
                });
        }

        function passwordIsRequiredField() {
            return (
                $scope.passwordData.password1 ||
                $scope.passwordData.password2 ||
                $scope.passwordData.oldPassword
            );
        }
        function clearFavorite() {

        }

        function switchChangeMode(changeMode) {
            $scope.changeMode = changeMode;
        }

        function getTotalCartPrice () {
            return cartFactory.getTotalPrice($rootScope.cart);
        }

        function cleanCart() {
            cartFactory.cleanCartItems().then(function() {
                $rootScope.cart.items = [];
                dialogFactory.success("Корзина успешно очищена");
            })
        }
        // variables
        $scope.profileTplUrl = '/static/app/templates/profile.html';
        $scope.passwordData = {oldPassword: '', password1: '', password2: ''};
        $scope.profileData = null;
        $scope.changeMode = false;
        $scope.loading = false;
        $scope.blocked = true;

        // methods
        $scope.getCartItemPrice = cartFactory.getItemPrice;
        $scope.passwordIsRequiredField = passwordIsRequiredField;
        $scope.getTotalCartPrice = getTotalCartPrice;
        $scope.switchChangeMode = switchChangeMode;
        $scope.changeProfile = changeProfile;
        $scope.clearFavorite = clearFavorite;
        $scope.cleanCart = cleanCart;

        init();
    }])
    .controller('orderCtrl', ['$scope', '$rootScope', '$interval', 'cartFactory', function($scope, $rootScope, $interval, cartFactory) {

        function startOrderTimeout() {
            $scope.currentTimerTick = parseInt(angular.element('#seconds').val());
            if ($scope.currentTimerTick > 0)
                $interval(function () { $scope.currentTimerTick -= 1; }, 1000);
        }

        function getDisplayTimer() {
            var value = '00:00',
                formatter = function(number) { return (number > 9? '': '0')  + number.toString();};
            if ($scope.currentTimerTick > 0) {
                value = formatter(parseInt($scope.currentTimerTick / 60)) + ':' + formatter($scope.currentTimerTick % 60);
            }
            return value;
        }

        function init() {
            $scope.startOrderTimeout();
            $scope.blocked = false;
        }

        function getPaymentLink(orderId) {
            if ($scope.blocked) {
                return;
            }
            $scope.blocked = true;
            cartFactory.getPaymentLink(orderId).then(
                function(response) {
                    if (response.form_url)
                        location.href = response.form_url;
                    else {
                        alert(response.message);
                        $scope.blocked = false;
                    }
                },
                function(response) {
                    switch (response.status) {
                        case 403:
                            alert(response.data.message)
                            break;
                        default:
                            alert(JSON.stringify(response.data.message));
                    }
                    $scope.blocked = false;
                }
            )
        }

        $scope.startOrderTimeout = startOrderTimeout;
        $scope.getDisplayTimer = getDisplayTimer;
        $scope.getPaymentLink = getPaymentLink;
        $scope.blocked = true;

        init();
    }])
    .controller('actionCtrl', ['$scope', '$filter', 'actionsFactory', function ($scope, $filter, actionsFactory) {
        function init() {
            $scope.nextPage().then(function(actionsResponse) {
                $scope.activeList = actionsResponse.actual_list;
                $scope.expiredList = actionsResponse.expired_list;
            });
        }

        function nextPage() {
            return actionsFactory.getActions($scope.limit, $scope.offset).then(function(actionsResponse) {
                console.log(actionsResponse)
                $scope.actions = Array.prototype.concat($scope.actions, actionsResponse.actual);
                $scope.offset += actionsResponse.actual.length;
                $scope.hasNext = actionsResponse.actual.length == $scope.limit;
                return actionsResponse;
            });

        }

        function getActionDate (item) {
            if (item.is_expired) {
                return 'АКЦИЯ НЕ ДЕЙСТВИТЕЛЬНА';
            }
            return [
                $filter('date')(item.active_from, "dd.MM.yyyy"),
                $filter('date')(item.active_until, "dd/MM.yyyy")
            ].join(' - ')
        }

        function getActionDateIcon (item) {
            return item.is_expired ?
                '/static/img/close-window.png' :
                '/static/img/calendar-24.png';
        }

        // variables
        $scope.limit = 5;
        $scope.offset = 0;
        $scope.hasNext = true;
        $scope.actions = [];
        $scope.activeList = [];
        $scope.expiredList = [];

        // methods
        $scope.nextPage = nextPage;
        $scope.getActionDate = getActionDate;
        $scope.getActionDateIcon = getActionDateIcon;

        init();
    }])
    .controller('modalLocationCtrl', ['$scope', 'authFactory', function ($scope, authFactory) {
        $scope.selectedLocation = null;
        $scope.locations = [];
        $scope.loading = true;

        authFactory.getLocations().then(function (locations) {
            $scope.loading = false;
            $scope.locations = locations;
        })
    }]);