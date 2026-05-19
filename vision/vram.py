import os
import glob
from typing import List
__all__ = ['get_vram']
def _find_amd_vram_paths():
    # Search for all possible card directories
    cards = glob.glob("/sys/class/drm/card*/device")
    
    for card in cards:
        # Check if this card actually belongs to the amdgpu driver
        uevent_path = os.path.join(card, "uevent")
        if os.path.exists(uevent_path):
            with open(uevent_path, 'r') as f:
                if "amdgpu" in f.read():
                    # Found an AMD GPU!
                    used_path = os.path.join(card, "mem_info_vram_used")
                    total_path = os.path.join(card, "mem_info_vram_total")
                    
                    if os.path.exists(used_path) and os.path.exists(total_path):
                        return used_path, total_path
    return None, None

def get_vram() -> List[float, float]:
    """Returns [vram_used, vram_total]"""
    used_p, total_p = _find_amd_vram_paths()
    
    if not used_p:
        print("Error: Could not find amdgpu mem_info in sysfs.")
        print("Try running: ls /sys/class/drm/card*/device/mem_info_vram_total")
        return
    u, t = 0, 0
    with open(used_p, "r") as f_used, open(total_p, "r") as f_total:
        used = int(f_used.read().strip())
        total = int(f_total.read().strip())
        u, t = float(f"{used/1024**2:.2f}"), float(f"{total/1024**2:.2f}")
    return u, t
