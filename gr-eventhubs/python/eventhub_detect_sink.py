#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import numpy as np
import pmt
from gnuradio import gr

from azure.eventhub import EventHubProducerClient, EventData
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import SchemaRegistryAvroSerializer
from azure.identity import DefaultAzureCredential
from eventhubs import models

schema_content = models.EventHubDetectFrame.avro_schema()

class eventhub_detect_sink(gr.sync_block):

    def __init__(self,connection_str: str = None,
                 endpoint: str = None, schema_group: str = None, eventhub_name: str = None):

        gr.sync_block.__init__(self,
                        name="eventhub_detect_sink",
                        in_sig=[],
                        out_sig=[])

        self.token_credential = DefaultAzureCredential()
        self.endpoint = endpoint
        self.schema_group = schema_group
        self.eventhub_connection_str = connection_str
        self.eventhub_name = eventhub_name

        self.schema_registry_client = SchemaRegistryClient(self.endpoint, self.token_credential)
        self.avro_serializer = SchemaRegistryAvroSerializer(self.schema_registry_client, self.schema_group)

        self.eventhub_producer = EventHubProducerClient.from_connection_string(
            conn_str=self.eventhub_connection_str,
            eventhub_name=self.eventhub_name)

        self.message_port_register_in(pmt.intern('in'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)

    def handle_msg(self, msg):
        pmsg = pmt.to_python(msg)
        zc_root = pmsg['zc_root']
        channel_idx = pmsg['chan_idx']
        timestamp=0
        score=0

        if 'timestamp' in pmsg:
            timestamp = pmsg['timestamp']
        if 'score' in pmsg:
            score = pmsg['score']
        
        event_msg = models.EventHubDetectFrame(zc_root, channel_idx, timestamp, score, "eventhub_detect_sink")
        event_data_batch = self.eventhub_producer.create_batch()
        payload_bytes = self.avro_serializer.serialize(data=event_msg.asdict(), schema=schema_content)
        #print(len(payload_bytes))
        event_data_batch.add(EventData(body=payload_bytes))
        self.eventhub_producer.send_batch(event_data_batch)

    def work(self, input_items, output_items):
        return 0

    def stop(self):
        self.eventhub_producer.close()
        return True


