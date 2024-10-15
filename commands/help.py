import interactions
from interactions import Extension, slash_command, SlashContext, Embed, EmbedField

from automations.log import log_command


class Help(Extension):

    @slash_command(
        name="help",
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
        
        # Get list of valid commands