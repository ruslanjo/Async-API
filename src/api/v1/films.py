from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query

from services.film import FilmService, get_film_service
from .utils import sort_type, Paginator, FilterGenre
from .models import Film, FilmShortModel

router = APIRouter()


@router.get('', response_model=list[FilmShortModel])
async def get_films(
        sort: str = Query(default='-imbd_rating'),
        paginator: Paginator = Depends(),
        film_service: FilmService = Depends(get_film_service),
        filter_genre: FilterGenre = Depends(),
) -> list[FilmShortModel]:

    _from = (paginator.page_number - 1) * paginator.page_size
    films = await film_service.get_films(
        _from=_from,
        size=paginator.page_size,
        filter_genre=filter_genre,
        sort=await sort_type(
            sorting_type=sort
        )
    )
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='films not found'
        )

    return [
        FilmShortModel(
            id=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating
        )
        for film in films
    ]


@router.get('/search', response_model=list[FilmShortModel])
async def film_search(
        query: str,
        paginator: Paginator = Depends(),
        film_service: FilmService = Depends(get_film_service)
) -> list[FilmShortModel]:

    _from = (paginator.page_number - 1) * paginator.page_size
    films = await film_service.search_films(
        query=query,
        _from=_from,
        size=paginator.page_size,
    )
    if not films:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='films not found'
        )

    return [
        FilmShortModel(
            id=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating
        )
        for film in films]


@router.get('/{film_id}', response_model=Film)
async def film_details(
        film_id: str,
        film_service: FilmService = Depends(get_film_service)
) -> Film:

    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='film not found'
        )

    return Film(
        id=film.id,
        title=film.title,
        description=film.description,
        genre=film.genre,
        directors=film.directors,
        writers=film.writers,
        actors=film.actors,
        writers_names=film.writers_names,
        directors_names=film.directors_names,
        actors_names=film.actors_names,
    )
