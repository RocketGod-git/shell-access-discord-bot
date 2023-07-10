# WARNING
#
# This Discord bot, intended for educational purposes, demonstrates a potential security vulnerability 
# associated with arbitrary code execution or system access from user input. The bot includes a command 
# for users to execute arbitrary shell commands using the "!shell" command. This should only be used in a 
# controlled and secure environment.
#
# The bot's feature includes:
# 1. Executing arbitrary shell commands using the "!shell" command. Tested and working on Windows and Linux.
#
# Please use this bot responsibly and understand the associated security risks of its functionality.
#
# RocketGod

import discord
import asyncio
from discord.ext import commands
import subprocess
import json
import signal
from time import sleep
import sys
import platform
import os
from discord import File
from pathlib import Path


with open('config.json', 'r') as file:
    config = json.load(file)

TOKEN = config.get("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(config.get("CHANNEL_ID")) 

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
channel = None

MAX_MESSAGE_LENGTH = 1500  # Leave some room for extra characters

async def run_command_with_timeout(command, timeout):
    process = await asyncio.create_subprocess_shell(
        command, 
        stdout=asyncio.subprocess.PIPE, 
        stderr=asyncio.subprocess.PIPE
    )

    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        process.kill()
        stdout, stderr = await process.communicate()

    return stdout, stderr, process.returncode

@bot.command(name="shell", help="Run a shell command.")
async def _shell(ctx, *, command: str):
    # Ignore DMs
    if ctx.guild is None:
        return

    # Ensure command is run in the designated channel
    if ctx.channel.id != CHANNEL_ID:
        await ctx.send("This command can only be run in the designated bot channel.")
        return

    try:
        stdout, stderr, returncode = await run_command_with_timeout(command, 10)  # 10 second timeout

        # Decode bytes to strings and join the stdout and stderr into a single string, separating them by a newline.
        stdout_str = stdout.decode()
        stderr_str = stderr.decode()
        result = "\n".join([stdout_str, stderr_str])

        if returncode != 0:
            # If the process exited with a non-zero status (indicating an error), raise an exception.
            error_message = f"Error: Command '{command}' returned non-zero exit status {returncode}. \n stdout: {stdout_str} \n stderr: {stderr_str}"
            raise subprocess.CalledProcessError(returncode, command, output=error_message)

        # Check if the result is too long to send in a single message
        while len(result) > 0:
            if len(result) > MAX_MESSAGE_LENGTH:
                await ctx.send(content=f"Output: {result[:MAX_MESSAGE_LENGTH - 9]}")  # -9 for "Output: " and a newline character
                result = result[MAX_MESSAGE_LENGTH - 9:]
            else:
                await ctx.send(content=f"Output: {result}")
                result = ""

    except subprocess.CalledProcessError as e:
        await ctx.send(content=str(e.output))  # Send the detailed error message
    except asyncio.TimeoutError:
        await ctx.send(content="Command timed out.")

@bot.event
async def on_message(message):
    if message.channel.id != CHANNEL_ID:
        return
    if message.author != bot.user:
        # Check if the message has any attachments
        if message.attachments:
            for attachment in message.attachments:
                try:
                    # Create the downloads directory if it doesn't exist
                    os.makedirs('downloads', exist_ok=True)

                    # Download the attachment
                    file_path = f'./downloads/{attachment.filename}'
                    await attachment.save(file_path)
                    print(f"File received: {attachment.filename}")
                    await message.channel.send(f"File received: `{attachment.filename}`")
                    await channel.send(f"File received in DM from `{message.author}`: `{attachment.filename}`")
                    
                    # If the file is executable, ask the user if they want to execute it
                    if os.access(file_path, os.X_OK):
                        await message.channel.send(f"The file `{attachment.filename}` Can be opened on the underlying server. Do you want to run it? Respond with 'yes' to execute, 'no' to ignore.")
                        await channel.send(f"The file `{attachment.filename}` Can be opened on the underlying server. User `{message.author}` was asked if they want to run it.")
                        
                        def check(m):
                            return m.content.lower() in ['yes', 'no'] and m.channel == message.channel and m.author == message.author

                        try:
                            confirmation = await bot.wait_for('message', check=check, timeout=30.0)
                        except asyncio.TimeoutError:
                            print(f"User did not respond in time. The file `{attachment.filename}` will not be executed.")
                            await message.channel.send(f"Timed out. The file `{attachment.filename}` will not be executed.")
                            await channel.send(f"User `{message.author}` did not respond in time. The file `{attachment.filename}` will not be executed.")
                        else:                         
                            if confirmation.content.lower() == 'yes':
                                # If system is Windows, use the 'start cmd /K' command to start a new CMD window
                                if platform.system() == "Windows":
                                    command_to_execute = f'start cmd /K "cd /D {os.path.dirname(os.path.abspath(file_path))} && {os.path.basename(file_path)}"'
                                else:  # For Unix-based systems, we can use the 'cd' command with '&&' to change directory and execute the command
                                    command_to_execute = f'cd {os.path.dirname(os.path.abspath(file_path))} && ./{os.path.basename(file_path)}'
    
                                stdout, stderr, returncode = await run_command_with_timeout(command_to_execute, 10)
                                stdout_str = stdout.decode()
                                stderr_str = stderr.decode()
                                result = "\n".join([stdout_str, stderr_str])
                                print(f"File executed: {attachment.filename}. Output: {result}")
                                await message.channel.send(f"File `{attachment.filename}` executed. Output: {result}")
                                await channel.send(f"File `{attachment.filename}` executed in DM for `{message.author}`. Output: {result}")

                            else:
                                print(f"The file `{attachment.filename}` will not be executed.")
                                await message.channel.send(f"The file `{attachment.filename}` will not be executed.")
                                await channel.send(f"User `{message.author}` chose not to execute the file `{attachment.filename}`.")
                    else:
                        print(f"The file `{attachment.filename}` is not an executable.")
                        await message.channel.send(f"The file `{attachment.filename}` is not an executable.")
                        await channel.send(f"The file received in DM from `{message.author}`: `{attachment.filename}` is not an executable.")
                except Exception as e:
                    print(f"An error occurred while handling the file `{attachment.filename}`: {str(e)}")
                    await message.channel.send(f"An error occurred while handling the file `{attachment.filename}`: {str(e)}")
                    await channel.send(f"An error occurred while handling the file `{attachment.filename}` in DM from `{message.author}`: {str(e)}")
                        
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    # Ignore DMs and commands from other channels
    if ctx.guild is None or ctx.channel.id != CHANNEL_ID:
        return

    await ctx.send(f"An error occurred: {str(error)}")

@bot.event
async def on_ready():
    global channel
    channel = bot.get_channel(CHANNEL_ID)
    print(f'{bot.user.name} has connected to Discord!')
    await channel.send(f'{bot.user.name} has connected to Discord!')

async def shutdown(signal, loop):
    print(f"Received exit signal {signal.name}...")
    await channel.send(f"Received exit signal {signal.name}...")
    print("Closing connections")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    print(f"Cancelling {len(tasks)} tasks")
    await bot.logout()
    loop.stop()

def handle_exception(loop, context):
    msg = context.get("exception", context["message"])
    print(f"Caught exception: {msg}")
    print("Shutting down...")
    asyncio.create_task(shutdown(loop))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    # Check if the operating system is not Windows before adding signal handlers
    if platform.system() != "Windows":
        for s in {signal.SIGTERM, signal.SIGINT}:
            loop.add_signal_handler(
                s, lambda s=s: asyncio.create_task(shutdown(s, loop))
            )

    loop.set_exception_handler(handle_exception)

    while True:
        try:
            loop.run_until_complete(bot.start(TOKEN))
        except Exception as e:
            print(f"Exception occurred: {str(e)}. Restarting bot.")
            sleep(5)
        else:
            break