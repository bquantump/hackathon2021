from gnuradio import gr, gr_unittest
from gnuradio import blocks
from eventhubs import eventhub_detect_sink
import numpy as np
import os
import pmt

class qa_eventhub_detect_sink(gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_instance(self):

        eventhub_connection_str = os.environ["EVENTHUB_CONNECTION_STRING"]
        endpoint = os.environ['EVENTHUB_HOSTNAME']
        schema_group = os.environ['SCHEMA_REGISTRY_GROUP']
        eventhub_name = os.environ['EVENTHUB_CONSUMER_TOPIC_NAME']

        instance = eventhub_detect_sink(connection_str=eventhub_connection_str,
                                endpoint=endpoint,
                                schema_group=schema_group,
                                eventhub_name=eventhub_name)

        # really only checking that the init didn't throw an exception above, but adding the check
        # below to keep flake8 happy
        self.assertTrue(instance is not None)

        a = pmt.make_dict()
        a = pmt.dict_add(a, pmt.string_to_symbol("zc_root"), pmt.from_long(1))
        a = pmt.dict_add(a, pmt.string_to_symbol("chan_idx"), pmt.from_long(2))

        instance.handle_msg(a)


if __name__ == '__main__':
    gr_unittest.run(qa_eventhub_detect_sink)
