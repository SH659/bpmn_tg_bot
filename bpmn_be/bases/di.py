from typing import Type, TypeVar

from fastapi import Depends
from injector import Injector, ProviderOf

injector = Injector()
T = TypeVar('T')


def di(type: Type[T]) -> T:
    return Depends(injector.get(ProviderOf[type]).get)
