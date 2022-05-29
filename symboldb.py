import peewee

database_proxy = peewee.DatabaseProxy()

class BaseModel(peewee.Model):
    class Meta:
        database = database_proxy

class SymbolModel(BaseModel):
    hash = peewee.CharField(index=True)
    file_name = peewee.CharField(index=True)
    link_mode = peewee.BooleanField()
    target_path = peewee.CharField()

    def as_str(self):
        return str("hash: " + str(self.hash) + "  file_name: " + str(self.file_name)
                  + "  link_mode: " + str(self.link_mode)
                  + "  target_path: " + str(self.target_path))

class SourceModel(BaseModel):
    path = peewee.CharField(index=True)
    loaded = peewee.BooleanField()
    failure_count = peewee.IntegerField()

    def as_str(self):
        return str("path: " + str(self.path) + "  loaded: " + str(self.loaded)
                  + "  failure_count: " + str(self.failure_count))

def init_db():
    global database_proxy
    database_proxy.initialize(peewee.SqliteDatabase(':memory:'))
    database_proxy.connect()
    database_proxy.create_tables([SymbolModel, SourceModel])


def fill_test_data():
    SymbolModel.create(
        hash = 'DEADBEEF',
        file_name = 'poo.exe',
        link_mode = True,
        target_path = 'http://example.com/poo.exe',
    )
    SymbolModel.create(
        hash = 'FEEDBABE',
        file_name = 'foo.exe',
        link_mode = True,
        target_path = 'http://example.com/foo.exe',
    )
    SourceModel.create(
        path = 'C:\\foo.exe',
        loaded = False,
        failure_count = 1,
    )
    SourceModel.create(
        path = 'C:\\moo.exe',
        loaded = True,
        failure_count = 0,
    )

def dump():
    res = ''
    for symbol in SymbolModel.select():
        res += symbol.as_str() + '\n'

    for source in SourceModel.select():
        res += source.as_str() + '\n'

    return res

init_db()
fill_test_data()
print(dump())
