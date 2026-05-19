from machine import UART
import asyncio
from _lib.micropyGPS import MicropyGPS
from logger import Logger
sensors = {
    "Latitude":  [],
    "Longitude": [],
    "Sat": 0
}
def GPS(gps_uart: UART,monitor: MicropyGPS) -> list[list]:
    if gps_uart.any():
        data = gps_uart.read()
        
        if data:
            
            for byte in data:
                monitor.update(chr(byte))
        sensors["Sat"] = monitor.satellites_in_use
        return [monitor.latitude, monitor.longitude]
    else:
        return [[0, 0.0, "N"], [0, 0.0, "W"]]
                    
async def sensor_task(gps_uart: UART, monitor: MicropyGPS, logger: Logger):
    
    while True:
        sensors["Latitude"], sensors["Longitude"] = GPS(gps_uart, monitor)
        
        logger.info(f"Sensor Data: {sensors["Sat"], sensors['Latitude']}")
        await asyncio.sleep(1)