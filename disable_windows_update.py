import subprocess
import ctypes
import sys
import platform
import argparse

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

def validate_service_status():
    """Validate that the Windows Update service is properly disabled."""
    print("[*] Validating Windows Update service status...")
    
    try:
        # Check service status
        result = subprocess.run(["sc", "query", "wuauserv"], shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[-] Failed to query service status: {result.stderr.strip()}")
            return False
        
        output = result.stdout.lower()
        is_stopped = "stopped" in output or "state" in output and "1" in output
        
        # Check service startup type
        result = subprocess.run(["sc", "qc", "wuauserv"], shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[-] Failed to query service configuration: {result.stderr.strip()}")
            return False
        
        config_output = result.stdout.lower()
        is_disabled = "disabled" in config_output
        
        if is_stopped and is_disabled:
            print("[+] Service validation: Windows Update service is stopped and disabled")
            return True
        else:
            print(f"[-] Service validation failed:")
            print(f"    - Service stopped: {is_stopped}")
            print(f"    - Service disabled: {is_disabled}")
            return False
            
    except Exception as e:
        print(f"[-] Error validating service status: {e}")
        return False

def validate_registry_policies():
    """Validate that registry policies are correctly set."""
    print("[*] Validating registry policies...")
    
    try:
        key_path = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ)
        
        validation_results = {}
        expected_values = {
            "NoAutoUpdate": 1,
            "AUOptions": 1
        }
        
        for value_name, expected_value in expected_values.items():
            try:
                value, reg_type = winreg.QueryValueEx(key, value_name)
                validation_results[value_name] = {
                    "exists": True,
                    "value": value,
                    "correct": value == expected_value,
                    "type": reg_type
                }
            except FileNotFoundError:
                validation_results[value_name] = {
                    "exists": False,
                    "value": None,
                    "correct": False,
                    "type": None
                }
        
        winreg.CloseKey(key)
        
        all_correct = True
        for value_name, result in validation_results.items():
            if result["correct"]:
                print(f"[+] Registry validation: {value_name} = {result['value']} ✓")
            else:
                print(f"[-] Registry validation: {value_name} = {result['value'] if result['exists'] else 'NOT SET'} ✗")
                all_correct = False
        
        if all_correct:
            print("[+] All registry policies are correctly configured")
        
        return all_correct
        
    except FileNotFoundError:
        print("[-] Registry validation failed: Policy key does not exist")
        return False
    except Exception as e:
        print(f"[-] Error validating registry policies: {e}")
        return False

def run_comprehensive_validation():
    """Run all validation checks and provide a comprehensive report."""
    print("\n" + "="*50)
    print("VALIDATION REPORT")
    print("="*50)
    
    service_valid = validate_service_status()
    registry_valid = validate_registry_policies()
    
    print("\n" + "-"*50)
    print("SUMMARY")
    print("-"*50)
    
    if service_valid and registry_valid:
        print("[✓] ALL VALIDATIONS PASSED")
        print("[✓] Windows Updates are successfully disabled")
        print("\nStatus Details:")
        print("  • Windows Update service: STOPPED and DISABLED")
        print("  • Registry policies: CORRECTLY CONFIGURED")
        print("  • Automatic updates: BLOCKED")
        return True
    else:
        print("[!] SOME VALIDATIONS FAILED")
        print("[!] Windows Updates may not be fully disabled")
        print("\nIssues found:")
        if not service_valid:
            print("  • Windows Update service configuration issues")
        if not registry_valid:
            print("  • Registry policy configuration issues")
        print("\nRecommendation: Try running the script again as Administrator")
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
        
        # Run comprehensive validation
        validation_passed = run_comprehensive_validation()
        
        print("\n[!] Important Notes:")
        print("    - You may need to restart your computer for changes to take full effect")
        print("    - To re-enable updates, you'll need to reverse these changes manually")
        print("    - This may prevent important security updates from installing")
        
        if validation_passed:
            print("\n[✓] OPERATION COMPLETED SUCCESSFULLY")
            print("    All validations passed - Windows Updates are fully disabled")
        else:
            print("\n[⚠] OPERATION PARTIALLY COMPLETED")
            print("    Some validations failed - please check the validation report above")
    else:
        print("\n[!] Some operations failed. Windows Updates may not be fully disabled.")
        print("[*] Running validation to check current state...")
        run_comprehensive_validation()
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Windows Update Disabler - Disable automatic Windows updates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python disable_windows_update.py           # Disable Windows Updates
  python disable_windows_update.py --validate # Only run validation checks
  python disable_windows_update.py --help    # Show this help message

Note: This script requires administrator privileges to run.
        """
    )
    
    parser.add_argument(
        '--validate', 
        action='store_true',
        help='Only run validation checks without making changes'
    )
    
    args = parser.parse_args()
    
    if args.validate:
        # Run validation only
        print("Windows Update Disabler - Validation Mode")
        print("=" * 40)
        
        if not is_admin():
            print("[-] Administrator privileges required for validation.")
            print("[-] Right-click and run as Administrator.")
            input("Press Enter to exit...")
            sys.exit(1)
        
        print("[*] Running validation checks only (no changes will be made)...")
        validation_passed = run_comprehensive_validation()
        
        if validation_passed:
            print("\n[✓] VALIDATION RESULT: Windows Updates are properly disabled")
        else:
            print("\n[!] VALIDATION RESULT: Windows Updates are NOT properly disabled")
            print("    Run the script without --validate to disable updates")
        
        input("\nPress Enter to exit...")
    else:
        # Run main disable function
        main()
