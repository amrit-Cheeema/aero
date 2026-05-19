
import bluetooth
import asyncio
from micropython import const 
import random
from gatt import N, SERIAL_NUMBER, DEVICE_NAME, COMPANY_ID
from gattBluetooth import BIOMARKER_SERVICE

# Bluetooth Constants
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_MTU_EXCHANGED = const(21)
_IRQ_GATTS_WRITE = const(3)


class BLEDevice:
    def __init__(self, UUID, name):
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        
        
        try:
            self.ble.config(tx_power=9)
        except:
            print("Could not set TX power")
            pass

        self.ble.irq(self.handle_irq)
        self.name = name
        self.conn_handle = None
        self.task_active = asyncio.Event()
        self.task_type = 0

        services = self.ble.gatts_register_services((BIOMARKER_SERVICE,))
        self.biomarker_char_handles = services[0][:N]
        self.biomarker_progress_handle = services[0][N]
        self.biomarker_control_handle = services[0][N+1]

        self.company_id = COMPANY_ID
        self.UUID = UUID
        self.payload = self._build_payload()

    def _build_payload(self):
        # Using a simple payload to ensure legacy ADV packet
        mfg_data = self.company_id + self.UUID
        adv_payload = (
            b'\x02\x01\x06' + 
            bytes([len(self.name) + 1, 0x09]) + self.name.encode() + 
            bytes([len(mfg_data) + 1, 0xFF]) + mfg_data
        )
        if len(adv_payload) > 31:
            name = "adv_error"
            return (
                b'\x02\x01\x06'+bytes([len(name) + 1, 0x09]) + name.encode()
            )
        return adv_payload

    def handle_irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            self.conn_handle, _, _ = data
            print(f"Connected (handle: {self.conn_handle})")
            
            # Request better connection parameters from Linux
            # (interval_min, interval_max, latency, timeout)
            # This makes the connection more stable on noisy links
            
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            if conn_handle == self.conn_handle and value_handle == self.biomarker_control_handle:
                cmd = self.ble.gatts_read(self.biomarker_control_handle)
                
                if len(cmd) == 2:
                    if cmd[0] == 0x01: # Start
                        if self.task_active.is_set():
                            return
                        self.task_type = cmd[1] if len(cmd) > 1 else 0
                        self.task_active.set()
                    elif cmd[0] == 0x00: # STOP
                        self.task_active.clear()

        elif event == _IRQ_CENTRAL_DISCONNECT:
            self.conn_handle = None
            print("Disconnected")
            self.advertise()
        elif event == _IRQ_MTU_EXCHANGED:
            print("MTU Exchanged")

    def advertise(self):
        # 100ms interval 
        self.ble.gap_advertise(100000, self.payload)
        print("Advertising...")

    def update_biomarker_service(self, values: list[int], progress: int):
        """
        implement read and notify for the biomarker service 
        
        :param values: this should exactly match N (number of chars implemented in gatt)
        :type values: list[int]
        :param progress: the progress indicator (how long until measurement is finished)
        """
        if len(values) != len(self.biomarker_char_handles) and len(values):
            print("data mismatch in biomarker service")
            return
        if progress < 0 or 100 < progress:
            print("progress is invalid")
            return
        
        # progress
        encoded_progress = progress.to_bytes(2, 'big')
        self.ble.gatts_write(self.biomarker_progress_handle, encoded_progress)
        
        if self.conn_handle is not None:
            try:
                # wrong stubs
                self.ble.gatts_notify(self.conn_handle, self.biomarker_progress_handle, encoded_progress)
            except OSError:
                pass
        # biomarkers
        encoded_data = [value.to_bytes(2, 'big') for value in values]
        for i, biomarker_handle in enumerate(self.biomarker_char_handles):
            self.ble.gatts_write(biomarker_handle, encoded_data[i])
            
            if self.conn_handle is not None:
                try:
                    self.ble.gatts_notify(self.conn_handle, biomarker_handle, encoded_data[i])
                except OSError:
                    pass


async def sensor_task(device: BLEDevice):
    while True:
        # wating for GATT READ on BLEDevice.biomarker_control_handle
        await device.task_active.wait()
        print("Sequence starting...")
        for progress in range(0, 101, 10):
            # Check if the event was cleared (STOP command) mid-run
            if not device.task_active.is_set():
                break
                
            # Simulate readings
            hr = random.randint(60, 100)
            print(f"Update: {hr} BPM, Progress: {progress}%")
            
            # Send to BLE
            device.update_biomarker_service([hr, hr-5], progress)
            
            await asyncio.sleep(1) # Frequency of updates
        
        print("Sequence complete. Going back to sleep.")
        device.task_active.clear()

async def main():
    device = BLEDevice(SERIAL_NUMBER, DEVICE_NAME)
    device.advertise()
    await asyncio.gather(sensor_task(device), )

try:
    asyncio.run(main())
except KeyboardInterrupt:
    # Clean shutdown
    print("Stopping...")
    ble = bluetooth.BLE()
    ble.active(False)
