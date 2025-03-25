from typing import Any, Optional
import orjson
from fastapi import HTTPException, Header, Query, Request
from pydantic import Field
from typing_extensions import Annotated
from . import formats

LIMIT_MAXIMUM = 100000

def get_format_query(
    _f_docs: Annotated[formats.ReturnFormat, Field(
        default=formats.ReturnFormat.get_default(), 
        description="Optional parameter which indicates the output format of the response",
    )] = Query(
        default=formats.ReturnFormat.get_default(), 
        description="Optional parameter which indicates the output format of the response",
        alias="f"
    ),    
    f: Annotated[formats.ReturnFormat, Field(
        default=formats.ReturnFormat.get_default(), 
    )] = Query(
        default=None, 
        include_in_schema=False
    ),
    content_type: Optional[str] = Header(None, alias="accept", include_in_schema=False)
) -> formats.ReturnFormat:
    """Get the format query parameter from the request and validate it."""
    
    if f is not None:
        return f
    
    if content_type and content_type != "*/*":
        if "text/html" in content_type:
            return formats.ReturnFormat.html
        elif "application/json" in content_type or "application/geo+json" in content_type:
            return formats.ReturnFormat.json
        
    return formats.ReturnFormat.get_default()

def validate_limit(limit: Any) -> int:
    """Validate and cap limit parameter to the maximum allowed value."""
    
    if type(limit) == str and limit.isdigit():
        limit = int(limit)
    elif type(limit) != int:
        raise HTTPException(
            status_code=400,
            detail="Input for parameter 'limit' of type 'query' is invalid. Input should be a valid integer, unable to parse string as an integer"
        )
    
    if limit > LIMIT_MAXIMUM:
        return LIMIT_MAXIMUM
    if limit < 1:
        return 1
    return limit

def validate_bbox(bbox_param: Any) -> list[float]:
    """Validate the bbox parameter format and values."""
    
    try:
        if type(bbox_param) == str:
            if bbox_param.startswith("[") and bbox_param.endswith("]"):
                # Convert JSON array string to list
                bbox_param = orjson.loads(bbox_param)
            else:
                # If string input (like "160,10,10,10"), convert to list of floats
                bbox_param = [float(x) for x in bbox_param.split(",")]
        elif type(bbox_param) == list:
            # If input is an actual list, convert to list of floats
            bbox_param = [float(x) for x in bbox_param]
        else:
            raise HTTPException(
                status_code=400,
                detail="Bounding box should be specified as comma-separated numbers"
            )
        
        # Check correct number of coordinates
        if len(bbox_param) != 4 and len(bbox_param) != 6:
            raise HTTPException(
                status_code=400,
                detail="Bounding box should contain 4 or 6 values"
            )
        
        return bbox_param
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Bounding box should be specified as comma-separated numbers"
        )
        
def validate_items_parameters(request: Request):
    allowed_params = {"limit", "offset", "bbox", "bbox-crs", "datetime", "crs", "f"}
    query_params = request.query_params
    unrecognized_params = set(query_params.keys()) - allowed_params
    
    if unrecognized_params:
        raise HTTPException(
            status_code=400,
            detail=f"Unrecognized query parameter(s): {', '.join(unrecognized_params)}"
        )