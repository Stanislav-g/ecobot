import discord
from discord.ext import commands
import asyncio
from time import sleep
import sqlite3
import os

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
    cashh BIGINT,
    rep INT,
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


    
    for guild in client.guilds:
         for member in guild.members:
             if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
                 cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 0)")
             else:
                 pass

    connection.commit()
    print('Bot connected')

@client.command()
async def status(ctx):
    await ctx.channel.purge( limit = 1 )
    while True:
        await client.change_presence(activity=discord.Game(name='youtube Nitagas'))
        await asyncio.sleep(60)
        activity = discord.Activity(name='$help', type=discord.ActivityType.watching)
        await client.change_presence(activity=activity)
        await asyncio.sleep(60)
        activity = discord.Activity(name='канал Nitagas', type=discord.ActivityType.watching)
        await client.change_presence(activity=activity)
        await asyncio.sleep(60)
        activity = discord.Activity(name='$help', type=discord.ActivityType.watching)
        await client.change_presence(activity=activity)
        await asyncio.sleep(60)

    

@client.event
async def on_member_join(member):
    if cursor.execute(f"SELECT id FROM users WHERE id = {member.id}").fetchone() is None:
        cursor.execute(f"INSERT INTO users VALUES ('{member}', {member.id}, 0, 0, 0)")
        connection.commit()
    else:
        pass

@client.command()
async def balance(ctx, member: discord.Member = None):
    await ctx.channel.purge( limit = 1 )
    if member is None:
        await ctx.author.send(embed = discord.Embed(
            description = f"""**{ctx.author}** ваш баланс составляет **{cursor.execute("SELECT cash From users WHERE id = {}".format(ctx.author.id)).fetchone()[0]} :dollar:**"""
        ))
    
    else:
        await ctx.author.send(embed = discord.Embed(
            description = f"""Баланс пользователя **{member}** составляет **{cursor.execute("SELECT cash From users WHERE id = {}".format(member.id)).fetchone()[0]} :dollar:**"""
        ))
        
    
@client.command()
@commands.has_permissions(administrator = True)
async def addmoney(ctx, member: discord.Member = None, amount: int = None):
     await ctx.channel.purge( limit = 1 )
     if member is None:
        await ctx.send(f"**{ctx.author}**, укажите пользователя, которому вы желаете выдать определенную сумму")
     else:
         if amount is None:
             await ctx.send(f"**{ctx.author}**, укажите сумму")
         elif amount < 1:
             await ctx.send(f"**{ctx.author}**, укажите сумму больше 1 :dollar:")
         else:
             cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(amount, member.id))
             connection.commit()

             await member.send( f'{ member.name}, вам было начислено на счет в банке **{amount} :dollar:**')
             await member.send( f'{ member.name}, ваш счет в банке **{cursor.execute("SELECT cash From users WHERE id = {}".format(member.id)).fetchone()[0]} :dollar:**')


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
             cursor.execute("UPDATE users SET cash = {} WHERE id = {}".format(0, member.id))
             connection.commit()

             await member.send( f'{ member.name}, с вашего счета в банке было списано **{amount} :dollar:**')
             await member.send( f'{ member.name}, ваш счет в банке **{cursor.execute("SELECT cash From users WHERE id = {}".format(member.id)).fetchone()[0]} :dollar:**')

             
         elif int(amount) < 1:
             await ctx.send(f"**{ctx.author}**, укажите сумму больше 1 :dollar:")
         else:
             cursor.execute("UPDATE users SET cash = cash - {} WHERE id = {}".format(int(amount), member.id))
             connection.commit()

             await member.send( f'{ member.name}, с вашего счета в банке было списано **{amount} :dollar:**')
             await member.send( f'{ member.name}, ваш счет в банке **{cursor.execute("SELECT cash From users WHERE id = {}".format(member.id)).fetchone()[0]} :dollar:**')


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
    embed = discord.Embed(title = 'Магазин ролей')

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





@client.command( pass_context = True )
@commands.has_permissions(administrator = True)
async def adminhelp( ctx ):
    
    emb = discord.Embed( title = 'HELP', colour = discord.Color.red() )
    emb.add_field( name = 'Commands',value = 'addmoney\nremovemoney\naddshop\nremoveshop\naddbusshop\nremovebusshop\n')
    await ctx.author.send( embed = emb )

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
@commands.has_permissions(administrator = True)
async def addbusshop(ctx, role: discord.Role = None, cost: int = None):
    await ctx.channel.purge( limit = 1 )
    if role is None:
        await ctx.send(f"**{ctx.author}**, укажите роль")
    if cost is None:
        await ctx.send(f"**{ctx.author}**, укажите стоимость данной роли")

    elif cost < 0:
        await ctx.send(f"**{ctx.author}**, стоимость роли не может быть отрицательной")
    else:
        cursor.execute("INSERT INTO shopbus VALUES ({}, {}, {})".format(role.id, ctx.guild.id, cost))
        connection.commit()
             
             
             
@client.command()
@commands.has_permissions(administrator = True)
async def removebusshop(ctx, role: discord.Role = None):
    await ctx.channel.purge( limit = 1 )
    if role is None:
        await ctx.send(f"**{ctx.author}**, укажите роль")
        
    else:
        cursor.execute("DELETE FROM shopbus WHERE role_id = {}".format(role.id))
        connection.commit()




@client.command()
async def shopbusiness(ctx):
    embed = discord.Embed(title = 'Магазин бизнессов')

    for row in cursor.execute("SELECT role_id, cost FROM shopbus WHERE id = {}".format(ctx.guild.id)):
        if ctx.guild.get_role(row[0]) != None:
            embed.add_field(
                name = f"Стоимость **{row[1]} :dollar:**",
                value = f"Вы приобретете бизнес {ctx.guild.get_role(row[0]).mention}",
                inline = False
            )
        else:
            pass
        
    await ctx.send(embed = embed)

            
        
    


@client.command()
async def buybus(ctx, role: discord.Role = None):
    await ctx.channel.purge( limit = 1 )
    if role is None:
        await ctx.send(f"**{ctx.author}**, укажите бизнес который вы желаете приобрести")
    else:
        if role in ctx.author.roles:
            await ctx.send(f"**{ctx.author}**, у вас уже имеется данная роль")
        elif cursor.execute("SELECT cost FROM shopbus WHERE role_id = {}".format(role.id)).fetchone()[0] > cursor.execute("SELECT cash FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]:
            await ctx.send(f"**{ctx.author}**, на вашем счету недостаточно средств")
        else:
            await ctx.author.add_roles(role)
            cursor.execute("UPDATE users SET cash = cash - {0} WHERE id = {1}".format(cursor.execute("SELECT cost FROM shopbus WHERE role_id = {}".format(role.id)).fetchone()[0], ctx.author.id))

            await ctx.author.send( f'{ctx.author.name}, поздравляю вас! Вы купили бизнес **{role}**')

            if role == 721707316105445436:
                while True:
                    cursor.execute("UPDATE users SET cash = cash + 5 WHERE id = {}".format(ctx.author.id))
                    connection.commit()
                    await asyncio.sleep(60)
                    cursor.execute("UPDATE users SET cash = cash + 5 WHERE id = {}".format(ctx.author.id))
                    connection.commit()
                    await asyncio.sleep(60)
                    cursor.execute("UPDATE users SET cash = cash + 5 WHERE id = {}".format(ctx.author.id))
                    connection.commit()
                    await asyncio.sleep(60)

            elif role == 721708788733837322:
                while True:
                    cursor.execute("UPDATE users SET cash = cash + 10 WHERE id = {}".format(ctx.author.id))
                    connection.commit()
                    await asyncio.sleep(60)
                    cursor.execute("UPDATE users SET cash = cash + 10 WHERE id = {}".format(ctx.author.id))
                    connection.commit()
                    await asyncio.sleep(60)
                    cursor.execute("UPDATE users SET cash = cash + 10 WHERE id = {}".format(ctx.author.id))
                    connection.commit()
                    await asyncio.sleep(60)

            else:
                while True:
                    cursor.execute("UPDATE users SET cash = cash + 20 WHERE id = {}".format(ctx.author.id))
                    connection.commit()
                    await asyncio.sleep(60)
                    cursor.execute("UPDATE users SET cash = cash + 20 WHERE id = {}".format(ctx.author.id))
                    connection.commit()
                    await asyncio.sleep(60)
                    cursor.execute("UPDATE users SET cash = cash + 20 WHERE id = {}".format(ctx.author.id))
                    connection.commit()
                    await asyncio.sleep(60)
                




                        

           
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

@client.command()
async def w(ctx, author, *args):
    cursor.execute("UPDATE users SET cash = cash + {} WHERE id = {}".format(len(args), ctx.author.id))
        


#+rep
@client.command()
async def reph(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send(embed = discord.Embed(
            description = f'У **{ctx.author}**, укажите пользователя, которому хотите отправить благодарность'
        ))
    else:
        if member.id == ctx.author.id:
            await ctx.send(f'**{ctx.author}**, нельзя выдавать благодарности самому себе!')
        else:
            cursor.execute("UPDATE users SET rep = rep + {} WHERE id = {}".format(1, member.id))
            connection.commit()
            await ctx.message.add_reaction('✔️')

#-rep
@client.command()
async def repl(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send(embed = discord.Embed(
            description = f'У **{ctx.author}**, укажите пользователя, которому хотите снять благодарность'
        ))
    else:
        if member.id == ctx.author.id:
            await ctx.send(f'**{ctx.author}**, нельзя снимать благодарности самому себе!')
        else:
            cursor.execute("UPDATE users SET rep = rep - {} WHERE id = {}".format(1, member.id))
            connection.commit()
            await ctx.message.add_reaction('✔️')

#reps
@client.command()
async def reps(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send(embed = discord.Embed(
            description = f'У **{ctx.author}** {cursor.execute("SELECT rep FROM users WHERE id = {}".format(ctx.author.id)).fetchone()[0]} благодарностей'
        ))
    else:
        if cursor.execute("SELECT rep FROM users WHERE id = {}".format(member.id)).fetchone()[0] == 1:
            await ctx.send(embed = discord.Embed(
            description = f'У **{member}** {cursor.execute("SELECT rep FROM users WHERE id = {}".format(member.id)).fetchone()[0]} благодарностей'
        ))
        else:
            await ctx.send(embed = discord.Embed(
                description = f'У **{member}** {cursor.execute("SELECT rep FROM users WHERE id = {}".format(member.id)).fetchone()[0]} благодарностей'
            ))        


#reactions
@client.event
async def on_raw_reaction_add(payload):
    if payload.message_id == 707908027524841522: # ID Сообщения
        guild = client.get_guild(payload.guild_id)
        role = None

        if str(payload.emoji) == '1️⃣': # Emoji для реакций
            role = guild.get_role(728595715600941126) # ID Ролей для выдачи
        elif str(payload.emoji) == '2️⃣':
            role = guild.get_role(707912296328069130)
        
        if role:
            member = guild.get_member(payload.user_id)
            if member:
                await member.add_roles(role)

#reactions
@client.event
async def on_raw_reaction_add(payload):
    if payload.message_id == 728594240669745172: # ID Сообщения
        guild = client.get_guild(payload.guild_id)
        role = None

        if str(payload.emoji) == ':1200pxPythonlogonotext:': # Emoji для реакций
            role = guild.get_role(728595441016373269) # ID Ролей для выдачи
        elif str(payload.emoji) == ':kisspnglogojavadevelopmentkitpor:':
            role = guild.get_role(728595853605994558)
        elif str(payload.emoji) == ' :cprogramminglanguageiconlettercp:':
            role = guild.get_role(728595568183738420)
        elif str(payload.emoji) == ':1200pxISO_C_Logo:':
            role = guild.get_role(728595513489883298)
        elif str(payload.emoji) == ':1200pxC_Sharp_wordmark:':
            role = guild.get_role(728595599917580350)
        elif str(payload.emoji) == ':1200pxUnofficial_JavaScript_logo:':
            role = guild.get_role(728595815718715423)
        elif str(payload.emoji) == ':1200pxPHPlogo: ':
            role = guild.get_role(728595715600941126)
        elif str(payload.emoji) == ':pngocean:':
            role = guild.get_role(728595650639429632)
    
        if role:
            member = guild.get_member(payload.user_id)
            if member:
                await member.add_roles(role)
    

             
token = os.environ.get('BOT_TOKEN')
client.run(str(token))
