.. _tests_so: https://stackoverflow.com/a/67500/3508719
.. _tests: https://github.com/Voyz/databay/tree/master/test/test
.. _github_community: https://github.com/Voyz/databay#community

.. _community_contributions:

Community Contributions
=======================

We aim to support the ecosystem of Databay users by collating and promoting third-party inlets and outlets that implement popular functionalities. We encourage you to share the inlets and outlets you write with the community. See the list of currently shared inlets and outlets, as well as the description of the submission process on `Databay's GitHub Page <github_community_>`_.

Guideline
#########

To ensure your contribution is widely adopted, we recommend the following guideline of implementation.

Read the documentation
----------------------

Understand the design decisions behind Databay, and the inlets and outlets. Read through the :ref:`examples <examples>` as well as the currently implemented :any:`inlets <databay.inlets>` and :any:`outlets <databay.outlets>` to understand how Databay can be used.

Write tests
-----------

The more reliable your code is, the more likely other users will choose to rely on it. In this `StackOverflow question <tests_so_>`_ you can read more about why tests matter. You can test some fundamental Databay functionality by using :any:`InletTester`. You should write additional tests outside of scope of :any:`InletTester` to cover the custom logic introduced by you. Remember that apart from writing unit tests, it is easy to write integration tests using :any:`Databay planners <databay.planners>`.

See to the `tests <tests_>`_ of the built-in inlets and outlets for reference.


Write documentation
-------------------

Your inlets and outlets should be well documented. Each implementation will be dependant on the functionality it provides, therefore your design decisions should be laid out and the API explained. We encourage you to write external standalone documentation apart from writing docstrings in code. Your GitHub page should also contain a short introduction, overview and examples.

Correctly use metadata
----------------------

.. container:: tutorial-block

    .. rubric:: Inlets

    When writing inlets, remember to not modify or read the metadata provided, and to correctly initialise your inlet using :code:`super().__init__(*args, **kwargs)`.

    Incorrect:

    .. code-block:: python

        class MyInlet(Inlet):

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.my_argument = self.metadata['my_argument']

    Correct:

    .. code-block:: python

        class MyInlet(Inlet):

            def __init__(self, my_argument, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.my_argument = my_argument

    .. rubric:: Outlets

    When writing outlets supporting metadata, you should clearly describe the expected behaviour of each metadata in the documentation.

    Your outlet should not exclusively rely on metadata and error out in its absence. Provide a method of setting default values for all metadata you expect and use these when encountering records that don't carry metadata.

    To prevent name clashing with other implementations, each metadata key should contain the name of your outlet included in its body.

    Incorrect:

    .. rst-class:: highlight-small

        .. code-block:: python

            FILEPATH:metadata = 'FILEPATH'

    Correct:

    .. rst-class:: highlight-small

        .. code-block:: python

            FILEPATH:metadata = 'CsvOutlet.FILEPATH'



