import os
from azure.eventhub import EventHubConsumerClient
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import SchemaRegistryAvroSerializer
from azure.identity import DefaultAzureCredential
import time
from eventhubcore import models


def run_server(consumer_group):
    consumer_group = consumer_group or '$Default'
    token_credential = DefaultAzureCredential()
    endpoint = os.environ['EVENTHUB_HOSTNAME']
    schema_group = os.environ['SCHEMA_REGISTRY_GROUP']
    eventhub_connection_str = os.environ['EVENTHUB_CONNECTION_STRING']
    eventhub_name = os.environ['EVENTHUB_CONSUMER_TOPIC_NAME']

    schema_registry_client = SchemaRegistryClient(endpoint, token_credential)
    avro_serializer = SchemaRegistryAvroSerializer(schema_registry_client, schema_group)

    eventhub_consumer = EventHubConsumerClient.from_connection_string(
        conn_str=eventhub_connection_str,
        consumer_group=consumer_group,
        eventhub_name=eventhub_name,
    )
    models.start = time.perf_counter()

    def on_event(partition_context, event):
        bytes_payload = b"".join(b for b in event.body)
        deserialized_data = avro_serializer.deserialize(bytes_payload)
        print("packet n is %s" % deserialized_data['packet_num'])

    with eventhub_consumer, avro_serializer:
        eventhub_consumer.receive(on_event=on_event, starting_position="-1")

if __name__ == '__main__':
    run_server(None)