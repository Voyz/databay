import logging
import random
import time
from typing import List

import elasticsearch
from databay import Inlet, Link, Outlet
from databay.planners import ApsPlanner
from databay.record import Record

TEXT = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Phasellus ex erat, viverra tincidunt tempus eget, hendrerit sed ligula. 
Quisque mollis nibh in imperdiet porttitor. Nulla bibendum lacus et est lobortis porta.
Nulla sed ligula at odio volutpat consectetur. Sed quis augue ac magna porta imperdiet interdum eu velit. 
Integer pretium ultrices urna, id viverra mauris ultrices ut. Etiam aliquet tellus porta nisl eleifend, non hendrerit nisl sodales. 
Aliquam eget porttitor enim. 
"""

_LOGGER = logging.getLogger('databay.elasticsearch_outlet')


class ElasticSearchIndexerOutlet(Outlet):
    " An example outlet for indexing text documents from any `Inlet`."

    def __init__(self, es_client: elasticsearch.Elasticsearch, index_name: str, overwrite_documents: bool = True):
        super().__init__()
        self.es_client = es_client
        self.index_name = index_name

        # if true existing documents will be overwritten
        # otherwise we will skip indexing and log that document id exists in index.
        self.overwrite_documents = overwrite_documents

        if self.es_client.indices.exists(self.index_name):
            pass
        else:
            raise RuntimeError(f"Index '{self.index_name}' does not exist ")

    def push(self, records: List[Record], update):
        for record in records:

            payload = record.payload

            # using dict keys from payload as unique id for index
            for k in payload.keys():
                _id = k
                text = payload[k]
                body = {"my_document": text}
                if self.overwrite_documents:
                    self.es_client.index(
                        self.index_name, body, id=_id)
                    _LOGGER.info(f"Indexed document with id {_id}")

                else:
                    if self.es_client.exists(self.index_name, _id):
                        # log that it is not possible
                        _LOGGER.info(
                            f"Document already exists for id {_id}. Skipping.")
                    else:
                        self.es_client.index(
                            self.index_name, body, id=_id)
                        _LOGGER.info(f"Indexed document with id {_id}")


class DummyTextInlet(Inlet):
    "A simple `Inlet` that randomly pulls a string from a list of strings."

    def __init__(self, text: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text
        self._id = 0

    def pull(self, update):
        text_selection = random.choice(self.text)
        self._id += 1
        time.sleep(1)
        return {self._id: text_selection}


_LOGGER.setLevel(logging.INFO)

es_client = elasticsearch.Elasticsearch(timeout=30)
text_inlet = DummyTextInlet(TEXT.split("."))

elasticsearch_outlet = ElasticSearchIndexerOutlet(
    es_client, "my-test-index", overwrite_documents=False)

link = Link(text_inlet,
            elasticsearch_outlet,
            interval=2,
            tags='elasticsearch_outlet')

planner = ApsPlanner(link)
planner.start()
