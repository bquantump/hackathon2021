#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import numpy as np
from gnuradio import gr
from azure.eventhub import EventHubConsumerClient
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import SchemaRegistryAvroSerializer
from azure.identity import DefaultAzureCredential
from eventhubs import models
import queue
import threading

schema_content = models.EventHubDataFrame.avro_schema()

class eventhub_source(gr.sync_block):

    def __init__(self,connection_str: str = None,
                 endpoint: str = None, schema_group: str = None, eventhub_name: str = None, consumer_group: str = None):

        gr.sync_block.__init__(self,
                        name="eventhub_source",
                        in_sig=[],
                        out_sig=[np.complex64])

        self.token_credential = DefaultAzureCredential()
        self.endpoint = endpoint
        self.schema_group = schema_group
        self.eventhub_connection_str = connection_str
        self.eventhub_name = eventhub_name
        self.consumer_group = consumer_group

        self.schema_registry_client = SchemaRegistryClient(self.endpoint, self.token_credential)
        self.avro_serializer = SchemaRegistryAvroSerializer(self.schema_registry_client, self.schema_group)

        self.eventhub_consumer = EventHubConsumerClient.from_connection_string(
            conn_str=self.eventhub_connection_str,
            consumer_group=self.consumer_group,
            eventhub_name=self.eventhub_name)

        self.q = queue.Queue()
        self.total_num_samples = 0
        self.lock = threading.Lock()
        self.rxthread = threading.Thread(target=self.receive)
        self.rxthread.start()

    def receive(self):
        self.eventhub_consumer.receive(on_event=self.on_event, starting_position="-1")


    def on_event(self, partition_context, event):
        bytes_payload = b"".join(b for b in event.body)
        deserialized_data = self.avro_serializer.deserialize(bytes_payload)
        print("packet n is %s" % deserialized_data['pkt_num'])
        if deserialized_data['imag'] != None and deserialized_data['real'] != None:
            samples = np.empty(len(deserialized_data['imag']), dtype=np.complex64)
            samples.real = deserialized_data['real']
            samples.imag = deserialized_data['imag']
            self.q.put(samples)
            self.lock.acquire()
            self.total_num_samples = self.total_num_samples + len(samples)
            self.lock.release()


    def work(self, input_items, output_items):
        out = output_items[0]
        noutput_items = len(out)
        nitems_produced = 0

        nitems_produced = min(self.total_num_samples, noutput_items)

        while not self.q.empty():
            print('total samples: %s noutput_items: %s out: %s'%(self.total_num_samples,noutput_items,out))
            samples = self.q.get()
            out[:nitems_produced] = samples
            nitems_produced = nitems_produced + len(samples)
            self.lock.acquire()
            self.total_num_samples = self.total_num_samples - len(samples)
            self.lock.release()

        return nitems_produced

    def stop(self):
        self.eventhub_consumer.close()
        self.rxthread.join()


