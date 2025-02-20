# -*- coding: utf8 -*-
import discord
import asyncio
from discord.ext.commands import Bot
from discord.ext import commands, tasks
import sys, traceback
import json
from cogs.utils import helper_functions as hf
from datetime import datetime
import os
from dotenv import load_dotenv

import logging
logging.basicConfig(level=logging.WARNING)
# logger = logging.getLogger('discord')
# logger.setLevel(logging.INFO)
# handler = logging.FileHandler(
#     filename=f'{dir_path}/log/{discord.utils.utcnow().strftime("%y%m%d_%H%M")}.log',
#     encoding='utf-8',
#     mode='a')
# handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)

# noinspection lines to fix pycharm error saying Intents doesn't have members and Intents is read-only
intents = discord.Intents.default()
# noinspection PyUnresolvedReferences,PyDunderSlots
intents.members = True
# noinspection PyUnresolvedReferences,PyDunderSlots
intents.message_content = True
dir_path = os.path.dirname(os.path.realpath(__file__))

# Change these two values to channel IDs in your testing server if you are forking the bot
TRACEBACK_LOGGING_CHANNEL = 554572239836545074
BOT_TEST_CHANNEL = 304110816607862785

t_start = datetime.now()


def prefix(bot, msg):
    if bot.user.name == "Rai":
        default = ';'
    else:
        default = 'r;'
    if msg.guild:
        return bot.db['prefix'].get(str(msg.guild.id), default)
    else:
        return default


class Rai(Bot):
    def __init__(self):
        super().__init__(description="Bot by Ryry013#9234", command_prefix=prefix, owner_id=202995638860906496,
                         help_command=None, intents=intents, max_messages=10000)
        self.language_detection = False
        print('starting loading of jsons')

        # Create json files if they don't exist
        if not os.path.exists(f"{dir_path}/db.json"):
            db = open(f"{dir_path}/db.json", 'w')
            new_db = {'ultraHardcore': {}, 'hardcore': {}, 'welcome_message': {}, 'roles': {}, 'ID': {},
                      'mod_channel': {}, 'mod_role': {}, 'deletes': {}, 'nicknames': {}, 'edits': {},
                      'leaves': {}, 'reactions': {}, 'captcha': {}, 'bans': {}, 'kicks': {}, 'welcomes': {},
                      'auto_bans': {}, 'global_blacklist': {}, 'super_voicewatch': {}, 'report': {},
                      'super_watch': {}, 'prefix': {}, 'questions': {}, 'mutes': {}, 'submod_role': {},
                      'colors': {}, 'submod_channel': {}, 'SAR': {}, 'channel_mod': {}, 'channel_mods': {},
                      'modlog': {}, 'dbtest': {}, 'modsonly': {}, 'voice_mods': [], 'voice_mutes': {},
                      'selfmute': {}, 'voicemod': {}, 'staff_ping': {}, 'voice': {}, 'new_user_watch': {},
                      'reactionroles': {}, 'pmbot': {}, 'joins': {}, 'timed_voice_role': {}, 'banlog': {},
                      'bansub': {}, 'forcehardcore': [], 'wordfilter': {}, 'ignored_servers': [], 'antispam': {},
                      'lovehug': {}, 'rawmangas': {}, 'risk': {}, 'guildstats': {}, 'bannedservers': [],
                      'spvoice': [], 'spam_links': []}
            # A lot of these are unnecessary now but I'll fix that later when I make a new database
            print("Creating default values for database.")
            json.dump(new_db, db)
            db.close()
        if not os.path.exists(f"{dir_path}/stats.json"):
            db = open(f"{dir_path}/stats.json", 'w')
            json.dump({}, db)
            db.close()

        try:
            with open(f"{dir_path}/db.json", "r") as read_file1:
                read_file1.seek(0)
                self.db = json.load(read_file1)
        except json.decoder.JSONDecodeError as e:
            if e.msg == "Expecting value":
                logging.warning("No data detected in db.json")
                self.db = {}
            else:
                raise

        try:
            with open(f"{dir_path}/stats.json", "r") as read_file2:
                read_file2.seek(0)
                self.stats = json.load(read_file2)
        except json.decoder.JSONDecodeError as e:
            if e.msg == "Expecting value":
                logging.warning("No data detected in stats.json")
                self.stats = {}
            else:
                raise

        initial_extensions = ['cogs.admin', 'cogs.channel_mods', 'cogs.general', 'cogs.jpserv', 'cogs.logger',
                              'cogs.math', 'cogs.owner', 'cogs.questions', 'cogs.reports', 'cogs.stats', 'cogs.submod']

        for extension in initial_extensions:
            try:  # in on_ready because if not I get tons of errors from on_message before bot loads
                self.load_extension(extension)
                print(f'Loaded {extension}')
            except Exception as e:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
                traceback.print_exc()
                continue

    async def on_ready(self):
        await hf.load_language_dection_model()
        self.language_detection = True

        test_channel = self.get_channel(BOT_TEST_CHANNEL)

        if test_channel:
            ctxmsg = await test_channel.send("Almost done!")
            self.ctx = await self.get_context(ctxmsg)
        else:
            ctxmsg = self.ctx = None

        try:  # in on_ready because if not I get tons of errors from on_message before bot loads
            self.load_extension('cogs.background')
            print(f'Loaded cogs.background')
        except Exception as e:
            print(f'Failed to load extension cogs.background.', file=sys.stderr)
            traceback.print_exc()

        print("Bot loaded")

        t_finish = datetime.now()

        if ctxmsg:
            ctxmsg = await ctxmsg.edit(content=f'Bot loaded (time: {t_finish - t_start})')

        await self.change_presence(activity=discord.Game(';help for help'))

        self.database_backups.start()

    @tasks.loop(hours=24)
    async def database_backups(self):
        date = datetime.today().strftime("%Y%m%d-%H.%M")
        with open(f"{dir_path}/database_backups/database_{date}.json", "w") as write_file:
            json.dump(self.db, write_file)
        with open(f"{dir_path}/database_backups/stats_{date}.json", "w") as write_file:
            json.dump(self.stats, write_file)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            # parsing or conversion failure is encountered on an argument to pass into a command.
            await ctx.send(f"Failed to find the object you tried to look up.  Please try again")
            return

        elif isinstance(error, commands.MaxConcurrencyReached):
            if ctx.author == self.user:
                pass
            else:
                await ctx.send("You're sending that command too many times. Please wait a bit.")
                return

        elif isinstance(error, discord.DiscordServerError):
            try:
                await asyncio.sleep(5)
                await ctx.send(f"There was a discord server error. Please try again.")
            except discord.DiscordServerError:
                return

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send("You can only use this in a guild.")
                return
            except discord.Forbidden:
                pass

        elif isinstance(error, discord.Forbidden):
            try:
                await ctx.author.send("Rai lacked permissions to do something there")
            except discord.Forbidden:
                pass

        elif isinstance(error, commands.BotMissingPermissions):
            msg = f"To do that command, Rai is missing the following permissions: " \
                  f"`{'`, `'.join(error.missing_permissions)}`"
            try:
                await ctx.send(msg)
            except discord.Forbidden:
                try:
                    await ctx.author.send(msg)
                except discord.Forbidden:
                    pass
            return

        elif isinstance(error, commands.CommandInvokeError):
            command = ctx.command.qualified_name
            try:
                await ctx.send(f"I couldn't execute the command.  I probably have a bug.  "
                               f"This has been reported to Ryan.")
            except discord.Forbidden:
                await ctx.author.send(f"I tried doing something but I lack permissions to send messages.  "
                                      f"I probably have a bug.  This has been reported to Ryan.")
            pass

        elif isinstance(error, commands.CommandNotFound):
            # no command under that name is found
            return

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown.  Try again in {round(error.retry_after)} seconds.")
            return

        elif isinstance(error, commands.CheckFailure):
            # the predicates in Command.checks have failed.
            if ctx.command.name == 'global_blacklist':
                return
            if ctx.guild:
                if str(ctx.guild.id) in self.db['modsonly']:
                    if self.db['modsonly'][str(ctx.guild.id)]['enable']:
                        if not hf.admin_check(ctx):
                            return

            if ctx.command.cog.qualified_name in ['Admin', 'Logger', 'ChannelMods', 'Submod'] and \
                    (str(ctx.guild.id) not in self.db['mod_channel'] and ctx.command.name != 'set_mod_channel'):
                try:
                    await ctx.send(
                        "Please set a mod channel or logging channel for Rai to send important error messages to"
                        " by typing `;set_mod_channel` in some channel.")
                except discord.Forbidden:
                    try:
                        await ctx.author.send("Rai lacks permission to send messages in that channel.")
                    except discord.Forbidden:
                        pass
                return
            try:
                if not ctx.guild:
                    raise discord.Forbidden
                if str(ctx.guild.id) in self.db['mod_role']:
                    await ctx.send("You lack permissions to do that.")
                else:
                    await ctx.send(f"You lack the permissions to do that.  If you are a mod, try using "
                                   f"`{self.db['prefix'].get(str(ctx.guild.id), ';')}set_mod_role <role name>`")
            except discord.Forbidden:
                await ctx.author.send(f"I tried doing something but I lack permissions to send messages.")
            return

        elif isinstance(error, commands.MissingRequiredArgument):
            # parsing a command and a parameter that is required is not encountered
            msg = f"You're missing a required argument ({error.param}).  " \
                  f"Try running `;help {ctx.command.qualified_name}`"
            if error.param.name in ['args', 'kwargs']:
                msg = msg.replace(f" ({error.param})", '')
            try:
                await ctx.send(msg)
            except discord.Forbidden:
                pass
            return

        elif isinstance(error, discord.Forbidden):
            await ctx.send(f"I tried to do something I'm not allowed to do, so I couldn't complete your command :(")

        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"To do that command, you are missing the following permissions: "
                           f"`{'`, `'.join(error.missing_permissions)}`")
            return

        elif isinstance(error, commands.NotOwner):
            await ctx.send(f"Only Ryan can do that.")
            return

        print(datetime.now())
        error = getattr(error, 'original', error)
        qualified_name = getattr(ctx.command, 'qualified_name', ctx.command.name)
        print(f'Error in {qualified_name}:', file=sys.stderr)
        traceback.print_tb(error.__traceback__)
        print(f'{error.__class__.__name__}: {error}', file=sys.stderr)

        e = discord.Embed(title='Command Error', colour=0xcc3366)
        e.add_field(name='Name  ', value=qualified_name)
        e.add_field(name='Command', value=ctx.message.content[:1000])
        e.add_field(name='Author', value=f'{ctx.author} (ID: {ctx.author.id})')

        fmt = f'Channel: {ctx.channel} (ID: {ctx.channel.id})'
        if ctx.guild:
            fmt = f'{fmt}\nGuild: {ctx.guild} (ID: {ctx.guild.id})'

        e.add_field(name='Location', value=fmt, inline=False)

        exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=False))
        traceback_text = f'{ctx.message.jump_url}\n```py\n{exc}```'
        e.timestamp = discord.utils.utcnow()
        await self.get_channel(TRACEBACK_LOGGING_CHANNEL).send(traceback_text[:2000], embed=e)
        print('')

    async def on_error(self, event, *args, **kwargs):
        e = discord.Embed(title='Event Error', colour=0xa32952)
        e.add_field(name='Event', value=event)
        e.description = f'```py\n{traceback.format_exc()}\n```'
        e.timestamp = discord.utils.utcnow()

        args_str = ['```py']
        jump_url = ''
        for index, arg in enumerate(args):
            args_str.append(f'[{index}]: {arg!r}')
            if type(arg) == discord.Message:
                e.add_field(name="Author", value=f'{arg.author} (ID: {arg.author.id})')
                fmt = f'Channel: {arg.channel} (ID: {arg.channel.id})'
                if arg.guild:
                    fmt = f'{fmt}\nGuild: {arg.guild} (ID: {arg.guild.id})'
                e.add_field(name='Location', value=fmt, inline=False)
                jump_url = arg.jump_url
        args_str.append('```')
        e.add_field(name='Args', value='\n'.join(args_str), inline=False)
        try:
            await self.get_channel(TRACEBACK_LOGGING_CHANNEL).send(jump_url, embed=e)
        except AttributeError:
            pass  # Set ID of TRACEBACK_LOGGING_CHANNEL at top of this file to a channel in your testing server
        traceback.print_exc()


bot = Rai()
guilds = [189571157446492161, 243838819743432704, 275146036178059265]
# There will be a discord.errors.Forbidden error here if you do not have these guilds on your bot


@bot.message_command(name="Delete message", guild_ids=guilds)
async def delete_and_log(ctx, message: discord.Message):
    delete = ctx.bot.get_command("delete")
    try:
        if await delete.can_run(ctx):
            await delete.__call__(ctx, str(message.id))
            await ctx.interaction.response.send_message("The message has been successfully deleted", ephemeral=True)
        else:
            await ctx.interaction.response.send_message("You don't have the permission to use that command",
                                                        ephemeral=True)
    except commands.BotMissingPermissions:
        await ctx.interaction.response.send_message("The bot is missing permissions here to use that command.",
                                                    ephemeral=True)


@bot.message_command(name="1h text/voice mute", guild_ids=guilds)
async def context_message_mute(ctx, message: discord.Message):
    mute = ctx.bot.get_command("mute")
    ctx.message = ctx.channel.last_message

    try:
        if await mute.can_run(ctx):
            await mute.__call__(ctx, args=f"{str(message.author.id)} 1h")
            await ctx.interaction.response.send_message("Command completed", ephemeral=True)

        else:
            await ctx.interaction.response.send_message("You don't have the permission to use that command",
                                                        ephemeral=True)
    except commands.BotMissingPermissions:
        await ctx.interaction.response.send_message("The bot is missing permissions here to use that command.",
                                                    ephemeral=True)


@bot.user_command(name="1h text/voice mute", guild_ids=guilds)
async def context_user_mute(ctx, member: discord.Member):
    mute = ctx.bot.get_command("mute")
    ctx.message = ctx.channel.last_message

    try:
        if await mute.can_run(ctx):
            await mute.__call__(ctx, args=f"{str(member.id)} 1h")
            await ctx.interaction.response.send_message("Command completed", ephemeral=True)

        else:
            await ctx.interaction.response.send_message("You don't have the permission to use that command",
                                                        ephemeral=True)
    except commands.BotMissingPermissions:
        await ctx.interaction.response.send_message("The bot is missing permissions here to use that command.",
                                                    ephemeral=True)


"""
@bot.message_command(name="Ban and clear3", check=hf.admin_check)  # creates a global message command
async def ban_and_clear(ctx, message: discord.Message):  # message commands return the message
    ban = ctx.bot.get_command("ban")
    if await ban.can_run(ctx):
        await ban.__call__(ctx, args=f"{str(message.author.id)} ⁣")  # invisible character to trigger ban shortcut
        await ctx.interaction.response.send_message("The message has been successfully deleted", ephemeral=True)
    else:
        await ctx.interaction.response.send_message("You don't have the permission to use that command", ephemeral=True)
"""

try:
    with open(f"{dir_path}/.env", 'r') as f:
        pass
except FileNotFoundError:
    txt = """BOT_TOKEN=\nGCSE_API="""
    with open(f'{dir_path}/.env', 'w') as f:
        f.write(txt)
    print("I've created a .env file for you, go in there and put your bot token in the file.\n"
          "There is also a spot for your GCSE api key if you have one, \n"
          "but if you don't you can leave that blank.")
    exit()

# Credentials
load_dotenv('.env')

if not os.getenv("BOT_TOKEN"):
    raise discord.LoginFailure("You need to add your bot token to the .env file in your bot folder.")

# A little bit of a detterent from my token instantly being used if the .env file gets leaked somehow
if "Rai" == os.path.basename(dir_path) and "Ryry013" in dir_path:
    bot.run(os.getenv("BOT_TOKEN") + 'k')  # Rai
elif "ForkedRai" == os.path.basename(dir_path) and "Ryry013" in dir_path:
    bot.run(os.getenv("BOT_TOKEN") + '4')  # Rai
elif "Local" in os.path.basename(dir_path) and "Ryry013" in dir_path:
    bot.run(os.getenv("BOT_TOKEN") + '4')  # Rai Test
else:
    bot.run(os.getenv("BOT_TOKEN"))  # For other people forking Rai bot
