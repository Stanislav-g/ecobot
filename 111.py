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
    else:
        pass

@client.command()
async def balancee(ctx, member: discord.Member = None):
    if member is None:
        a = int(ctx.author.id) + int(ctx.guild.id)
        if cursor.execute(f"SELECT id FROM users WHERE id = {a}").fetchone() is None:
            await ctx.send("23456")
        else:
            await ctx.send(embed = discord.Embed(
                description = f"""**{ctx.author}** ваш баланс составляет **{cursor.execute("SELECT cash From users WHERE id = {}".format(a)).fetchone()[0]} :dollar:**"""
            ))
        
        
    
    else:
        b = str(member.id) + str(ctx.author.guild.id)
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
             b = str(member.id) + str(ctx.author.guild.id)
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
             b = str(member.id) + str(ctx.author.guild.id)
             cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(int(amount), b))
             connection.commit()

             await member.send( f'{ member.name}, с вашего счета в банке было списано **{amount} :dollar:**')
             await member.send( f'{ member.name}, ваш счет в банке **{cursor.execute("SELECT cash From users WHERE id = {}".format(b)).fetchone()[0]} :dollar:**')



















    
@client.command()
async def message(ctx, member: discord.Member = None):
    if member is None:
        lvlnum = cursor.execute("SELECT lvl FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]
        totallvl = lvlnum
        await ctx.send(embed = discord.Embed(
            description = f'У {ctx.author} {totallvl} отправленых сообщений'
        ))
    else:
        if cursor.execute("SELECT lvl FROM users WHERE id = {}".format(member.id)).fetchone()[0] == 1:
            await ctx.send(embed = discord.Embed(
            description = f'У {member} {cursor.execute("SELECT lvl FROM users WHERE id = {}".format(member.id)).fetchone()[0]} отправленых сообщений'
        ))
        else:
            await ctx.send(embed = discord.Embed(
                description = f'У {member} {cursor.execute("SELECT lvl FROM users WHERE id = {}".format(member.id)).fetchone()[0]} отправленых сообщений'
            ))
    

@client.command()
@commands.has_permissions(administrator = True)
async def addshop(ctx, role: discord.Role = None, cost: int = None):
    await ctx.channel.purge( limit = 1 )
    if role is None:
        await ctx.send(f"**{ctx.author}**, укажите роль")
    if cost is None:
        await ctx.send(f"**{ctx.author}**, укажите стоимость данной роли")

    elif cost < 0:
        await ctx.send(f"**{ctx.author}**, стоимость роли не может быть отрицательной")
    else:
        cursor.execute("INSERT INTO shop VALUES ({}, {}, {})".format(role.id, ctx.guild.id, cost))
        connection.commit()
             
             

                
@client.command()
@commands.has_permissions(administrator = True)
async def removeshop(ctx, role: discord.Role = None):
    await ctx.channel.purge( limit = 1 )
    if role is None:
        await ctx.send(f"**{ctx.author}**, укажите роль")
        
    else:
        cursor.execute("DELETE FROM shop WHERE role_id = {}".format(role.id))
        connection.commit()




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
        if role in ctx.author.roles:
            await ctx.send(f"**{ctx.author}**, у вас уже имеется данная роль")
        elif cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0] > cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]:
            await ctx.send(f"**{ctx.author}**, на вашем счету недостаточно средств")
        else:
            await ctx.author.add_roles(role)
            cursor.execute("UPDATE users SET cash = cash - {0} WHERE id = {1}".format(cursor.execute("SELECT cost FROM shop WHERE role_id = {}".format(role.id)).fetchone()[0], ctx.author.id))

            await ctx.author.send( f'{ctx.author.name}, поздравляю вас! Вы купили роль **{role}**')
            if role == 728595813663506467:
                s = random.choise(['100','500','1000','1100','2000','200','1300','1400','100','3000','100','700','800','900','999','2000','1111'])
                cursor.execute("UPDATE users SET cash = cash + {s} WHERE id = {}".format(ctx.author.id))
                connection.commit()
                await ctx.author.send( f'{ctx.author.name}, поздравляю вас! Вам выпало {s} ')
                await asyncio.sleep(3)
                ppp_role = discord.utils.get( ctx.message.guild.roles, name = 'Кейс с деньгами от 100 до 3000!')
                await member.remove_roles( ppp_role )
            

#help
@client.command( pass_context = True )

async def help( ctx ):
    
    embert = discord.Embed( title = 'HELP', colour = discord.Color.red() )
    embert.add_field( name = 'Commands',value = 'balance - баланс игрока\nshop - магазин ролей\nbuyrole - купить роль\nclik - кликер\nshopbusiness - магазин бизнеса\nbuybus - купить бизнес (@coffee, @restaurant, @carservice)\ntext - отправить сообщение другому пользователю за 50 :dollar:\nperevod - перевод денег пользователю(ник, сумма)')
    await ctx.author.send( embed = embert )


@client.command()
async def clik(ctx):
     await ctx.channel.purge( limit = 1 )
     cursor.execute("UPDATE users SET cash = cash + 1 WHERE id = {}".format(ctx.author.id))
     connection.commit()
     

#------------------------------------------------------------------------------           
@client.command()
async def text(ctx, arg = None, member: discord.Member = None):
     await ctx.channel.purge( limit = 1 )
     if member is None:
        await ctx.author.send(f"**{ctx.author}**, укажите пользователя, которому вы желаете написать сообщение")
     else:
         if arg is None:
             await ctx.author.send(f"**{ctx.author}**, укажите пользователя, которому вы желаете написать сообщение")
         else:
             cursor.execute("UPDATE users SET cash = cash - 50 WHERE id = {}".format(ctx.author.id))
             connection.commit()

             await member.send(arg)

@client.command()
async def perevod(ctx, member: discord.Member = None, amount: int = None):
     
     if member is None:
        await ctx.send(f"**{ctx.author}**, укажите пользователя, которому вы желаете выдать определенную сумму")
     else:
         if amount is None:
             await ctx.send(f"**{ctx.author}**, укажите сумму")
         elif amount < 1:
             await ctx.send(f"**{ctx.author}**, укажите сумму больше 1 :dollar:")
         
         else:
             cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, member.id))
             cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(amount, ctx.author.id))
             connection.commit()

             await member.send( f'{ member.name}, вам было начислено на счет в банке **{amount} :dollar:**')
             await member.send( f'{ member.name}, ваш счет в банке **{cursor.execute("SELECT cash From users WHERE id = {}".format(member.id)).fetchone()[0]} :dollar:**')

       



token = os.environ.get('BOT_TOKEN')
client.run(str(token))
