
import os
from azure.eventhub import EventHubProducerClient, EventData
from azure.schemaregistry import SchemaRegistryClient
from azure.schemaregistry.serializer.avroserializer import SchemaRegistryAvroSerializer
from azure.identity import DefaultAzureCredential
from models import DataFrame

token_credential = DefaultAzureCredential()
endpoint = "hackathon2021.servicebus.windows.net"
schema_group = "rfframe"
eventhub_connection_str = os.environ["EVENTHUB_CONNECTION_STRING"]
eventhub_name = "rfinfo2"
schema_content = DataFrame.avro_schema()


schema_registry_client = SchemaRegistryClient(endpoint, token_credential)
avro_serializer = SchemaRegistryAvroSerializer(schema_registry_client, schema_group)

eventhub_producer = EventHubProducerClient.from_connection_string(
    conn_str=eventhub_connection_str,
    eventhub_name=eventhub_name
)
data = [1,0] * 100000
mock_msg = DataFrame( data, 0,0,"steves pc!")
with eventhub_producer, avro_serializer:
    c = 0
    while c < 10000:
        mock_msg = DataFrame( data, c,0,"steves pc!")
        event_data_batch = eventhub_producer.create_batch()
        payload_bytes = avro_serializer.serialize(data=mock_msg.asdict(), schema=schema_content)
        print(len(payload_bytes))
        event_data_batch.add(EventData(body=payload_bytes))
        eventhub_producer.send_batch(event_data_batch)
        c+=1