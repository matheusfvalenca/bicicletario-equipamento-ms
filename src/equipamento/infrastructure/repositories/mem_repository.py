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
    
# Alterado para retornar apenas se existir E não estiver deletada
     def buscar_por_id(self, bicicleta_id: int) -> Optional[Bicicleta]:
        bicicleta = self._dados.get(bicicleta_id)
        if bicicleta and not bicicleta.is_deleted:
            return bicicleta
        return None

# Alterado para filtrar os deletados por padrão
    def listar_todas(self, include_deleted: bool = False) -> List[Bicicleta]:
        if not include_deleted:
            return [b for b in self._dados.values() if not b.is_deleted]
        return list(self._dados.values())
    
# Alterado para aplicar lógica de Soft Delete
   def deletar(self, bicicleta_id: int) -> None:
        bicicleta = self._dados.get(bicicleta_id)
        if bicicleta:
            # Marca como deletada e salva
            bicicleta.is_deleted = True
            self.salvar(bicicleta)

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

# Alterado para retornar apenas se existir E não estiver deletada
    def buscar_por_id(self, tranca_id: int) -> Optional[Tranca]:
        tranca = self._dados.get(tranca_id)
        if tranca and not tranca.is_deleted:
            return tranca
        return None
    
# Alterado para filtrar os deletados por padrão
    def listar_todas(self, include_deleted: bool = False) -> List[Tranca]:
        if not include_deleted:
            return [t for t in self._dados.values() if not t.is_deleted]
        return list(self._dados.values())

# Alterado para aplicar lógica de Soft Delete
    def deletar(self, tranca_id: int) -> None:
        tranca = self._dados.get(tranca_id)
        if tranca:
            # Marca como deletada e salva
            tranca.is_deleted = True
            self.salvar(tranca)

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

# Alterado para retornar apenas se existir E não estiver deletada
    def buscar_por_id(self, totem_id: int) -> Optional[Totem]:
        totem = self._dados.get(totem_id)
        if totem and not totem.is_deleted:
            return totem
        return None
    
# Alterado para filtrar os deletados por padrão
    def listar_todos(self, include_deleted: bool = False) -> List[Totem]:
        if not include_deleted:
            return [t for t in self._dados.values() if not t.is_deleted]
        return list(self._dados.values())
    
# Alterado para aplicar lógica de Soft Delete
    def deletar(self, totem_id: int) -> None:
        totem = self._dados.get(totem_id)
        if totem:
            # Marca como deletada e salva
            totem.is_deleted = True
            self.salvar(totem)