from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
replay_meta = Table('replay_meta', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=100)),
    Column('value', Text),
    Column('replay_id', Integer),
)

replay = Table('replay', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('title', String(length=100)),
    Column('upvotes', Integer, default=ColumnDefault(1)),
    Column('downvotes', Integer, default=ColumnDefault(0)),
    Column('hotness', Float, default=ColumnDefault(0.0)),
    Column('posted', DateTime),
    Column('author', Integer),
    Column('filename', String(length=200)),
    Column('wgid', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['replay_meta'].create()
    post_meta.tables['replay'].columns['wgid'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['replay_meta'].drop()
    post_meta.tables['replay'].columns['wgid'].drop()
