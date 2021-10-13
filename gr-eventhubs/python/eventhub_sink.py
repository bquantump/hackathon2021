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

    def work(self, input_items, output_items):
        samples = input_items[0]

        # get size of input and chunk it into block size parts
        number_of_blocks = math.ceil(len(samples)*gr.sizeof_gr_complex/self.block_len)
        number_of_samples_per_block = int(self.block_len/gr.sizeof_gr_complex)
        #print('inputlen: %s numsamples: %s numblocks: %s samplesperblock: %s'%(len(input_items),len(samples),number_of_blocks,number_of_samples_per_block))
        data = np.array(samples,dtype=complex)

        for idx in range(0,number_of_blocks):
            msg = models.EventHubDataFrame(list(data[idx*number_of_samples_per_block:idx*number_of_samples_per_block+number_of_samples_per_block].real),\
                    list(data[idx*number_of_samples_per_block:idx*number_of_samples_per_block+number_of_samples_per_block].imag),\
                    idx,\
                    number_of_blocks,\
                    "eventhub_sink")
            event_data_batch = self.eventhub_producer.create_batch()
            payload_bytes = self.avro_serializer.serialize(data=msg.asdict(), schema=schema_content)
            #print(len(payload_bytes))
            event_data_batch.add(EventData(body=payload_bytes))
            self.eventhub_producer.send_batch(event_data_batch)

        return len(samples)

    def stop(self):
        self.eventhub_producer.close()

        return True

