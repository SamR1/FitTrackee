Map tile server
###############

.. versionadded:: 0.4.0 added possibility to change map tile provider
.. versionchanged:: 0.6.10 handle tile server subdomains
.. versionchanged:: 0.7.23 default tile server (**OpenStreetMap**) no longer requires subdomains

Default tile server is **OpenStreetMap**'s standard tile layer (if environment variables are not initialized).
The tile server can be changed by updating ``TILE_SERVER_URL`` and ``MAP_ATTRIBUTION`` variables (`list of tile servers <https://wiki.openstreetmap.org/wiki/Raster_tile_providers>`__).

To keep using **ThunderForest Outdoors**, the configuration is:

- ``TILE_SERVER_URL=https://{s}.tile.thunderforest.com/outdoors/{z}/{x}/{y}.png?apikey=XXXX`` where **XXXX** is **ThunderForest** API key
- ``MAP_ATTRIBUTION=&copy; <a href="http://www.thunderforest.com/">Thunderforest</a>, &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors``

.. note::
    | Check the terms of service of tile provider for map attribution.

Since the tile server can be used for static map generation, some servers require a subdomain.

For instance, to set OSM France tile server, the expected values are:

- ``TILE_SERVER_URL=https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png``
- ``MAP_ATTRIBUTION='fond de carte par <a href="http://www.openstreetmap.fr/mentions-legales/" target="_blank" rel="nofollow noopener">OpenStreetMap France</a>, sous&nbsp;<a href="http://creativecommons.org/licenses/by-sa/2.0/fr/" target="_blank" rel="nofollow noopener">licence CC BY-SA</a>'``
- ``STATICMAP_SUBDOMAINS=a,b,c``

The subdomain will be chosen randomly.

The default tile server (**OpenStreetMap**) no longer requires subdomains.