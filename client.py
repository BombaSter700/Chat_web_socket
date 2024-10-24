import asyncio
import websockets
import aioconsole

async def receive_messages(websocket):
    while True:
        try:
            message = await websocket.recv()
            if message:
                print(f'\n{message}')  # Выводим сообщение от сервера
                print(':', end='', flush=True)  # Повторно выводим приглашение для ввода
        except websockets.exceptions.ConnectionClosed:
            break

async def send_messages(websocket):
    awaiting_calc_expression = False
    while True:
        if not awaiting_calc_expression:
            user_input = await aioconsole.ainput(':')  # Асинхронный ввод
            await websocket.send(user_input)  # Отправляем на сервер

            if user_input.strip() == '/calc':
                awaiting_calc_expression = True
        else:
            # Ожидаем ввод выражения для расчета
            expression = await aioconsole.ainput()
            await websocket.send(expression)
            awaiting_calc_expression = False

        await asyncio.sleep(0)  # Позволяем другим задачам выполняться

async def main():
    uri = "ws://localhost:8080"
    async with websockets.connect(uri) as websocket:
        # Получаем запрос на ввод ника от сервера
        request_for_nickname = await websocket.recv()
        print(request_for_nickname)

        # Вводим ник и отправляем его на сервер
        username = await aioconsole.ainput()
        await websocket.send(username)

        # Получаем приветствие от сервера
        greeting = await websocket.recv()
        print(greeting)

        # Запускаем задачи для отправки и получения сообщений
        receive_task = asyncio.create_task(receive_messages(websocket))
        send_task = asyncio.create_task(send_messages(websocket))

        await asyncio.gather(receive_task, send_task)

asyncio.run(main())
