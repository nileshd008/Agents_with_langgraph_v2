
from .contracts import CheckPointerConfig, StoreConfig

class CheckpointerFactory:
    def __init__(self, config: CheckPointerConfig):
        self.cfg = config

    def create(self):
        kind = self.cfg.kind.lower()

        if kind == 'memory':
            from langgraph.checkpoint.memory import InMemorySaver
            return InMemorySaver()
        
        if kind == 'sqlite':
            import sqlite3
            from langgraph.checkpoint.sqlite import SqliteSaver
            
            if self.cfg.connection_str:
                conn = sqlite3.connect(self.cfg.connection_str, check_same_thread=False)
                return SqliteSaver(conn)

            if not self.cfg.connection_str:
                raise ValueError('SQlite checkpointer requires connection string')
        
        
        if kind == 'postgres':
            from langgraph.checkpoint.postgres import PostgresSaver
            return PostgresSaver.from_conn_str(self.cfg.connection_str)
        

class StoreFactory:
    def __init__(self, config: StoreConfig):
        self.cfg = config

    def create(self):
        kind = self.cfg.kind.lower()

        if kind == 'memory':
            from langgraph.store.memory import InMemoryStore
            return InMemoryStore()
        
        if kind == 'sqlite':
            import sqlite3
            from langgraph.store.sqlite import SqliteStore

            if self.cfg.connection_str:
                conn = sqlite3.connect(self.cfg.connection_str, check_same_thread=False)
                return SqliteStore(conn)

            if not self.cfg.connection_str:
                raise ValueError('SQlite checkpointer requires connection string')
        
        if kind == 'postgres':
            from langgraph.store.postgres import PostgresStore
            return PostgresStore.from_conn_str(self.cfg.connection_str)
        
