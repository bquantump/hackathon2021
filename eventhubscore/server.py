import os
from azure.eventhub import EventHubConsumerClient
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import SchemaRegistryAvroSerializer
from azure.identity import DefaultAzureCredential
import time
import models

token_credential = DefaultAzureCredential()
endpoint = "hackathon2021.servicebus.windows.net"
schema_group = "rfframe"
eventhub_connection_str = os.environ["CONNECTION_STRING"]
eventhub_name = "rfinfo"

schema_registry_client = SchemaRegistryClient(endpoint, token_credential)
avro_serializer = SchemaRegistryAvroSerializer(schema_registry_client, schema_group)

eventhub_consumer = EventHubConsumerClient.from_connection_string(
    conn_str=eventhub_connection_str,
    consumer_group='$Default',
    eventhub_name=eventhub_name,
)
models.start = time.perf_counter()

def on_event(partition_context, event):
    bytes_payload = b"".join(b for b in event.body)
    deserialized_data = avro_serializer.deserialize(bytes_payload)
    print("packet n is %s" % deserialized_data['packet_num'])
    ##models.count += 1
    #models.total += len(bytes_payload)
    if (models.count % 20 == 0):
        val = models.total / (time.perf_counter() - models.start)
        #print("bytest per second %s " % val)
        #models.start = time.perf_counter()
        #models.total = 0


with eventhub_consumer, avro_serializer:
    eventhub_consumer.receive(on_event=on_event, starting_position="-1")