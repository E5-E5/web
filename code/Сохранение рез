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

        play.pr = f'{play.win/(play.win + play.lose + play.pat) * 100}%'
        db_sess.commit()
