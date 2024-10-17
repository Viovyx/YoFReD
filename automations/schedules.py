import aioschedule as schedule
import asyncio
from automations import reminders

async def schedules(bot):
    print("RUNNING: schedules.py")

    schedule.every().minute.do(lambda: reminders.check(bot))

    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)
