from pathlib import Path
from symbolmodel import Symbol, Source
from typing import Optional
import peewee

database_proxy = peewee.DatabaseProxy()

class BaseModel(peewee.Model):
    class Meta:
        database = database_proxy

class SymbolModel(BaseModel):
    hash = peewee.CharField(index=True)
    filename = peewee.CharField(index=True)
    url = peewee.CharField()
    store_path = peewee.CharField()

    def as_str(self):
        return str("hash: " + str(self.hash) + "  filename: " + str(self.filename)
                  + "  url: " + str(self.url)
                  + "  store_path: " + str(self.store_path))

class SourceModel(BaseModel):
    path = peewee.CharField(index=True)
    loaded = peewee.BooleanField()
    failure_count = peewee.IntegerField()

    def as_str(self):
        return str("path: " + str(self.path) + "  loaded: " + str(self.loaded)
                  + "  failure_count: " + str(self.failure_count))

def fill_test_data():
    store_symbol(Symbol('DEADBEEF', 'poo.exe', 'http://example.com/poo.exe', None))
    store_symbol(Symbol('FEEDBABE', 'foo.pd_', 'http://example.com/foo.exe', 'stored/FEEDBABE/foo.pd_'))
    store_symbol(Symbol('FEEDBABE', 'foo.pd_', 'http://example.com/foo.pdb', 'stored/FEEDBABE/foo.pd_'))
    store_symbol(Symbol('FEEDBABE', 'boo.dll', None, 'stored/FEEDBABE/boo.dll'))
    store_source(Source('C:\\foo.exe', False, 1))
    store_source(Source('C:\\foo.pdb', False, 2))
    store_source(Source('C:\\foo.pdb', True, 2))
    store_source(Source('C:\\moo.exe', True, 0))

def init_db(path: Path):
  global database_proxy
  database_proxy.initialize(peewee.SqliteDatabase(path))
  database_proxy.connect()
  database_proxy.create_tables([SymbolModel, SourceModel])

def dump():
    res = ''
    for symbol in SymbolModel.select():
        res += symbol.as_str() + '\n'

    for source in SourceModel.select():
        res += source.as_str() + '\n'

    return res

def find_symbol(hash: str, filename: str) -> Optional[Symbol]:
  for symbol in SymbolModel.select().where(
    (SymbolModel.hash == hash) |
    (SymbolModel.filename == filename)):
    symbol_opt = symbol.url if len(symbol.url) > 0 else None
    store_path_opt = symbol.store_path if len(symbol.store_path) > 0 else None
    return Symbol(symbol.hash, symbol.filename, symbol_opt, store_path_opt)

  return None

def store_symbol(symbol: Symbol) -> None:
  url_not_null: str = symbol.url or ''
  store_path_not_null: str = symbol.store_path or ''

  for existing in SymbolModel.select().where(
      (SymbolModel.hash == symbol.hash) |
      (SymbolModel.filename == symbol.filename)):
    existing.url = url_not_null
    existing.store_path = store_path_not_null
    existing.save()
    return

  SymbolModel.create(
    hash = symbol.hash,
    filename = symbol.filename,
    url = url_not_null,
    store_path = store_path_not_null)

def find_source(url: str) -> Optional[Source]:
  for source in SourceModel.select().where((SourceModel.path == url)):
    return Source(source.url, source.loaded, source.failure_count)
  return None

def store_source(source: Source) -> None:
  for existing in SourceModel.select().where((SourceModel.path == source.path)):
    existing.loaded = source.stored
    existing.failure_count = source.failures
    existing.save()
    return

  SourceModel.create(
    path = source.path,
    loaded = source.stored,
    failure_count = source.failures)

def test():
  init_db(':memory:')
  fill_test_data()
  print(find_symbol('FEEdBABE', 'foo.pd_'))
  print(dump())
  pass
