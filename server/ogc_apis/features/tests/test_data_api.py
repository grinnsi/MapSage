# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictFloat, StrictInt, StrictStr  # noqa: F401
from typing import Any, List, Optional, Union  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from server.ogc_apis.features.models.exception import Exception  # noqa: F401
from server.ogc_apis.features.models.feature_collection_geo_json import FeatureCollectionGeoJSON  # noqa: F401
from server.ogc_apis.features.models.feature_geo_json import FeatureGeoJSON  # noqa: F401


def test_get_feature(client: TestClient):
    """Test case for get_feature

    fetch a single feature
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/collections/{collectionId}/items/{featureId}".format(collectionId='collection_id_example', featureId='feature_id_example'),
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


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

