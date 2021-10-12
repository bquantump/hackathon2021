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

        eventhub_connection_str = os.environ["CONNECTION_STRING"]

        instance = eventhub_sink(connection_str=eventhub_connection_str,
                                endpoint="hackathon2021.servicebus.windows.net",
                                schema_group="rfframe",
                                eventhub_name="rfinfo")

        # really only checking that the init didn't throw an exception above, but adding the check
        # below to keep flake8 happy
        self.assertTrue(instance is not None)


if __name__ == '__main__':
    gr_unittest.run(qa_blob_sink)
