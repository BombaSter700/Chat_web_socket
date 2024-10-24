import asyncio
import websockets
import json
import os
from datetime import datetime

# Сохраняем всех клиентов, подключенных к серверу
client_list = []
user_data_file = 'user_data.json'  # файлик с данными пользователей

# Получаем текущее время для имени лог-файла при запуске сервера
log_filename = f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"

def load_user_data():
    if os.path.exists(user_data_file):
        with open(user_data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

user_data = load_user_data()

def save_user_data(data):
    with open(user_data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def log_message(message):
    # Записываем сообщение в лог-файл
    with open(log_filename, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

async def handler(websocket, path):
    client_list.append(websocket)
    await websocket.send("Введите ник:")
    nickname = await websocket.recv()
    nickname = nickname.strip()

    if nickname in user_data:
        user_data[nickname]['session_messages'] = 0  # Обнуление сообщений за сессию
    else:
        user_data[nickname] = {'total_messages': 0, 'session_messages': 0}

    welcome_message = f"Привет, {nickname}!"
    await websocket.send(welcome_message)

    # Логируем подключение пользователя
    log_message(f"{nickname} подключился к серверу.")

    try:
        while True:
            # Ждем сообщение от клиента
            message = await websocket.recv()
            log_message(f"Получено сообщение от {nickname}: {message}")

            # Обработка команды /userinfo
            if message.strip() == '/userinfo':
                # Формируем сообщение со статистикой
                stats_message = (f"Статистика для {nickname}:\n"
                                 f"Сообщений за сессию: {user_data[nickname]['session_messages']}\n"
                                 f"Сообщений всего: {user_data[nickname]['total_messages']}")
                await websocket.send(stats_message)
                log_message(f"Отправлена статистика для {nickname}")
            # Обработка команды /calc
            elif message.strip() == '/calc':
                # Отправляем запрос на ввод выражения
                await websocket.send("Введите выражение для расчета:")
                expression = await websocket.recv()  # Получаем выражение от клиента
                log_message(f"{nickname} ввел выражение для расчета: {expression}")
                try:
                    # Вычисляем результат
                    result = eval(expression)
                    await websocket.send(f"Результат: {result}")
                    log_message(f"Результат для {nickname}: {result}")
                except Exception as e:
                    error_message = f"Ошибка при вычислении: {e}"
                    await websocket.send(error_message)
                    log_message(f"{nickname} получил ошибку при вычислении: {e}")

            else:
                # Увеличиваем счётчик сообщений для обычных сообщений
                user_data[nickname]['session_messages'] += 1
                user_data[nickname]['total_messages'] += 1

                # Сохраняем данные пользователя после каждого сообщения
                save_user_data(user_data)

                # Рассылаем сообщение всем подключённым клиентам
                broadcast_message = f"{nickname}: {message}"
                await broadcast(broadcast_message)
                log_message(f"Рассылалось сообщение: {broadcast_message}")

    except websockets.ConnectionClosed:
        log_message(f"{nickname} отключился от сервера.")
    finally:
        client_list.remove(websocket)

async def broadcast(message):
    for client in client_list:
        try:
            await client.send(message)
        except websockets.ConnectionClosed:
            pass  # Игнорируем ошибки при рассылке

async def main():
    async with websockets.serve(handler, "", 8080):
        print("Сервер запущен на порту 8080")
        log_message("Сервер запущен и готов принимать подключения.")
        await asyncio.Future()  # Бесконечная работа

if __name__ == "__main__":
    asyncio.run(main())
