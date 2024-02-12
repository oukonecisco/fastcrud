import abc


class BaseStorage(abc.ABC):
    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def get(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def create(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def update(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def replace(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def delete(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def find(self, *args, **kwargs):
        ...
