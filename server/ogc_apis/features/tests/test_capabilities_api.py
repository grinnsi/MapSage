# coding: utf-8

from fastapi.testclient import TestClient
from . import conftest
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


def test_describe_collection(client: TestClient, headers: httpx.Headers):
    """Test case for describe_collection

    describe the feature collection with id `collectionId`
    """

    headers.update({
        
    })
    # uncomment below to make a request
    response = client.request(
       "GET",
       "/collections/{collectionId}".format(collectionId='collection_id_example'),
       headers=headers,
    )

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


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
    assert "http://www.opengis.net/def/crs/OGC/1.3/CRS84" in json["crs"][0]
    
    # check links
    links = json["links"]
    assert all("rel" in link and "type" in link for link in links)
    rels = [link["rel"] for link in links]
    assert any(rel == "self" for rel in rels)
    assert len(filter(lambda rel: rel == "alternate", rels)) == len(ogc_api_config.formats.ReturnFormat.get_all() - 1)
    
    # check items
    assert json["collections"] is not None
    collections = json["collections"]
    assert all()

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
    assert ConfClasses.model_validate_json(json)
    assert "http://www.opengis.net/spec/ogcapi-features-1/1.1/conf/core" in json["conformsTo"]


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
    assert LandingPage.model_validate_json(json)
    links = json.get('links')
    
    rels = [link.get('rel') for link in links]
    assert 'service-desc' in rels
    assert 'service-doc' in rels
    assert 'conformance' in rels
    assert 'data' in rels
    assert 'self' in rels
    
    # Test different formats
    conftest.formats("GET", "/", headers)

def test_get_api(client: TestClient, headers: httpx.Headers):
    """Test case for get_api in both formats

    api page
    """
    
    headers.update({
        
    })
    
    conftest.formats("GET", ogc_api_config.routes.API, headers)    