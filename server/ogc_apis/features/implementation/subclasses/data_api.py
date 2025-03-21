import datetime as dt
from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from fastapi import HTTPException, Request
from pydantic import BeforeValidator, Field, StrictFloat, StrictInt, StrictStr
from typing import Any, List, Optional, Union
import sqlmodel
from typing_extensions import Annotated
from server.database import models
from server.ogc_apis.features.apis.data_api_base import BaseDataApi
from server.ogc_apis.features.models.exception import Exception as ogc_Exception
from server.ogc_apis.features.models.feature_collection_geo_json import FeatureCollectionGeoJSON
from server.ogc_apis.features.models.feature_geo_json import FeatureGeoJSON

from server.ogc_apis import ogc_api_config
from server.ogc_apis.features.implementation import dynamic
from server.utils import gdal_utils


class DataApi(BaseDataApi):
    async def get_feature(
        self,
        collectionId: Annotated[StrictStr, Field(description="local identifier of a collection")],
        featureId: Annotated[StrictStr, Field(description="local identifier of a feature")],
        crs: Annotated[Optional[StrictStr], Field(description="The optional `crs` parameter is used to specify the coordinate reference system of the geometries in the response document. The value of the parameter is a URI identifying the coordinate reference system.  If the parameter is omitted, the default coordinate reference system  http://www.opengis.net/def/crs/OGC/1.3/CRS84 for 2D or http://www.opengis.net/def/crs/OGC/0/CRS84h for 3D is used.")],
        format: ogc_api_config.ReturnFormat,
        request: Request,
        session: sqlmodel.Session,
    ) -> FeatureGeoJSON:
        """Fetch the feature with id `featureId` in the feature collection with id `collectionId`.  Use content negotiation to request HTML or GeoJSON."""
        
        collections: list[models.CollectionTable] = dynamic.collection_impl.get_collection_by_id(id=collectionId, session=session)
        if len(collections) == 0:
            raise HTTPException(status_code=404, detail="The requested resource does not exist on the server. For example, a path parameter had an incorrect value.")
        
        collection = collections[0]
        dataset_wrapper = gdal_utils.get_dataset_from_collection_table(collection, session)
        try:
            featureId = int(featureId)
            feature = dynamic.feature_impl.get_feature_by_id(dataset_wrapper, collection.layer_name, featureId)
        except ValueError:
            raise HTTPException(status_code=404, detail="The requested resource does not exist on the server. For example, a path parameter had an incorrect value.")
        
        if crs is None:
            crs = "http://www.opengis.net/def/crs/OGC/1.3/CRS84" if not collection.is_3D else "http://www.opengis.net/def/crs/OGC/0/CRS84h"
        
        if crs not in collection.crs_json:
            raise HTTPException(status_code=400, detail="The requested CRS is not applicable to this collection. List of supported CRSs: " + ", ".join(collection.crs_json))
        
        if crs != collection.storage_crs:
            dynamic.feature_impl.transform_feature(feature, crs)
        
        feature_json = feature.ExportToJson(as_object=True)
        feature_json["links"] = dynamic.feature_impl.generate_feature_links(base_url=request.base_url._url, collection_id=collectionId, feature_id=featureId)
        
        headers = {
            "Content-Crs": "<" + crs + ">",
        }
        if format == ogc_api_config.ReturnFormat.html:
            return ogc_api_config.templates.response("feature.html",
                request=request,
                context={
                    "feature": feature_json,
                    "collection": collection,
                    "crs_wkt": gdal_utils.get_wkt_from_uri(crs),
                },
                headers=headers
            )
            
            # return HTMLResponse(status_code=200, content=html)

        return ogc_api_config.formats.GeoJSONResponse(
            status_code=200,
            content=feature_json, 
            headers=headers,
        )

    async def get_features(
        self,
        collectionId: Annotated[StrictStr, Field(description="local identifier of a collection")],
        limit: Annotated[Optional[Annotated[int, Field(le=ogc_api_config.params.LIMIT_MAXIMUM, ge=1), BeforeValidator(ogc_api_config.params.validate_limit)]], Field(description=f"The optional limit parameter limits the number of items that are presented in the response document.  Only items are counted that are on the first level of the collection in the response document. Nested objects contained within the explicitly requested items shall not be counted.  Minimum = 1. Maximum = {ogc_api_config.params.LIMIT_MAXIMUM}. Default = 100.")],
        offset: Annotated[Optional[Annotated[int, Field(default=0, ge=0)]], Field(description="The optional offset parameter is used to skip the specified number of items in the result set. The offset is applied after the limit parameter. The first element has the index 0.")],
        bbox: Annotated[Optional[Annotated[List[Union[StrictFloat, StrictInt]], BeforeValidator(ogc_api_config.params.validate_bbox)]], Field(description="Only features that have a geometry that intersects the bounding box are selected. The bounding box is provided as four or six numbers, depending on whether the coordinate reference system includes a vertical axis (height or depth):  * Lower left corner, coordinate axis 1 * Lower left corner, coordinate axis 2 * Minimum value, coordinate axis 3 (optional) * Upper right corner, coordinate axis 1 * Upper right corner, coordinate axis 2 * Maximum value, coordinate axis 3 (optional)  If the value consists of four numbers, the coordinate reference system is WGS 84 longitude/latitude (http://www.opengis.net/def/crs/OGC/1.3/CRS84) unless a different coordinate reference system is specified in the parameter `bbox-crs`.  If the value consists of six numbers, the coordinate reference system is WGS 84 longitude/latitude/ellipsoidal height (http://www.opengis.net/def/crs/OGC/0/CRS84h) unless a different coordinate reference system is specified in the parameter `bbox-crs`.  The query parameter `bbox-crs` is specified in OGC API - Features - Part 2: Coordinate Reference Systems by Reference.  For WGS 84 longitude/latitude the values are in most cases the sequence of minimum longitude, minimum latitude, maximum longitude and maximum latitude. However, in cases where the box spans the antimeridian the first value (west-most box edge) is larger than the third value (east-most box edge).  If the vertical axis is included, the third and the sixth number are the bottom and the top of the 3-dimensional bounding box.  If a feature has multiple spatial geometry properties, it is the decision of the server whether only a single spatial geometry property is used to determine the extent or all relevant geometries.")],
        datetime: Annotated[Optional[StrictStr], Field(description="Either a date-time or an interval. Date and time expressions adhere to RFC 3339. Intervals may be bounded or half-bounded (double-dots at start or end).  Examples:  * A date-time: \"2018-02-12T23:20:50Z\" * A bounded interval: \"2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\" * Half-bounded intervals: \"2018-02-12T00:00:00Z/..\" or \"../2018-03-18T12:31:12Z\"  Only features that have a temporal property that intersects the value of `datetime` are selected.  If a feature has multiple temporal properties, it is the decision of the server whether only a single temporal property is used to determine the extent or all relevant temporal properties.")],
        bbox_crs: Annotated[Optional[StrictStr], Field(description="The optional `bbox-crs` parameter is used to specify the coordinate reference system of the bounding box. The value of the parameter is a URI identifying the coordinate reference system.  If the parameter is omitted, the default coordinate reference system http://www.opengis.net/def/crs/OGC/1.3/CRS84 for 2D or http://www.opengis.net/def/crs/OGC/0/CRS84h for 3D is used.")],
        crs: Annotated[Optional[StrictStr], Field(description="The optional `crs` parameter is used to specify the coordinate reference system of the geometries in the response document. The value of the parameter is a URI identifying the coordinate reference system.  If the parameter is omitted, the default coordinate reference system  http://www.opengis.net/def/crs/OGC/1.3/CRS84 for 2D or http://www.opengis.net/def/crs/OGC/0/CRS84h for 3D is used.")],
        format: ogc_api_config.ReturnFormat,
        request: Request,
        session: sqlmodel.Session,
    ) -> FeatureCollectionGeoJSON:
        """Fetch features of the feature collection with id `collectionId`.  Every feature in a dataset belongs to a collection. A dataset may consist of multiple feature collections. A feature collection is often a collection of features of a similar type, based on a common schema.  Use content negotiation to request HTML or GeoJSON."""
        ...
