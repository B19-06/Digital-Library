from peewee import *
from playhouse.sqlite_ext import *
from playhouse.flask_utils import FlaskDB
from flask_admin.contrib.peewee import ModelView

from digital_library.app import app, admin

db_wrapper = FlaskDB(app)
database = db_wrapper.database


class BaseModel(db_wrapper.Model):
    admin_view = ModelView


# `id` field is created by peewee


class TAG(BaseModel):
    Name = TextField(unique=True)


class USER(BaseModel):
    Email = TextField(unique=True)
    FirstName = TextField()
    SecondName = TextField()

    @property
    def FullName(self):
        return self.FirstName + ' ' + self.SecondName


class MATERIAL(BaseModel):
    Type = TextField()
    Description = TextField(default='')
    tags = ManyToManyField(TAG, backref='materials')  # TAGGED_WITH
    authors = ManyToManyField(
        USER, backref='suggested_materials')  # SUGGESTED_BY


class COMMENT(BaseModel):
    Text = TextField()
    commented_material = ForeignKeyField(
        MATERIAL, backref='comments')  # COMMENTED_WITH
    author = ForeignKeyField(USER, backref='comments')  # PROVIDED_BY__COMMENT


class ATTACHMENT(BaseModel):
    Type = TextField()
    URLS = JSONField()  # mirrors for the same file
    material = ForeignKeyField(
        MATERIAL, backref='attachments')  # WITH_ATTACHMENT


class REVIEW(BaseModel):
    Text = TextField()
    Rating = IntegerField()
    reviewed_material = ForeignKeyField(
        MATERIAL, backref='reviews')  # REVIEWED_WITH
    author = ForeignKeyField(USER, backref='reviews')  # PROVIDED_BY__REVIEW


class ADMIN_RIGHTS(BaseModel):
    Description = TextField(unique=True)
    users = ManyToManyField(USER, backref='rights')


class USER_AdminView(ModelView):
    inline_models = (ADMIN_RIGHTS.users.get_through_model(),)


USER.admin_view = USER_AdminView


class MATERIAL_AdminView(ModelView):
    inline_models = (MATERIAL.tags.get_through_model(),
                     MATERIAL.authors.get_through_model(),
                     ATTACHMENT, COMMENT, REVIEW)


MATERIAL.admin_view = MATERIAL_AdminView

tables = [
    TAG,
    USER,
    MATERIAL,
    MATERIAL.tags.get_through_model(),
    MATERIAL.authors.get_through_model(),
    COMMENT,
    ATTACHMENT,
    REVIEW,
    ADMIN_RIGHTS,
    ADMIN_RIGHTS.users.get_through_model(),
]

admin_views = [
    x.admin_view(x) for x in tables if getattr(x, 'admin_view', None)
]

for view in admin_views:
    admin.add_view(view)


def create_tables():
    with database:
        database.create_tables(tables)


if __name__ == "__main__":
    # Running: python -m digital_library.db.db
    create_tables()
