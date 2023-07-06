# WARNING
#
# This Discord bot, intended for educational purposes, demonstrates various potential security vulnerabilities 
# associated with arbitrary code execution or system access from user input. The bot includes several commands 
# for users to interact with the underlying system, which should only be used in a controlled and secure environment.
#
# The bot's features include:
# 1. Executing JavaScript code with a Node.js runtime using the "!js" command.
# 2. Executing Python code in a limited environment using the "!python" command.
# 3. Reading file content from the local filesystem using the "!read_file" command.
# 4. Writing to a file on the local filesystem using the "!write_file" command.
# 5. Listing files in a specified directory using the "!list_files" command.
# 6. Executing arbitrary shell commands using the "!shell" command.
# 7. Retrieving the value of an environment variable using the "!get_env" command.
# 8. Deleting a file from the local filesystem using the "!delete_file" command.
# 9. Changing file permissions on the local filesystem using the "!chmod" command.
#
# Each command is accompanied by a help message that describes its functionality and usage. The bot also includes 
# error handling to respond with informative messages in case of command errors. 
# Please use this bot responsibly and understand the associated security risks of its functionalities.
#
# RocketGod

import discord
from discord.ext import commands
import subprocess
import os
import json

with open('config.json', 'r') as file:
    config = json.load(file)

TOKEN = config.get("DISCORD_BOT_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')

@bot.command(name="js", help="Run JavaScript code.")
async def _js(ctx, *, code: str):
    try:
        result = subprocess.check_output(["node", "-e", code], text=True)
        await ctx.send(content=f"Output: {result}")
    except subprocess.CalledProcessError as e:
        await ctx.send(content=f"Error: {str(e)}")

@bot.command(name="python", help="Run Python code.")
async def _python(ctx, *, code: str):
    try:
        exec_locals = {}
        exec(code, {"__builtins__": None}, exec_locals)
        await ctx.send(content=f"Output: {exec_locals}")
    except Exception as e:
        await ctx.send(content=f"Error: {str(e)}")

@bot.command(name="read_file", help="Read a file.")
async def _read_file(ctx, *, file_path: str):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        await ctx.send(content=content)
    except Exception as e:
        await ctx.send(content=str(e))

@bot.command(name="write_file", help="Write to a file.")
async def _write_file(ctx, file_path: str, *, content: str):
    try:
        with open(file_path, 'w') as file:
            file.write(content)
        await ctx.send(content="File written successfully.")
    except Exception as e:
        await ctx.send(content=str(e))

@bot.command(name="list_files", help="List files in a directory.")
async def _list_files(ctx, *, directory: str):
    try:
        files = os.listdir(directory)
        await ctx.send(content="\n".join(files))
    except Exception as e:
        await ctx.send(content=str(e))

@bot.command(name="shell", help="Run a shell command.")
async def _shell(ctx, *, command: str):
    try:
        result = subprocess.check_output(command, shell=True, text=True, timeout=10)  # set timeout to 10 seconds
        await send_long_message(ctx, f"Output: {result}")
    except subprocess.CalledProcessError as e:
        await ctx.send(content=f"Error: {str(e)}")
    except subprocess.TimeoutExpired:
        await ctx.send(content="Command timed out.")

@bot.command(name="get_env", help="Get an environment variable.")
async def _get_env(ctx, *, variable: str):
    try:
        value = os.environ.get(variable)
        await ctx.send(content=f"Value: {value}")
    except Exception as e:
        await ctx.send(content=str(e))

@bot.command(name="delete_file", help="Delete a file.")
async def _delete_file(ctx, *, file_path: str):
    try:
        os.remove(file_path)
        await ctx.send(content="File deleted successfully.")
    except Exception as e:
        await ctx.send(content=str(e))

@bot.command(name="chmod", help="Change file permissions.")
async def _chmod(ctx, file_path: str, *, mode: str):
    try:
        os.chmod(file_path, int(mode, 8))  # Mode is expected to be a string representing octal number (like "777", "644")
        await ctx.send(content="File permissions changed successfully.")
    except Exception as e:
        await ctx.send(content=str(e))

@bot.command(name="help", help="Get help about the bot commands.")
async def _help(ctx):
    help_text = """
    WARNING: This bot is intentionally insecure and should only be used in a controlled, educational setting.

    **!js <code>** - Run JavaScript code.
    **!python <code>** - Run Python code.
    **!read_file <file_path>** - Read content of a file.
    **!write_file <file_path> <content>** - Write content to a file.
    **!list_files <directory>** - List files in a directory.
    **!shell <command>** - Run a shell command.
    **!get_env <variable>** - Get an environment variable.
    **!delete_file <file_path>** - Delete a file.
    **!chmod <file_path> <mode>** - Change file permissions.
    **!help** - Show this help message.

    The educational objective of this bot is to illustrate potential security vulnerabilities associated with arbitrary code execution or system access from user input.
    """
    await ctx.send(content=help_text)

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"An error occurred: {str(error)}")

if __name__ == "__main__":
    while True:
        try:
            bot.run(TOKEN)  # Use the TOKEN variable here
        except Exception as e:
            print(f"Exception occurred: {str(e)}. Restarting bot.")