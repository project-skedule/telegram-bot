import asyncio
import zmq, zmq.asyncio as azmq
from src.bot import dp, bot
from src.logger import logger
from src.handlers.error_handlers import register_error_handlers
from src.handlers.parent_handlers import register_parent_handlers
from src.handlers.student_handers import register_student_handlers
from src.handlers.teacher_handers import register_teacher_handlers
from src.handlers.administration_handlers import register_administration_handlers
from src.handlers.find_handlers import register_find_handlers
from src.handlers.registration_handlers import register_registration_handlers
from os import getenv
import aiohttp


<<<<<<< HEAD

@routes.get("/")
async def healthcheck(request):
    return web.Response(text="Healthy")


app = web.Application()
app.add_routes(routes)
web.run_app(app)
=======
>>>>>>> dev_tg

async def web():
    
    app = aiohttp.web.Application()
    app.add_routes([
        aiohttp.web.get('/', lambda req: aiohttp.web.Response(text='Healthy')),
    ])

    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    
    await aiohttp.web.TCPSite(runner).start()
    await asyncio.Event().wait()

async def run():
    await register_error_handlers()
    await register_parent_handlers()
    await register_student_handlers()
    await register_teacher_handlers()
    await register_administration_handlers()
    await register_find_handlers()
    await register_registration_handlers()

    logger.debug("Registered handlers")

    # await aiogram.executor.start_polling(dp, skip_updates=True)
    await dp.start_polling()


async def zmq():
    context = azmq.Context()
    socket = context.socket(zmq.SUB)
    port = getenv("ZMQ_PORT")
    host = getenv("ZMQ_HOST")
    await socket.connect(f"tcp://{port}:{host}")
    await socket.subscribe("")

    while True:
        json = await socket.recv_json()
        text = json.get("text")

        if text is None or not isinstance(text, str) or text.strip() == "":
            continue

        ids = json.get("telegram_ids", [])
        args = json.get("args", {})

        for id in ids:
            await bot.send_message(chat_id=id, text=text, parse_mode="markdown", **args)


async def main():
    bot_service = main_loop.create_task(run())
    zmq_service = main_loop.create_task(zmq())
    web_service = main_loop.create_task(web())
    await asyncio.wait([zmq_service, web_service, bot_service])


if __name__ == "__main__":
    # TODO: load env variables for zmq
    main_loop = asyncio.get_event_loop()
    main_loop.run_until_complete(main())
    main_loop.close()
