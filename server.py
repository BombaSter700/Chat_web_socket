import asyncio
import websockets
import json
import os

# Сохраняем всех клиентов, подключенных к серверу
client_list = []
user_data_file = 'user_data.json'  # файлик с данными пользователей

def load_user_data():
    if os.path.exists(user_data_file):
        with open(user_data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

user_data = load_user_data()

def save_user_data(data):
    with open(user_data_file, 'w', encoding='utf-8') as f:  # encoding='utf-8' и ensure_ascii=False для норм отображения кириллицы
        json.dump(data, f, indent=4, ensure_ascii=False)

async def handler(websocket, path):
    client_list.append(websocket)
    await websocket.send("Введите ник: ")
    nickname = await websocket.recv()
    nickname = nickname.strip()

    if nickname in user_data:
        user_data[nickname]['session_messages'] = 0  # Обнуление сообщений за сессию
    else:
        user_data[nickname] = {'total_messages': 0, 'session_messages': 0}

    await websocket.send(f"Привет, {nickname}!")

    try:
        while True:
            # Ждем сообщение от клиента
            message = await websocket.recv()
            
            print(f'Message received from client {nickname}:', message)

            # Обработка команды /userinfo
            if message.strip() == '/userinfo':
                # Формируем сообщение со статистикой
                stats_message = (f"Статистика для {nickname}:\n"
                                 f"Сообщений за сессию: {user_data[nickname]['session_messages']}\n"
                                 f"Сообщений всего: {user_data[nickname]['total_messages']}")
                print(f"Отправляю статистику для {nickname}: {stats_message}")
                
                # Отправляем сообщение пользователю только если оно не пустое
                if stats_message.strip():
                    await websocket.send(stats_message)
                else:
                    print("Нет статистики")
            else:
                # Увеличиваем счётчик сообщений для обычных сообщений
                user_data[nickname]['session_messages'] += 1
                user_data[nickname]['total_messages'] += 1

                # Сохраняем данные пользователя после каждого сообщения
                save_user_data(user_data)

                # Рассылаем сообщение всем подключённым клиентам
                await broadcast(f"{nickname}: {message}")

    except websockets.ConnectionClosed:
        print(f'Client {nickname} disconnected')
    finally:
        client_list.remove(websocket)

async def broadcast(message):
    for client in client_list:
        try:
            await client.send(message)
        except websockets.ConnectionClosed:
            pass

async def main():
    async with websockets.serve(handler, "", 8080):
        await asyncio.Future()  # бесконечная работа

if __name__ == "__main__":
    asyncio.run(main())
