import logging
from typing import TypeAlias, TypeVar

from gql.client import AsyncClientSession
from gql.client import Client as GraphQLClient
from gql.client import SyncClientSession
from gql.transport import AsyncTransport, Transport

from .config import Config, ConnectParams
from .context import ResourceManager, SyncResourceManager
from .transport.httpx import HTTPXAsyncTransport, HTTPXTransport

logger = logging.getLogger(__name__)


_T = TypeVar("_T")


ClientSession: TypeAlias = AsyncClientSession | SyncClientSession


class Session(ResourceManager, SyncResourceManager):
    """Establishes a GraphQL client connection to the engine."""

    def __init__(self, conn: ConnectParams, cfg: Config):
        super().__init__()
        self.conn = conn
        self.cfg = cfg

    def make_transport(self) -> AsyncTransport:
        return self._make_transport(HTTPXAsyncTransport)

    def make_sync_transport(self) -> Transport:
        return self._make_transport(HTTPXTransport)

    def _make_transport(self, cls: type[_T]) -> _T:
        return cls(
            self.conn.host.copy_with(path="/query"),
            timeout=self.cfg.execute_timeout,
            auth=(self.conn.session_token, ""),
        )

    def make_graphql_client(
        self, transport: AsyncTransport | Transport
    ) -> GraphQLClient:
        return GraphQLClient(
            transport=transport,
            fetch_schema_from_transport=True,
            execute_timeout=self.cfg.execute_timeout,
        )

    async def __aenter__(self) -> AsyncClientSession:
        transport = self.make_transport()
        client = self.make_graphql_client(transport)

        async with self.get_stack() as stack:
            # FIXME: handle errors from establishing session
            # FIXME: handle cancellation, retries and timeout (self.cfg.timeout)
            session = await stack.enter_async_context(client)

        return session

    def __enter__(self) -> SyncClientSession:
        transport = self.make_sync_transport()
        client = self.make_graphql_client(transport)

        with self.get_sync_stack() as stack:
            # FIXME: handle errors from establishing session
            # FIXME: handle cancellation, retries and timeout (self.cfg.timeout)
            session = stack.enter_context(client)

        return session