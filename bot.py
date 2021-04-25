import discord
from discord.ext import commands
from data import db_session, players
from data.players import Player
import os
import requests

TOKEN = "ODMxOTA0MjE2NDg1MTk5ODky.YHcBLQ.AKORvfWyCYteQbz0S15wdmNi4uw"


class Tic_Tac_Toe(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def stat(self, n):
        if not n:
            return False
        else:
            db_session.global_init("blogs.db")

            db_sess = db_session.create_session()
            name = db_sess.query(Player).filter(Player.name == n).first()
            db_sess.close()
            return name

    def sort_players(self):
        db_session.global_init("blogs.db")

        db_sess = db_session.create_session()
        names = db_sess.query(Player).order_by(Player.win.desc()).all()
        db_sess.close()

        return names

    @commands.command()
    async def map(self, ctx, city=None):
        if city:
            toponym_to_find = city

            geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba" \
                               f"-98533de7710b&geocode={toponym_to_find}&format=json"

            # Выполняем запрос.
            response = requests.get(geocoder_request)
            if response:
                # Преобразуем ответ в json-объект
                json_response = response.json()

                # Получаем первый топоним из ответа геокодера.
                # Согласно описанию ответа, он находится по следующему пути:
                toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                toponym_coodrinates = toponym["Point"]["pos"].replace(' ', ',')
                print(toponym_coodrinates)

                search_api_server = "https://search-maps.yandex.ru/v1/"
                api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

                address_ll = toponym_coodrinates

                search_params = {
                    "apikey": api_key,
                    "text": "тайм-кофе",
                    "lang": "ru_RU",
                    "ll": address_ll,
                    "type": "biz"
                }

                response = requests.get(search_api_server, params=search_params)
                if not response:
                    # ...
                    pass

                # Преобразуем ответ в json-объект
                json_response = response.json()
                # Получаем первую найденную организацию.
                org_point = ''
                fl = False
                res = '**Устал играть в крестики-нолики? Сходи с друзьями поиграй в другие настольные игры в тайм-кафе!!!**```'
                for i, name in enumerate(json_response["features"]):
                    fl = True
                    # Название организации.
                    org_name = name["properties"]["CompanyMetaData"]["name"]
                    # Адрес организации.
                    org_address = name["properties"]["CompanyMetaData"]["address"]
                    res += f'\n{i + 1}) {org_name}: {org_address}'
                    # Получаем координаты ответа.
                    point = name["geometry"]["coordinates"]
                    org_point += "{0},{1},pm2ywl{2}~".format(point[0], point[1], i + 1)
                if fl:
                    delta = "0.05"
                    print(org_point)
                    # Собираем параметры для запроса к StaticMapsAPI:
                    map_params = {
                        # позиционируем карту центром на наш исходный адрес
                        "ll": address_ll,
                        "spn": ",".join([delta, delta]),
                        "l": "map",
                        # добавим точку, чтобы указать найденную аптеку
                        "pt": org_point[:-1]
                    }

                    res += '```'
                    map_api_server = "http://static-maps.yandex.ru/1.x/"
                    # ... и выполняем запрос
                    response = requests.get(map_api_server, params=map_params)
                    map_file = "map.png"
                    with open(map_file, "wb") as file:
                        file.write(response.content)
                    await ctx.send(res, file=discord.File('map.png'))
                    os.remove(map_file)

                else:
                    await ctx.send('В вашем городе нет тайм-кафе(')
        else:
            await ctx.send('```Не указан город```')

    @commands.command()
    async def info(self, ctx):
        res = '**!top** - выводит 5 лучших игроков(по победам)\n' \
              '**!top <name>** - выводит место игрока в топе\n' \
              '**!statistics <name_1> <name_2>** - выводит сравнение двух указанных игроков\n' \
              '**!statistic <name>** - выводит статистику выбранного игрока\n' \
              '**!map <city>** - показывает тайм-кафе в указанном городе'

        await ctx.send(res)

    @commands.command()
    async def top(self, ctx, n=None):
        if n:
            nick = n
            name = self.stat(nick)
            names = self.sort_players()
            if name:
                k = 1
                top = None
                for i in names:
                    if k == 1:
                        top = i
                    if name.name != i.name:
                        k += 1
                    else:
                        break
                res = f'```css\n{name.name} находится на {k} месте в топе.'
                if k != 1:
                    res += f'\nДо первого места {name.name} не хватает {top.win - name.win} побед.'
                await ctx.send(res + '```')
            else:
                await ctx.send('```Такого игрока нет```')
        else:
            names = self.sort_players()
            i = 1
            res = '>>> '
            for name in names:
                if i != 1:
                    res += '\n'
                res += f"{i} - **{name.name}**\n```css\nПобед: {name.win}\nПоражений: {name.lose}" \
                    f"\nНичей: {name.pat}\nПроцент побед: {name.pr}\n```"
                i += 1
                if i > 5:
                    break
            if len(res) < 5:
                await ctx.send('Топ пустует, будь первым!')
            else:
                await ctx.send(res)

    @commands.command()
    async def statistic(self, ctx, n=None):
        if n:
            nick = n
            name = self.stat(nick)
            if not name:
                await ctx.send('```bash\nТакого игрока не существует```')
            else:
                res = f"Статистика игрока - **{name.name}**\n```css\nПобед: {name.win}\nПоражений: {name.lose}" \
                      f"\nНичей: {name.pat}\nПроцент побед: {name.pr}\n```"
                await ctx.send(res)
        else:
            await ctx.send('```Вы не ввели имя```')

    @commands.command()
    async def statistics(self, ctx, n=None, k=None):
        if n and k:
            name1 = self.stat(n)
            name2 = self.stat(k)
            if not name1 or not name2:
                await ctx.send('```bash\nТакого(-их) игрока(-ов) не существует```')
            else:
                win, lose, pat, pr = '', '', '', ''
                if name1.win - name2.win > 0:
                    win = f'{name1.name} одержал на {name1.win - name2.win} побед больше чем {name2.name}'
                elif name1.win - name2.win < 0:
                    win = f'{name2.name} одержал на {name2.win - name1.win} побед больше чем {name1.name}'
                else:
                    win = f'{name1.name} и {name2.name} выиграли {name1.win} партий'

                if name1.lose - name2.lose > 0:
                    lose = f'{name1.name} проиграл на {name1.lose - name2.lose} партий больше чем {name2.name}'
                elif name1.lose - name2.lose < 0:
                    lose = f'{name2.name} проиграл на {name2.lose - name1.lose} партий больше чем {name1.name}'
                else:
                    lose = f'{name1.name} и {name2.name} проиграли {name1.lose} партий'

                if name1.pat - name2.pat > 0:
                    pat = f'{name1.name} сыграл в ничью на {name1.pat - name2.pat} партий больше чем {name2.name}'
                elif name1.pat - name2.pat < 0:
                    pat = f'{name2.name} сыграл в ничью на {name2.pat - name1.pat} партий больше чем {name1.name}'
                else:
                    pat = f'{name1.name} и {name2.name} сыграли в ничью {name1.pat} партий'

                temp = float(name1.pr[:-1]) - float(name2.pr[:-1])
                if temp > 0:
                    pr = f'У {name1.name} процент побед на {temp}% больше чем у {name2.name}'
                elif temp < 0:
                    pr = f'У {name2.name} процент побед на {-temp}% больше чем у {name1.name}'
                else:
                    pr = f'У {name1.name} и {name2.name} одинаковый процент побед: {name1.pr}'

                res = f"```css\n{win}\n{lose}\n{pat}\n{pr}```"
                await ctx.send(res)
        else:
            await ctx.send('```Неверно введены имена```')


bot = commands.Bot(command_prefix='!')
bot.add_cog(Tic_Tac_Toe(bot))
bot.run(TOKEN)
