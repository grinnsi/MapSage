# coding: utf-8

import mimetypes
from fastapi.testclient import TestClient
from sqlmodel import select
from server.ogc_apis.features.tests import conftest
import httpx


from pydantic import Field, StrictStr  # noqa: F401
from typing import Any  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from server.ogc_apis.features.models.collection import Collection  # noqa: F401
from server.ogc_apis.features.models.collections import Collections  # noqa: F401
from server.ogc_apis.features.models.conf_classes import ConfClasses  # noqa: F401
from server.ogc_apis.features.models.exception import Exception  # noqa: F401
from server.ogc_apis.features.models.landing_page import LandingPage  # noqa: F401
from server.ogc_apis import ogc_api_config
from server.database.db import Database, DatabaseSession
from server.database import models


def test_describe_collection(client: TestClient, headers: httpx.Headers):
    """Test case for describe_collection

    describe the feature collection with id `collectionId`
    """

    headers.update({
        
    })
    
    response = client.request(
       "GET",
       "/collections",
       headers=headers,
    )

    collections_json = response.json()
    collections = collections_json["collections"]
    # Not an official ogc test
    assert collections is not None and len(collections) > 0
    
    for index, collection in enumerate(collections):
        collection_id = collection["id"]
        response = client.request(
            "GET",
            f"/collections/{collection_id}",
            headers=headers,
        )
        
        assert response.status_code == 200
        json = response.json()
        assert json["id"] == collections[index]["id"]
        assert json["title"] == collections[index]["title"]
        assert json["description"] == collections[index]["description"]
        assert json["extent"] == collections[index]["extent"]
        assert json["itemType"] == collections[index]["itemType"]
        assert json["storageCrs"] == collections[index]["storageCrs"]
        assert json["storageCrsCoordinateEpoch"] == collections[index]["storageCrsCoordinateEpoch"]
        assert all(crs in collections[index]["crs"] or crs in collections_json["crs"] for crs in json["crs"])
        
        assert Collection.model_validate(json)
        
        # Test different formats
        conftest.formats("GET", f"/collections/{collection_id}", headers, client)

def test_get_collections(client: TestClient, headers: httpx.Headers):
    """Test case for get_collections

    the feature collections in the dataset
    """

    headers.update({
        
    })

    response = client.request(
        "GET",
        "/collections",
        headers=headers,
    )

    assert response.status_code == 200
    json = response.json()
    assert "http://www.opengis.net/def/crs/OGC/1.3/CRS84" in json["crs"]
    
    # check links
    links = json["links"]
    assert all("rel" in link and "type" in link for link in links)
    rels = [link["rel"] for link in links]
    assert any(rel == "self" for rel in rels)
    assert len(list(filter(lambda rel: rel == "alternate", rels))) == len(ogc_api_config.formats.ReturnFormat.get_all()) - 1
    
    # check items
    assert json["collections"] is not None
    collections = json["collections"]
    with DatabaseSession() as session:
        assert len(collections) == len(session.exec(select(models.CollectionTable)).all())
        for collection in collections:
            assert "id" in collection
            
            links = collection["links"]
            # Verify that each Collection item in the Collections Metadata document includes a link property for each supported encoding.?????
            assert len(links) % len(ogc_api_config.ReturnFormat.get_all()) == 0
            items_links = [link for link in links if link["rel"] == "items"]
            types = [mimetypes.types_map["." + _format] for _format in ogc_api_config.formats.ReturnFormat.get_all()]
            assert all([link["type"] in types or link["type"] == "application/geo+json" for link in items_links])
            
            assert "extent" in collection
            extent = collection["extent"]
            assert "spatial" in extent and "bbox" in extent["spatial"] and len(extent["spatial"]["bbox"][0]) >= 4
            db_collection: models.CollectionTable = session.exec(select(models.CollectionTable).where(models.CollectionTable.id == collection["id"])).first()
            if db_collection.date_time_field is not None:
                assert "temporal" in extent
    
    assert Collections.model_validate(json)
    # Test different formats
    conftest.formats("GET", "/collections", headers, client)
            
def test_get_conformance_declaration(client: TestClient, headers: httpx.Headers):
    """Test case for get_conformance_declaration

    information about specifications that this API conforms to
    """

    headers.update({
        
    })

    response = client.request(
       "GET",
       "/conformance",
       headers=headers,
    )

    assert response.status_code == 200
    json = response.json()
    assert ConfClasses.model_validate(json)
    assert "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core" in json["conformsTo"]


def test_get_landing_page(client: TestClient, headers: httpx.Headers):
    """Test case for get_landing_page

    landing page
    """

    headers.update({
        
    })
    
    response = client.request(
       "GET",
       "/",
       headers=headers,
    )

    assert response.status_code == 200
    json = response.json()
    assert json is not None
    assert LandingPage.model_validate(json)
    links = json.get('links')
    
    rels = [link.get('rel') for link in links]
    assert 'service-desc' in rels
    assert 'service-doc' in rels
    assert 'conformance' in rels
    assert 'data' in rels
    assert 'self' in rels
    
    # Test different formats
    conftest.formats("GET", "/", headers, client)

def test_get_api(client: TestClient, headers: httpx.Headers):
    """Test case for get_api in both formats

    api page
    """
    
    headers.update({
        
    })
    
    conftest.formats("GET", ogc_api_config.routes.API, headers)    