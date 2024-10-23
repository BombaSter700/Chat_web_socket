import asyncio
import websockets

# Глобальная переменная для хранения статистики пользователя
user_info = None

async def receive_messages(websocket):
    global user_info  # Будем обновлять статистику в этой переменной
    while True:
        try:
            message = await websocket.recv()
            if message:
                if message.startswith("Статистика для"):
                    # Если это статистика, сохраняем её в user_info
                    user_info = message
        except websockets.exceptions.ConnectionClosed:
            break

async def send_messages(websocket, username):
    global user_info
    while True:
        user_input = input(':')  # Пользователь вводит сообщение или команду
        await websocket.send(user_input)  # Отправляем его на сервер

        # Проверка на ввод команды /userinfo
        if user_input.strip() == '/userinfo':
            await asyncio.sleep(1)  # Даем время серверу отправить статистику
            if user_info:  # Если статистика была получена, выводим её
                print(f"Выгружаю твои логи, {username}")
                print(user_info)
                user_info = None  # Сбрасываем статистику после вывода

        await asyncio.sleep(0)

async def main():
    uri = "ws://localhost:8080"
    async with websockets.connect(uri) as websocket:
        # Сначала получаем запрос от сервера на ввод ника
        request_for_nickname = await websocket.recv()
        print(request_for_nickname)
        
        # Вводим ник и отправляем его на сервер
        username = input()
        await websocket.send(username)

        # Ждём приветствие от сервера
        greeting = await websocket.recv()
        print(greeting)

        # После получения приветствия запускаем задачи для отправки и получения сообщений
        receive_task = asyncio.create_task(receive_messages(websocket))
        send_task = asyncio.create_task(send_messages(websocket, username))

        await asyncio.gather(receive_task, send_task)

asyncio.run(main())
