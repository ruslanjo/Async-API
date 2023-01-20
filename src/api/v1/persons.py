from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.film import FilmService, get_film_service
from services.persons import PersonService, get_person_service

router = APIRouter()


class Person(BaseModel):
    id: str
    full_name: str


@router.get('/{person_id}', response_model=Person)
async def get_one(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return Person(id=person.id, full_name=person.full_name)


@router.get('/', response_model=list[Person])
async def get_all(person_service: PersonService = Depends(get_person_service)) -> list[Person]:
    persons = await person_service.get_all()
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='no persons in index')
    return [Person(id=person.id, full_name=person.full_name) for person in persons]




