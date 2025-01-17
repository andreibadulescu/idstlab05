#!./.venv/bin/python

# Copyright (C) 2024 Andrei Bădulescu
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

BOT_TOKEN="MTMwOTg4ODE2NjAzNDkzNTkyOQ.GKJL7j.p3zdl7GccgUuCZQoDbafsJumPoU6gJVGZZsVAMX"
 
import discord      # base discord module
import code         # code.interact
import os           # environment variables
import inspect      # call stack inspection
import random       # dumb random number generator
import IPython
from discord.ext import commands    # Bot class and utils
from discord import FFmpegPCMAudio

################################################################################
############################### HELPER FUNCTIONS ###############################
################################################################################
 
# log_msg - fancy print
#   @msg   : string to print
#   @level : log level from {'debug', 'info', 'warning', 'error'}
def log_msg(msg: str, level: str):
    # user selectable display config (prompt symbol, color)
    dsp_sel = {
        'debug'   : ('\033[34m', '-'),
        'info'    : ('\033[32m', '*'),
        'warning' : ('\033[33m', '?'),
        'error'   : ('\033[31m', '!'),
    }
 
    # internal ansi codes
    _extra_ansi = {
        'critical' : '\033[35m',
        'bold'     : '\033[1m',
        'unbold'   : '\033[2m',
        'clear'    : '\033[0m',
    }
 
    # get information about call site
    caller = inspect.stack()[1]
 
    # input sanity check
    if level not in dsp_sel:
        print('%s%s[@] %s:%d %sBad log level: "%s"%s' % \
            (_extra_ansi['critical'], _extra_ansi['bold'],
             caller.function, caller.lineno,
             _extra_ansi['unbold'], level, _extra_ansi['clear']))
        return
 
    # print the damn message already
    print('%s%s[%s] %s:%d %s%s%s' % \
        (_extra_ansi['bold'], *dsp_sel[level],
         caller.function, caller.lineno,
         _extra_ansi['unbold'], msg, _extra_ansi['clear']))
 
################################################################################
############################## BOT IMPLEMENTATION ##############################
################################################################################
 
# bot instantiation
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)
 
# on_ready - called after connection to server is established
@bot.event
async def on_ready():
    log_msg('logged on as <%s>' % bot.user, 'info')
 
# on_message - called when a new message is posted to the server
#   @msg : discord.message.Message
@bot.event
async def on_message(msg):
    # filter out our own messages
    if msg.author == bot.user:
        return
 
    log_msg('message from <%s>: "%s"' % (msg.author, msg.content), 'debug')
 
    # overriding the default on_message handler blocks commands from executing
    # manually call the bot's command processor on given message
    await bot.process_commands(msg)
 
# roll - rng chat command
#   @ctx     : command invocation context
#   @max_val : upper bound for number generation (must be at least 1)
@bot.command(brief='Generate random number between 1 and <arg>')
async def roll(ctx, max_val: int):
    # argument sanity check
    if max_val < 1:
        raise Exception('argument <max_val> must be at least 1')
 
    await ctx.send(random.randint(1, max_val))
 

# summon - connect to VC command
#   @ctx     : command invocation context
@bot.command(brief='Connects bot to user voice channel')
async def summon(ctx):
    # checks if invoker is connected to a voice channel
    if (ctx.author.voice):
        await ctx.author.voice.channel.connect()
    else:
        await ctx.send("Connect to a voice channel first!")

# leave - disconnect from VC command
#   @ctx     : command invocation context
@bot.command(brief='Disconnects bot from voice channel')
async def leave(ctx):
    # checks if bot is connected to a voice channel
    if (ctx.bot.voice_clients):
        await ctx.bot.voice_clients[0].disconnect()
    else:
        await ctx.send("I am not connected to any voice channel...")

# audiotracks - lists the available audio tracks
#   @ctx     : command invocation context
@bot.command(brief='Lists the available audio tracks')
async def audiotracks(ctx):
    await ctx.send("I can play the following tracks:\n - pipe.mp3")

# play - play a MP3 file from a given list
#   @ctx       : command invocation context
#   @file_name : MP3 file name provided by the user
@bot.command(brief='Plays the selected song from the provided list')
async def play(ctx, file_name: str):
    # checks if bot is connected to a voice channel
    if (ctx.bot.voice_clients):
        if (ctx.bot.voice_clients[0].is_playing()):
            await ctx.bot.voice_clients[0].stop()
        voice_channel = ctx.bot.voice_clients[0]
        source = FFmpegPCMAudio(file_name)
        player = voice_channel.play(source)
    else:
        await ctx.send("I am not connected to any voice channel...")

# roll_error - error handler for the <roll> command
#   @ctx     : command that crashed invocation context
#   @error   : ...
@roll.error
async def roll_error(ctx, error):
    await ctx.send(str(error))
 
################################################################################
############################# PROGRAM ENTRY POINT ##############################
################################################################################
 
if __name__ == '__main__':
    # check that token exists in environment
    if 'BOT_TOKEN' not in os.environ:
        log_msg('save your token in the BOT_TOKEN env variable!', 'error')
        exit(-1)
 
    # launch bot (blocking operation)
    bot.run(os.environ['BOT_TOKEN'])
