from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.genre import GenreService, get_genre_service

router = APIRouter()


class Genre(BaseModel):
    id: str
    name: str


@router.get('/{genre_id}', response_model=Genre, summary='Получить жанр по id')
async def genre_details(
        genre_id: str,
        genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return Genre(id=genre.id, name=genre.name)


@router.get('/', response_model=list[Genre], summary='Получить все жанры')
async def genre_details(
        genre_service: GenreService = Depends(get_genre_service)
) -> list[Genre]:
    genres = await genre_service.get_all_genres()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return [Genre(id=genre.id, name=genre.name) for genre in genres]



