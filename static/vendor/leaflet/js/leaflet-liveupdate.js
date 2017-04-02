L.Control.Liveupdate = L.Control.extend({

    timer: false,

    options: {
        position: 'topleft',
        title: {
            'false': 'Start live updates',
            'true': 'Stop live updates'
        },
        is_updating: true,
        update_map: false,  // callback function
        interval: 10000
    },

    onAdd: function (map) {
        this.container = L.DomUtil.create('div', 'leaflet-control-liveupdate leaflet-bar leaflet-control');

        this.link = L.DomUtil.create('a', 'leaflet-control-liveupdate-button leaflet-bar-part', this.container);
        this.link.href = '#';

        this._map = map;
        this._setUpdating(this.options.is_updating);
        map.liveUpdateControl = this;

        L.DomEvent.on(this.link, 'click', this._click, this);
        return this.container;
    },

    _click: function (e) {
        L.DomEvent.stopPropagation(e);
        L.DomEvent.preventDefault(e);
        this.toggleUpdating();
    },

    _toggleTitle: function() {
        this.link.title = this.options.title[this.isUpdating()];
    },

    isUpdating: function () {
        return this._isUpdating || false;
    },

    _setUpdating: function (updating) {
        this._isUpdating = updating;
        if (updating) {
            L.DomUtil.addClass(this.container, 'leaflet-liveupdate-on');
        } else {
            L.DomUtil.removeClass(this.container, 'leaflet-liveupdate-on');
        }
        this._toggleTitle();
    },

    toggleUpdating: function () {
        if (this.isUpdating ()) {
            this.stopUpdating ();
            a = 'stopped';
        }
        else {
            this.startUpdating ();
            a = 'started';
        }
        if (this._map.messagebox) {
            this._map.messagebox.show('Live updates ' + a);
        }
        return this;
    },

    startUpdating: function () {

        var map = this._map;
        var update_map = this.options.update_map;
        var _this = this;

        this._setUpdating(true);
        update_map(this);
        this.timer = setInterval(function() {
            update_map(_this);
        }, this.options.interval);
        return this;
    },

    stopUpdating: function () {
        this._setUpdating(false);
        clearInterval(this.timer);
        this.timer = false;
        return this;
    },

    updateNow: function () {
        var update_map = this.options.update_map;
        update_map(this);
        return this;
    }

});

L.control.liveupdate = function (options) {
    return new L.Control.Liveupdate(options);
};
