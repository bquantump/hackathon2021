import typing
from dataclasses_avroschema import AvroModel
from dataclasses import dataclass
count = 0
total = 0
start = None
@dataclass
class DataFrame(AvroModel):
    samples: typing.List[int]
    packet_num: int
    frame_num: int
    source: str

    class Meta:
        namespace = "hackathon2021"

#@TODO message to pub back to clients


#TODO Message to send secret ZC to clients


