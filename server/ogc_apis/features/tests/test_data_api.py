# coding: utf-8

from fastapi.testclient import TestClient


import httpx, datetime
from pydantic import Field, StrictFloat, StrictInt, StrictStr  # noqa: F401
from typing import Any, List, Optional, Union  # noqa: F401
from sqlmodel import select
from typing_extensions import Annotated  # noqa: F401
from server.database import models
from server.ogc_apis.features.models.exception import Exception  # noqa: F401
from server.ogc_apis.features.models.feature_collection_geo_json import FeatureCollectionGeoJSON  # noqa: F401
from server.ogc_apis.features.models.feature_geo_json import FeatureGeoJSON  # noqa: F401

from server.database.db import DatabaseSession
from server.ogc_apis import ogc_api_config
from server.ogc_apis.features.tests import conftest

def test_get_feature(client: TestClient, headers: httpx.Headers):
    """Test case for get_feature

    fetch a single feature
    """

    headers.update({
    })
    
    collectionId = "hausumringe"
    
    response = client.request(
       "GET",
       f"/collections/{collectionId}/items/",
       headers=headers,
    )
    
    items_json = response.json()
    items = items_json["features"]
    for item in items:
        response = client.request(
            "GET",
            f"/collections/{collectionId}/items/{item['id']}",
            headers=headers,
        )

        assert response.status_code == 200
        item_json = response.json()
        links = item_json["links"]
        # Link 1: self
        assert any(link["rel"] == "self" for link in links)
        # Link 3: collection
        assert any(link["rel"] == "collection" for link in links)
        
        alternates = 0
        for link in links:
            if link["rel"] == "self":
                assert link["href"] == f"http://testserver{ogc_api_config.routes.FEATURES}/collections/{collectionId}/items/{item['id']}?f=json"
            if link["rel"] == "alternate":
                alternates += 1
            if link["rel"] == "collection":
                assert f"http://testserver{ogc_api_config.routes.FEATURES}/collections/{collectionId}" in link["href"]
        
        # Link 2: alternate
        assert alternates == len(ogc_api_config.formats.ReturnFormat.get_all()) - 1
        # Link 4: rel and type
        assert all("rel" in link and "type" in link for link in links)
        assert FeatureGeoJSON.from_dict(item_json)
        conftest.formats("GET", f"/collections/{collectionId}/items/{item['id']}", headers, client)

def help_get_features(response: httpx.Response, collection_id: str, correct_match: int, limit: int):
    assert response.status_code == 200
    feature_collection_json = response.json()
    feature_collection_model = FeatureCollectionGeoJSON.from_dict(feature_collection_json)
    assert feature_collection_model is not None
    assert feature_collection_model.type == "FeatureCollection"
    assert feature_collection_model.features and len(feature_collection_model.features) > 0
    
    links = feature_collection_json["links"]
    # Link 1: self
    assert any(link["rel"] == "self" for link in links)
    alternates = 0
    for link in links:
        if link["rel"] == "self":
            # Check without features route because the url is constructed in a different way
            assert f"http://testserver/collections/{collection_id}/items" in link["href"]
        if link["rel"] == "alternate":
            alternates += 1
    
    # Link 2: alternate
    assert alternates == len(ogc_api_config.formats.ReturnFormat.get_all()) - 1
    # Link 3: rel and type
    assert all("rel" in link and "type" in link for link in links)
    
    assert feature_collection_model.time_stamp
    assert feature_collection_model.number_matched 
    assert feature_collection_model.number_matched == correct_match
    
    correct_return = min(limit, correct_match, ogc_api_config.params.LIMIT_MAXIMUM)
    
    assert feature_collection_model.number_returned
    assert feature_collection_model.number_returned == correct_return
    assert feature_collection_model.features 
    assert len(feature_collection_model.features) <= limit and len(feature_collection_model.features) <= ogc_api_config.params.LIMIT_MAXIMUM
    assert len(feature_collection_model.features) == correct_return
    
def test_get_features(client: TestClient, headers: httpx.Headers):
    """Test case for get_features

    fetch features
    """
    
    headers.update({
    })
    
    test_collections = {
        "hausumringe": {
            "total": 1_738_310,
            "bbox": 789,
            "limit": 100_000,
        },
        "verwaltungsgrenzen": {
            "total": 237, # 4 with NULL geometry
            "bbox": 7,    # 4 with NULL geometry
            "limit": 237, # 4 with NULL geometry
            "datetime": 144,
        },
    }
    
    with DatabaseSession() as session:
        collections = session.exec(select(models.CollectionTable)).all()
        assert collections
        
        for collection in collections:
            if collection.id not in test_collections:
                continue
            
            # Main Test
            response = client.request(
                "GET",
                f"/collections/{collection.id}/items",
                headers=headers,
            )

            help_get_features(response, collection.id, test_collections[collection.id]["total"], 100)
            conftest.formats("GET", f"/collections/{collection.id}/items", headers, client)
            
            # BBOX test
            response = client.request(
                "GET",
                f"/collections/{collection.id}/items",
                headers=headers,
                params=[("bbox", [11.646199,52.089114,11.657634,52.096041])],
            )
            
            help_get_features(response, collection.id, test_collections[collection.id]["bbox"], 100)
            conftest.formats("GET", f"/collections/{collection.id}/items?bbox=11.646199,52.089114,11.657634,52.096041", headers, client)
            
            # Limit test 1
            response = client.request(
                "GET",
                f"/collections/{collection.id}/items",
                headers=headers,
                params=[("limit", 10_000)],
            )
            
            help_get_features(response, collection.id, test_collections[collection.id]["total"], 10_000)
            conftest.formats("GET", f"/collections/{collection.id}/items?limit=10000", headers, client)
            
            # Limit test 2
            response = client.request(
                "GET",
                f"/collections/{collection.id}/items",
                headers=headers,
                params=[("limit", 1_000_000)],
            )
            
            help_get_features(response, collection.id, test_collections[collection.id]["total"], 1_000_000)
            conftest.formats("GET", f"/collections/{collection.id}/items?limit=1000000", headers, client)
            
            # Datetime test
            if "datetime" in test_collections[collection.id]:
                response = client.request(
                    "GET",
                    f"/collections/{collection.id}/items",
                    headers=headers,
                    params=[("datetime", "2024-06-20T00:00:00/2024-06-30T00:00:00")],
                )
                
                help_get_features(response, collection.id, test_collections[collection.id]["datetime"], 100)
                conftest.formats("GET", f"/collections/{collection.id}/items?datetime=2024-06-20T00:00:00/2024-06-30T00:00:00", headers, client)
            
            # Invalid query parameter
            response = client.request(
                "GET",
                f"/collections/{collection.id}/items",
                headers=headers,
                params=[("bbox", [10, 20, 100])],
            )
            
            assert response.status_code == 400
            
            # Unknown query parameter
            response = client.request(
                "GET",
                f"/collections/{collection.id}/items",
                headers=headers,
                params=[("amount", "get_all")],
            )
            
            assert response.status_code == 400