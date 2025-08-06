import subprocess
import ctypes
import sys
import platform
import argparse
import logging
import os
from datetime import datetime

# Check if running on Windows
if platform.system() != "Windows":
    print("[-] This script only works on Windows systems.")
    sys.exit(1)

import winreg

# Configure logging
def setup_logging(verbose=False):
    """Setup logging configuration."""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(log_dir, f"windows_update_disabler_{timestamp}.log")
    
    # Configure logging format
    log_format = '%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Get logger
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Log file: {log_filename}")
    logger.info(f"Log level: {'DEBUG' if verbose else 'INFO'}")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"Python version: {sys.version}")
    
    return logger, log_filename

# Global logger (will be initialized in main)
logger = None

def is_admin():
    """Check if the script is running with administrator privileges."""
    if logger:
        logger.debug("Checking administrator privileges")
    
    try:
        result = ctypes.windll.shell32.IsUserAnAdmin()
        if logger:
            logger.info(f"Administrator check result: {result}")
        return result
    except AttributeError as e:
        # Not on Windows or missing windll
        if logger:
            logger.error(f"AttributeError checking admin privileges: {e}")
        return False
    except Exception as e:
        if logger:
            logger.error(f"Error checking admin privileges: {e}")
        print(f"[-] Error checking admin privileges: {e}")
        return False

def disable_windows_update_service():
    """Disable the Windows Update service."""
    print("[*] Disabling Windows Update service...")
    if logger:
        logger.info("Starting Windows Update service disable operation")
    
    try:
        # Stop the service
        if logger:
            logger.debug("Executing: sc stop wuauserv")
        result = subprocess.run(["sc", "stop", "wuauserv"], shell=True, capture_output=True, text=True)
        if logger:
            logger.debug(f"Stop service result - Return code: {result.returncode}")
            logger.debug(f"Stop service stdout: {result.stdout}")
            logger.debug(f"Stop service stderr: {result.stderr}")
        
        if result.returncode != 0 and "service is not started" not in result.stderr.lower():
            warning_msg = f"Warning: Failed to stop service: {result.stderr.strip()}"
            print(f"[-] {warning_msg}")
            if logger:
                logger.warning(warning_msg)
        
        # Disable the service
        if logger:
            logger.debug("Executing: sc config wuauserv start= disabled")
        result = subprocess.run(["sc", "config", "wuauserv", "start=", "disabled"], shell=True, capture_output=True, text=True)
        if logger:
            logger.debug(f"Disable service result - Return code: {result.returncode}")
            logger.debug(f"Disable service stdout: {result.stdout}")
            logger.debug(f"Disable service stderr: {result.stderr}")
        
        if result.returncode == 0:
            success_msg = "Service disabled successfully"
            print(f"[+] {success_msg}.")
            if logger:
                logger.info(success_msg)
        else:
            error_msg = f"Failed to disable service: {result.stderr.strip()}"
            print(f"[-] {error_msg}")
            if logger:
                logger.error(error_msg)
            return False
            
    except Exception as e:
        error_msg = f"Error managing Windows Update service: {e}"
        print(f"[-] {error_msg}")
        if logger:
            logger.error(error_msg, exc_info=True)
        return False
    
    if logger:
        logger.info("Windows Update service disable operation completed successfully")
    return True

def set_update_policies():
    """Set registry keys to block Windows Update."""
    print("[*] Setting registry keys to block Windows Update...")
    if logger:
        logger.info("Starting registry policy configuration")

    try:
        key_path = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
        if logger:
            logger.debug(f"Registry key path: {key_path}")
        
        # Create the registry key if it doesn't exist
        if logger:
            logger.debug("Creating registry key if it doesn't exist")
        winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        
        # Open the key for writing
        if logger:
            logger.debug("Opening registry key for writing")
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)

        # Set NoAutoUpdate to 1 (Disable automatic updates)
        if logger:
            logger.debug("Setting NoAutoUpdate = 1")
        winreg.SetValueEx(key, "NoAutoUpdate", 0, winreg.REG_DWORD, 1)
        if logger:
            logger.info("NoAutoUpdate registry value set to 1")
        
        # Set AUOptions to 1 (Never check for updates)
        if logger:
            logger.debug("Setting AUOptions = 1")
        winreg.SetValueEx(key, "AUOptions", 0, winreg.REG_DWORD, 1)
        if logger:
            logger.info("AUOptions registry value set to 1")

        winreg.CloseKey(key)
        success_msg = "Registry keys applied successfully"
        print(f"[+] {success_msg}.")
        if logger:
            logger.info(success_msg)
        return True

    except PermissionError as e:
        error_msg = "Permission denied while writing to registry"
        print(f"[-] {error_msg}.")
        print("[-] Make sure you're running as Administrator.")
        if logger:
            logger.error(f"{error_msg}: {e}")
        return False
    except Exception as e:
        error_msg = f"Error setting registry policies: {e}"
        print(f"[-] {error_msg}")
        if logger:
            logger.error(error_msg, exc_info=True)
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

def enable_windows_update_service():
    """Re-enable the Windows Update service."""
    print("[*] Re-enabling Windows Update service...")
    
    try:
        # Set service to automatic startup
        result = subprocess.run(["sc", "config", "wuauserv", "start=", "auto"], shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[-] Failed to set service to automatic: {result.stderr.strip()}")
            return False
        
        # Start the service
        result = subprocess.run(["sc", "start", "wuauserv"], shell=True, capture_output=True, text=True)
        if result.returncode != 0 and "service is already running" not in result.stderr.lower():
            print(f"[-] Warning: Failed to start service: {result.stderr.strip()}")
            # Don't return False here as the service might start automatically
        
        print("[+] Windows Update service re-enabled successfully.")
        return True
            
    except Exception as e:
        print(f"[-] Error re-enabling Windows Update service: {e}")
        return False

def remove_update_policies():
    """Remove registry policies that block Windows Update."""
    print("[*] Removing registry policies that block Windows Update...")

    try:
        key_path = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
        
        # Try to open the key
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
            
            # Remove the specific values we set
            values_to_remove = ["NoAutoUpdate", "AUOptions"]
            removed_count = 0
            
            for value_name in values_to_remove:
                try:
                    winreg.DeleteValue(key, value_name)
                    print(f"[+] Removed registry value: {value_name}")
                    removed_count += 1
                except FileNotFoundError:
                    print(f"[*] Registry value {value_name} was not set (already clean)")
                except Exception as e:
                    print(f"[-] Failed to remove {value_name}: {e}")
            
            winreg.CloseKey(key)
            
            if removed_count > 0:
                print(f"[+] Successfully removed {removed_count} registry policy values.")
            else:
                print("[*] No registry policies were found to remove.")
            
            return True
            
        except FileNotFoundError:
            print("[*] Registry policy key doesn't exist (already clean)")
            return True
        
    except PermissionError:
        print("[-] Permission denied while accessing registry.")
        print("[-] Make sure you're running as Administrator.")
        return False
    except Exception as e:
        print(f"[-] Error removing registry policies: {e}")
        return False

def validate_rollback_status():
    """Validate that Windows Updates have been successfully re-enabled."""
    print("[*] Validating that Windows Updates are re-enabled...")
    
    try:
        # Check service status
        result = subprocess.run(["sc", "query", "wuauserv"], shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[-] Failed to query service status: {result.stderr.strip()}")
            return False
        
        output = result.stdout.lower()
        is_running = "running" in output or "state" in output and "4" in output
        
        # Check service startup type
        result = subprocess.run(["sc", "qc", "wuauserv"], shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[-] Failed to query service configuration: {result.stderr.strip()}")
            return False
        
        config_output = result.stdout.lower()
        is_automatic = "auto" in config_output and "start_type" in config_output
        
        # Check registry policies
        registry_clean = True
        try:
            key_path = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ)
            
            # Check if the problematic values still exist
            problematic_values = []
            for value_name in ["NoAutoUpdate", "AUOptions"]:
                try:
                    value, _ = winreg.QueryValueEx(key, value_name)
                    if value == 1:  # Still set to disable updates
                        problematic_values.append(value_name)
                except FileNotFoundError:
                    pass  # Good, value doesn't exist
            
            winreg.CloseKey(key)
            
            if problematic_values:
                registry_clean = False
                print(f"[-] Registry validation: These values are still blocking updates: {', '.join(problematic_values)}")
            else:
                print("[+] Registry validation: No blocking policies found")
                
        except FileNotFoundError:
            print("[+] Registry validation: Policy key doesn't exist (clean)")
        
        # Overall validation
        service_ok = is_automatic  # Don't require running, as it may start automatically
        
        if service_ok and registry_clean:
            print("[+] Service validation: Windows Update service is enabled")
            print("[+] Rollback validation: Windows Updates are successfully re-enabled")
            return True
        else:
            print(f"[-] Rollback validation failed:")
            if not service_ok:
                print(f"    - Service not properly configured (Running: {is_running}, Auto-start: {is_automatic})")
            if not registry_clean:
                print(f"    - Registry policies still blocking updates")
            return False
            
    except Exception as e:
        print(f"[-] Error validating rollback status: {e}")
        return False

def run_rollback_validation():
    """Run comprehensive validation for rollback operation."""
    print("\n" + "="*50)
    print("ROLLBACK VALIDATION REPORT")
    print("="*50)
    
    rollback_valid = validate_rollback_status()
    
    print("\n" + "-"*50)
    print("ROLLBACK SUMMARY")
    print("-"*50)
    
    if rollback_valid:
        print("[✓] ROLLBACK SUCCESSFUL")
        print("[✓] Windows Updates are re-enabled and ready to work")
        print("\nStatus Details:")
        print("  • Windows Update service: ENABLED and ready to start")
        print("  • Registry policies: REMOVED/CLEAN")
        print("  • Automatic updates: RESTORED")
        return True
    else:
        print("[!] ROLLBACK INCOMPLETE")
        print("[!] Some changes may not have been fully reversed")
        print("\nRecommendation: Try running the rollback again or check manually")
        return False

def rollback_changes():
    """Main rollback function to re-enable Windows Updates."""
    print("Windows Update Disabler - ROLLBACK MODE")
    print("=" * 40)
    print("[*] This will re-enable Windows automatic updates")
    print("[*] All previous disable operations will be reversed")
    print()
    
    if not is_admin():
        print("[-] This script must be run as administrator for rollback.")
        print("[-] Right-click and run as Administrator or use an elevated command prompt.")
        input("Press Enter to exit...")
        sys.exit(1)

    # Confirm rollback
    confirm = input("Are you sure you want to re-enable Windows Updates? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("[*] Rollback cancelled by user.")
        input("Press Enter to exit...")
        return

    success = True
    
    # Re-enable the Windows Update service
    if not enable_windows_update_service():
        success = False
    
    # Remove registry policies
    if not remove_update_policies():
        success = False
    
    if success:
        print("\n[✓] Windows Update rollback completed successfully.")
        
        # Run comprehensive validation
        validation_passed = run_rollback_validation()
        
        print("\n[!] Important Notes:")
        print("    - Windows Updates are now re-enabled")
        print("    - The system will resume automatic update checking")
        print("    - You may want to check for updates manually in Windows Settings")
        
        if validation_passed:
            print("\n[✓] ROLLBACK COMPLETED SUCCESSFULLY")
            print("    All validations passed - Windows Updates are fully re-enabled")
        else:
            print("\n[⚠] ROLLBACK PARTIALLY COMPLETED")
            print("    Some validations failed - please check the validation report above")
    else:
        print("\n[!] Some rollback operations failed. Windows Updates may not be fully re-enabled.")
        print("[*] Running validation to check current state...")
        run_rollback_validation()
    
    input("\nPress Enter to exit...")

def main():
    """Main function to disable Windows Updates."""
    print("Windows Update Disabler")
    print("=" * 30)
    
    if logger:
        logger.info("=== STARTING WINDOWS UPDATE DISABLE OPERATION ===")
    
    if not is_admin():
        error_msg = "This script must be run as administrator"
        print(f"[-] {error_msg}.")
        print("[-] Right-click and run as Administrator or use an elevated command prompt.")
        if logger:
            logger.error(error_msg)
        input("Press Enter to exit...")
        sys.exit(1)

    success = True
    
    # Disable the Windows Update service
    if logger:
        logger.info("Phase 1: Disabling Windows Update service")
    if not disable_windows_update_service():
        success = False
        if logger:
            logger.error("Phase 1 failed: Service disable operation unsuccessful")
    
    # Set registry policies
    if logger:
        logger.info("Phase 2: Setting registry policies")
    if not set_update_policies():
        success = False
        if logger:
            logger.error("Phase 2 failed: Registry policy operation unsuccessful")
    
    if success:
        print("\n[✓] Windows Updates have been disabled successfully.")
        if logger:
            logger.info("All disable operations completed successfully")
        
        # Run comprehensive validation
        if logger:
            logger.info("Phase 3: Running comprehensive validation")
        validation_passed = run_comprehensive_validation()
        
        print("\n[!] Important Notes:")
        print("    - You may need to restart your computer for changes to take full effect")
        print("    - To re-enable updates, you'll need to reverse these changes manually")
        print("    - This may prevent important security updates from installing")
        
        if validation_passed:
            final_msg = "OPERATION COMPLETED SUCCESSFULLY - All validations passed - Windows Updates are fully disabled"
            print("\n[✓] OPERATION COMPLETED SUCCESSFULLY")
            print("    All validations passed - Windows Updates are fully disabled")
            if logger:
                logger.info(final_msg)
        else:
            partial_msg = "OPERATION PARTIALLY COMPLETED - Some validations failed"
            print("\n[⚠] OPERATION PARTIALLY COMPLETED")
            print("    Some validations failed - please check the validation report above")
            if logger:
                logger.warning(partial_msg)
    else:
        failure_msg = "Some operations failed. Windows Updates may not be fully disabled"
        print(f"\n[!] {failure_msg}.")
        print("[*] Running validation to check current state...")
        if logger:
            logger.error(failure_msg)
            logger.info("Running validation to assess current state")
        run_comprehensive_validation()
    
    if logger:
        logger.info("=== WINDOWS UPDATE DISABLE OPERATION COMPLETED ===")
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
  python disable_windows_update.py --rollback # Re-enable Windows Updates
  python disable_windows_update.py --verbose  # Enable detailed logging
  python disable_windows_update.py -v --rollback # Verbose rollback
  python disable_windows_update.py --help    # Show this help message

Note: This script requires administrator privileges to run.
Logs are automatically saved to the 'logs' directory with timestamps.
        """
    )
    
    parser.add_argument(
        '--validate', 
        action='store_true',
        help='Only run validation checks without making changes'
    )
    
    parser.add_argument(
        '--rollback', 
        action='store_true',
        help='Re-enable Windows Updates (reverse all disable operations)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging (shows detailed debug information)'
    )
    
    args = parser.parse_args()
    
    # Initialize logging first
    global logger
    logger, log_filename = setup_logging(verbose=args.verbose)
    
    # Log command line arguments
    logger.info(f"Command line arguments: {' '.join(sys.argv)}")
    logger.info(f"Parsed arguments - validate: {args.validate}, rollback: {args.rollback}, verbose: {args.verbose}")
    
    # Check for mutually exclusive options
    if args.validate and args.rollback:
        error_msg = "Error: --validate and --rollback cannot be used together"
        print(f"[-] {error_msg}")
        logger.error(error_msg)
        parser.print_help()
        sys.exit(1)
    
    # Display log file location if verbose
    if args.verbose:
        print(f"[*] Verbose logging enabled. Log file: {log_filename}")
    
    if args.rollback:
        # Run rollback operation
        rollback_changes()
    elif args.validate:
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
