# src/equipamento/infrastructure/repositories/mem_repository.py

from typing import Dict, List, Optional

# Importando as interfaces que vamos implementar
from ...application.repositories import (
    BicicletaRepositoryInterface,
    TrancaRepositoryInterface,
    TotemRepositoryInterface,
)
# Importando as entidades que vamos armazenar
from ...domain.entities import Bicicleta, Tranca, Totem, StatusBicicleta, StatusTranca


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
        bicicleta = self._dados.get(bicicleta_id)
        # Retorna apenas se existir E não estiver deletada
        if bicicleta and not bicicleta.is_deleted:
            return bicicleta
        return None

    def listar_todas(self, include_deleted: bool = False) -> List[Bicicleta]:
        # Filtra os deletados por padrão
        if not include_deleted:
            return [b for b in self._dados.values() if not b.is_deleted]
        return list(self._dados.values())
    
    def deletar(self, bicicleta_id: int) -> None:
        # Lógica de Soft Delete
        bicicleta = self._dados.get(bicicleta_id)
        if bicicleta:
            bicicleta.is_deleted = True
            self.salvar(bicicleta)

    def buscar_por_ids(self, bicicleta_ids: List[int]) -> List[Bicicleta]:
        # Filtra o dicionário de dados, pegando apenas as bicicletas
        # cujos IDs estão na lista fornecida e que não estão deletadas.
        return [
            bicicleta for bicicleta_id, bicicleta in self._dados.items()
            if bicicleta_id in bicicleta_ids and not bicicleta.is_deleted
        ]

    def restaurar_para_estado_inicial(self):
        """Limpa todos os dados e recria um estado inicial para testes."""
        self._dados.clear()
        self._proximo_id = 1
        
        # Adiciona bicicletas iniciais
        bicicleta1 = Bicicleta(id=1, marca="Caloi", modelo="Ceci", ano="1992", numero=100, status=StatusBicicleta.DISPONIVEL)
        bicicleta2 = Bicicleta(id=2, marca="Monark", modelo="Barra Forte", ano="1985", numero=200, status=StatusBicicleta.DISPONIVEL)
        
        self.salvar(bicicleta1)
        self.salvar(bicicleta2)

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
        tranca = self._dados.get(tranca_id)
        if tranca and not tranca.is_deleted:
            return tranca
        return None
    
    def listar_todas(self, include_deleted: bool = False) -> List[Tranca]:
        if not include_deleted:
            return [t for t in self._dados.values() if not t.is_deleted]
        return list(self._dados.values())

    def deletar(self, tranca_id: int) -> None:
        tranca = self._dados.get(tranca_id)
        if tranca:
            tranca.is_deleted = True
            self.salvar(tranca)

    def buscar_por_totem_id(self, totem_id: int) -> List[Tranca]:
        # Filtra a lista de trancas, retornando apenas aquelas
        # que pertencem ao totem_id informado e não estão deletadas.
        return [
            tranca for tranca in self._dados.values()
            if tranca.totem_id == totem_id and not tranca.is_deleted
        ]

    def restaurar_para_estado_inicial(self):
        self._dados.clear()
        self._proximo_id = 1

        # Adiciona trancas iniciais (associadas aos totens e bicicletas)
        tranca1 = Tranca(id=1, numero=10, localizacao="Totem 1", ano_de_fabricacao="2022", modelo="T1", status=StatusTranca.OCUPADA, bicicleta_id=1, totem_id=1)
        tranca2 = Tranca(id=2, numero=20, localizacao="Totem 1", ano_de_fabricacao="2022", modelo="T1", status=StatusTranca.LIVRE, totem_id=1)
        tranca3 = Tranca(id=3, numero=30, localizacao="Totem 2", ano_de_fabricacao="2023", modelo="T2", status=StatusTranca.OCUPADA, bicicleta_id=2, totem_id=2)
        
        self.salvar(tranca1)
        self.salvar(tranca2)
        self.salvar(tranca3)

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
        totem = self._dados.get(totem_id)
        if totem and not totem.is_deleted:
            return totem
        return None

    def listar_todos(self, include_deleted: bool = False) -> List[Totem]:
        if not include_deleted:
            return [t for t in self._dados.values() if not t.is_deleted]
        return list(self._dados.values())

    def deletar(self, totem_id: int) -> None:
        totem = self._dados.get(totem_id)
        if totem:
            totem.is_deleted = True
            self.salvar(totem)

    def restaurar_para_estado_inicial(self):
        self._dados.clear()
        self._proximo_id = 1

        # Adiciona totens iniciais
        totem1 = Totem(id=1, localizacao="Praça Central", descricao="Totem perto do chafariz")
        totem2 = Totem(id=2, localizacao="Parque da Cidade", descricao="Totem na entrada principal")

        self.salvar(totem1)
        self.salvar(totem2)