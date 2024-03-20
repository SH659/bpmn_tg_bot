from fastapi import Depends
from injector import Injector, ProviderOf

injector = Injector()


def di(type):
    return Depends(injector.get(ProviderOf[type]).get)
