# src/equipamento/domain/entities.py

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional 

class StatusBicicleta(str, Enum):
    DISPONIVEL = "DISPONÍVEL"
    EM_USO = "EM_USO"
    NOVA = "NOVA"
    APOSENTADA = "APOSENTADA"
    REPARO_SOLICITADO = "REPARO_SOLICITADO"
    EM_REPARO = "EM_REPARO"


class StatusTranca(str, Enum):
    DISPONIVEL = "DISPONÍVEL"
    OCUPADA = "OCUPADA"
    NOVA = "NOVA"
    APOSENTADA = "APOSENTADA"
    EM_REPARO = "EM_REPARO"
    REPARO_SOLICITADO = "REPARO_SOLICITADO"

@dataclass 
class Bicicleta:
    marca: str
    modelo: str
    ano: str
    numero: int
    status: StatusBicicleta 
    id: Optional[int] = None
    is_deleted: bool = False

@dataclass
class Tranca:
    numero: int
    localizacao: str
    ano_de_fabricacao: str
    modelo: str
    status: StatusTranca
    id: Optional[int] = None
    bicicleta_id: Optional[int] = None
    totem_id: Optional[int] = None
    is_deleted: bool = False

@dataclass
class Totem:
    localizacao: str
    descricao: str
    id: Optional[int] = None 
    tranca_ids: List[int] = field(default_factory=list)
    is_deleted: bool = False