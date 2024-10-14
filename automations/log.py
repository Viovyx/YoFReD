from datetime import datetime

from tinydb import TinyDB

from shared import ROOT_DIR


def log_command(ctx, cmd):
    db = TinyDB(f'{ROOT_DIR}/db/logs.json', indent=4, create_dirs=True)
    db.default_table_name = f'{cmd}'
    db.insert({
        'time-utc': f'{datetime.utcnow()}',
        'user': f'{ctx.user.username}',
        'user-id': f'{ctx.user.id}',
        'guild-id': f'{ctx.guild_id}',
        'channel': f'{ctx.channel.name}',
        'channel-id': f'{ctx.channel_id}'
    })
    db.close()
    print(
        f"{ctx.user.username}(uid:{ctx.user.id}) used /{cmd} in {ctx.channel.name}(chid:{ctx.channel_id})(gid:{ctx.guild_id}) at UTC:{datetime.utcnow()}")
