import typing
from dataclasses_avroschema import AvroModel
from dataclasses import dataclass
import numpy as np

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

@dataclass
class EventHubDataFrame(AvroModel):
    real: typing.List[float]
    imag: typing.List[float]
    pkt_num: int
    total_pkt: int
    source: str

    class Meta:
        namespace = "hackathon2021"

@dataclass
class EventHubDetectFrame(AvroModel):
    zc_root: int
    channel_idx: int
    timestap: int
    score: float
    source: str

    class Meta:
        namespace = "hackathon2021"
