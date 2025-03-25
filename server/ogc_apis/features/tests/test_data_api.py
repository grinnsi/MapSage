# coding: utf-8

from fastapi.testclient import TestClient


import httpx
from pydantic import Field, StrictFloat, StrictInt, StrictStr  # noqa: F401
from typing import Any, List, Optional, Union  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from server.ogc_apis.features.models.exception import Exception  # noqa: F401
from server.ogc_apis.features.models.feature_collection_geo_json import FeatureCollectionGeoJSON  # noqa: F401
from server.ogc_apis.features.models.feature_geo_json import FeatureGeoJSON  # noqa: F401

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
        
        conftest.formats("GET", f"/collections/{collectionId}/items/{item['id']}", headers, client)


def test_get_features(client: TestClient):
    """Test case for get_features

    fetch features
    """
    params = [("limit", 10),     ("bbox", [3.4]),     ("datetime", 'datetime_example')]
    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/collections/{collectionId}/items".format(collectionId='collection_id_example'),
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

