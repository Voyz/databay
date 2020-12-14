Twitter Inlet
-------------

.. container:: tutorial-block

    In this example we create an implementation of an :any:`Inlet` that connects to the Twitter API and either listens for new tweets for a specific user or to the home timeline for an authenticated account. 
    
    **Note**: this example assumes that the Tweepy client is correctly configured and that the Twitter account is registered to use the API. For more details on Tweepy click here_. 

    .. _here: http://docs.tweepy.org/en/latest/

    #. Extend the :any:`Inlet` by passing in an instance of the Tweepy client :code:`api`. Depending on the use case users can also pass in :code:`user` if they want to run the Inlet on a specific username. 

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/twitter_inlet.py
        :language: python
        :start-at: class TwitterInlet
        :end-at:  self.is_user_timeline = True

    
    #. For the :code:`pull` method we perform a number of configuration specific checks: 
        
        * If the flag :code:`self.is_user_timeline` is :code:`True` we'll be using the :code:`user_timeline` method of the Tweepy API. This pulls tweets from a specific users' timeline rather than the registered accounts' home timeline.
        * Additionally there is a check in both conditional branches that checks for :code:`self.most_recent_id`, if a recent ID exists then this ID is passed an additional parameter to Tweepy. This will ensure that only new tweets since the last pull are fetched. 
        * :code:`self.most_recent_id` is assigned by taking the ID from the first tweet in the results list.

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/twitter_inlet.py
        :language: python
        :start-at: def pull(self, update):
        :end-at:  return tweets
    
    #. To authenticate Tweepy correctly the appropriate keys and secrets must be passed to the API. 

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/twitter_inlet.py
        :language: python
        :start-at: auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        :end-at:  api = tweepy.API(

    #. The :any:`TwitterInlet` can then be instantiated as seen below. We are using the :any:`PrintOutlet` to print the results of each successful pull. 

        * **Note**: Be mindful of the :code:`interval` you pass to :any:`Link` as the Twitter API has strict rate limiting policies. 

    .. rst-class:: highlight-small
    .. literalinclude:: ../../examples/twitter_inlet.py
        :language: python
        :start-at: # create TwitterUserInlet() pointed at a specific account name
        :end-at:  planner.start()
    
    Output:


    .. rst-class:: highlight-small
    .. code-block:: python

        >>> {'user': 'BarackObama', 'text': 'Georgia’s runoff election will determine whether the American people have a Senate that’s actually fighting for the… https://t.co/igUiRzxNxe'}
        >>> {'user': 'BarackObama', 'text': 'Here’s a great way to call voters in Georgia and help them get ready to vote. A couple hours this weekend could hel… https://t.co/x6Nc8w7F38'}
        >>> {'user': 'BarackObama', 'text': "Happy Hanukkah to all those celebrating around the world. This year has tested us all, but it's also clarified what… https://t.co/k2lzUQ9LNm"}
        >>> {'user': 'BarackObama', 'text': 'In A Promised Land, I talk about the decisions I had to make during the first few years of my presidency. Here are… https://t.co/KbE2FDStYr'}
        >>> {'user': 'BarackObama', 'text': "With COVID-19 cases reaching an all-time high this week, we've got to continue to do our part to protect one anothe… https://t.co/Gj0mEFfuLY"}
        >>> {'user': 'BarackObama', 'text': 'To all of you in Georgia, today is the last day to register to vote in the upcoming runoff election. Take a few min… https://t.co/Jif3Gd7NpQ'}




    Full example:

    .. literalinclude:: ../../examples/twitter_inlet.py
        :language: python