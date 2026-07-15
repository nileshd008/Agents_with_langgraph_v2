
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from contextlib import AsyncExitStack
from .contracts import CheckPointerConfig, StoreConfig


from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres import AsyncPostgresStore, PoolConfig



class CheckpointerFactory:
    def __init__(self, config):
        self.cfg = config

    async def create(self, stack: AsyncExitStack):
        kind = self.cfg.kind.lower()
        
        if kind == 'sqlite':
            safe_serializer = JsonPlusSerializer(allowed_objects="core")
            if not self.cfg.connection_str:
                raise ValueError('SQLite checkpointer requires a connection string')
            
            ctx_manager = AsyncSqliteSaver.from_conn_string(self.cfg.connection_str, serde=safe_serializer)
            checkpointer = await stack.enter_async_context(ctx_manager)
            
            if hasattr(checkpointer, 'setup'):
                await checkpointer.setup()
            return checkpointer
        
        elif kind == 'postgres':
            if not self.cfg.connection_str:
                raise ValueError('Postgres checkpointer requires a connection string')
                
            ctx_manager = AsyncPostgresSaver.from_conn_string(self.cfg.connection_str)
            checkpointer = await stack.enter_async_context(ctx_manager)
            await checkpointer.setup()
            return checkpointer
            
        else:
            raise ValueError(f"Unsupported checkpointer type: {kind}")


class StoreFactory:
    def __init__(self, config):
        self.cfg = config

    async def create(self, stack: AsyncExitStack):
        kind = self.cfg.kind.lower()
        
        # if kind == 'sqlite':
        #     if not self.cfg.connection_str:
        #         raise ValueError('SQLite store requires a connection string')
                
        #     ctx_manager = AsyncSqliteStore.from_conn_string(self.cfg.connection_str)
        #     store = await stack.enter_async_context(ctx_manager)
        #     await store.setup()
        #     return store
        
        if kind == 'postgres':
            if not self.cfg.connection_str:
                raise ValueError('Postgres store requires a connection string')
                
            ctx_manager = AsyncPostgresStore.from_conn_string(
                self.cfg.connection_str,
                pool_config=PoolConfig(min_size=5, max_size=20)
            )
            store = await stack.enter_async_context(ctx_manager)
            await store.setup()
            return store
            
        else:
            raise ValueError(f"Unsupported store type: {kind}")
