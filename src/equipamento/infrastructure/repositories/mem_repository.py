# src/equipamento/infrastructure/repositories/mem_repository.py

from typing import Dict, List, Optional

# Importando as interfaces que vamos implementar
from ...application.repositories import (
    BicicletaRepositoryInterface,
    TrancaRepositoryInterface,
    TotemRepositoryInterface,
)
# Importando as entidades que vamos armazenar
from ...domain.entities import Bicicleta, Tranca, Totem


class MemBicicletaRepository(BicicletaRepositoryInterface):
    """Implementação em memória do repositório de bicicletas."""

    def __init__(self):
        self._dados: Dict[int, Bicicleta] = {}
        self._proximo_id: int = 1

    def salvar(self, bicicleta: Bicicleta) -> Bicicleta:
        if bicicleta.id is None:
            bicicleta.id = self._proximo_id
            self._proximo_id += 1
        
        self._dados[bicicleta.id] = bicicleta
        return bicicleta

    def buscar_por_id(self, bicicleta_id: int) -> Optional[Bicicleta]:
        return self._dados.get(bicicleta_id)

    def listar_todas(self) -> List[Bicicleta]:
        return list(self._dados.values())
    
    def deletar(self, bicicleta_id: int) -> None:
        if bicicleta_id in self._dados:
            del self._dados[bicicleta_id]

    def buscar_por_ids(self, bicicleta_ids: List[int]) -> List[Bicicleta]:
        # Filtra o dicionário de dados, pegando apenas as bicicletas
        # cujos IDs estão na lista fornecida.
        return [
            bicicleta for bicicleta_id, bicicleta in self._dados.items()
            if bicicleta_id in bicicleta_ids
        ]


class MemTrancaRepository(TrancaRepositoryInterface):
    """Implementação em memória do repositório de trancas."""

    def __init__(self):
        self._dados: Dict[int, Tranca] = {}
        self._proximo_id: int = 1

    def salvar(self, tranca: Tranca) -> Tranca:
        if tranca.id is None:
            tranca.id = self._proximo_id
            self._proximo_id += 1
        self._dados[tranca.id] = tranca
        return tranca

    def buscar_por_id(self, tranca_id: int) -> Optional[Tranca]:
        return self._dados.get(tranca_id)
    
    def listar_todas(self) -> List[Tranca]:
        return list(self._dados.values())

    def deletar(self, tranca_id: int) -> None:
        if tranca_id in self._dados:
            del self._dados[tranca_id]

    def buscar_por_totem_id(self, totem_id: int) -> List[Tranca]:
        # Filtra a lista de trancas, retornando apenas aquelas
        # que pertencem ao totem_id informado.
        return [
            tranca for tranca in self._dados.values()
            if tranca.totem_id == totem_id
        ]


class MemTotemRepository(TotemRepositoryInterface):
    """Implementação em memória do repositório de totens."""

    def __init__(self):
        self._dados: Dict[int, Totem] = {}
        self._proximo_id: int = 1

    def salvar(self, totem: Totem) -> Totem:
        if totem.id is None:
            totem.id = self._proximo_id
            self._proximo_id += 1
        self._dados[totem.id] = totem
        return totem

    def buscar_por_id(self, totem_id: int) -> Optional[Totem]:
        return self._dados.get(totem_id)

    def listar_todos(self) -> List[Totem]:
        return list(self._dados.values())

    def deletar(self, totem_id: int) -> None:
        if totem_id in self._dados:
            del self._dados[totem_id]