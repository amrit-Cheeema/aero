import bluetooth
from gatt import *

_FLAG_READ = bluetooth.FLAG_READ
_FLAG_NOTIFY = bluetooth.FLAG_NOTIFY
_FLAG_WRITE = bluetooth.FLAG_WRITE

BIOMARKER_UUID = bluetooth.UUID(BIOMARKER_INT)
BASE_MESUREMENT_UUID = BASE_MESUREMENT_INT # Base UUID for biomarker measurements
BIOMARKER_N_MEASUREMENT_UUIDS = [bluetooth.UUID(BASE_MESUREMENT_UUID + i) for i in range(N)]
PROGRESS_UUID = bluetooth.UUID(PROGRESS_INT)     # For 0-100 updates
CONTROL_POINT_UUID = bluetooth.UUID(CONTROL_POINT_INT) # For client -> server commands

characteristics = []
for m_uuid in BIOMARKER_N_MEASUREMENT_UUIDS: characteristics.append((m_uuid, _FLAG_READ | _FLAG_NOTIFY))
characteristics.append((PROGRESS_UUID, _FLAG_READ | _FLAG_NOTIFY))
characteristics.append((CONTROL_POINT_UUID, _FLAG_WRITE))
BIOMARKER_SERVICE = (
    BIOMARKER_UUID,
    tuple(characteristics),
)