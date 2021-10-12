#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import numpy as np
from gnuradio import gr
from azure.eventhub import EventHubProducerClient, EventData
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import SchemaRegistryAvroSerializer
from azure.identity import DefaultAzureCredential
from models import DataFrame

schema_content = DataFrame.avro_schema()

class eventhub_sink(gr.sync_block):

    def __init__(self,connection_str: str = None,
                 endpoint: str = None, schema_group: str = None, eventhub_name: str = None):

        gr.sync_block.__init__(self,
                        name="eventhub_sink",
                        in_sig=[np.complex64],
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

    def work(self, input_items, output_items):

        for data in input_items:
            with self.eventhub_producer, self.avro_serializer:
                msg = DataFrame(data,0,0,"testing")
                event_data_batch = self.eventhub_producer.create_batch()
                payload_bytes = self.avro_serializer.serialize(data=msg.asdict(), schema=self.schema_content)
                event_data_batch.add(EventData(body=payload_bytes))
                self.eventhub_producer.send_batch(event_data_batch)
                print('sending msg of length %s'%len(payload_bytes))


