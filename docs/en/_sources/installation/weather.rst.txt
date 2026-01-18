Weather data
############

.. versionchanged:: 0.7.11 Add Visual Crossing to weather providers
.. versionremoved:: 0.7.15 Remove Darksky from weather providers

The following weather data providers are supported by **FitTrackee**:

- `Visual Crossing <https://www.visualcrossing.com>`__ (**note**: historical data are provided on hourly period)

.. note::

   **DarkSky** support is discontinued, since the service shut down on March 31, 2023.

To configure a weather provider, set the following environment variables:

- ``WEATHER_API_PROVIDER``: the name of the provider (currently ``visualcrossing`` is the only choice)
- ``WEATHER_API_KEY``: the key to the corresponding weather provider