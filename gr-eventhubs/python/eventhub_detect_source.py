#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gnuradio import gr
from azure.eventhub import EventHubConsumerClient
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import SchemaRegistryAvroSerializer
from azure.identity import DefaultAzureCredential
from eventhubs import models

import threading
import pmt

schema_content = models.EventHubDataFrame.avro_schema()

class eventhub_detect_source(gr.sync_block):

    def __init__(self,connection_str: str = None,
                 endpoint: str = None, schema_group: str = None, eventhub_name: str = None, consumer_group: str = None, starting_position = None):

        gr.sync_block.__init__(self,
                        name="eventhub_detect_source",
                        in_sig=[],
                        out_sig=[])

        self.token_credential = DefaultAzureCredential()
        self.endpoint = endpoint
        self.schema_group = schema_group
        self.eventhub_connection_str = connection_str
        self.eventhub_name = eventhub_name
        self.consumer_group = consumer_group
        self.starting_position = starting_position

        self.schema_registry_client = SchemaRegistryClient(self.endpoint, self.token_credential)
        self.avro_serializer = SchemaRegistryAvroSerializer(self.schema_registry_client, self.schema_group)

        self.eventhub_consumer = EventHubConsumerClient.from_connection_string(
            conn_str=self.eventhub_connection_str,
            consumer_group=self.consumer_group,
            eventhub_name=self.eventhub_name)

        self.message_port_register_out(pmt.intern('detect_msg'))

        self.rxthread = threading.Thread(target=self.receive)
        self.rxthread.start()

    def receive(self):
        self.eventhub_consumer.receive(on_event=self.on_event, starting_position=self.starting_position)
        

    def on_event(self, partition_context, event):
        bytes_payload = b"".join(b for b in event.body)
        deserialized_data = self.avro_serializer.deserialize(bytes_payload)
        #print("packet n is %s" % deserialized_data['pkt_num'])
        if deserialized_data['zc_root'] != None and deserialized_data['channel_idx'] != None:
            a = pmt.make_dict()
            a = pmt.dict_add(a, pmt.string_to_symbol("zc_root"), pmt.from_long(deserialized_data['zc_root']))
            a = pmt.dict_add(a, pmt.string_to_symbol("chan_idx"), pmt.from_long(deserialized_data['channel_idx']))
            self.message_port_pub(pmt.intern("detect_msg"), a)


    def work(self, input_items, output_items):
        return 0

    def stop(self):
        self.eventhub_consumer.close()
        self.rxthread.join()


