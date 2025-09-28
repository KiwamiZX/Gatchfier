<p align="center"><img width="400" height="400" alt="vertical logo" src="https://github.com/user-attachments/assets/cd5289e7-17ab-49d6-848f-da71d8a3c2cd" /></p>


Gatchfier is a modern network diagnostic tool built with PySide6. It provides a clean, intuitive interface for performing essential network operations like ping, traceroute, port scanning, DNS lookups, and WHOIS queries—all in one place. Designed for IT professionals, students, and enthusiasts, Gatchfier makes network troubleshooting simple and visually appealing.

## Features

-   Ping utility with IPv4 and IPv6 support, including continuous and limited modes
    
-   Traceroute with live output and cancel option
    
-   Port scanner to detect open ports on a target host
    
-   DNS lookup tool for resolving domain names and viewing DNS records
    
-   WHOIS query tool for retrieving domain registration information
    
-   Light and dark theme toggle with dynamic splash screen
    
-   Custom icons and branding for a polished user experience
    

## Screenshots

<p align="center"><img width="752" height="539" alt="image" src="https://github.com/user-attachments/assets/cf330f12-a464-4698-aa72-3b355d638d00" /></p>


<p align="center"><img width="752" height="539" alt="image" src="https://github.com/user-attachments/assets/257a5d22-a375-4bc4-9b5a-76d39c1b7a57" /></p>

<p align="center"><img width="752" height="539" alt="image" src="https://github.com/user-attachments/assets/b20498fb-1562-4759-ade8-247794704df8" /></p>


## Installation

Requirements:

-   Python 3.10 or higher
    
-   Recommended: virtual environment
    

To install dependencies:

Código

```
pip install -r requirements.txt

```

To run the application:

Código

```
python app.py

```

## Packaging with PyInstaller

To build a standalone executable:

Código

```
pyinstaller gatchfier.spec

```

Make sure all icons, splash screens, and config files are included in the `.spec` file and that your code uses `sys._MEIPASS` to access bundled resources.

## Project Structure

-   `app.py`: Main application entry point
    
-   `config.json`: Stores theme preferences
    
-   `icons/`: Contains all logos, icons, and splash images
    
-   `tabs/`: Contains individual modules for each network tool
    
-   `requirements.txt`: Lists all required Python packages
    

## Contributing

Pull requests are welcome! If you have ideas for new features, UI improvements, or bug fixes, feel free to contribute.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
