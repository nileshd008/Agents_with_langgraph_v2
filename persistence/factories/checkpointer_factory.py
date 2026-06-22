
from contracts import CheckPointerConfig, StoreConfig

class CheckpointerFactory:
    def __init__(self, config: CheckPointerConfig):
        self.cfg = config

    def create(self):
        kind = self.cfg.kind.lower()

        if kind == 'memory':
            from langgraph.checkpoint.memory import InMemorySaver
            return InMemorySaver()
        
        if kind == 'sqlite':
            if not self.cfg.connection_str:
                raise ValueError('SQlite checkpointer requires connection string')
            
            #if cfg.async_mode:
            from langgraph.checkpoint.sqlite import SqliteSaver
            return SqliteSaver.from_conn_str(self.cfg.connection_str)
        
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
            if not self.cfg.connection_str:
                raise ValueError('SQlite checkpointer requires connection string')
            
            #if cfg.async_mode:
            from langgraph.store.sqlite import SqliteStore
            return SqliteStore.from_conn_str(self.cfg.connection_str)
        
        if kind == 'postgres':
            from langgraph.store.postgres import PostgresStore
            return PostgresStore.from_conn_str(self.cfg.connection_str)
        
