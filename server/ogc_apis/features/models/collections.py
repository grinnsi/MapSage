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
import pprint
import re  # noqa: F401
import json




from pydantic import BaseModel, ConfigDict, Field, StrictStr
from typing import Any, ClassVar, Dict, List, Optional
from server.ogc_apis.features.models.collection import Collection
from server.ogc_apis.features.models.link import Link
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

class Collections(BaseModel):
    """
    Collections
    """ # noqa: E501
    links: List[Link]
    collections: List[Collection]
    crs: Optional[List[StrictStr]] = Field(default=None, description="a global list of CRS identifiers that are supported by spatial feature collections offered by the service")
    __properties: ClassVar[List[str]] = ["links", "collections", "crs"]

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "protected_namespaces": (),
    }


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        return self.model_dump_json(by_alias=True, exclude_unset=True)

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of Collections from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        _dict = self.model_dump(
            by_alias=True,
            exclude={
            },
            exclude_none=True,
        )
        # override the default output from pydantic by calling `to_dict()` of each item in links (list)
        _items = []
        if self.links:
            for _item in self.links:
                if _item:
                    _items.append(_item.to_dict())
            _dict['links'] = _items
        # override the default output from pydantic by calling `to_dict()` of each item in collections (list)
        _items = []
        if self.collections:
            for _item in self.collections:
                if _item:
                    _items.append(_item.to_dict())
            _dict['collections'] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: Dict) -> Self:
        """Create an instance of Collections from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "links": [Link.from_dict(_item) for _item in obj.get("links")] if obj.get("links") is not None else None,
            "collections": [Collection.from_dict(_item) for _item in obj.get("collections")] if obj.get("collections") is not None else None,
            "crs": obj.get("crs")
        })
        return _obj


