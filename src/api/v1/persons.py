from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query

from core.errors_text import http_errors
from .models import FilmShortModel, Person
from services.persons import PersonService, get_person_service

router = APIRouter()


@router.get('/', response_model=list[Person], summary='Get all persons paginated')
async def get_all(person_service: PersonService = Depends(get_person_service),
                  page_size: int = Query(50, alias="page[size]", gt=0),
                  page_number: int = Query(1, alias="page[number]", gt=0)) -> list[Person]:
    _from = (page_number - 1) * page_size
    persons = await person_service.get_all(_from, page_size)
    if not persons:
        return []

    return [Person(id=person.id,
                   full_name=person.full_name,
                   roles=person.roles,
                   film_ids=person.film_ids) for person in persons]


@router.get('/search', response_model=list[Person], summary='Search in persons data by text field')
async def search_persons(query: str,
                         page_size: int = Query(50, alias="page[size]", gt=0),
                         page_number: int = Query(1, alias="page[number]", gt=0),
                         person_service: PersonService = Depends(get_person_service)) -> list[Person]:
    _from = (page_number - 1) * page_size
    persons = await person_service.search_persons_by_name(query, _from, page_size)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=http_errors.get('persons_not_found'))
    return persons


@router.get('/{person_id}', response_model=Person, summary='Get person by UUID')
async def get_one(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=http_errors.get('person_not_found'))
    return Person(id=person.id, full_name=person.full_name, roles=person.roles, film_ids=person.film_ids)


@router.get('/{person_id}/film', response_model=list[FilmShortModel],
            summary='Get all films, in which person took place')
async def get_films_by_pid(person_id: str,
                           page_size: int = Query(50, alias="page[size]", gt=0),
                           page_number: int = Query(1, alias="page[number]", gt=0),
                           person_service: PersonService = Depends(get_person_service)) -> list[FilmShortModel]:
    _from = (page_number - 1) * page_size

    films = await person_service.get_films_by_person_id(person_id, _from, page_size)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=http_errors.get('films_not_found'))
    return [FilmShortModel(id=film.id, title=film.title, imdb_rating=film.imdb_rating) for film in films]




