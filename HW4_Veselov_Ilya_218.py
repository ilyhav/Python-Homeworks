import asyncio
import warnings
import sqlalchemy as db

from aiogram import Bot, Dispatcher, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Message
from aiofiles import open as aiopen
from random import choice
from typing import Coroutine

warnings.filterwarnings('ignore')

BOT_TOKEN = ''


class Database:

    def __init__(self):
        self.engine = db.create_engine('sqlite:///game_bot.db')
        self.connection = self.engine.connect()
        self.metadata = db.MetaData()
        self._create_table()

    def _create_table(self):
        self.gamer = db.Table('gamers', self.metadata,
                              db.Column('uuid', db.Integer, primary_key=True),
                              db.Column('nickname', db.Text),
                              db.Column('hp', db.Integer),
                              db.Column('CurHp', db.Integer),
                              db.Column('exp', db.Integer),
                              db.Column('money', db.Integer),
                              db.Column('attack', db.Integer),
                              db.Column('armour', db.Integer),
                              db.Column('MagicArmour', db.Integer),
                              db.Column('location', db.Integer),
                              db.Column('inventory', db.Integer)
                              )
        self.mobs = db.Table('mobs', self.metadata,
                             db.Column('uuid', db.Integer, primary_key=True),
                             db.Column('hp', db.Integer),
                             db.Column('reqxp', db.Integer),
                             db.Column('attacktype', db.Integer),  # 1 - fisical, 2 - magic
                             db.Column('attack', db.Integer),
                             db.Column('armour', db.Integer),
                             db.Column('MagicArmour', db.Integer)
                             )
        self.location = db.Table('locations', self.metadata,
                                 db.Column('uuid', db.Integer, primary_key=True),
                                 db.Column('XCoord', db.Integer),
                                 db.Column('YCoord', db.Integer),
                                 db.Column('locationtype', db.Integer)  # 1 - city, 2 - no city
                                 )
        self.items = db.Table('items', self.metadata,
                              db.Column('uuid', db.Integer, primary_key=True),
                              db.Column('cost', db.Integer),
                              db.Column('CostToSale', db.Integer),
                              db.Column('ItemType', db.Integer),
                              # 1 - оружие, 2 - броня, 3 - шлем, 4 - сапоги, 5 - наручи, 6 - зелье
                              db.Column('hp', db.Integer),  # Only 6!
                              db.Column('mana', db.Integer),  # Only 6!
                              db.Column('attack', db.Integer),
                              db.Column('MagicAttack', db.Integer),
                              db.Column('armour', db.Integer),
                              db.Column('MagicArmour', db.Integer),
                              db.Column('ReqLevel', db.Integer)
                              )
        self.metadata.create_all(self.engine)

    # Edit

    async def update_gamer(self, uuid: int, where: str, what: str):
        # print(uuid)
        self.connection.execute(
            db.update(self.gamer).where(self.gamer.columns.uuid == uuid).values(**{f'{where}': f'{what}'}))

    async def edit_location(self, uuid: int, where: str, what: str) -> None:
        self.connection.execute(
            db.update(self.location).where(self.location.columns.uuid == uuid).values(**{f'{where}': f'{what}'}))

    async def edit_mobs(self, uuid: int, where: str, what: str) -> None:
        self.connection.execute(
            db.update(self.mobs).where(self.mobs.columns.uuid == uuid).values(**{f'{where}': f'{what}'}))

    async def edit_item(self, uuid: int, where: str, what: str) -> None:
        self.connection.execute(
            db.update(self.items).where(self.items.columns.uuid == uuid).values(**{f'{where}': f'{what}'}))

    # Registration

    async def admin_add_mobs(self, data: dict) -> None:
        self.connection.execute(self.mobs.insert().values([data]))

    async def admin_add_location(self, data: dict) -> None:
        self.connection.execute(self.location.insert().values([data]))

    async def admin_add_item(self, data: dict) -> None:
        self.connection.execute(self.location.insert().values([data]))

    async def reg_player(self, insertion_data: dict) -> None:
        self.connection.execute(self.gamer.insert().values([insertion_data]))

    # Delete

    async def delete_player(self, uuid: int) -> None:
        self.connection.execute(db.delete(self.gamer).where(self.gamer.columns.uuid == uuid))

    async def admin_delete_mobs(self, uuid: int) -> None:
        self.connection.execute(db.delete(self.mobs).where(self.mobs.columns.uuid == uuid))

    async def admin_delete_location(self, uuid: int) -> None:
        self.connection.execute(db.delete(self.location).where(self.location.columns.uuid == uuid))

    async def delete_item(self, uuid: int) -> None:
        self.connection.execute(db.delete(self.items).where(self.items.columns.uuid == uuid))

    # Gets

    async def get_player(self, uuid: int) -> dict:
        data = self.connection.execute(db.select([self.gamer]).where(self.gamer.columns.uuid == uuid)).fetchall()
        if data:
            return {
                'uuid': data[0][0],
                'nickname': data[0][1],
                'hp': data[0][2],
                'CurHp': data[0][3],
                'exp': data[0][4],
                'money': data[0][5],
                'attack': data[0][6],
                'armour': data[0][7],
                'MagicArmour': data[0][8],
                'location': data[0][9],
                'inventory': data[0][10]
            }
        return data

    async def get_location(self, uuid: int) -> dict:
        data = self.connection.execute(db.select([self.location]).where(self.location.columns.uuid == uuid)).fetchall()
        if data:
            return {
                'uuid': data[0][0],
                'XCoord': data[0][1],
                'YCoord': data[0][2],
                'locationtype': data[0][3]
            }
        return data

    async def get_mobs(self, uuid: int) -> dict:
        data = self.connection.execute(db.select([self.mobs]).where(self.mobs.columns.uuid == uuid)).fetchall()
        if data:
            return {
                'uuid': data[0][0],
                'hp': data[0][1],
                'reqxp': data[0][2],
                'attacktype': data[0][3],
                'attack': data[0][4],
                'armour': data[0][5],
                'MagicArmour': data[0][6]
            }
        return data

    async def get_all_mobs(self) -> list:
        data = self.connection.execute(db.select([self.mobs])).fetchall()
        if data:
            return list(map(
                lambda data:
                {
                    'uuid': data[0][0],
                    'hp': data[0][1],
                    'reqxp': data[0][2],
                    'attacktype': data[0][3],
                    'attack': data[0][4],
                    'armour': data[0][5],
                    'MagicArmour': data[0][6]
                },
                data
            ))
        return data

    # Get items

    async def get_items_weapons(self) -> list:
        data = self.connection.execute(db.select([self.items]).where(self.items.columns.ItemType == 1)).fetchall()
        if data:
            return list(map(
                lambda data:
                {'uuid': data[0][0],
                 'cost': data[0][1],
                 'CostToSale': data[0][2],
                 'ItemType': data[0][3],
                 'hp': data[0][4],
                 'mana': data[0][5],
                 'attack': data[0][6],
                 'MagicAttack': data[0][7],
                 'armour': data[0][8],
                 'MagicArmour': data[0][9],
                 'ReqLevel': data[0][10]},
                data
            ))
        return data

    async def get_items_armour(self) -> list:
        data = self.connection.execute(db.select([self.items]).where(self.items.columns.ItemType == 2)).fetchall()
        if data:
            return list(map(
                lambda data:
                {
                    'uuid': data[0][0],
                    'cost': data[0][1],
                    'CostToSale': data[0][2],
                    'ItemType': data[0][3],
                    'hp': data[0][4],
                    'mana': data[0][5],
                    'attack': data[0][6],
                    'MagicAttack': data[0][7],
                    'armour': data[0][8],
                    'MagicArmour': data[0][9],
                    'ReqLevel': data[0][10]
                },
                data
            ))
        return data

    async def get_items_helmet(self) -> list:
        data = self.connection.execute(db.select([self.items]).where(self.items.columns.ItemType == 3)).fetchall()
        if data:
            return list(map(
                lambda data:
                {
                    'uuid': data[0][0],
                    'cost': data[0][1],
                    'CostToSale': data[0][2],
                    'ItemType': data[0][3],
                    'hp': data[0][4],
                    'mana': data[0][5],
                    'attack': data[0][6],
                    'MagicAttack': data[0][7],
                    'armour': data[0][8],
                    'MagicArmour': data[0][9],
                    'ReqLevel': data[0][10]
                },
                data
            ))
        return data

    async def get_items_boots(self) -> list:
        data = self.connection.execute(db.select([self.items]).where(self.items.columns.ItemType == 4)).fetchall()
        if data:
            return list(map(
                lambda data:
                {
                    'uuid': data[0][0],
                    'cost': data[0][1],
                    'CostToSale': data[0][2],
                    'ItemType': data[0][3],
                    'hp': data[0][4],
                    'mana': data[0][5],
                    'attack': data[0][6],
                    'MagicAttack': data[0][7],
                    'armour': data[0][8],
                    'MagicArmour': data[0][9],
                    'ReqLevel': data[0][10]
                },
                data
            ))
        return data

    async def get_items_braces(self) -> list:
        data = self.connection.execute(db.select([self.items]).where(self.items.columns.ItemType == 5)).fetchall()
        if data:
            return list(map(
                lambda data:
                {
                    'uuid': data[0][0],
                    'cost': data[0][1],
                    'CostToSale': data[0][2],
                    'ItemType': data[0][3],
                    'hp': data[0][4],
                    'mana': data[0][5],
                    'attack': data[0][6],
                    'MagicAttack': data[0][7],
                    'armour': data[0][8],
                    'MagicArmour': data[0][9],
                    'ReqLevel': data[0][10]
                },
                data
            ))
        return data

    async def get_items_potion(self) -> list:
        data = self.connection.execute(db.select([self.items]).where(self.items.columns.ItemType == 6)).fetchall()
        if data:
            return list(map(
                lambda data:
                {
                    'uuid': data[0][0],
                    'cost': data[0][1],
                    'CostToSale': data[0][2],
                    'ItemType': data[0][3],
                    'hp': data[0][4],
                    'mana': data[0][5],
                    'attack': data[0][6],
                    'MagicAttack': data[0][7],
                    'armour': data[0][8],
                    'MagicArmour': data[0][9],
                    'ReqLevel': data[0][10]
                },
                data
            ))
        return data

    async def get_items(self, uuid: int) -> list:
        data = self.connection.execute(db.select([self.items]).where(self.items.columns.ItemType == uuid)).fetchall()
        if data:
            return list(map(
                lambda data:
                {
                    'uuid': data[0][0],
                    'cost': data[0][1],
                    'CostToSale': data[0][2],
                    'ItemType': data[0][3],
                    'hp': data[0][4],
                    'mana': data[0][5],
                    'attack': data[0][6],
                    'MagicAttack': data[0][7],
                    'armour': data[0][8],
                    'MagicArmour': data[0][9],
                    'ReqLevel': data[0][10]
                },
                data
            ))
        return data

    # Files

    async def _save_file(self, filename: str, strings: list) -> None:
        async with aiopen(filename, 'w', encoding='utf-8') as file:
            await file.writelines(strings)

    async def admin_write_all_columns_in_file(self):
        all_player = self.connection.execute(db.select([self.gamer])).fetchall()
        await self._save_file('players.txt', [
            f'ID: {gamer["uuid"]}\nNick: {gamer["nickname"]}\nHp - CurHP: {gamer["hp"]} - {gamer["curhp"]}\nMoney: {gamer["money"]}\nAttack: {gamer["attack"]}\nArmour - MagicArmour: {gamer["armour"]} - {gamer["magicarmour"]}\nLocation: {gamer["location"]}\n\n'
            for gamer in all_player])
        all_mobs = self.connection.execute(db.select([self.mobs])).fetchall()
        await self._save_file('mobs.txt', [
            f'ID: {mob["uuid"]}\nHP: {mob["hp"]}\nReqXP: {mob["reqxp"]}\nAttack Type - attack: {mob["attacktype"]} - {mob["attack"]}\nArmour - Magic Armour: {mob["armour"]} - {mob["magicarmour"]}\n\n'
            for mob in all_mobs])
        all_locations = self.connection.execute(db.select([self.location])).fetchall()
        await self._save_file('locations.txt', [
            f'ID: {location["uuid"]}\nX - Y: {location["xcoord"]} - {location["ycoord"]}\nLocation type: {location["type_of_location"]}\n\n'
            for location in all_locations])
        all_items = [await coro() for coro in
                     [self.get_items_weapons, self.get_items_armour, self.get_items_helmet, self.get_items_boots,
                      self.get_items_braces, self.get_items_potion]]
        await self._save_file('all_items.txt', [
            f'ID: {item["uuid"]}\nCost - Cost to sale: {item["cost"]} - {item["cost_to_sale"]}\nItem type: {item["item_type"]}\nHP - Mana: {item["hp"]} - {item["mana"]}\nAttack - MAgic attack: {item["attack"]} - {item["magicattack"]}\nReqLVL: {item["reqlvl"]}\n\n'
            for item in all_items])


class RegState(StatesGroup):
    nickname = State()


async def run_sleep(coro: Coroutine) -> None:
    await asyncio.gather(asyncio.create_task(coro))


database = Database()
bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start'])
async def start(message: Message):
    await message.answer(
        'Здравствуйте! Перед началом игры вам необходимо пройти регистрацию командой "/reg" (нажать на команду)')


@dp.message_handler(commands=['reg', 'registartion'], state='*')
async def regfisatrtion(message: Message, state: FSMContext):
    exists = await database.get_player(message['from']['id'])
    if not exists:
        await message.answer('Введите ваш ник!')
        await state.set_state(state=RegState.nickname.state)
    else:
        await message.answer('Вы уже зарегестрирвоаны!')


@dp.message_handler(state=RegState.nickname.state)
async def register_stop(message: Message, state: FSMContext):
    await state.finish()
    await message.answer('Регистрация успешно завершена! Теперь вам доступен профиль по команде "/profile"')
    await database.reg_player({
        'uuid': message['from']['id'],
        'nickname': message['text'],
        'hp': 100,
        'CurHp': 100,
        'money': 100,
        'attack': 1,
        'armour': 0,
        'MagicArmour': 0,
        'location': 1
    })


@dp.message_handler(commands=['profile', 'profile', 'account'])
async def profile(message: Message):
    exists = await database.get_player(message['from']['id'])
    if exists:
        await message.answer(f'''Ваш аккаунт!
Ник: {exists['nickname']}
Хп: {exists['CurHp']}
Монеты: {exists['money']}
Защита: {exists['armour']}
Магическая защита: {exists['MagicArmour']}
Локация: {exists['location']}

Возможности:
"/shop (target)" Перейти в магазин (target - цифра от 1 до 6 обозначающая какой товар вам нужен. См. "/FAQ")
"/go (target)" Перейти в локацию (target - цифра локации. Например 0 - начальный город)
"/fight" Начать бой с монстром (подземелье)''')
    else:
        await message.answer('У вас нет профиля!')


@dp.message_handler(commands=['shop'])
async def shop(message: Message):
    exists = await database.get_player(message['from']['id'])
    if exists:
        target = message.text.split()[-1]
        if (target.isdigit()) and (0 < int(target) < 7):
            all_items = await database.get_items(int(target))
            text = 'Предметы доступные в этом магазине:\n'
            for item_data in all_items:
                text += f'ID: {item_data["uuid"]}\nCost - Cost to sale: {item_data["cost"]} - {item_data["cost_to_sale"]}\nItem type: {item_data["item_type"]}\nHP - Mana: {item_data["hp"]} - {item_data["mana"]}\nAttack - MAgic attack: {item_data["attack"]} - {item_data["magicattack"]}\nReqLVL: {item_data["reqlvl"]}\n'
            text += 'Если вы хотите что-то купить, то введите команду "/buy (ID предмета)" если же вы хотите прожать предмет "/cost (ID предмета)"'
            await message.answer(text)
        else:
            await message.answer('Неизвестный магазин')
    else:
        await message.answer('У вас нет профиля!')


@dp.message_handler(commands=['cost'])
async def cost(message: Message):
    exists = await database.get_player(message['from']['id'])
    if exists:
        target_to_cost = message.text.split()[-1]
        item_exists = await database.get_items(int(target_to_cost))
        inventory = eval(f'list({exists["inventor"]})')
        if (item_exists != []) and (target_to_cost in inventory):
            for item in range(len(inventory)):
                if inventory[item] == target_to_cost:
                    del inventory[item]
                    break
            await database.update_gamer(message['from']['id'], 'inventory', f'"{inventory}"')
            await database.update_gamer(message['from']['id'], 'inventory',
                                        f'{exists["money"] + item_exists["CostToSale"]}')
            await message.answer(f'Вы успешно продали предмет получив {item_exists["CostToSale"]} монет')
        elif not item_exists:
            await message.answer('Такого предмета не существует')
        elif target_to_cost not in inventory:
            await message.answer('У вас нет этого предмета')
        else:
            await message.answer('Неверное название предмета')
    else:
        await message.answer('У вас нет профиля!')


@dp.message_handler(commands=['buy'])
async def buy(message: Message):
    exists = await database.get_player(message['from']['id'])
    if exists:
        target_to_buy = message.text.split()[-1]
        item_exists = await database.get_items(int(target_to_buy))
        inventory = eval(f'list({exists["inventory"]})')
        if (item_exists != []) and (target_to_buy in inventory):
            if exists.money > item_exists.cost:
                await database.update_gamer(message['from']['id'], 'money', f'{exists["money"] - item_exists["cost"]}')
                inventory.append(target_to_buy)
                await database.update_gamer(message['from']['id'], 'inventory', f'"{inventory}"')
                await message.answer(f'Вы успешно купили {target_to_buy}')
            else:
                await message.answer('У вас недостаточно монет')
        elif not item_exists:
            await message.answer('Такого предмета не существует')
        elif target_to_buy not in inventory:
            await message.answer('У вас нет этого предмета')
        else:
            await message.answer('Неверное название предмета')
    else:
        await message.answer('У вас нет профиля!')


@dp.message_handler(commands=['go'])
async def relocation(message: Message):
    exists = await database.get_player(message['from']['id'])
    if exists:
        location_id = message.text.split()[-1]
        location_info = await database.get_location(int(location_id))
        if location_info:
            async def go_to_location(id: int, lid: int) -> None:
                await asyncio.sleep(10)
                await bot.send_message(
                    chat_id=id,
                    text='Вы успешно пришли на локацию!'
                )
                await database.update_gamer(id, 'location', str(lid))

            await run_sleep(go_to_location(message['from']['id'], int(location_id)))
        else:
            await message.answer('Такой локации не существует!')
    else:
        await message.answer('У вас нет профиля!')


@dp.message_handler(commands=['fight'])
async def fight(message: Message):
    exists = await database.get_player(message['from']['id'])
    if exists:
        location_info = await database.get_location(exists['location'])
        if location_info:
            if location_info['locationtype'] == 1:
                await message.answer('Вы в городе и вы не можете драться (даже в трактире!)')
            elif location_info['locationtype'] == 2:
                all_mobs = await database.get_all_mobs()
                mob_attacker = choice(
                    list(filter(
                        lambda x: x['reqlvl'] < exists['lvl'],
                        all_mobs
                    )))
                await message.answer(f'Вы нападаете на {mob_attacker.uuid}')
                await database.update_gamer(message['from']['id'], 'CurHp', f'{exists["CurHp"] - 3}')
                await database.update_gamer(message['from']['id'], 'exp', f'{exists["exp"] - 2}')
            else:
                await message.answer('Ошибка! Неизвестное наименование локации!')
        else:
            await message.answer('Вы не можете драться в пустоте (локация где вы находитесь удалена или не существует)')
    else:
        await message.answer('У вас нет профиля!')


@dp.message_handler(commands=['admin'])
async def admin_codes(message: Message):
    admin_message = message.text.lower().split()[1:]
    if admin_message[0] == 'mob':
        await database.admin_add_mobs({
            'uuid': admin_message[1],
            'hp': admin_message[2],
            'reqxp': admin_message[3],
            'attacktype': admin_message[4],
            'attack': admin_message[5],
            'armour': admin_message[6],
            'MagicArmour': admin_message[7]
        })
    elif admin_message[0] == 'item':
        await database.admin_add_item({
            'uuid': admin_message[1],
            'cost': admin_message[2],
            'CostToSale': admin_message[3],
            'ItemType': admin_message[4],
            'hp': admin_message[5],
            'mana': admin_message[6],
            'attack': admin_message[7],
            'MagicAttack': admin_message[8],
            'armour': admin_message[9],
            'MagicArmour': admin_message[10],
            'ReqLevel': admin_message[11]
        })
    elif admin_message[0] == 'location':
        await database.admin_add_location({
            'uuid': admin_message[1],
            'XCoord': admin_message[2],
            'YCoord': admin_message[3],
            'locationtype': admin_message[4]
        })
    elif admin_message[0] == 'delete':
        if admin_message[1] == 'mobs':
            await database.admin_delete_mobs(int(admin_message[2]))
        elif admin_message[1] == 'location':
            await database.admin_delete_location(int(admin_message[2]))
    elif admin_message[0] == 'save':
        await database.admin_write_all_columns_in_file()


@dp.message_handler(commands=['faq'])
async def faq(message: Message):
    async with aiopen('faq.txt', 'r', encoding='urf-8') as file:
        lines = await file.read()
    await message.answer(lines)


@dp.message_handler()
async def example(message: Message):
    await message.answer('Команда не раcпознана')


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    executor.start_polling(dispatcher=dp, loop=loop, skip_updates=True)
