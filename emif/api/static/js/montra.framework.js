/*
# -*- coding: utf-8 -*-
# Copyright (C) 2017 BMD software, Lda
#
# Author: Luís A. Bastião Silva <bastiao@bmd-software.com 
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
*/


function Controller(module, view) {
    this.module = module;
    this.view = view;
    this.data = {};
}

Controller.prototype.initialize = function ($container, data) {
    this.view.initialize($container, data);
};

Controller.prototype.init = function () {
    
};

function View(controller, template) {
    this.controller = controller;
    this.template = template;
    this.templateRaw = null;
    this.$container = null;
    this.$elements = {}
}

View.prototype.initialize = function ($container, data) {
    // Set container
    this.$container = $container;

    // Add view template
    if (this.template) {
        var self = this;
        $.ajax({
            url: this.template,
            type: "GET",
        })
        .done(function (e) {           
            var template = Handlebars.compile(e)
            self.templateRaw = template;
            self.onAfterTemplateLoading();
        })
        .fail(function (e) {
            
        });
        /*if (data) {
            this.$container.html(Urls[this.template](data));
        } else {
            this.$container.html(Urls[this.template]());
        }*/
    }


    // Get view components
    this._loadViewComponents();


    // Validate view permissions
    //Permissions.validate(this.$container);
};

View.prototype.onAfterTemplateLoading = function(){
    this.controller.init();
}

View.prototype._loadViewComponents = function () {


    // Permissions validate
    //Permissions.validate(this.$container);

    var self = this;
    var v;

    this.$elements = {};

    if ((v = this.$container.attr('mf-init'))) {
        this._setKeyValuePairs(v);
    }

    this.$container.find('[m-init]').each(function () {
        self._setKeyValuePairs(name);
    });

    this.$container.find('[m-view]').each(function () {
        var $element = $(this);
        var name = $element.attr('m-view');
        self.$elements[name] = $element;
    });

    this.$container.find('[m-click]').each(function () {
        var $element = $(this);
        var functionCall = $element.attr('m-click');

        var json = self._getFunctionContextNameAndArguments(functionCall);
        var name = json.name;
        var args = json.args;
        var context = json.context;

        if ($element.is('a')) {
            $element.attr('href', 'javascript:void(0)');
        }

        $element.off('click tap');
        $element.on('click tap', function (event) {
            //context[name](args);
            args.push($element, event);
            context[name].apply(context, args);
        });
    });

    this.$container.find('[m-change]').each(function () {
        var $element = $(this);
        var functionCall = $element.attr('m-change');

        var json = self._getFunctionContextNameAndArguments(functionCall);
        var name = json.name;
        var args = json.args;
        var context = json.context;

        $element.off('change');
        $element.on('change', function (event) {
            args.push($element);
            context[name].apply(context, args);
        });
    });


    this.$container.find('[m-hidden]').each(function () {
        var $element = $(this);
        $element.hide();
    });

    this.$container.find('[m-submit]').each(function () {
        var $element = $(this);
        var functionCall = $element.attr('vf-submit');

        var json = self._getFunctionContextNameAndArguments(functionCall);
        var name = json.name;
        var args = json.args;
        var context = json.context;

        $element.attr('action', 'javascript:void(0);');

        $element.off();
        $element.on('submit', function (event) {
            if (event.preventDefault())
                event.preventDefault();
            if (event.stopPropagation())
                event.stopPropagation();
            if (event.stopImmediatePropagation())
                event.stopImmediatePropagation();

            // Validate form if possible
            var bv = $element.data('bootstrapValidator');
            if (bv) {
                var valid = bv.isValid();
                if (valid == false) {
                    bv.validate();
                    if (!bv.isValid()) {
                        return false;
                    }
                }
            }
            //context[name](args);
            context[name].apply(context, args);
            return false;
        });

        // Press Enter to submit form
        $element.on('keypress', function (event) {
            // Enter
            if (event.keyCode == 13) {
                if (event.preventDefault())
                    event.preventDefault();
                if (event.stopPropagation())
                    event.stopPropagation();
                if (event.stopImmediatePropagation())
                    event.stopImmediatePropagation();

                $element.submit();
            }
        });

        // If we have a modal, resetForm when it is hiden
        $('.modal').on('hide.bs.modal', function () {
            var f;
            if ((f = $(this).find('form'))) {
                f.bootstrapValidator('resetForm', true);
            }
        });
    });
};

View.prototype._setKeyValuePairs = function (text) {
    var self = this;

    var pairs = View.getKeyValuePairs(text);
    _.each(pairs, function (pair) {
        self[pair.key] = pair.value;
    });
};

View.show = function ($element) {
    $element.removeClass('hidden');
    $element.show();
};
View.hide = function ($element) {
    $element.addClass('hidden');
    $element.hide();
};

View.getKeyValuePairs = function (text) {
    var pairs = [];
    if (text.indexOf(',') > -1) {
        pairs = text.split(',');
    } else {
        pairs.push(text);
    }

    var ret = [];
    _.each(pairs, function (pair) {
        var args = pair.split(':');
        if (args.length != 2) {
            throw new Error('Wrong init format on: ' + text);
        }

        var key = args[0].trim();
        var value = args[1].trim();

        ret.push({
            key: key,
            value: value
        });
    });

    return ret;
};

View.prototype._getFunctionContextNameAndArguments = function (functionCall) {
    var name = functionCall;
    var args = [];
    var context = null;

    if (functionCall.indexOf('view.') > -1) {
        context = this;
    } else if (functionCall.indexOf('controller.') > -1) {
        context = this.controller;
    }

    if (functionCall.indexOf('(') > -1) {

        var idx = 2;
        var nameRegex = /(view|controller)\.(.*)\(/g;
        if (_.isNull(context)) {
            idx = 1;
            nameRegex = /(.*)\(/g;
        }

        // Get name
        var matches = nameRegex.exec(functionCall);
        name = matches[idx];

        // Get arguments
        var argumentsRegex = /\((.*)\)/g;
        matches = argumentsRegex.exec(functionCall);
        var argumentsText = matches[1];

        if (argumentsText) {
            args = argumentsText.split(',');
        }

        args = _.map(args, function (arg) {
            return arg.trim();
        })
    }

    // Check if functions exists on view or context
    if (_.isNull(context)) {
        if (_.isFunction(this[name])) {
            context = this;
        } else if (_.isFunction(this.controller[name])) {
            context = this.controller;
        } else {
            throw new Error('Function ' + name + ' does not exist.');
        }
    }

    return {
        context: context,
        name: name,
        args: args
    };
};