from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
post = Table('post', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('body', String(length=140)),
    Column('timestamp', DateTime),
    Column('user_id', Integer),
    Column('language', String(length=5)),
    Column('image', String(length=140)),
    Column('link1', String(length=140)),
    Column('link1_text', String(length=140)),
)

link = Table('link', pre_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('url', String),
    Column('body', String),
    Column('post_id', Integer),
    Column('link1', String),
    Column('link1_text', String),
    Column('link2', String),
    Column('link2_text', String),
    Column('link3', String),
    Column('link3_text', String),
    Column('link4', String),
    Column('link4_text', String),
    Column('link5', String),
    Column('link5_text', String),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['post'].columns['link1'].create()
    post_meta.tables['post'].columns['link1_text'].create()
    pre_meta.tables['link'].columns['link2'].drop()
    pre_meta.tables['link'].columns['link2_text'].drop()
    pre_meta.tables['link'].columns['link3'].drop()
    pre_meta.tables['link'].columns['link3_text'].drop()
    pre_meta.tables['link'].columns['link4'].drop()
    pre_meta.tables['link'].columns['link4_text'].drop()
    pre_meta.tables['link'].columns['link5'].drop()
    pre_meta.tables['link'].columns['link5_text'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['post'].columns['link1'].drop()
    post_meta.tables['post'].columns['link1_text'].drop()
    pre_meta.tables['link'].columns['link2'].create()
    pre_meta.tables['link'].columns['link2_text'].create()
    pre_meta.tables['link'].columns['link3'].create()
    pre_meta.tables['link'].columns['link3_text'].create()
    pre_meta.tables['link'].columns['link4'].create()
    pre_meta.tables['link'].columns['link4_text'].create()
    pre_meta.tables['link'].columns['link5'].create()
    pre_meta.tables['link'].columns['link5_text'].create()
