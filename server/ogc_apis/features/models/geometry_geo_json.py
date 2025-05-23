# coding: utf-8

"""
    Building Blocks specified in the OGC API - Features - Part 1 and Part 2: Core and CRS standard

    Common components used in the [OGC API - Features - Part 1: Core corrigendum standard](https://docs.ogc.org/is/17-069r4/17-069r4.html) and [OGC API - Features - Part 2: Coordinate Reference Systems by Reference corrigendum](https://docs.ogc.org/is/18-058r1/18-058r1.html).    OGC API - Features - Part 1: Core corrigendum 1.0.1 is an OGC Standard.   Copyright (c) 2022 Open Geospatial Consortium.   To obtain additional rights of use, visit http://www.opengeospatial.org/legal/ .    OGC API - Features - Part 2: Reference corrigendum 1.0.1 is an OGC Standard.   Copyright (c) 2022 Open Geospatial Consortium.   To obtain additional rights of use, visit http://www.opengeospatial.org/legal/ .    This is an informative document. The building blocks in this document are also available on the OGC schema repository.   [OGC API - Features - Part 1: Core schema](http://schemas.opengis.net/ogcapi/features/part1/1.0/openapi/ogcapi-features-1.yaml)   [OGC API - Features - Part 2: Coordinate Reference Systems schema](https://schemas.opengis.net/ogcapi/features/part2/1.0/openapi/ogcapi-features-2.yaml)  

    The version of the OpenAPI document: 1.0.1
    Contact: standards-team@ogc.org
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
from inspect import getfullargspec
import json
import pprint
import re  # noqa: F401



from pydantic import BaseModel, ConfigDict, Field, StrictStr, ValidationError, field_validator
from typing import Any, List, Optional
from server.ogc_apis.features.models.linestring_geo_json import LinestringGeoJSON
from server.ogc_apis.features.models.multilinestring_geo_json import MultilinestringGeoJSON
from server.ogc_apis.features.models.multipoint_geo_json import MultipointGeoJSON
from server.ogc_apis.features.models.multipolygon_geo_json import MultipolygonGeoJSON
from server.ogc_apis.features.models.point_geo_json import PointGeoJSON
from server.ogc_apis.features.models.polygon_geo_json import PolygonGeoJSON
from typing import Union, Any, List, TYPE_CHECKING, Optional, Dict
from typing_extensions import Literal
from pydantic import StrictStr, Field
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

GEOMETRYGEOJSON_ONE_OF_SCHEMAS = ["GeometrycollectionGeoJSON", "LinestringGeoJSON", "MultilinestringGeoJSON", "MultipointGeoJSON", "MultipolygonGeoJSON", "PointGeoJSON", "PolygonGeoJSON"]

class GeometryGeoJSON(BaseModel):
    """
    GeometryGeoJSON
    """
    # data type: PointGeoJSON
    oneof_schema_1_validator: Optional[PointGeoJSON] = None
    # data type: MultipointGeoJSON
    oneof_schema_2_validator: Optional[MultipointGeoJSON] = None
    # data type: LinestringGeoJSON
    oneof_schema_3_validator: Optional[LinestringGeoJSON] = None
    # data type: MultilinestringGeoJSON
    oneof_schema_4_validator: Optional[MultilinestringGeoJSON] = None
    # data type: PolygonGeoJSON
    oneof_schema_5_validator: Optional[PolygonGeoJSON] = None
    # data type: MultipolygonGeoJSON
    oneof_schema_6_validator: Optional[MultipolygonGeoJSON] = None
    # data type: GeometrycollectionGeoJSON
    oneof_schema_7_validator: Optional[GeometrycollectionGeoJSON] = None
    actual_instance: Optional[Union[GeometrycollectionGeoJSON, LinestringGeoJSON, MultilinestringGeoJSON, MultipointGeoJSON, MultipolygonGeoJSON, PointGeoJSON, PolygonGeoJSON]] = None
    one_of_schemas: List[str] = Literal["GeometrycollectionGeoJSON", "LinestringGeoJSON", "MultilinestringGeoJSON", "MultipointGeoJSON", "MultipolygonGeoJSON", "PointGeoJSON", "PolygonGeoJSON"]

    model_config = {
        "validate_assignment": True,
        "protected_namespaces": (),
    }


    def __init__(self, *args, **kwargs) -> None:
        if args:
            if len(args) > 1:
                raise ValueError("If a position argument is used, only 1 is allowed to set `actual_instance`")
            if kwargs:
                raise ValueError("If a position argument is used, keyword arguments cannot be used.")
            super().__init__(actual_instance=args[0])
        else:
            super().__init__(**kwargs)

    @field_validator('actual_instance')
    def actual_instance_must_validate_oneof(cls, v):
        instance = GeometryGeoJSON.model_construct()
        error_messages = []
        match = 0
        # validate data type: PointGeoJSON
        if not isinstance(v, PointGeoJSON):
            error_messages.append(f"Error! Input type `{type(v)}` is not `PointGeoJSON`")
        else:
            match += 1
        # validate data type: MultipointGeoJSON
        if not isinstance(v, MultipointGeoJSON):
            error_messages.append(f"Error! Input type `{type(v)}` is not `MultipointGeoJSON`")
        else:
            match += 1
        # validate data type: LinestringGeoJSON
        if not isinstance(v, LinestringGeoJSON):
            error_messages.append(f"Error! Input type `{type(v)}` is not `LinestringGeoJSON`")
        else:
            match += 1
        # validate data type: MultilinestringGeoJSON
        if not isinstance(v, MultilinestringGeoJSON):
            error_messages.append(f"Error! Input type `{type(v)}` is not `MultilinestringGeoJSON`")
        else:
            match += 1
        # validate data type: PolygonGeoJSON
        if not isinstance(v, PolygonGeoJSON):
            error_messages.append(f"Error! Input type `{type(v)}` is not `PolygonGeoJSON`")
        else:
            match += 1
        # validate data type: MultipolygonGeoJSON
        if not isinstance(v, MultipolygonGeoJSON):
            error_messages.append(f"Error! Input type `{type(v)}` is not `MultipolygonGeoJSON`")
        else:
            match += 1
        # validate data type: GeometrycollectionGeoJSON
        if not isinstance(v, GeometrycollectionGeoJSON):
            error_messages.append(f"Error! Input type `{type(v)}` is not `GeometrycollectionGeoJSON`")
        else:
            match += 1
        if match > 1:
            # more than 1 match
            raise ValueError("Multiple matches found when setting `actual_instance` in GeometryGeoJSON with oneOf schemas: GeometrycollectionGeoJSON, LinestringGeoJSON, MultilinestringGeoJSON, MultipointGeoJSON, MultipolygonGeoJSON, PointGeoJSON, PolygonGeoJSON. Details: " + ", ".join(error_messages))
        elif match == 0:
            # no match
            raise ValueError("No match found when setting `actual_instance` in GeometryGeoJSON with oneOf schemas: GeometrycollectionGeoJSON, LinestringGeoJSON, MultilinestringGeoJSON, MultipointGeoJSON, MultipolygonGeoJSON, PointGeoJSON, PolygonGeoJSON. Details: " + ", ".join(error_messages))
        else:
            return v

    @classmethod
    def from_dict(cls, obj: dict) -> Self:
        return cls.from_json(json.dumps(obj))

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Returns the object represented by the json string"""
        instance = cls.model_construct()
        error_messages = []
        match = 0

        # deserialize data into PointGeoJSON
        try:
            instance.actual_instance = PointGeoJSON.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into MultipointGeoJSON
        try:
            instance.actual_instance = MultipointGeoJSON.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into LinestringGeoJSON
        try:
            instance.actual_instance = LinestringGeoJSON.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into MultilinestringGeoJSON
        try:
            instance.actual_instance = MultilinestringGeoJSON.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into PolygonGeoJSON
        try:
            instance.actual_instance = PolygonGeoJSON.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into MultipolygonGeoJSON
        try:
            instance.actual_instance = MultipolygonGeoJSON.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into GeometrycollectionGeoJSON
        try:
            instance.actual_instance = GeometrycollectionGeoJSON.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))

        if match > 1:
            # more than 1 match
            raise ValueError("Multiple matches found when deserializing the JSON string into GeometryGeoJSON with oneOf schemas: GeometrycollectionGeoJSON, LinestringGeoJSON, MultilinestringGeoJSON, MultipointGeoJSON, MultipolygonGeoJSON, PointGeoJSON, PolygonGeoJSON. Details: " + ", ".join(error_messages))
        elif match == 0:
            # no match
            raise ValueError("No match found when deserializing the JSON string into GeometryGeoJSON with oneOf schemas: GeometrycollectionGeoJSON, LinestringGeoJSON, MultilinestringGeoJSON, MultipointGeoJSON, MultipolygonGeoJSON, PointGeoJSON, PolygonGeoJSON. Details: " + ", ".join(error_messages))
        else:
            return instance

    def to_json(self) -> str:
        """Returns the JSON representation of the actual instance"""
        if self.actual_instance is None:
            return "null"

        to_json = getattr(self.actual_instance, "to_json", None)
        if callable(to_json):
            return self.actual_instance.to_json()
        else:
            return json.dumps(self.actual_instance)

    def to_dict(self) -> Dict:
        """Returns the dict representation of the actual instance"""
        if self.actual_instance is None:
            return None

        to_dict = getattr(self.actual_instance, "to_dict", None)
        if callable(to_dict):
            return self.actual_instance.to_dict()
        else:
            # primitive type
            return self.actual_instance

    def to_str(self) -> str:
        """Returns the string representation of the actual instance"""
        return pprint.pformat(self.model_dump())

from server.ogc_apis.features.models.geometrycollection_geo_json import GeometrycollectionGeoJSON
GeometryGeoJSON.model_rebuild(raise_errors=False)

