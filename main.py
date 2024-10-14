import os

import asyncio
import interactions
from dotenv import load_dotenv

from automations.schedules import schedules
from shared import ROOT_DIR

if __name__ == '__main__':
    load_dotenv()
    token = os.getenv('TOKEN')
    bot = interactions.Client()


    # Startup
    async def main():
        asyncio.create_task(schedules(bot))

        # load all commands from the commands folder
        for file in os.listdir(f'{ROOT_DIR}/commands'):
            if file.endswith('.py'):
                name = file[:-3]
                bot.load_extension(f'commands.{name}')

        await bot.astart(token)


    @interactions.listen()
    async def on_startup():
        print("Bot is ready!")


    asyncio.run(main())
