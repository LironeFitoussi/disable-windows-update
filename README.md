# Windows Update Disabler

A robust Python-based tool to disable Windows automatic updates through service management and registry modifications.

## ⚠️ Important Disclaimer

**USE AT YOUR OWN RISK:** This tool disables Windows automatic updates, which may prevent important security updates from being installed. Only use this if you understand the implications and plan to manually manage updates.

## 📋 Features

- **Service Management**: Stops and disables the Windows Update service (`wuauserv`)
- **Registry Policies**: Sets system policies to prevent automatic updates
- **Auto Python Installation**: Automatically installs Python if not present
- **Administrator Privilege Check**: Ensures script runs with required permissions
- **Comprehensive Error Handling**: Robust error checking and user feedback
- **Cross-Platform Safety**: Prevents execution on non-Windows systems
- **✨ Validation System**: Comprehensive post-execution validation to verify all changes
- **Standalone Validation**: Check current Windows Update status without making changes
- **🔄 Rollback Feature**: Complete rollback functionality to re-enable Windows Updates
- **Safety Confirmation**: User confirmation required for rollback operations
- **📝 Comprehensive Logging**: Detailed logging with timestamps and multiple log levels
- **🔍 Verbose Mode**: Optional detailed debug output for troubleshooting

## 📁 Files Overview

- `disable_windows_update.py` - Main Python script that performs the update disabling
- `run_disable_script.bat` - Windows batch launcher with Python auto-installation
- `install_python.ps1` - PowerShell script for automatic Python installation
- `requirements.txt` - Python dependencies (currently empty - no external deps needed)

## 🚀 Quick Start

### Method 1: Using the Batch Launcher (Recommended)

**To Disable Windows Updates:**
1. Download all files to a folder
2. Right-click on `run_disable_script.bat`
3. Select "Run as administrator"
4. Follow the on-screen prompts

**To Re-enable Windows Updates (Rollback):**
1. Right-click on `run_disable_script.bat`
2. Select "Run as administrator" 
3. Or use: `run_disable_script.bat --rollback`

### Method 2: Direct Python Execution
```bash
# Disable Windows Updates
python disable_windows_update.py

# Re-enable Windows Updates (rollback)
python disable_windows_update.py --rollback

# Check current status
python disable_windows_update.py --validate
```

## 🔧 System Requirements

- **Operating System**: Windows 7/8/10/11
- **Python**: 3.7+ (automatically installed if missing)
- **Privileges**: Administrator/elevated privileges required
- **Internet**: Required for Python auto-installation (if needed)

## 📖 Detailed Usage

### What the Script Does

1. **Platform Check**: Verifies the script is running on Windows
2. **Admin Check**: Ensures administrator privileges are present
3. **Service Disable**: Stops and disables the `wuauserv` (Windows Update) service
4. **Registry Modification**: Sets the following registry keys:
   - `HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU\NoAutoUpdate = 1`
   - `HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU\AUOptions = 1`

### Command Line Options

The Python script supports several command-line options:

```bash
# Disable Windows Updates (default behavior)
python disable_windows_update.py

# Only run validation checks (no changes made)
python disable_windows_update.py --validate

# Re-enable Windows Updates (complete rollback)
python disable_windows_update.py --rollback

# Enable verbose logging (detailed debug output)
python disable_windows_update.py --verbose

# Combine options (verbose rollback)
python disable_windows_update.py --rollback --verbose

# Show help and usage information
python disable_windows_update.py --help
```

#### Validation Mode
Use the `--validate` flag to check if Windows Updates are currently disabled without making any changes:
- Checks Windows Update service status
- Verifies registry policy settings  
- Provides detailed validation report
- Perfect for verifying the script worked correctly

#### Rollback Mode  
Use the `--rollback` flag to completely reverse all disable operations and re-enable Windows Updates:
- Re-enables the Windows Update service (sets to automatic startup)
- Removes all blocking registry policies
- Includes user confirmation prompt for safety
- Comprehensive validation to verify rollback success
- **Safe and complete**: Fully restores Windows Update functionality

#### Verbose Logging Mode
Use the `--verbose` or `-v` flag to enable detailed debug logging:
- **Detailed execution logs**: Shows every step the script performs
- **Debug information**: Command outputs, registry operations, service calls
- **Automatic log files**: Saves timestamped logs to `logs/` directory
- **Troubleshooting**: Perfect for diagnosing issues or understanding what went wrong
- **Combine with any mode**: Works with disable, rollback, and validation modes

## 🛠️ Technical Details

### Registry Keys Modified

| Key | Value | Description |
|-----|-------|-------------|
| `NoAutoUpdate` | `1` | Disables automatic update checking |
| `AUOptions` | `1` | Sets update option to "Never check for updates" |

### Services Modified

- **wuauserv** (Windows Update Service) - Stopped and set to disabled

### Logging System

The script includes comprehensive logging functionality:

#### **Log Files**
- **Location**: `logs/` directory (created automatically)
- **Naming**: `windows_update_disabler_YYYYMMDD_HHMMSS.log`
- **Format**: Timestamp - Level - Function:Line - Message
- **Encoding**: UTF-8 for proper character support

#### **Log Levels**
- **INFO**: General operation status and progress
- **DEBUG**: Detailed command execution and system calls (verbose mode only)
- **WARNING**: Non-critical issues that don't stop execution
- **ERROR**: Failures and critical issues with full exception details

#### **Example Log Output**
```
2024-01-15 14:30:15,123 - INFO - main:534 - === STARTING WINDOWS UPDATE DISABLE OPERATION ===
2024-01-15 14:30:15,125 - INFO - is_admin:64 - Administrator check result: True
2024-01-15 14:30:15,126 - INFO - main:549 - Phase 1: Disabling Windows Update service
2024-01-15 14:30:15,127 - DEBUG - disable_windows_update_service:86 - Executing: sc stop wuauserv
2024-01-15 14:30:15,234 - DEBUG - disable_windows_update_service:89 - Stop service result - Return code: 0
2024-01-15 14:30:15,235 - INFO - disable_windows_update_service:112 - Service disabled successfully
```

## 🔒 Security Considerations

- Script requires administrator privileges to modify system settings
- Registry modifications affect system-wide update behavior
- Service changes persist until manually reversed
- Disabling updates may leave system vulnerable to security threats

## 🐛 Troubleshooting

### Common Issues

**"Permission denied" errors:**
- Ensure you're running as Administrator
- Check if antivirus is blocking the script

**"Python not found" errors:**
- Run the batch launcher which auto-installs Python
- Or manually install Python from [python.org](https://www.python.org)

**Script doesn't run:**
- Verify all files are in the same directory
- Check Windows execution policy for PowerShell scripts

### Error Messages

| Error | Solution |
|-------|----------|
| `This script must be run as administrator` | Right-click and "Run as administrator" |
| `This script only works on Windows systems` | Only run on Windows machines |
| `Permission denied while writing to registry` | Ensure admin privileges and check antivirus |
| `Python installation failed` | Install Python manually or check internet connection |
| `Service validation failed` | Service may still be running; try restarting as admin |
| `Registry validation failed` | Registry keys not set correctly; re-run script |
| `Rollback cancelled by user` | User chose not to proceed with rollback |
| `Rollback validation failed` | Some rollback operations didn't complete; try again |

### Validation Troubleshooting

If validation fails after running the script:

1. **Check the detailed validation report** - it shows exactly what failed
2. **Run validation separately**: `python disable_windows_update.py --validate`
3. **Common validation issues**:
   - Service still running: Windows may have restarted the service
   - Registry keys missing: Antivirus may have blocked registry changes
   - Partial success: Some operations succeeded, others failed

**Pro tip**: Use the validation mode regularly to check if Windows Updates are still disabled, especially after Windows feature updates.

## 🔄 Reversing Changes (Rollback)

### Automatic Rollback (Recommended)
The easiest way to re-enable Windows Updates is using the built-in rollback feature:

```bash
# Using Python directly
python disable_windows_update.py --rollback

# Using the batch launcher
run_disable_script.bat --rollback
```

The rollback feature will:
- ✅ Re-enable the Windows Update service automatically
- ✅ Remove all blocking registry policies
- ✅ Validate that rollback was successful
- ✅ Provide confirmation prompts for safety

### Manual Rollback (If Needed)
If you prefer to manually re-enable Windows Updates:

1. **Re-enable the service:**
   ```cmd
   sc config wuauserv start= auto
   sc start wuauserv
   ```

2. **Remove registry keys:**
   - Navigate to `HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU`
   - Delete `NoAutoUpdate` and `AUOptions` values
   - Or delete the entire `AU` key

3. **Alternative:** Use Windows Settings → Update & Security → Windows Update

## 📝 Version History

### Current Version
- Enhanced error handling and validation
- Improved user feedback and messaging
- Added platform compatibility checks
- Robust Python auto-installation
- Comprehensive logging and status reporting
- **✨ NEW**: Post-execution validation system
- **✨ NEW**: Standalone validation mode (`--validate` flag)
- **✨ NEW**: Detailed validation reports with success/failure indicators
- **🔄 NEW**: Complete rollback functionality (`--rollback` flag)
- **🔄 NEW**: Automatic service re-enabling and registry cleanup
- **🔄 NEW**: Rollback validation and safety confirmations
- **📝 NEW**: Comprehensive logging system with timestamped log files
- **📝 NEW**: Verbose mode (`--verbose`/`-v`) for detailed debug output
- **📝 NEW**: Automatic log file generation in `logs/` directory

## ⚖️ Legal Notice

This software is provided "as is" without warranty. Users are responsible for understanding the implications of disabling Windows updates on their systems. The authors are not liable for any damage or security issues that may result from using this tool.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this tool.

## 📧 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Ensure all prerequisites are met
3. Run with administrator privileges
4. Verify all files are present and unmodified

---

**Remember:** Keeping your system updated is generally recommended for security. Only disable updates if you have a specific need and plan to manage updates manually.