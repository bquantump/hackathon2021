from gnuradio import gr, gr_unittest
from gnuradio import blocks
import numpy as np
import os
from eventhubs import eventhub_sink


class qa_eventhub_sink(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_instance(self):

        eventhub_connection_str = os.environ["EVENTHUB_CONNECTION_STRING"]
        endpoint = os.environ['EVENTHUB_HOSTNAME']
        schema_group = os.environ['SCHEMA_REGISTRY_GROUP']
        eventhub_name = os.environ['EVENTHUB_CONSUMER_TOPIC_NAME']

        instance = eventhub_sink(connection_str=eventhub_connection_str,
                                endpoint=endpoint,
                                schema_group=schema_group,
                                eventhub_name=eventhub_name,
                                block_len=512)

        # really only checking that the init didn't throw an exception above, but adding the check
        # below to keep flake8 happy
        self.assertTrue(instance is not None)

        instance.work([np.linspace(1.0, 100.0, num=100)],None)


if __name__ == '__main__':
    gr_unittest.run(qa_eventhub_sink)
