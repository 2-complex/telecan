import database

from sqlalchemy import inspect
from sqlalchemy import MetaData
from sqlalchemy import Column, Integer, ForeignKey

from alembic.migration import MigrationContext
from alembic.operations import Operations


def mimic_foreign_key(fk):
    return ForeignKey(fk.target_fullname)


def mimic_column(col):
    return Column(
        col.name,
        col.type,
        *(map(mimic_foreign_key, col.foreign_keys)),
        primary_key=col.primary_key,
        nullable=col.nullable,
        unique=col.unique,
        server_default=col.server_default)


def get_current_database_info(engine):
    inspector = inspect(engine)
    return {table_name : [column['name'] for column in inspector.get_columns(table_name)] for table_name in inspector.get_table_names()}


def create_missing_database_entities(Model, engine):
    m = Model.metadata
    current_info = get_current_database_info(engine)

    print(current_info)

    conn = engine.connect()
    ctx = MigrationContext.configure(conn)
    op = Operations(ctx)

    print "metadata", m
    for table_name in m.tables:
        table = m.tables[table_name]
        print "tab;e", table
        if current_info.has_key(table_name):
            print "stuff", table_name
            for col in table.columns:
                print "col", col
                if not col.name in current_info[table_name]:
                    print "    IN TABLE: %s CREATING COLUMN: %s"%(table_name, col.name)
                    op.add_column(table_name, mimic_column(col))
                    print "    ... done"
        else:
            args = [table_name] + map(mimic_column, list(table.columns))
            print "CREATING TABLE: " + repr(args)
            op.create_table(*args)


if __name__=='__main__':
    from sys import argv as args
    assert(args[1].endswith('.db'))
    db = database.Database("sqlite:///" + args[1])

    print("updating database: " + args[1])
    create_missing_database_entities(database.Model, db.engine)

