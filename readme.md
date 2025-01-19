# Prerequisites
1. Install Python: via the Microsoft store (recommended) or https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe
2. Install Git: https://git-scm.com/download/win

# Installation
1. Open Powershell: Press the Windows key, then type "Powershell" and press Enter when the application appears
2. Clone the repository: `git clone https://github.com/ExpiringFrog/block_rfq_in_excel`
3. Move into the new folder: `cd block_rfq_in_excel`
4. Install Python libraries: `pip install -r requirements.txt`

# Configuration
1. Open the `block_rfq_in_excel` folder in Windows Explorer
2. Rename `example_config.ini` to `config.ini`

3. Open `config.ini`.

4. Under `API`:
- - `environment` can either be `prod` for www.deribit.com or `test` for test.deribit.com
- - `key` and `secret` should be filled in with the API credentials from https://www.deribit.com/account/BTC/api if `evironment = prod` or https://test.deribit.com/account/BTC/api if `environment = test`

5. Under `Excel`:
- - If Excel should be used, `state` should be `on`. If `state = off`, Excel is not used.
- - `file_path` should contain the relative or absolute path to the Excel spreadsheet to be used.
- - `sheet_name` should be the name of the sheet inside the Excel file.
- - NOTE: this app will wipe all previous content from the configured sheet.
- - NOTE: the default configuration will use the Excel file included with the application.
- - NOTE: only contents are wiped, all formatting is kept.

Under `Telegram`:
- - If notifications should be sent via Telegram, `state` should be `on`. If `state = off`, Telegram is not used.
- - `bot_token` should be equal to the token received from the BotFather (https://telegram.me/BotFather).
- - `chat_id` should be equal to the group chat to be used for notifications. How to easily get the `chat_id` is explained here: https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id.

# Usage
To start the application, type `python main.py` in Powershell.
It is best to let the application open the Excel file.