from modelio import BaseModel, _PKey


class User(BaseModel):

    def __init__(self, _id: _PKey) -> None:
        super().__init__(_id)

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, name: str) -> None:
        self.__name = name
