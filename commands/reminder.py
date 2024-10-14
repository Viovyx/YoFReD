from datetime import datetime, timedelta

import interactions
from interactions import Extension, slash_command, SlashContext, Embed, EmbedField
from tinydb import TinyDB

from automations.log import log_command
from shared import ROOT_DIR, User


class Reminder(Extension):
    @slash_command(
        name="reminder",
        dm_permission=False,
        sub_cmd_name="create",
        sub_cmd_description="Create a friendly reminder.",
        options=[
            interactions.SlashCommandOption(
                name="title",
                description="What should the reminder be called?",
                type=interactions.OptionType.STRING,
                required=True
            ),
            interactions.SlashCommandOption(
                name="time",
                description="When should the reminder be triggered? (Format: 31-04-2024T23:59:59 or +2h30m)",
                type=interactions.OptionType.STRING,
                required=True
            ),
            interactions.SlashCommandOption(
                name="content",
                description="Add extra information to the reminder.",
                type=interactions.OptionType.STRING,
                required=False
            ),
            interactions.SlashCommandOption(
                name="user",
                description="Which user should be reminded? Default is yourself.",
                type=interactions.OptionType.USER,
                required=False
            ),
            interactions.SlashCommandOption(
                name="private",
                description="Should the creation of the reminder be private? Default is false.",
                type=interactions.OptionType.BOOLEAN,
                required=False
            ),
        ],
    )
    async def reminder(self, ctx: SlashContext, user: interactions.Member = None, title: str = None, content: str = None, private: bool = False, time: str = None):
        log_command(ctx=ctx, cmd="reminder.create")

        user = user if user else ctx.user

        if user.id != ctx.user.id and private:
            await ctx.send("ERROR: You can't create a private reminder for someone else!", ephemeral=True)
            return

        # Check if time is in the future
        try:
            time = datetime.strptime(time, '%d-%m-%YT%H:%M:%S') if '+' not in time else datetime.now() + timedelta(hours=int(time.replace('+', '').split('h')[0]), minutes=int(time.split('h')[1].split('m')[0]))
        except ValueError:
            await ctx.send("ERROR: Invalid time format! Please use the format: 31-04-2024T23:59:59 or +2h30m", ephemeral=True)
            return


        db = TinyDB(f'{ROOT_DIR}/db/reminders.json', indent=4, create_dirs=True)
        db.default_table_name = f'{user.id}'
        db.insert({
            "title": title, 
            "content": content, 
            "time": time.strftime("%d-%m-%YT%H:%M:%S"),
            "private": private, 
            "created-by": ctx.user.username, 
            "created-by-id": ctx.user.id
        })
        db.close()

        msg_embed = Embed(
            title=f"{'Private reminder' if private else 'Reminder'} created succesfully!",
            description=f"**{title}** \n {content if content else ''}",
            color="#02ce0c",
            fields=[
                EmbedField(name="Created by", value=ctx.user.mention, inline=True),
                EmbedField(name="Created for", value=user.mention, inline=True),
                EmbedField(name="Time", value=time.strftime("%d-%m-%YT%H:%M:%S"), inline=True),  # TODO: Format time to unix timestamp
            ]
        )

        await ctx.send(embed=msg_embed, ephemeral=private)
    
    @reminder.subcommand(
        sub_cmd_name="list",
        sub_cmd_description="List all public reminders for a user.",
        options=[
            interactions.SlashCommandOption(
                name="user",
                description="Which user's reminders should be listed? Default is yourself.",
                type=interactions.OptionType.USER,
                required=False
            ),
            interactions.SlashCommandOption(
                name="private",
                description="Should your own private reminders be included? The list will be hidden. Default is false.",
                type=interactions.OptionType.BOOLEAN,
                required=False
            ),
        ],
    )
    async def reminder_list(self, ctx: SlashContext, user: interactions.Member = None, private: bool = False):
        log_command(ctx=ctx, cmd="reminder.list")

        user = user if user else ctx.user
        db = TinyDB(f'{ROOT_DIR}/db/reminders.json', indent=4, create_dirs=True)
        db.default_table_name = f'{user.id}'
        
        if user.id != ctx.user.id and private:
            await ctx.send("ERROR: You can't list someone else's private reminders!", ephemeral=True)
            return
        
        if user.id == ctx.user.id and private:
            reminders = db.all()
        else:
            reminders = db.search(User['private'] == False)

        print(f'Reminders: {reminders}')

        db.close()

        msg_embed = Embed(
            title=f"Reminders for {user.username}:",
            color="#d28854"
        )
        for r in reminders:
            msg_embed.add_field(name=f"{'(Private)' if r['private'] else ''} {r['title']}", value=f"{r['content'] if r['content'] else ''} \n Time: {r['time']}", inline=False)  # TODO: Format time to unix timestamp

        await ctx.send(embed=msg_embed, ephemeral=private)