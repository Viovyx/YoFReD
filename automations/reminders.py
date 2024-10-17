import os
from datetime import datetime
from tinydb import TinyDB
import interactions
from shared import ROOT_DIR, User

async def check(bot):
    db = TinyDB(f'{ROOT_DIR}/db/reminders.json', indent=4, create_dirs=True)
    current_time = round(datetime.now().timestamp())
    channel_id = os.getenv('REMINDER_CHANNEL_ID')
    channel = bot.get_channel(channel_id)

    for user_id in db.tables():
        db.default_table_name = user_id
        reminders = db.all()

        for reminder in reminders:
            if reminder['unix-time'] <= current_time:
                msg_embed = interactions.Embed(
                    title=reminder['title'],
                    description=f"{reminder['content'] if reminder['content'] else ''}",
                    color="#ce02c4",
                    fields=[
                        interactions.EmbedField(name="For", value=f"<@{user_id}>", inline=True),
                        interactions.EmbedField(name="Created by", value=f"<@{reminder['created-by']}>", inline=True),
                        interactions.EmbedField(name="Time", value=f"<t:{reminder['unix-time']}:R>", inline=True),
                    ]
                )
                private = reminder['private']

                await channel.send(embed=msg_embed, content=f"||<@{user_id}>||", ephemeral=private)
                db.remove(User['id'] == reminder['id'])
    db.close()