
#imports
import discord
import json
import time
import random
import youtube_dl
import os
from discord.ext import commands, tasks
from discord.utils import get

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Set up
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#pulling the info from the json file
def getPrefix(client, message):
    with open('Prefixes.json', 'r') as f: #r means read mode
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)] #guild.id is the server id

#client variable
#client = commands.Bot(command_prefix = getPrefix)
client = commands.Bot(command_prefix = '-')
client.remove_command('help') #Removing the default help command
os.chdir(r'C:\Users\danie\OneDrive\Documents\ParadoxBot')

players = {}

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Events
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

#notifying us when bot is working
@client.event
async def on_ready():
    await client.change_presence(status = discord.Status.online) #3 main things to manipulate in change_presence
    await client.change_presence(activity = discord.Game('-help | Ur a bot'))
    print('Bot is ready')

#events are a piece of code that is triggered when the bot detects something
#has happened
@client.event
async def on_message(message): #Detecting users' messages
    #await client.process_commands(message)
    #methods with message class
    author = message.author
    content = message.content
    #format prints it in the order of th second parameter: author: content
    print('{}: {}'.format(author, content))
    
@client.event
async def on_message_delete(message): #Detecting users deleting message
    author = message.author
    content = message.content
    channel = message.channel
    print('Deleted message: ', channel, '{}: {}'.format(author, content))

@client.event
async def on_member_join(member):
    print(f'{member} has joined the server.')

@client.event
async def on_member_remove(member):
    print(f'{member} has left the server.')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please enter a value!!')
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('That is not a command >:(')
    if isinstance(error, commands.CheckFailure):
        await ctx.send('You dont have perms to do that :c')
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send('Sorry bud, I cant do that')

@client.event
async def on_guild_join(guild): #event that is triggered when bot joins server
    with open('Prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)]= '-' #Adding . as default prefix for the server to the json file

    with open('Prefixes.json', 'w') as f: #w means write mode
        json.dump(prefixes, f, indent = 4)

@client.event
async def on_guild_remove(guild): #event when bot leaves the server
    with open('Prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id)) #removing the piece that applies to the server in the file 

    with open('Prefixes.json', 'w') as f: 
        json.pop(prefixes, f, indent = 4)

@client.event
async def on_member_join(member):
    with open('users.json', 'r') as f:
        users = json.load(f)

    await update_data(users, member)

    with open('users.json', 'w') as f:
        json.dump(users, f)
        

@client.event
async def on_message(message):
    with open('users.json', 'r') as f:
        users = json.load(f)

    await update_data(users, message.author)
    await add_experience(users, message.author, 5)
    await level_up(users, message.author, message.channel)

    with open('users.json', 'w') as f:
        json.dump(users, f)

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Helper Functions
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
async def update_data(users, user):
    if not user.id in users:
        users[user.id] = {}
        users[user.id]['experience'] = 0
        users[user.id]['level'] = 1

async def add_experience(users, user, exp):
    users[user.id]['experience'] = users[user.id]['experience'] + exp

async def level_up(users, user, channel):
    experience = users[user.id]['experience']
    lvl_start = users[user.id]['level']
    lvl_end = int(experience ** (1/4))

    if lvl_start < lvl_end:
        await client.send(channel, '{} has leveled up to level {}'.format(users.mention, lvl_end))
        users[user.id]['level'] = lvl_end

'''
@client.event
async def on_member_join():
    role = discord.utils.get(member.server.roles, name = 'Clan Member')
    await client.add_roles(member, role)
'''

#Command is similar to events in such way that it is a piece of code that is
#triggered when the user tells it to be triggered when they send a literal
#command

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Commands
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

@client.command()
async def changePrefix(ctx, prefix):
    with open('Prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)]= prefix

    with open('Prefixes.json', 'w') as f: 
        json.dump(prefixes, f, indent = 4)

    await ctx.send(f'Prefix changed to: {prefix}')

@client.command() #need brackets because there are different attributes Eg. hidden (dev-only) commands
async def ping(ctx): #method name is the command name
    await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

@client.command(aliases = ['8ball', 'AliasTest']) #Aliases are different ways to call the command
async def _8ball(ctx, *, question): #The * allows the intake of multiple arguments
    responses = ['It is certain.',
                 'It is decidedly so.',
                 'Without a doubt',
                 'Definitely.',
                 'You may rely on it.',
                 'As I see it, yes.',
                 'Most likely.',
                 'Outlook good.',
                 'Signs points to yes.',
                 'Reply hazy, try again later.',
                 'Ask again later.',
                 'Better not tell you now.',
                 'Cannot predict rn.',
                 'Concentrate and ask again.',
                 "Don't count on it.",
                 "My reply is no.",
                 'Outlook not so good.',
                 'Very doubtful.',]
    await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

@client.command()
@commands.has_permissions(manage_messages = True)
async def clear(ctx, amount : int):
    await ctx.channel.purge(limit = amount + 1) #Limit = messages to purge

@client.command()
@commands.has_permissions(kick_members = True)
async def kick(ctx, member : discord.Member, *, reason = None): #argument member reads member object from discord modules
    await member.kick(reason = reason) # kick is a method of member
    await ctx.send(f'Kicked {member.mention}')

@client.command()
@commands.has_permissions(ban_members = True)
async def ban(ctx, member : discord.Member, *, reason = None):
    await member.ban(reason = reason)
    await ctx.send(f'Banned {member.mention}') #mention is a method of member

@client.command()
async def unban(ctx, *, member): #no member object and cant ping because they arent in the server
    banned_users = await ctx.guild.bans() #bans is a method of guild that goes through the bans in the server and returns them as a named tuple with the user objects and reasons
    member_name, member_discriminator = member.split('#') #Splitting member into name and discriminator

    for ban_entry in banned_users: #scannning the banned people for the user entered
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator): #creating 2 tuples to see if they match
            await ctx.guild.unban(user) #unban is a guild method
            await ctx.send(f'Unbanned {user.name}#{user.discriminator}')
            return

@client.command(pass_context = True)
async def help(ctx):
    author = ctx.message.author

    embed = discord.Embed(colour = discord.Colour.purple())

    embed.set_author(name = 'Help')
    #Describing functions
    embed.add_field(name = '-ping', value = "Returns the bot's ping.", inline = False)
    embed.add_field(name = '-8ball (Question)', value = 'Answers your yes/no question.', inline = False)
    embed.add_field(name = '-changePrefix (Prefix)', value = 'Changes server prefix.', inline = False)
    embed.add_field(name = '-clear (amount)', value = 'Clears the specified amount of messages.', inline = False)
    embed.add_field(name = '-kick (user)', value = 'Kicks the user from the server.', inline = False)
    embed.add_field(name = '-ban (user)', value = 'Bans the user from the server.', inline = False)
    embed.add_field(name = '-unban (user)', value = 'Unbans the user from the server.', inline = False)

    await ctx.send(embed = embed) #sending message to user

@client.command()
async def spam(ctx, member : discord.Member):
    for i in range (5):
        await ctx.send(f'Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \nWake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n Wake up! {member.mention} \n ')
    
    

#cogs allow you to organize your code to split up commands and files; class with different commands etc.
#Checks prevent certain people from using certain commands, eg. only admins can ban

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
Audio Commands
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
'''
@client.command(pass_context = True)
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild = ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f'The bot has connexted to {channel}\n')

    await ctx.send(f'Joined {channel}')

@client.command(pass_context = True)
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild = ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f'The bot has left {channel}')
        await ctx.send(f'Left {channel}')
    else:
        print("Bot was told to leave voice channel, but was not in one")
        await ctx.send("Don't think I am in a channel rn..")

@client.command(pass_context = True)
async def play(ctx, url: str):
    song_there = os.path.isfile('song.mp3')
    try:
        if song_there:
            os.remove('song.mp3')
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file but it's being played")
        await ctx.send("Error: Music already playing")
        return

    await ctx.send("GEtting everything ready now..")

    voice = get(cleint.voice_clients, guild = ctx.guild)

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now")
        ydl.download((url))

    for file in os.listedit("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}")
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAduio("song.mp3"), after = lambda e: print(f'{name} has finished playing'))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07

    newName = name.rsplit("-", 2)
    await ctx.send(f'Playing: {newName(0)}')
    print("Playing\n")
'''
    
client.run('NjcwNzQ2MDQ4NzU0NjE0MzE0.XizFxA.1xrB9n9JNY4az4XttUOvRhZnZRY')

