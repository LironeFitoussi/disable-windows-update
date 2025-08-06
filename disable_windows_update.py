import subprocess
import ctypes
import sys
import platform

# Check if running on Windows
if platform.system() != "Windows":
    print("[-] This script only works on Windows systems.")
    sys.exit(1)

import winreg

def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except AttributeError:
        # Not on Windows or missing windll
        return False
    except Exception as e:
        print(f"[-] Error checking admin privileges: {e}")
        return False

def disable_windows_update_service():
    """Disable the Windows Update service."""
    print("[*] Disabling Windows Update service...")
    
    try:
        # Stop the service
        result = subprocess.run(["sc", "stop", "wuauserv"], shell=True, capture_output=True, text=True)
        if result.returncode != 0 and "service is not started" not in result.stderr.lower():
            print(f"[-] Warning: Failed to stop service: {result.stderr.strip()}")
        
        # Disable the service
        result = subprocess.run(["sc", "config", "wuauserv", "start=", "disabled"], shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("[+] Service disabled successfully.")
        else:
            print(f"[-] Failed to disable service: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"[-] Error managing Windows Update service: {e}")
        return False
    
    return True

def set_update_policies():
    """Set registry keys to block Windows Update."""
    print("[*] Setting registry keys to block Windows Update...")

    try:
        key_path = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
        
        # Create the registry key if it doesn't exist
        winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        
        # Open the key for writing
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)

        # Set NoAutoUpdate to 1 (Disable automatic updates)
        winreg.SetValueEx(key, "NoAutoUpdate", 0, winreg.REG_DWORD, 1)
        
        # Set AUOptions to 1 (Never check for updates)
        winreg.SetValueEx(key, "AUOptions", 0, winreg.REG_DWORD, 1)

        winreg.CloseKey(key)
        print("[+] Registry keys applied successfully.")
        return True

    except PermissionError:
        print("[-] Permission denied while writing to registry.")
        print("[-] Make sure you're running as Administrator.")
        return False
    except Exception as e:
        print(f"[-] Error setting registry policies: {e}")
        return False

def main():
    """Main function to disable Windows Updates."""
    print("Windows Update Disabler")
    print("=" * 30)
    
    if not is_admin():
        print("[-] This script must be run as administrator.")
        print("[-] Right-click and run as Administrator or use an elevated command prompt.")
        input("Press Enter to exit...")
        sys.exit(1)

    success = True
    
    # Disable the Windows Update service
    if not disable_windows_update_service():
        success = False
    
    # Set registry policies
    if not set_update_policies():
        success = False
    
    if success:
        print("\n[✓] Windows Updates have been disabled successfully.")
        print("\n[!] Important Notes:")
        print("    - You may need to restart your computer for changes to take full effect")
        print("    - To re-enable updates, you'll need to reverse these changes manually")
        print("    - This may prevent important security updates from installing")
    else:
        print("\n[!] Some operations failed. Windows Updates may not be fully disabled.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
