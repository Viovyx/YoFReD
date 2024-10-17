from datetime import datetime, timedelta

import interactions
from interactions import Extension, slash_command, SlashContext, Embed, EmbedField
from tinydb import TinyDB

from automations.log import log_command
from shared import ROOT_DIR, User


class Reminder(Extension):
    def get_unix_time(self, time: str):
        time = time.lower()
        times = time.split()

        weeks, days, hours, minutes = 0, 0, 0, 0

        for t in times:
            weeks = int(t[:-1]) if 'w' in t else weeks
            days = int(t[:-1]) if 'd' in t else days
            hours = int(t[:-1]) if 'h' in t else hours
            minutes = int(t[:-1]) if 'm' in t else minutes

        future_timeH = datetime.now() + timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes)
        future_timeUnix = round(future_timeH.timestamp())

        if future_timeUnix <= round(datetime.now().timestamp()):
            raise ValueError
        
        return future_timeUnix

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
                description="When should the reminder be triggered relative to now? (Format: 1d 2h 30m or 1w -3h 15m)",
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
        db = TinyDB(f'{ROOT_DIR}/db/reminders.json', indent=4, create_dirs=True)
        db.default_table_name = f'{user.id}'
        reminders = db.all()

        if user.id != ctx.user.id and private:
            await ctx.send("ERROR: You can't create a private reminder for someone else!", ephemeral=True)
            return
        
        if reminders:
            last_id = max(reminder['id'] for reminder in reminders)
            id = last_id + 1
        else:
            id = 1    

        try:
            time = self.get_unix_time(time)
        except ValueError:
            await ctx.send("ERROR: Make sure your time is in the future and the formatting is correct! Use `/help` for more info.", ephemeral=True)
            return


        db.insert({
            "id": id,
            "title": title, 
            "content": content, 
            "unix-time": time,
            "private": private, 
            "created-by": ctx.user.id
        })
        db.close()

        msg_embed = Embed(
            title=f"{'Private reminder' if private else 'Reminder'} created succesfully!",
            description=f"**{title}** (id: {id}) \n {content if content else ''}",
            color="#02ce0c",
            fields=[
                EmbedField(name="For", value=user.mention, inline=True),
                EmbedField(name="Created by", value=ctx.user.mention, inline=True),
                EmbedField(name="Time", value=f"<t:{time}:R>", inline=True),
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
        elif user.id == ctx.user.id and private:
            reminders = db.all()
        else:
            reminders = db.search(User['private'] == False)

        db.close()

        if not reminders:
            await ctx.send(f"ERROR: No reminders found for {user.mention}!", ephemeral=True)
            return

        msg_embed = Embed(
            title=f"Reminders for {user.username}:",
            color="#d28854"
        )
        for r in reminders:
            id = r['id']
            name = f"{'(Private) ' if r['private'] else ''}{r['title']}"
            content = r['content'] if r['content'] else ''
            time = f"<t:{r['unix-time']}:R>"
            createdBy = r['created-by']

            msg_embed.add_field(
                name=f"{name} (id: {id})", 
                value=f"{content} \n{time} \nCreated by: <@{createdBy}>", 
                inline=False)

        await ctx.send(embed=msg_embed, ephemeral=private)

    @reminder.subcommand(
        sub_cmd_name="delete",
        sub_cmd_description="Delete a reminder by its id.",
        options=[
            interactions.SlashCommandOption(
                name="id",
                description="Which reminder should be deleted?",
                type=interactions.OptionType.INTEGER,
                required=True
            ),
            interactions.SlashCommandOption(
                name="user",
                description="Which user's reminder should be deleted? Default is yourself.",
                type=interactions.OptionType.USER,
                required=False
            ),
        ],
    )
    async def reminder_delete(self, ctx: SlashContext, user: interactions.Member = None, id: int = None):
        log_command(ctx=ctx, cmd="reminder.delete")

        user = user if user else ctx.user
        db = TinyDB(f'{ROOT_DIR}/db/reminders.json', indent=4, create_dirs=True)
        db.default_table_name = f'{user.id}'
        reminders = db.all()

        if not reminders:
            await ctx.send(f"ERROR: No reminders found for {user.mention}!", ephemeral=True)
            return
        
        reminder = db.search(User['id'] == id)

        if not reminder:
            await ctx.send(f"ERROR: Reminder with id {id} not found for {user.mention}!", ephemeral=True)
            return
        elif user.id != ctx.user.id and reminder[0]['created-by'] != ctx.user.id:
            await ctx.send("ERROR: You can't delete someone else's reminder that you haven't created!", ephemeral=True)
            return
        
        reminder = reminder[0]

        if reminder['created-by'] == ctx.user.id and not reminder['private']:
            hidden = False
        else:
            hidden = True

        msg_embed = Embed(
            title=f"Reminder deleted succesfully!",
            description=f"**{reminder['title']}** (id: {id}) \n {reminder['content'] if reminder['content'] else ''}",
            color="#f73711",
            fields=[
                EmbedField(name="For", value=user.mention, inline=True),
                EmbedField(name="Created by", value=ctx.user.mention, inline=True),
                EmbedField(name="Time", value=f"<t:{reminder['unix-time']}:R>", inline=True),
            ]
        )

        db.remove(User['id'] == id)
        db.close()

        await ctx.send(embed=msg_embed, ephemeral=hidden)

    @reminder.subcommand(
        sub_cmd_name="edit",
        sub_cmd_description="Edit a reminder.",
        options=[
            interactions.SlashCommandOption(
                name="id",
                description="Which reminder should be edited?",
                type=interactions.OptionType.INTEGER,
                required=True
            ),
            interactions.SlashCommandOption(
                name="user",
                description="Which user's reminder should be edited? Default is yourself.",
                type=interactions.OptionType.USER,
                required=False
            ),
            interactions.SlashCommandOption(
                name="change_title",
                description="Change the title of the reminder.",
                type=interactions.OptionType.STRING,
                required=False
            ),
            interactions.SlashCommandOption(
                name="change_time",
                description="When should the reminder be triggered relative to now? (Format: 1d 2h 30m or 1w -3h 15m)",
                type=interactions.OptionType.STRING,
                required=False
            ),
            interactions.SlashCommandOption(
                name="change_content",
                description="Change the extra information of the reminder.",
                type=interactions.OptionType.STRING,
                required=False
            ),
            interactions.SlashCommandOption(
                name="change_private",
                description="Should the reminder be made (not) private?",
                type=interactions.OptionType.BOOLEAN,
                required=False
            ),
        ],
    )
    async def reminder_edit(self, ctx: SlashContext, id: int = None, user: interactions.Member = None, change_title: str = None, change_content: str = None, change_time: str = None, change_private: bool = None):
        log_command(ctx=ctx, cmd="reminder.edit")

        user = user if user else ctx.user
        db = TinyDB(f'{ROOT_DIR}/db/reminders.json', indent=4, create_dirs=True)
        db.default_table_name = f'{user.id}'
        reminders = db.all()

        title = change_title
        content = change_content
        time = change_time
        private = change_private

        if not reminders:
            await ctx.send(f"ERROR: No reminders found for {user.mention}!", ephemeral=True)
            return
        
        reminder = db.search(User['id'] == id)

        if not reminder:
            await ctx.send(f"ERROR: Reminder with id {id} not found for {user.mention}!", ephemeral=True)
            return
        elif reminder[0]['created-by'] != ctx.user.id:
            await ctx.send("ERROR: You can't edit someone else's reminder!", ephemeral=True)
            return
        
        reminder = reminder[0]

        if title:
            reminder['title'] = title
        if content:
            reminder['content'] = content
        if private is not None:
            if user.id != ctx.user.id:
                await ctx.send("ERROR: You can't make a reminder private for someone else!", ephemeral=True)
                return
            reminder['private'] = private
        if time:
            try:
                time = self.get_unix_time(time)
            except ValueError:
                await ctx.send("ERROR: Make sure your time is in the future and the formatting is correct! Use `/help` for more info.", ephemeral=True)
                return
            reminder['unix-time'] = time

        db.update(reminder, User['id'] == id)
        db.close()

        msg_embed = Embed(
            title=f"Reminder edited succesfully!",
            description=f"**{reminder['title']}** (id: {id}) \n {reminder['content'] if reminder['content'] else ''}",
            color="#f7f711",
            fields=[
                EmbedField(name="For", value=user.mention, inline=True),
                EmbedField(name="Created by", value=ctx.user.mention, inline=True),
                EmbedField(name="Time", value=f"<t:{reminder['unix-time']}:R>", inline=True),
            ]
        )

        private = True if reminder['private'] else False
        await ctx.send(embed=msg_embed, ephemeral=private)