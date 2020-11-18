import random
from datetime import timedelta

import elasticsearch
from databay import Inlet, Link, Outlet
from databay.inlets import RandomIntInlet
from databay.planners import ApsPlanner
from databay.record import Record
import time
import logging

TEXT = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Phasellus ex erat, viverra tincidunt tempus eget, hendrerit sed ligula. 
Quisque mollis nibh in imperdiet porttitor. Nulla bibendum lacus et est lobortis porta.
Nulla sed ligula at odio volutpat consectetur. Sed quis augue ac magna porta imperdiet interdum eu velit. 
Integer pretium ultrices urna, id viverra mauris ultrices ut. Etiam aliquet tellus porta nisl eleifend, non hendrerit nisl sodales. 
Aliquam eget porttitor enim. 
"""


class DummyTextInlet(Inlet):

    def __init__(self, text: list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text
        self._id = 0

    def pull(self, update):
        text_selection = random.choice(self.text)
        self._id += 1
        time.sleep(1)
        return {self._id: text_selection}


class ElasticSearchIndexerOutlet(Outlet):

    def __init__(self, es_client: elasticsearch.Elasticsearch, index_name: str, overwrite_documents: bool = True):
        super().__init__()
        self.es_client = es_client
        self.index_name = index_name
        self.overwrite_documents = overwrite_documents

        try:
            assert self.es_client.indices.exists(self.index_name)

        except:
            raise RuntimeError(f"Index '{self.index_name}' does not exist ")

    def push(self, records: [Record], update):
        print("starting")
        for record in records:

            payload = record.payload
            for k in payload.keys():
                _id = k
                text = payload[k]
                body = {"my_document": text}
                if self.overwrite_documents:
                    self.es_client.index(
                        self.index_name, body, id=_id, doc_type="json")
                    logging.info("Indexed document with id ", _id)
                    print(es_client.search(index=self.index_name,body={"query": {"match_all": {}}}))
                else:
                    if self.es_client.exists(self.index_name, _id):
                        # log that it is not possible
                        logging.info(f"Document already exists for id {_id}. Skipping.")
                    else:
                        self.es_client.index(
                            self.index_name, body, id=_id, doc_type="json")
                        logging.info("Indexed document with id ", _id)



es_client = elasticsearch.Elasticsearch(timeout=30)
random_int_inlet = DummyTextInlet(TEXT.split("."))
elasticsearch_outlet = ElasticSearchIndexerOutlet(es_client, "my-test-index")

link = Link(random_int_inlet,
            elasticsearch_outlet,
            interval=2,
            tags='print_outlet')

planner = ApsPlanner(link)
planner.start()
