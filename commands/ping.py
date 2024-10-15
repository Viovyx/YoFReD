from interactions import Extension, slash_command, SlashContext

from automations.log import log_command


class Ping(Extension):
    @slash_command(
        name="ping",
        description="Test bot latency",
        dm_permission=False
    )
    async def ping(self, ctx: SlashContext):
        log_command(ctx=ctx, cmd="ping")
        await ctx.send(f"Pong! The response time is {self.bot.latency * 1000}ms")