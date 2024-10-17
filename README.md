# YoFReD (Your Friendly Reminder Discord bot)

A Discord bot made with Python used for making reminders for yourself and friends!

The bot uses TinyDB to create file based databases in readable json format. This makes it easy to manage saved data.

## Current command list:

##### General commands
- `/ping`
- `/help`

##### Reminder commands
- `/reminder create`
- `/reminder list`
- `/reminder edit`
- `/reminder delete`

## How to set up?
1) Make sure you got an application set up [here](https://discord.com/developers/applications)
   
2) Clone the repository and unpack it somewhere safe.

3) Make sure to have python3 installed and install the `requirements.txt` packages.

4) Create a `.env` file at the root of the project containing the following.
Make sure to replace the parameters inside `<...>` with your own parameters!

    ```dotenv
    TOKEN='<YOUR BOTS TOKEN>'
    ```
5) Run the bot with `python3 main.py` and you're done!

**Any problems? Feel free to contact me on discord: @viovyx**

## TO-DO

- [ ] add help command
- [ ] add check for reminding
- [ ] pishock support?
