from fastapi import Query
from pydantic import Field
from typing_extensions import Annotated
from . import formats


def get_format_query(f: Annotated[formats.ReturnFormat, Field(
        default=formats.ReturnFormat.get_default(), 
        description="Optional parameter which indicates the output format of the response"
    )] = Query(
        default=formats.ReturnFormat.get_default(), 
        description="Optional parameter which indicates the output format of the response"
    )) -> None:
    return f