# shell-access-discord-bot

<b>WARNING</b>

This Discord bot, intended for educational purposes, demonstrates various potential security vulnerabilities 
associated with arbitrary code execution or system access from user input. The bot includes several commands 
for users to interact with the underlying system, which should only be used in a controlled and secure environment.<br>

The bot's features include:
1. Executing JavaScript code with a Node.js runtime using the "!js" command.
2. Executing Python code in a limited environment using the "!python" command.
3. Reading file content from the local filesystem using the "!read_file" command.
4. Writing to a file on the local filesystem using the "!write_file" command.
5. Listing files in a specified directory using the "!list_files" command.
6. Executing arbitrary shell commands using the "!shell" command.
7. Retrieving the value of an environment variable using the "!get_env" command.
8. Deleting a file from the local filesystem using the "!delete_file" command.
9. Changing file permissions on the local filesystem using the "!chmod" command.<br>

Each command is accompanied by a help message that describes its functionality and usage. The bot also includes 
error handling to respond with informative messages in case of command errors. 
Please use this bot responsibly and understand the associated security risks of its functionalities.<br>

<b>RocketGod</b>

## INSTALLATION INSTRUCTIONS

1. Clone the repository to your local machine:
    ```
    git clone https://github.com/RocketGod-git/shell-access-discord-bot.git
    ```
2. Navigate into the project's directory:
    ```
    cd shell-access-discord-bot
    ```
3. Install the necessary Python packages. This bot requires Python 3.7 or newer, and the discord.py library:
    ```
    pip install discord.py
    ```
4. Install Node.js and npm (if not already installed). The installation process depends on your operating system. Please follow the instructions on the official Node.js website: https://nodejs.org/.
5. Update the `config.json` file with your bot's token. The `config.json` file should look something like this:
    ```json
    {
        "DISCORD_BOT_TOKEN": "your-token-here"
    }
    ```
6. Run the bot with the following command:
    ```
    python3 shell-bot.py
    ```



![RocketGod Logo](https://user-images.githubusercontent.com/57732082/213221533-171b37da-46e5-4661-ac47-c7f23d24b816.png)
