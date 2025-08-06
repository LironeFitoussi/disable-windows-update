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

## 📁 Files Overview

- `disable_windows_update.py` - Main Python script that performs the update disabling
- `run_disable_script.bat` - Windows batch launcher with Python auto-installation
- `install_python.ps1` - PowerShell script for automatic Python installation
- `requirements.txt` - Python dependencies (currently empty - no external deps needed)

## 🚀 Quick Start

### Method 1: Using the Batch Launcher (Recommended)
1. Download all files to a folder
2. Right-click on `run_disable_script.bat`
3. Select "Run as administrator"
4. Follow the on-screen prompts

### Method 2: Direct Python Execution
1. Ensure Python is installed
2. Right-click Command Prompt and "Run as administrator"
3. Navigate to the script directory
4. Run: `python disable_windows_update.py`

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

The Python script currently doesn't accept command-line arguments, but you can run it directly:

```bash
# Run with Python (requires admin privileges)
python disable_windows_update.py
```

## 🛠️ Technical Details

### Registry Keys Modified

| Key | Value | Description |
|-----|-------|-------------|
| `NoAutoUpdate` | `1` | Disables automatic update checking |
| `AUOptions` | `1` | Sets update option to "Never check for updates" |

### Services Modified

- **wuauserv** (Windows Update Service) - Stopped and set to disabled

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

## 🔄 Reversing Changes

To re-enable Windows Updates, you need to manually:

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