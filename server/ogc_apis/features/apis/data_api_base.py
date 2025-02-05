# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictFloat, StrictInt, StrictStr
from typing import Any, List, Optional, Union
from typing_extensions import Annotated
from server.ogc_apis.features.models.exception import Exception
from server.ogc_apis.features.models.feature_collection_geo_json import FeatureCollectionGeoJSON
from server.ogc_apis.features.models.feature_geo_json import FeatureGeoJSON


class BaseDataApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseDataApi.subclasses = BaseDataApi.subclasses + (cls,)
    async def get_feature(
        self,
        collectionId: Annotated[StrictStr, Field(description="local identifier of a collection")],
        featureId: Annotated[StrictStr, Field(description="local identifier of a feature")],
    ) -> FeatureGeoJSON:
        """Fetch the feature with id &#x60;featureId&#x60; in the feature collection with id &#x60;collectionId&#x60;.  Use content negotiation to request HTML or GeoJSON."""
        ...


    async def get_features(
        self,
        collectionId: Annotated[StrictStr, Field(description="local identifier of a collection")],
        limit: Annotated[Optional[Annotated[int, Field(le=10000, strict=True, ge=1)]], Field(description="The optional limit parameter limits the number of items that are presented in the response document.  Only items are counted that are on the first level of the collection in the response document. Nested objects contained within the explicitly requested items shall not be counted.  Minimum = 1. Maximum = 10000. Default = 10.")],
        bbox: Annotated[Optional[List[Union[StrictFloat, StrictInt]]], Field(description="Only features that have a geometry that intersects the bounding box are selected. The bounding box is provided as four or six numbers, depending on whether the coordinate reference system includes a vertical axis (height or depth):  * Lower left corner, coordinate axis 1 * Lower left corner, coordinate axis 2 * Minimum value, coordinate axis 3 (optional) * Upper right corner, coordinate axis 1 * Upper right corner, coordinate axis 2 * Maximum value, coordinate axis 3 (optional)  If the value consists of four numbers, the coordinate reference system is WGS 84 longitude/latitude (http://www.opengis.net/def/crs/OGC/1.3/CRS84) unless a different coordinate reference system is specified in the parameter `bbox-crs`.  If the value consists of six numbers, the coordinate reference system is WGS 84 longitude/latitude/ellipsoidal height (http://www.opengis.net/def/crs/OGC/0/CRS84h) unless a different coordinate reference system is specified in the parameter `bbox-crs`.  The query parameter `bbox-crs` is specified in OGC API - Features - Part 2: Coordinate Reference Systems by Reference.  For WGS 84 longitude/latitude the values are in most cases the sequence of minimum longitude, minimum latitude, maximum longitude and maximum latitude. However, in cases where the box spans the antimeridian the first value (west-most box edge) is larger than the third value (east-most box edge).  If the vertical axis is included, the third and the sixth number are the bottom and the top of the 3-dimensional bounding box.  If a feature has multiple spatial geometry properties, it is the decision of the server whether only a single spatial geometry property is used to determine the extent or all relevant geometries.")],
        datetime: Annotated[Optional[StrictStr], Field(description="Either a date-time or an interval. Date and time expressions adhere to RFC 3339. Intervals may be bounded or half-bounded (double-dots at start or end).  Examples:  * A date-time: \"2018-02-12T23:20:50Z\" * A bounded interval: \"2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\" * Half-bounded intervals: \"2018-02-12T00:00:00Z/..\" or \"../2018-03-18T12:31:12Z\"  Only features that have a temporal property that intersects the value of `datetime` are selected.  If a feature has multiple temporal properties, it is the decision of the server whether only a single temporal property is used to determine the extent or all relevant temporal properties.")],
    ) -> FeatureCollectionGeoJSON:
        """Fetch features of the feature collection with id &#x60;collectionId&#x60;.  Every feature in a dataset belongs to a collection. A dataset may consist of multiple feature collections. A feature collection is often a collection of features of a similar type, based on a common schema.  Use content negotiation to request HTML or GeoJSON."""
        ...
