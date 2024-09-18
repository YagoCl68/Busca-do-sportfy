from typing import List

from pydantic import BaseModel


class Musica(BaseModel):
    link: str


class Musicas(BaseModel):
    musicas: List[Musica]
