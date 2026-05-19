

SERIAL_NUMBER=b'\x01\x02\x03\x04\x05\x06'
DEVICE_NAME="Nextfuge"
COMPANY_ID=b'\xdd\xee' 
N = 2  # Number of biomarker measurements

BIOMARKER_INT = 0x180D
BASE_MESUREMENT_INT = 0x2A37 # Base UUID for biomarker measurements
BIOMARKER_N_MEASUREMENT_INTS = [BASE_MESUREMENT_INT + i for i in range(N)]
PROGRESS_INT = 0x2A52     # For 0-100 updates
CONTROL_POINT_INT = 0x2A55 # For client -> server commands


TASK_TYPES = {
    
}