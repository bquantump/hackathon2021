#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import numpy as np
from gnuradio import gr
from azure.eventhub import EventHubProducerClient, EventData
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import SchemaRegistryAvroSerializer
from azure.identity import DefaultAzureCredential
from eventhubs import models
import math

schema_content = models.EventHubDataFrame.avro_schema()

class eventhub_sink(gr.sync_block):

    def __init__(self,connection_str: str = None,
                 endpoint: str = None, schema_group: str = None, eventhub_name: str = None, block_len: int = None):

        gr.sync_block.__init__(self,
                        name="eventhub_sink",
                        in_sig=[np.complex64],
                        out_sig=[])

        self.token_credential = DefaultAzureCredential()
        self.endpoint = endpoint
        self.schema_group = schema_group
        self.eventhub_connection_str = connection_str
        self.eventhub_name = eventhub_name
        self.block_len = block_len/2 # payload data bytes is less with avro overhead 

        self.schema_registry_client = SchemaRegistryClient(self.endpoint, self.token_credential)
        self.avro_serializer = SchemaRegistryAvroSerializer(self.schema_registry_client, self.schema_group)

        self.eventhub_producer = EventHubProducerClient.from_connection_string(
            conn_str=self.eventhub_connection_str,
            eventhub_name=self.eventhub_name)
        self.data = np.array(block_len, dtype=complex)
        self.idx = 0
        self.pack_count = 0
        
    def work(self, input_items, output_items):
        samples = input_items[0]

        samps_to_fill = min(len(samples), len(self.data) - self.idx)
        self.data[self.idx:self.idx + samps_to_fill] = samples[0:samps_to_fill]
        self.idx += samps_to_fill
        if self.idx >= len(self.data):
            msg = models.EventHubDataFrame(list(self.data.real),\
                    list(self.data.imag),\
                    self.pack_count,\
                    1,\
                    "eventhub_sink")
            event_data_batch = self.eventhub_producer.create_batch()
            payload_bytes = self.avro_serializer.serialize(data=msg.asdict(), schema=schema_content)
            #print(len(payload_bytes))
            event_data_batch.add(EventData(body=payload_bytes))
            self.eventhub_producer.send_batch(event_data_batch)
            self.idx = 0
            self.pack_count += 1


        return samps_to_fill

    def stop(self):
        self.eventhub_producer.close()

        return True

