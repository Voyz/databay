Weather Inlet
------------

.. _OpenWeatherMap: https://openweathermap.org/current

.. container:: tutorial-block

    This example demonstrates an inlet that produces weather prognostic using OpenWeatherMap_. It showcases what a realistic implementation of :any:`Inlet` may look like.

    #. Create the :code:`WeatherInlet` implementing :any:`Inlet` class. We expect :code:`api_key` and :code:`city_name` to be provided when constructing this inlet.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/weather_inlet.py
        :language: python
        :lines: 10-19


    #. Implement :any:`pull` method, starting by creating the OpenWeatherMap URL using the :code:`api_key` and :code:`city_name` provided.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/weather_inlet.py
        :language: python
        :lines: 21-24

    #. Make a request to OpenWeatherMap using :any:`urllib.request`.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/weather_inlet.py
        :language: python
        :lines: 26

    #. Parse the response and return produced data.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/weather_inlet.py
        :language: python
        :lines: 28-29

    #. Instantiate :code:`WeatherInlet`.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/weather_inlet.py
        :language: python
        :lines: 32-33


    Full example:

    .. literalinclude:: ../../examples/weather_inlet.py
        :language: python

    Produces:

    .. rst-class:: highlight-small
    .. code-block:: python

        >>> bangkok_weather.0 light rain
        >>> bangkok_weather.1 light rain
        >>> bangkok_weather.2 light rain
        >>> ...