import interactions
from interactions import Extension, slash_command, SlashContext, Embed, EmbedField

from automations.log import log_command


class Help(Extension):

    @slash_command(
        name="help",
        description="Get extra information about a command.",
        dm_permission=False,
        options=[
            interactions.SlashCommandOption(
                name="command",
                description="Which command do you need help with?",
                type=interactions.OptionType.STRING,
                required=True
            ),
        ],
    )
    async def reminder(self, ctx: SlashContext, command: str = None):
        log_command(ctx=ctx, cmd="help")
        
        # Unfinished message
        embed = Embed(
            title="Help",
            description="This is a help command. It is still under development.",
            color="#ce02c4",
            fields=[
                EmbedField(name="Command", value=command, inline=True),
            ]
        )
        await ctx.send(embed=embed)

        # Get list of valid commands