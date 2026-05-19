import typer
import esptool
import serial.tools.list_ports
from typing import Optional
import os
import sys
from mpremote.main import main as mpremoteMain
import interface_helpers.helper as helper
from interface_helpers.config import *

app = typer.Typer(help="🚀 Pro ESP32 Helper Utility using esptool engine")
detection_keywords = helper.detection_keywords

@app.command()
def scan():
    """List all available serial ports and descriptions."""
    ports = serial.tools.list_ports.comports()
    if not ports:
        typer.secho("❌ No ports found!", fg=typer.colors.RED)
        return
    for p in ports:
        for key in detection_keywords:
            if key in p.description:
                typer.secho(f"✅ {p.device}: {p.description}", fg=typer.colors.GREEN)
                break
        else:
            typer.echo(f"?? {p.device}: {p.description}")

@app.command()
def info(port: Optional[str] = typer.Option(None, help="Serial port (auto-detects if omitted)")):
    """Get detailed chip information (MAC, Flash ID, Chip Type)."""
    target_port = helper.getPort(port)
    typer.secho(target_port)
    typer.echo(f"🔍 Querying device on {target_port}...")
    
    chip_info, warnings = helper.get_chip_details(target_port)

    # Output formatting
    typer.secho("\n--------------------------------------\n--------------------------------------", fg=typer.colors.CYAN, bold=True)
    for key, value in chip_info.items():
        if value == "Unknown":
            typer.secho(f"{typer.style(key, bold=True)}: {value}", fg=typer.colors.BRIGHT_RED)
        else:
            typer.secho(f"{typer.style(key, bold=True)}: {value}", fg=typer.colors.GREEN)

    if warnings:
        for w in warnings:
            typer.echo(f" - {w}")

@app.command()
def erase(port: Optional[str] = typer.Option(None)):
    """Wipe the entire flash memory of the ESP32."""
    target_port = helper.getPort(port)
    if typer.confirm(f"⚠️ Are you sure you want to ERASE flash on {target_port}?"):
        esptool.main(["--port", target_port, "erase-flash"])

@app.command()
def flash(
    file: str = typer.Argument(..., help="Path to the .bin firmware"),
    port: Optional[str] = typer.Option(None),
    address: str = "0x1000",
    baud: int = 115200
):
    """Flash a firmware file to the device."""
    target_port = helper.getPort(port)
    typer.secho(f"⚡ Flashing {file} to {target_port} at {address}...", fg=typer.colors.CYAN)
    
    args = [
        "--port", target_port,
        "--baud", str(baud),
        "write-flash", "-z", address, file
    ]
    esptool.main(args)

@app.command()
def run(
    port: Optional[str] = typer.Option(None),
    project: str = typer.Argument(..., help=f"project name inside {ESP_PROJECT_DIR}")
):
    """run project inside ESP_PROJECT_DIR."""
    if project == "_lib":
        typer.secho("_lib is reserved", err=True)
        return
    target_port = helper.getPort(port)
    typer.secho(f"⚡ Running {ESP_PROJECT_DIR}/{project} on {target_port}...", fg=typer.colors.CYAN)
    
    # storing orginal args
    commands = [
    ]
    original_args = sys.argv

    # copying all files in the dir
    for file in os.listdir(f"{ESP_PROJECT_DIR}/{project}"):
        if file.endswith(".py"):
            commands.append(
                ["mpremote", "connect", target_port, "cp", f"{ESP_PROJECT_DIR}/{project}/{file}", f":/{file}"]
            )
    
    # copying _lib
    commands.append(["mpremote", "connect", target_port, "mkdir", "_lib"])
    for file in os.listdir(f"{ESP_PROJECT_DIR}/_lib"):
        if file.endswith(".py"):
            commands.append(
                ["mpremote", "connect", target_port, "cp", f"{ESP_PROJECT_DIR}/_lib/{file}", f":/_lib/{file}"]
            )
    # reseting at the end and running
    commands.append(["mpremote", "connect", target_port, f"soft-reset"])
    for cmd in commands:
        sys.argv = cmd
        mpremoteMain()

    # running main on esp
    sys.argv = original_args
    esptool.main(["--port", target_port, "run"])
    # launch repl
    sys.argv = ["mpremote", "connect", target_port, "repl"]
    mpremoteMain()
    
    
    
@app.command()
def reset(
    port: Optional[str] = typer.Option(None)
):
    """Reset the ESP32 device."""
    target_port = port or helper.get_auto_port()
    typer.secho(f"🔄 Resetting device on {target_port}...", fg=typer.colors.CYAN)
    if not target_port:
        typer.secho("❌ Could not auto-detect port.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    MAC = helper.get_chip_details(target_port)[0]["MAC"]
    helper.clear_serial_port(target_port)
    # helper.reset_bluetooth_device(target_port, MAC)
    esptool.main(["--port", target_port, "run"])

@app.command()
def create(
    name: str = typer.Argument(..., help=f"The name of the project and folder stored in {ESP_PROJECT_DIR}")
):
    os.umask(0)
    try:
        os.makedirs(f"{ESP_PROJECT_DIR}/{name}", exist_ok=False)
    except OSError:
        typer.secho(f"Project name: {name} already taken")
        return
    if not os.path.isdir(f"{ESP_PROJECT_DIR}/_lib"): os.makedirs(f"{ESP_PROJECT_DIR}/{name}", exist_ok=True)
    os.symlink(f"{ESP_PROJECT_DIR}/_lib", f"{ESP_PROJECT_DIR}/{name}/_lib")


def main():
    helper.require_admin()
    helper.clear_serial_port(helper.get_auto_port())
    app()

if __name__ == "__main__":
    main()