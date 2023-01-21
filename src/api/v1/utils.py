from pydantic import BaseModel, validator
from fastapi import Query


class FilterGenre(BaseModel):
    filter_genre: str = Query(default='')


class Paginator(BaseModel):
    page_size: int = Query(default=50, alias='size')
    page_number: int = Query(default=1, alias='number')

    @validator('page_number')
    def page_number_is_valid(cls, page_number):
        if page_number < 1:
            page_number = 1
        return page_number


async def sort_type(sorting_type):
    sort_types = {
        '+imbd_rating': [
            {
                "imdb_rating": {
                    "order": "asc"
                }
            }
        ],
        '-imbd_rating': [
            {
                "imdb_rating": {
                    "order": "desc"
                }
            }
        ]
    }
    return sort_types.get(sorting_type)