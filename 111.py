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
async def balance(ctx, member: discord.Member = None):
    if member is None:
        a = int(ctx.author.id) + int(ctx.guild.id)
        if cursor.execute(f"SELECT id FROM users WHERE id = {a}").fetchone() is None:
            await ctx.send("У вас не открыт счет в банке, откройте его командой: =bank")
        else:
            await ctx.send(embed = discord.Embed(
                description = f"""**{ctx.author}** ваш баланс составляет **{cursor.execute("SELECT cash From users WHERE id = {}".format(a)).fetchone()[0]} :dollar:**"""
            ))
        
        
    
    else:
        b = int(member.id) + int(ctx.author.guild.id)
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

@client.command()
@commands.has_permissions(administrator = True)
async def addshop(ctx, role: discord.Role = None, cost: int = None):
    if role is None:
        await ctx.send(f"**{ctx.author}**, укажите роль")
    if cost is None:
        await ctx.send(f"**{ctx.author}**, укажите стоимость данной роли")

    elif cost < 0:
        await ctx.send(f"**{ctx.author}**, стоимость роли не может быть отрицательной")
    else:
        r = int(role.id) + int(ctx.guild.id)
        if cursor.execute(f"SELECT id FROM shop WHERE role_id = {role.id}").fetchone() is None:
            cursor.execute("INSERT INTO shop VALUES ({}, {}, {})".format(role.id, ctx.guild.id, cost))
            connection.commit()
            await ctx.send("Роль добавленна в магазин!")
        else:
            await ctx.send("Данная роль уже в магазине!")
             

                
@client.command()
@commands.has_permissions(administrator = True)
async def removeshop(ctx, role: discord.Role = None):
    await ctx.channel.purge( limit = 1 )
    if role is None:
        await ctx.send(f"**{ctx.author}**, укажите роль")
        
    else:
        r = int(role.id) + int(ctx.guild.id)
        cursor.execute("DELETE FROM shop WHERE role_id = {}".format(role.id))
        connection.commit()
        await ctx.send("Роль удалена из магазина!")




@client.command()
async def shop(ctx):
    embed = discord.Embed(title = 'Магазин ролей $buyrole @роль')
    for row in cursor.execute("SELECT role_id, cost FROM shop WHERE id = {}".format(ctx.guild.id)):
        if ctx.guild.get_role(row[0]) != None:
            embed.add_field(
                name = f"Стоимость **{row[1]} :dollar:**",
                value = f"Вы приобретете роль {ctx.guild.get_role(row[0]).mention}",
                inline = False
            )
        else:
            pass
        
    await ctx.send(embed = embed)



@client.command()
async def buyrole(ctx, role: discord.Role = None):
    await ctx.channel.purge( limit = 1 )
    
    if role is None:
        await ctx.send(f"**{ctx.author}**, укажите роль которую вы желаете приобрести")
    else:
        a = int(ctx.author.id) + int(ctx.guild.id)
        if cursor.execute(f"SELECT id FROM users WHERE id = {a}").fetchone() is None:
            await ctx.send("У вас не открыт счет в банке, откройте его командой: =bank")
        else:
            r = int(role.id) + int(ctx.guild.id)
            a = int(ctx.author.id) + int(ctx.guild.id)
            if role in ctx.author.roles:
                await ctx.send(f"**{ctx.author}**, у вас уже имеется данная роль")
            elif cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0] > cursor.execute("SELECT cash FROM users WHERE id = {}".format(a)).fetchone()[0]:
                await ctx.send(f"**{ctx.author}**, на вашем счету недостаточно средств")
            else:
                await ctx.author.add_roles(role)
                r = int(role.id) + int(ctx.guild.id)
                a = int(ctx.author.id) + int(ctx.guild.id)
                cursor.execute("UPDATE users SET cash = cash - {0} WHERE id = {1}".format(cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0], a))

                await ctx.author.send( f'{ctx.author.name}, поздравляю вас! Вы купили роль **{role}**')

            




@client.command()
async def perevod(ctx, member: discord.Member = None, amount: int = None):
     a = int(ctx.author.id) + int(ctx.guild.id)
     
     if cursor.execute(f"SELECT id FROM users WHERE id = {a}").fetchone() is None:
         await ctx.send("У вас не открыт счет в банке, откройте его командой: =bank")
     else:
         if member is None:
             await ctx.send(f"**{ctx.author}**, укажите пользователя, которому вы желаете перевести определенную сумму")
         else:
             b = int(member.id) + int(ctx.author.guild.id)
             if cursor.execute(f"SELECT id FROM users WHERE id = {b}").fetchone() is None:
                 await ctx.send("У данного пользователя не открыт счет в банке!")
             else:
                 if amount is None:
                     await ctx.send(f"**{ctx.author}**, укажите сумму")
                 elif amount < 1:
                     await ctx.send(f"**{ctx.author}**, укажите сумму больше 1 :dollar:")
                 
                 else:
                     cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, b))
                     cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(amount, a))
                     connection.commit()

                     await member.send( f'{ member.name}, вам было начислено на счет в банке **{amount} :dollar:**')
                     await member.send( f'{ member.name}, ваш счет в банке **{cursor.execute("SELECT cash From users WHERE id = {}".format(b)).fetchone()[0]} :dollar:**')

               







token = os.environ.get('BOT_TOKEN')
client.run(str(token))
