import discord
from discord.ext import commands
import asyncio
from time import sleep
import sqlite3
import os
import datetime

client = commands.Bot( command_prefix = '$')
client.remove_command('help')

connection = sqlite3.connect('server.db')
cursor = connection.cursor()

@client.event
async def on_ready():
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    name TEXT,
    id INT,
    rep INT,
    cash BIGINT,
    xp INT,
    lvl INT
    
)""")



    cursor.execute("""CREATE TABLE IF NOT EXISTS shop (
        role_id INT,
        id INT,
        cost BIGINT
)""")

    cursor.execute("""CREATE TABLE IF NOT EXISTS shopbus (
        role_id INT,
        id INT,
        cost BIGINT
)""")
    



    


    connection.commit()
    print('Bot connected')

    
@client.command()
async def bank(ctx):
    useree = int(ctx.author.id) + int(ctx.guild.id)
    if cursor.execute(f"SELECT id FROM users WHERE id = {useree}").fetchone() is None:
        cursor.execute(f"INSERT INTO users VALUES ('ctx.author.name', {useree}, 0, 0, 0, 0)")
        connection.commit()
        await ctx.send("Вы успешно открыли счет в банке!")
    else:
        pass

@client.command()
async def balancee(ctx, member: discord.Member = None):
    if member is None:
        a = int(ctx.author.id) + int(ctx.guild.id)
        if cursor.execute(f"SELECT id FROM users WHERE id = {a}").fetchone() is None:
            await ctx.send("У вас не открыт счет в банке, откройте его командой: =bank")
        else:
            await ctx.send(embed = discord.Embed(
                description = f"""**{ctx.author}** ваш баланс составляет **{cursor.execute("SELECT cash From users WHERE id = {}".format(a)).fetchone()[0]} :dollar:**"""
            ))
        
        
    
    else:
        b = str(member.id) + str(ctx.author.guild.id)
        if cursor.execute(f"SELECT id FROM users WHERE id = {b}").fetchone() is None:
            await ctx.send("У данного пользователя не открыт счет в банке")
        else:
            await ctx.send(embed = discord.Embed(
                description = f"""Баланс пользователя **{member}** составляет **{cursor.execute("SELECT cash From users WHERE id = {}".format(b)).fetchone()[0]} :dollar:**"""
            ))




@client.command()
@commands.has_permissions(administrator = True)
async def addmoney(ctx, member: discord.Member = None, amount: int = None):
     if member is None:
        await ctx.send(f"**{ctx.author}**, укажите пользователя, которому вы желаете выдать определенную сумму")
     else:
         if amount is None:
             await ctx.send(f"**{ctx.author}**, укажите сумму")
         elif amount < 1:
             await ctx.send(f"**{ctx.author}**, укажите сумму больше 1 :dollar:")
         else:
             b = int(member.id) + int(ctx.author.guild.id)
             if cursor.execute(f"SELECT id FROM users WHERE id = {b}").fetchone() is None:
                 await ctx.send("У данного пользователя не открыт счет в банке")
             else:
             
                 cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, b))
                 connection.commit()

                 await ctx.message.add_reaction('👍')
            

@client.command()
@commands.has_permissions(administrator = True)
async def removemoney(ctx, member: discord.Member = None, amount = None):
     await ctx.channel.purge( limit = 1 )
     if member is None:
        await ctx.send(f"**{ctx.author}**, укажите пользователя, которому вы желаете выдать определенную сумму")
     else:
         if amount is None:
             await ctx.send(f"**{ctx.author}**, укажите сумму")
         elif amount == 'all':
             b = int(member.id) + int(ctx.author.guild.id)
             cursor.execute("UPDATE users SET cash = {} WHERE id = {}".format(0, b))
             connection.commit()

             await member.send( f'{ member.name}, с вашего счета в банке было списано **{amount} :dollar:**')
             await member.send( f'{ member.name}, ваш счет в банке **{cursor.execute("SELECT cash From users WHERE id = {}".format(b)).fetchone()[0]} :dollar:**')

             
         elif int(amount) < 1:
             await ctx.send(f"**{ctx.author}**, укажите сумму больше 1 :dollar:")
         else:
             b = int(member.id) + int(ctx.author.guild.id)
             cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(int(amount), b))
             connection.commit()

             await member.send( f'{ member.name}, с вашего счета в банке было списано **{amount} :dollar:**')
             await member.send( f'{ member.name}, ваш счет в банке **{cursor.execute("SELECT cash From users WHERE id = {}".format(b)).fetchone()[0]} :dollar:**')







token = os.environ.get('BOT_TOKEN')
client.run(str(token))
