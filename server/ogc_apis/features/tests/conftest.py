import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
import httpx
import mimetypes

from server.ogc_apis.features.main import init_api_server
from server.ogc_apis import ogc_api_config
from server.database.db import Database

Database.init_sqlite_db(False)

@pytest.fixture(scope="session")
def app() -> FastAPI:
    application = init_api_server()
    application.dependency_overrides = {}

    return application

@pytest.fixture(scope="session")
def client(app) -> TestClient:
    return TestClient(app)

@pytest.fixture(scope="session")
def headers() -> httpx.Headers:
    return {
    }

def formats(operation: str, rel_url: str, headers: httpx.Headers, test_client: TestClient = None, data: str = None) -> None:
    for _format in ogc_api_config.formats.ReturnFormat.get_all():
        url = f"{rel_url}{"&" if "?" in rel_url else "?"}f={_format}"
        
        if _format == "json":
            _format = "geojson"
        
        headers.update({
            "Accept": mimetypes.types_map["." + _format]
        })
        
        response: httpx.Response = test_client.request(
            method=operation,
            url=url,
            headers=headers,
            data=data
        )
        
        assert response.status_code == 200  