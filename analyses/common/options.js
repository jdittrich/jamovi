
'use strict';

var _ = require('underscore');
var $ = require('jquery');
var Backbone = require('backbone');
Backbone.$ = $;

var keyedQueue = function() {
    this._list = [];

    this.push = function(key, obj) {
        if (_.isUndefined(this[key]))
            this._list.push(obj);

        this[key] = obj;
    };

    this.contains = function(key) {
        return _.isUndefined(this[key]) === false;
    };

    this.length = function() {
        return this._list.length;
    };
};

var Options = Backbone.Model.extend({

    _beginEdit: 0,
    _queuedEvents: new keyedQueue(),

    beginEdit: function() {
        this._beginEdit += 1;
    },

    endEdit: function() {
        this._beginEdit -= 1;
        if (this._beginEdit === 0) {
            this.fireQueuedEvents();
        }
    },

    _refList: { },
    _refListIndex: 0,

    getOption: function(name) {

        var list = this.get("options");

        if ( ! list)
            return null;

        if ($.isNumeric(name))
            return list[name];

        var option = this._refList[name];

        if (_.isUndefined(option) === true) {
            var i = this._refListIndex;
            for (; i < list.length; i++) {
                var optObj = list[i];
                this._refList[optObj.name] = optObj;
                if (optObj.name === name) {
                    option = optObj;
                    i += 1;
                    break;
                }
            }

            this._refListIndex = i;
        }

        return option;
    },

    setOptionValue: function(name, value) {

        var option = null;
        if (_.isUndefined(name.type) === false)
            option = name;
        else
            option = this.getOption(name);

        if (option.setValue(value))
            this.onValueChanged(option);
    },

    onValueChanged: function(option) {

        this._queuedEvents.push(option.name, option);

        if (this._beginEdit === 0)
            this.fireQueuedEvents();
    },

    fireQueuedEvents: function() {
        if (this._queuedEvents.length() > 0) {
            this.trigger("options.valuesChanged", this._queuedEvents);
            this._queuedEvents = new keyedQueue();
        }
    }

});

module.exports = Options;
