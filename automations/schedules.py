import aioschedule as schedule
import asyncio

async def schedules(bot):
    print("RUNNING: schedules.py")

    # schedule.every().day.at("00:00").do()

    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)
