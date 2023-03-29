function Module(name) {
    this.name = name;
    this.$container = null;
    this.controllers = {};
}

Module.prototype.initialize = function ($container) {
    this.$container = $container;
    var self = this, v;

    if ((v = this.$container.attr('controller'))) {
        self._setController(this.$container, v);
    }

    this.$container.find('[controller]').each(function () {
        var $element = $(this);
        var name = $element.attr('controller');

        self._setController($element, name);
    });
};

Module.prototype._setController = function ($element, name) {
    if (!window[name]) {
        throw new Error('Controller ' + name + ' not found.');
    }

    var self = this;

    // Create module and initialize it
    var controller = new window[name](self);

    // Get init variables
    var v;
    if ((v = $element.attr('m-controller-init'))) {
        self._setKeyValuePairs(v, controller);
    }

    // Get controller data models
    if ((v = $element.attr('m-controller-data'))) {
        self._setDataModels(v, controller);
    }

    controller.initialize($element);
    this.controllers[name] = controller;
};

Module.prototype._setKeyValuePairs = function (text, controller) {
    var pairs = View.getKeyValuePairs(text);
    _.each(pairs, function (pair) {
        controller[pair.key] = pair.value;
    });
};

Module.prototype._setDataModels = function (text, controller) {
    var pairs = View.getKeyValuePairs(text);
    _.each(pairs, function (pair) {
        controller.data[pair.key] = window[pair.value] ? window[pair.value] : null;
    });
};

$(document).ready(function (event) {
    $(this).find('[module]').each(function () {
        var $element = $(this);
        var name = $element.attr('module');

        // Create module and initialize it
        var module = new Module(name);
        window['module'] = module;
        module.initialize($element);

        console.log('Module created:');
        console.log(module);
    });
});