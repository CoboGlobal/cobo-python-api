from abc import abstractmethod, ABCMeta


class ApiSigner(metaclass=ABCMeta):

    @abstractmethod
    def sign(self, message):
        pass
