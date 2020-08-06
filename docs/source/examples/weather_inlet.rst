Weather Inlet
------------

.. _OpenWeatherMap: https://openweathermap.org/current

.. container:: tutorial-block

    This example demonstrates an inlet that produces weather prognostic using OpenWeatherMap_. It showcases what a realistic implementation of :any:`Inlet` may look like.

    #. Create the :code:`WeatherInlet` implementing :any:`Inlet` class. We expect :code:`api_key` and :code:`city_name` to be provided when constructing this inlet.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/weather_inlet.py
        :language: python
        :start-at: from databay.inlet
        :end-at: self.city_name = city_name


    #. Implement :any:`pull` method, starting by creating the OpenWeatherMap URL using the :code:`api_key` and :code:`city_name` provided.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/weather_inlet.py
        :language: python
        :start-at: def pull(
        :end-at: f'appid={

    #. Make a request to OpenWeatherMap using :any:`urllib.request`.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/weather_inlet.py
        :language: python
        :start-at: urllib.request.
        :end-at: urllib.request.

    #. Parse the response and return produced data.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/weather_inlet.py
        :language: python
        :start-at: formatted =
        :end-at: return formatted

    #. Instantiate :code:`WeatherInlet`.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/weather_inlet.py
        :language: python
        :start-at: api_key = os.environ.get
        :end-at: weather_inlet = WeatherInlet

    #. Create link, add it to planner and schedule.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/weather_inlet.py
        :language: python
        :start-at: link = Link
        :end-at: planner.start

    Output:

    .. rst-class:: highlight-small
    .. code-block:: python

        >>> bangkok_weather.0 light rain
        >>> bangkok_weather.1 light rain
        >>> bangkok_weather.2 light rain
        >>> ...

    On each transfer :code:`WeatherInlet` makes a request to OpenWeatherMap API and returns a description of the weather in selected city.

    Full example:

    .. literalinclude:: ../../examples/weather_inlet.py
        :language: python

