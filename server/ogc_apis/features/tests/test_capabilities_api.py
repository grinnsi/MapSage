# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictStr  # noqa: F401
from typing import Any  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from server.ogc_apis.features.models.collection import Collection  # noqa: F401
from server.ogc_apis.features.models.collections import Collections  # noqa: F401
from server.ogc_apis.features.models.conf_classes import ConfClasses  # noqa: F401
from server.ogc_apis.features.models.exception import Exception  # noqa: F401
from server.ogc_apis.features.models.landing_page import LandingPage  # noqa: F401


def test_describe_collection(client: TestClient):
    """Test case for describe_collection

    describe the feature collection with id `collectionId`
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/collections/{collectionId}".format(collectionId='collection_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_get_collections(client: TestClient):
    """Test case for get_collections

    the feature collections in the dataset
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/collections",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_get_conformance_declaration(client: TestClient):
    """Test case for get_conformance_declaration

    information about specifications that this API conforms to
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/conformance",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_get_landing_page(client: TestClient):
    """Test case for get_landing_page

    landing page
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

