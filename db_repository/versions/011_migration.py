from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
link = Table('link', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('post_id', Integer),
    Column('url', String(length=140)),
    Column('body', String(length=140)),
    Column('link1', String(length=120)),
    Column('link2', String(length=120)),
    Column('link3', String(length=120)),
    Column('link4', String(length=120)),
    Column('link5', String(length=120)),
    Column('link1_text', String(length=120)),
    Column('link2_text', String(length=120)),
    Column('link3_text', String(length=120)),
    Column('link4_text', String(length=120)),
    Column('link5_text', String(length=120)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['link'].columns['link1'].create()
    post_meta.tables['link'].columns['link1_text'].create()
    post_meta.tables['link'].columns['link2'].create()
    post_meta.tables['link'].columns['link2_text'].create()
    post_meta.tables['link'].columns['link3'].create()
    post_meta.tables['link'].columns['link3_text'].create()
    post_meta.tables['link'].columns['link4'].create()
    post_meta.tables['link'].columns['link4_text'].create()
    post_meta.tables['link'].columns['link5'].create()
    post_meta.tables['link'].columns['link5_text'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['link'].columns['link1'].drop()
    post_meta.tables['link'].columns['link1_text'].drop()
    post_meta.tables['link'].columns['link2'].drop()
    post_meta.tables['link'].columns['link2_text'].drop()
    post_meta.tables['link'].columns['link3'].drop()
    post_meta.tables['link'].columns['link3_text'].drop()
    post_meta.tables['link'].columns['link4'].drop()
    post_meta.tables['link'].columns['link4_text'].drop()
    post_meta.tables['link'].columns['link5'].drop()
    post_meta.tables['link'].columns['link5_text'].drop()
