import abc


class BaseStorage(abc.ABC):
    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        ...

    @property
    @abc.abstractmethod
    def db(self):
        ...

    @abc.abstractmethod
    def get(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def put(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def patch(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def create(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def delete(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def get_many(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def put_many(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def patch_many(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def delete_many(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def start(self, *args, **kwargs):
        ...

    @abc.abstractmethod
    def stop(self, *args, **kwargs):
        ...
