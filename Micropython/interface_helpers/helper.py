import typer
import esptool
import serial.tools.list_ports
import io
from contextlib import redirect_stdout
import subprocess
import os
import sys
import time

detection_keywords = ["CP210", "CH340", "USB to UART", "UART Bridge"]
def get_chip_details(port: str) -> tuple[dict[str, str], list[str]]:
    """
    Connects to the ESP chip once and retrieves all metadata.
    """
    # Define what we are looking for and the storage for warnings
    esp_data = {
        "Chip type": "Chip type",
        "Features": "Features",
        "Crystal frequency": "Crystal frequency",
        "MAC:": "MAC",
        "Manufacturer:": "Flash Memory Manufacturer",
        "Device:": "Flash Memory Device",
        "Flash voltage set by a strapping pin:": "Flash Memory voltage",
        "Detected flash size": "Flash Memory size",
    }
    
    results = {v: "Unknown" for v in esp_data.values()}
    warnings = []
    
    def capture_output(command):
        try:
            f = io.StringIO()
            with redirect_stdout(f):
                esptool.main(command)
            
            output = f.getvalue()
            lines = output.splitlines()

            for line in lines:
                # Check for warnings
                if "Warning:" in line:
                    warnings.append(line.strip())
                
                # Map output to our dictionary
                for key, label in esp_data.items():
                    if key in line:
                        parts = line.split(":", 1)
                        if len(parts) > 1:
                            results[label] = parts[1].strip()
            # print(output)
        except Exception as e:
            typer.secho(f"❌ Failed to get info: {e}", fg=typer.colors.RED)
            
    commands =  [
                    ["--port", port, "chip-id"],
                    ["--port", port, "flash-id"],
                    # ["--port", port, "image-info"],
                ]
    for cmd in commands: capture_output(cmd)
    return results, list(set(warnings))

def get_auto_port() -> str | None:
    """ 
    Detects the most likely ESP32 port automatically.
    Returns the first port string if found, else None.
    """
    ports = serial.tools.list_ports.comports()
    # Common USB-to-UART chip descriptions
    for p in ports:
        if any(key in p.description for key in detection_keywords):
            return p.device
    return None

def clear_serial_port(port):
    try:
        subprocess.run(
            ["sudo", "fuser", "-k", port],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print(f"Failed to clear port: {e}")

def is_admin():
    try:
        # For Windows
        if os.name == 'nt':
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        # For Linux/macOS
        else:
            return os.getuid() == 0
    except AttributeError:
        return False

def require_admin():
    if not is_admin():
        print("Error: This utility requires administrator/root privileges.")
        print("Please re-run the command using 'sudo' or as an Administrator.")
        sys.exit(1)

def getPort(port: str | None):
    target_port = port or get_auto_port()
    if not target_port:
        typer.secho("❌ Could not auto-detect port.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    return target_port

def reset_bluetooth_device(port: str, mac_address: str):
    # mac_address = "00:70:07:17:D5:8A"
    commands = [
        f"disconnect {mac_address}",
        f"untrust {mac_address}",
        f"remove {mac_address}",
        f"scan off",
        "power off",
        "power on",
        "scan on",
    ]
    
    try:
        for cmd in commands:
            # Runs bluetoothctl and pipes the command into it
            process = subprocess.run(
                ['bluetoothctl'], 
                input=cmd, 
                text=True, 
                capture_output=True, 
                check=True
            )
            
            typer.secho(f"Executed: {cmd}", fg=typer.colors.GREEN)
            time.sleep(5)
            
        print(f"\nSuccessfully reset device: {mac_address}")
        print("Please put your device into pairing mode and reconnect.")
        
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr}")

