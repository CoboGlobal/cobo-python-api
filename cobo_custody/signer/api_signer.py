from abc import abstractmethod, ABCMeta


class ApiSigner(metaclass=ABCMeta):

    @abstractmethod
    def sign(self, message: str):
        pass

    @abstractmethod
    def get_public_key(self):
        pass
