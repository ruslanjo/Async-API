from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from core.errors_text import http_errors
from services.genre import GenreService, get_genre_service
from .models import Genre

router = APIRouter()


@router.get('/{genre_id}', response_model=Genre, summary='Get genre by UUID')
async def genre_details(
        genre_id: str,
        genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=http_errors.get('genre_not_found'))
    return Genre(id=genre.id, name=genre.name)


@router.get('/', response_model=list[Genre], summary='Get all genres from DB')
async def genre_details(
        genre_service: GenreService = Depends(get_genre_service)
) -> list[Genre]:
    genres = await genre_service.get_all_genres()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=http_errors.get('genres_not_found'))
    return [Genre(id=genre.id, name=genre.name) for genre in genres]



