from pydantic import BaseModel
from fastapi import Query


class FilterGenre(BaseModel):
    filter_genre: str = Query(default='')


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