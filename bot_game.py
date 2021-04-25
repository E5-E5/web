import discord
from discord.ext import commands
import random

client = commands.Bot(command_prefix="!")

gameoverflag = True
player1 = ""
player2 = ""
turn = ""
first = ""

board = []

winpositions = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6],
                [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]
                ]


@client.command()
async def info(ctx):
    if gameoverflag:
        res = '**!startgame <@name> <@name>** - команда для начала игры\n' \
               '**!endgame** - команда для преждевременного завершения игры\n' \
               '**!place <pos>** - получает позицию ячейки для игры\n' \
                'правила:\n' \
                'игра происходит на поле 3х3\n' \
                'чтобы начать игру необходимо написать команду **!startgame <@name> <@name>**\n' \
                'клетки игрового поля обозначаются цифрами от 1 до 9\n' \
                'нумерация клеток идёт слева на права, сверху вниз\n' \
                'примерно вот так:\n' \
                '-----------\n' \
                '|1|--|2|-|3|\n'\
                '|4|-|5|-|6|\n' \
                '|7|-|8|-|9|\n' \
                '-----------\n'
        await ctx.send(res)


@client.command()
async def startgame(ctx, p1: discord.Member, p2: discord.Member):
    global gameoverflag
    global count
    global player1
    global player2
    global turn
    global first

    if gameoverflag:
        if p1 != p2:
            global board
            board = [":white_large_square:", ":white_large_square:", ":white_large_square:",
                     ":white_large_square:", ":white_large_square:", ":white_large_square:",
                     ":white_large_square:", ":white_large_square:", ":white_large_square:"]
            turn = ""
            gameoverflag = False
            count = 0
            player1 = p1
            player2 = p2

            line = ""
            for x in range(len(board)):
                if x == 8 or x == 5 or x == 2:
                    line += " " + board[x]
                    await ctx.send(line)
                    line = ""
                else:
                    line += " " + board[x]

            num = random.randint(1, 2)
            if num == 1:
                turn = player1
                first = player1
                await ctx.send(f"Первым ходит {player1}")
            elif num == 2:
                turn = player2
                first = player2
                await ctx.send(f"Первым ходит {player2}")
        else:
            await ctx.send("Нельзя играть с самим собой!")
    else:
        await ctx.send("Игра в процессе, сначала завершите игру.")


@client.command()
async def place(ctx, pos: int):
    global gameoverflag
    global turn
    global player1
    global player2
    global board
    global count
    if not gameoverflag:
        wnrname = ""
        if turn == ctx.author:
            if turn == player1:
                wnrname = ":regional_indicator_x:"
            elif turn == player2:
                wnrname = ":o2:"
            if 0 < pos < 10 and board[pos - 1] == ":white_large_square:" :
                board[pos - 1] = wnrname
                count += 1
                line = ""
                for x in range(len(board)):
                    if x == 2 or x == 5 or x == 8:
                        line += " " + board[x]
                        await ctx.send(line)
                        line = ""
                    else:
                        line += " " + board[x]

                checkWinner(winpositions, wnrname)
                if gameoverflag == True:
                    await ctx.send(wnrname + " побеждает!")
                elif count >= 9:
                    gameoverflag = True
                    await ctx.send("Увы и ах, ничья.")

                if turn == player1:
                    turn = player2
                elif turn == player2:
                    turn = player1
            else:
                await ctx.send("Координаты хода должны быть в диапазоне от 1 до 9.")
        else:
            await ctx.send("Подождите, сейчас очередь другого игрока.")
    else:
        await ctx.send("Проверьте корректность ввода команды.")


def checkWinner(winningConditions, wnrname):
    global gameoverflag
    for condition in winningConditions:
        if board[condition[0]] == wnrname and board[condition[1]] == wnrname and board[condition[2]] == wnrname:
            gameoverflag = True


@client.command()
async def endgame(ctx):
    global gameoverflag
    if not gameoverflag:
        gameoverflag = True
        await ctx.send("Игра окончена")
    else:
        await ctx.send("Игра и так окончена")


@startgame.error
async def startgame_error(ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Для игры нужно указать двух игроков.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Проверьте правильность ввода имён игроков (@никнейм).")


@place.error
async def place_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Введите координаты вашего хода")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Проверьте правильность написания координат хода.")

client.run("")
