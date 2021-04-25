from flask import Flask, render_template, session, redirect, url_for, request
from flask_session import Session
from tempfile import mkdtemp
import math
import random

from data import db_session, players
from data.players import Player

app = Flask(__name__)
app.secret_key = "secret_key"
player1 = ''
player2 = ''

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html", player1='Player1', player2='Player2')
    else:
        # create a new board
        session["boardsize"] = int(request.form.get("boardsize"))
        session["player1n"] = str(request.form.get("player1n"))
        session["player2n"] = str(request.form.get("player2n"))
        if session["player1n"] == session["player2n"] or session["player1n"].strip() == ''\
                or session["player2n"].strip() == '':
            return render_template("index.html", player1='Player1', player2='Player2')
        setboard()
        global player1, player2
        player1 = session["player1n"]
        player2 = session["player2n"]
        return redirect(url_for("game"))


def setboard():
    session["board"] = [[None]*session["boardsize"] for _ in range(session["boardsize"])]
    session["turn"] = "X"
    session["xrow"] = [0]*session["boardsize"]
    session["xcol"] = [0]*session["boardsize"]
    session["orow"] = [0]*session["boardsize"]
    session["ocol"] = [0]*session["boardsize"]
    session["xdiagonal"] = 0
    session["xantidiagonal"] = 0
    session["odiagonal"] = 0
    session["oantidiagonal"] = 0
    session["movecount"] = 0
    session["winner"] = None
    session["movehistory"] = []
    return


@app.route("/game")
def game():
    print(player1, player2)
    return render_template("game.html", game=session["board"], turn=session["turn"],
                           row=session["boardsize"], col=session["boardsize"], name1=player1, name2=player2)


@app.route("/play/<int:row>/<int:col>")
def play(row, col):
    
    session["board"][row][col] = session["turn"]

    if session["turn"] == "X":
        session["xrow"][row] += 1
        session["xcol"][col] += 1
        if row == col:
            session["xdiagonal"] += 1
        if row + col + 1 == session["boardsize"]:
            session["xantidiagonal"] += 1
        session["turn"] = "O"
    else:
        session["orow"][row] += 1
        session["ocol"][col] += 1
        if row == col:
            session["odiagonal"] += 1
        if row + col + 1 == session["boardsize"]:
            session["oantidiagonal"] += 1
        session["turn"] = "X"

    session["movecount"] += 1
    session["movehistory"].append([row, col])
    session["winner"] = checkWinner(session)

    if session["winner"]:
        db_session.global_init("blogs.db")

        if session["winner"] == "X":
            win = session["player1n"]
            bd(win)
            names = sorted_2_0()

            session.clear()
            return render_template("winner.html",  winner=win + " выигрывает", names=names)
        elif session["winner"] == "O":
            win = session["player2n"]
            bd(win)
            names = sorted_2_0()

            session.clear()
            return render_template("winner.html", winner=win + " выигрывает", names=names)
        elif session["winner"] == "Draw":
            bd()
            names = sorted_2_0()

            session.clear()
            return render_template("winner.html", winner="Ничья", names=names)
    else:
        return redirect(url_for("game"))


def checkWinner(board):
    bs = board["boardsize"]
    if bs in board["xrow"] or bs in board["xcol"] or board["xdiagonal"] == bs or board["xantidiagonal"] == bs:
        return "X"
    elif bs in board["orow"] or bs in board["ocol"] or board["odiagonal"] == bs or board["oantidiagonal"] == bs:
        return "O"
    elif board["movecount"] == bs*bs:
        return "Draw"
    else:
        return None


def sorted_2_0():
    db_session.global_init("blogs.db")
    db_sess = db_session.create_session()
    names = db_sess.query(Player).order_by(Player.win.desc()).all()
    db_sess.close()

    return names


def bd(winner=None):
    db_session.global_init("blogs.db")

    db_sess = db_session.create_session()
    player = db_sess.query(Player)
    names = []
    for i in player.all():
        names.append(i.name)

    for i in [session['player1n'], session['player2n']]:
        if i not in names:
            play = Player()
            play.name = i
            db_sess.add(play)
            db_sess.commit()

        play = player.filter(Player.name == i).first()
        if i == winner:
            play.win += 1
        elif winner:
            play.lose += 1
        else:
            play.pat += 1

        play.pr = f'{round(play.win/(play.win + play.lose + play.pat), 2) * 100}%'
        db_sess.commit()
        db_sess.close()



@app.route("/minmax")
def comPlay():
    cloneboard = session
    value, row, col = minimax(cloneboard, session["turn"])
    return redirect(url_for('play', row=row, col=col))


def minimax(board, turn):
    winner = checkWinner(board)
    if winner == "X":
        return [1, None, None]
    elif winner == "O":
        return [-1, None, None]
    elif winner == "Draw":
        return [0, None, None]

    moves = findempty(board)

    if len(moves) == board["boardsize"]*board["boardsize"]:
        steprow = random.randint(0,board["boardsize"]-1)
        stepcol = random.randint(0,board["boardsize"]-1)
        return [None, steprow, stepcol]
    
    steprow = None
    stepcol = None
    if turn == "X":
        value = -math.inf
        for row, col in moves:
            board = move(board, row, col)
            value = max(value, minimax(board, "O")[0])
            board = unmove(board, row, col)
            steprow = row
            stepcol = col
    else:
        value = math.inf
        for row, col in moves:
           board = move(board, row, col)
           value = min(value, minimax(board, "X")[0])
           board = unmove(board, row, col)
           steprow = row
           stepcol = col
    return [value, steprow, stepcol]


def findempty(board):
    moves = []
    for i in range(len(board["board"])):
        for j in range(len(board["board"][i])):
            if board["board"][i][j] == None:
                moves.append([i, j])
    return moves


def move(board, row, col):
    board["board"][row][col] = board["turn"]

    if board["turn"] == "X":
        board["xrow"][row] += 1
        board["xcol"][col] += 1
        if row == col:
            board["xdiagonal"] += 1
        if row + col + 1 == board["boardsize"]:
            board["xantidiagonal"] += 1
        board["turn"] = "O"
    else:
        board["orow"][row] += 1
        board["ocol"][col] += 1
        if row == col:
            board["odiagonal"] += 1
        if row + col + 1 == session["boardsize"]:
            board["oantidiagonal"] += 1
        board["turn"] = "X"

    board["movecount"] += 1
    board["movehistory"].append([row, col])
    return board


def unmove(board, row, col):
    if board["movecount"] == 0:
        return board
    row, col = board["movehistory"].pop()
    board["board"][row][col] = None
    if board["turn"] == "X":
        board["orow"][row] -= 1
        board["ocol"][col] -= 1
        if row == col:
            board["odiagonal"] -= 1
        if row + col + 1 == board["boardsize"]:
            board["oantidiagonal"] -= 1
        board["movecount"] -= 1
        board["turn"] = "O"
    else:
        board["xrow"][row] -= 1
        board["xcol"][col] -= 1
        if row == col:
            board["xdiagonal"] -= 1
        if row + col + 1 == board["boardsize"]:
            board["xantidiagonal"] -= 1
        board["movecount"] -= 1
        board["turn"] = "X"
    return board

if __name__ == "__main__":
    app.run(debug=True)