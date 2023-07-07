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
async def on_command_error(ctx, error):
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