from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.persons import PersonService, get_person_service

router = APIRouter()


class Person(BaseModel):
    id: str
    full_name: str
    roles: list[str] = ['']
    film_ids: list[str] = ['']


class FilmShort(BaseModel):
    id: str
    title: str
    imdb_rating: float


@router.get('/', response_model=list[Person])
async def get_all(person_service: PersonService = Depends(get_person_service)) -> list[Person]:
    persons = await person_service.get_all()
    if not persons:
        return []

    return [Person(id=person.id,
                   full_name=person.full_name,
                   roles=person.roles,
                   film_ids=person.film_ids) for person in persons]


@router.get('/search', response_model=list[Person])
async def search_persons(query: str,
                         page_number: int = 1,
                         page_size: int = 50,
                         person_service: PersonService = Depends(get_person_service)) -> list[Person]:
    persons = await person_service.search_persons_by_name(query, page_number, page_size)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons not found')
    return persons


@router.get('/{person_id}', response_model=Person)
async def get_one(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return Person(id=person.id, full_name=person.full_name, roles=person.roles, film_ids=person.film_ids)


@router.get('/{person_id}/film', response_model=list[FilmShort])
async def get_films_by_pid(person_id: str,
                           person_service: PersonService = Depends(get_person_service)) -> list[FilmShort]:
    films = await person_service.get_films_by_person_id(person_id)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return [FilmShort(id=film.id, title=film.title, imdb_rating=film.imdb_rating) for film in films]




