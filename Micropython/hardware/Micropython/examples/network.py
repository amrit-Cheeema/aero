from _lib.network import Network
import asyncio


net = Network()
SSID = "Amrit"
PASSWORD = "AmritWifi!"  # Replace with the actual password
nets = net.scan()
if SSID in [net[0] for net in nets]:
    connection = asyncio.run(net.connect(SSID, PASSWORD))
    if connection:
        print(f"Successfully connected to {SSID}")
    else:
        print(f"Failed to connect to {SSID}. Status message: {net.get_status_message()}")
    
    asyncio.run(net.wifi_monitor(check_time=10))
else:
    print(f"Network {SSID} not found")
