# Telegram Bot for Electricity Outages

This Telegram bot provides information on electricity outages based on user inputs for locality and street. The bot scrapes data from a specific website and returns relevant information to the user.

## Installation

1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd <repository_directory>
   
2. Create a virtual environment and activate it:
   ```
  python -m venv venv
  source venv/bin/activate   # On Windows: venv\Scripts\activate

4. Install the required dependencies:
   ```
   pip install -r requirements.txt

5. Create a file named info.py in the project directory and add your bot token:

  # info.py
  BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
