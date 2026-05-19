import network
import asyncio
import time

class Network:
    """
    A wrapper class to manage Wi-Fi connectivity for MicroPython devices.

    This class simplifies scanning for networks, managing connection states,
    and handling common hardware-level connection errors.

    Attributes:
        ssid (str): The name of the Wi-Fi network.
        password (str): The password for the Wi-Fi network.
        wlan (network.WLAN): The network interface object.
    """

    def __init__(self):
        """
        Initializes the Network class and activates the WLAN interface.
        """
        self.ssid = ""
        self.password = ""
        self.IP = ""
        self.wlan = network.WLAN(network.STA_IF)
        self.connected = self.wlan.isconnected
        if not self.wlan.active():
            self.wlan.active(True)
            
    async def wifi_monitor(self, check_time: int):
        """Background task to ensure Wi-Fi stays connected."""
        print("[wifi-monitor] Wi-Fi Monitor started...")
        while True:
            print("[wifi-monitor] ok")
            if not self.connected():
                print("[wifi-monitor] Wi-Fi lost! Attempting to reconnect...")
                if self.connect(self.ssid, self.password, retries=1):
                    print("[wifi-monitor] Wi-Fi restored!")
            await asyncio.sleep(check_time)
            
    def scan(self, print_details: bool = False) -> list[tuple[str, int]]:
        """
        Scans for available Wi-Fi networks and prints their details.

        Returns:
            list: A list of tuples containing (ssid, RSSI).
        """
        if print_details:
            print("Scanning for available networks...")
        networks = self.wlan.scan()
        ret = []
        for net in networks:
            ssid = net[0].decode('utf-8') if net[0] else "Hidden"
            rssi = net[3]
            if print_details:
                print(f"SSID: {ssid:20} | Strength: {rssi} dBm")
            ret.append((ssid, rssi))
        return ret

    def get_status_message(self):
        """
        Retrieves a human-readable string representing the current connection status.

        Returns:
            str: The current status message (e.g., "Connected (IP Assigned)", "Wrong Password").
        """
        status: int = self.wlan.status() # type: ignore
        
        messages = {
            network.STAT_IDLE: "Idle",
            network.STAT_CONNECTING: "Connecting...",
            network.STAT_WRONG_PASSWORD: "Wrong Password",
            network.STAT_NO_AP_FOUND: "Access Point Not Found",
            network.STAT_CONNECT_FAIL: "Connection Failed",
            network.STAT_GOT_IP: "Connected (IP Assigned)"
        }
        return messages.get(status, f"Unknown status: {status}")


    def fix_dns(self):
        """
        Internal helper used to fix issues regrading mip installation and dns failure
        used to set the dns to a known server like 8.8.8.8
        """
        if self.wlan.isconnected():
        # Get current config: (ip, subnet, gateway, dns)
            ip, subnet, gateway, current_dns = self.wlan.ifconfig()
            
            # Force DNS to Google (8.8.8.8)
            self.wlan.ifconfig((ip, subnet, gateway, '8.8.8.8'))
            

    async def connect(self, ssid: str, password: str, timeout=15, retries=2):
        """
        Attempts to connect to the configured Wi-Fi network with retries.

        Args:
            ssid (str): The name of the Wi-Fi network.
            password (str): The password for the Wi-Fi network.
            timeout (int): Seconds to wait for a connection per attempt. Defaults to 15.
            retries (int): Number of times to retry the hardware connection. Defaults to 2.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        self.ssid = ssid
        self.password = password

        if self.wlan.isconnected():
            print(f"Already connected! IP: {self.wlan.ifconfig()[0]}")
            return True

        for attempt in range(retries):
            print(f"Connection Attempt {attempt + 1}/{retries}...")
            
            # Force a clean hardware state
            self.wlan.active(False)
            await asyncio.sleep(0.5) 
            self.wlan.active(True)
            await asyncio.sleep(1.0)

            if not self.wlan.isconnected():
                self.wlan.connect(self.ssid, self.password)
                
                start_time = time.time()
                while not self.wlan.isconnected():
                    if (time.time() - start_time) > timeout:
                        print("Connection timeout")
                        break
                    
                    status = self.wlan.status()
                    if status == network.STAT_WRONG_PASSWORD:
                        print("Connection failed")
                        break 

                    print('.', end='')
                    await asyncio.sleep(0.5)

            if self.wlan.isconnected():
                self.IP = self.wlan.ifconfig()[0]
                print(f'\nSuccess! IP: {self.wlan.ifconfig()[0]}')
                self.fix_dns()
                return True
                
        
        return False