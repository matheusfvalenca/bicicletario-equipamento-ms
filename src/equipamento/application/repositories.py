# src/equipamento/application/repositories.py

from abc import ABC, abstractmethod
from typing import List, Optional

from ..domain.entities import Bicicleta, Totem, Tranca

# ABC (Abstract Base Class) define a estrutura para uma classe abstrata.
# Nossas interfaces de repositório herdam dela.

class BicicletaRepositoryInterface(ABC):
    """Interface para o Repositório de Bicicletas."""

    @abstractmethod
    def salvar(self, bicicleta: Bicicleta) -> Bicicleta:
        """Salva uma nova bicicleta ou atualiza uma existente."""
        pass

    @abstractmethod
    def buscar_por_id(self, bicicleta_id: int) -> Optional[Bicicleta]:
        """Busca uma bicicleta pelo seu ID."""
        pass

    @abstractmethod
    def listar_todas(self, include_deleted: bool = False) -> List[Bicicleta]:
        """Lista todas as bicicletas, com opção de incluir as deletadas."""
        pass
    
    @abstractmethod
    def deletar(self, bicicleta_id: int) -> None:
        """Deleta uma bicicleta pelo seu ID."""
        pass

    @abstractmethod
    def buscar_por_ids(self, bicicleta_ids: List[int]) -> List[Bicicleta]:
        """Busca uma lista de bicicletas por seus IDs."""
        pass


class TrancaRepositoryInterface(ABC):
    """Interface para o Repositório de Trancas."""

    @abstractmethod
    def salvar(self, tranca: Tranca) -> Tranca:
        """Salva uma nova tranca ou atualiza uma existente."""
        pass

    @abstractmethod
    def buscar_por_id(self, tranca_id: int) -> Optional[Tranca]:
        """Busca uma tranca pelo seu ID."""
        pass
    
    @abstractmethod
    def listar_todas(self, include_deleted: bool = False) -> List[Tranca]:
        """Lista todas as trancas, com opção de incluir as deletadas."""
        pass

    @abstractmethod
    def deletar(self, tranca_id: int) -> None:
        """Deleta uma tranca pelo seu ID."""
        pass

    @abstractmethod
    def buscar_por_totem_id(self, totem_id: int) -> List[Tranca]:
        """Busca todas as trancas associadas a um totem específico."""
        pass


class TotemRepositoryInterface(ABC):
    """Interface para o Repositório de Totens."""

    @abstractmethod
    def salvar(self, totem: Totem) -> Totem:
        """Salva um novo totem ou atualiza um existente."""
        pass

    @abstractmethod
    def buscar_por_id(self, totem_id: int) -> Optional[Totem]:
        """Busca um totem pelo seu ID."""
        pass

    @abstractmethod
    def listar_todos(self, include_deleted: bool = False) -> List[Totem]:
        """Lista todos os totens, com opção de incluir os deletados."""
        pass

    @abstractmethod
    def deletar(self, totem_id: int) -> None:
        """Deleta um totem pelo seu ID."""
        pass
