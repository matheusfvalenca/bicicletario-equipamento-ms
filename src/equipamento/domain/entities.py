# src/equipamento/domain/entities.py

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

# Usamos Enums para garantir que os status sejam sempre valores válidos.
# Isso evita erros de digitação e torna o código mais legível.

class StatusBicicleta(str, Enum):
    DISPONIVEL = "DISPONÍVEL"
    EM_USO = "EM_USO"
    NOVA = "NOVA"
    APOSENTADA = "APOSENTADA"
    REPARO_SOLICITADO = "REPARO_SOLICITADO"
    EM_REPARO = "EM_REPARO"


class StatusTranca(str, Enum):
    LIVRE = "LIVRE"
    OCUPADA = "OCUPADA"
    NOVA = "NOVA"
    APOSENTADA = "APOSENTADA"
    EM_REPARO = "EM_REPARO"

# O decorador @dataclass cria automaticamente métodos como __init__, __repr__, etc.
# Isso nos ajuda a escrever classes de dados concisas.

@dataclass
class Bicicleta:
    marca: str
    modelo: str
    ano: str
    numero: int
    status: StatusBicicleta
    # O ID é opcional porque uma bicicleta recém-criada
    # ainda não tem um ID até ser salva no banco de dados.
    id: Optional[int] = None

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

@dataclass
class Totem:
    localizacao: str
    descricao: str
    id: Optional[int] = None
    # Um totem contém uma lista de IDs de trancas.
    # Usamos field(default_factory=list) para inicializar uma lista vazia de forma segura.
    tranca_ids: List[int] = field(default_factory=list)