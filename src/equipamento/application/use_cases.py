# src/equipamento/application/use_cases.py (VERSÃO COMPLETA)

from typing import List, Optional, Dict, Any

from ..domain.entities import Bicicleta, Tranca, Totem, StatusBicicleta, StatusTranca
from .repositories import (
    BicicletaRepositoryInterface,
    TrancaRepositoryInterface,
    TotemRepositoryInterface,
)

# ======================================================
# --- Constantes de Mensagens de Erro ---
# ======================================================
# Definir constantes para mensagens de erro evita a repetição de "magic strings",
# o que melhora a manutenibilidade e previne erros de digitação.
ERRO_BICICLETA_NAO_ENCONTRADA = "Bicicleta não encontrada."
ERRO_TRANCA_NAO_ENCONTRADA = "Tranca não encontrada."
ERRO_TOTEM_NAO_ENCONTRADO = "Totem não encontrado."


# ======================================================
# --- Casos de Uso para Bicicleta ---
# ======================================================
class CadastrarBicicletaUseCase:
    def __init__(self, repository: BicicletaRepositoryInterface):
        self.repository = repository
    def execute(self, dados_bicicleta: Dict[str, Any]) -> Bicicleta:
        nova_bicicleta = Bicicleta(
            marca=dados_bicicleta["marca"],
            modelo=dados_bicicleta["modelo"],
            ano=dados_bicicleta["ano"],
            numero=dados_bicicleta["numero"],
            status=StatusBicicleta.NOVA,
        )
        return self.repository.salvar(nova_bicicleta)

class ListarBicicletasUseCase:
    def __init__(self, repository: BicicletaRepositoryInterface):
        self.repository = repository
    def execute(self) -> List[Bicicleta]:
        return self.repository.listar_todas()

class BuscarBicicletaPorIdUseCase:
    def __init__(self, repository: BicicletaRepositoryInterface):
        self.repository = repository
    def execute(self, bicicleta_id: int) -> Optional[Bicicleta]:
        return self.repository.buscar_por_id(bicicleta_id)

class DeletarBicicletaUseCase:
    def __init__(self, repository: BicicletaRepositoryInterface):
        self.repository = repository
    def execute(self, bicicleta_id: int) -> None:
        self.repository.deletar(bicicleta_id)

class AlterarStatusBicicletaUseCase:
    def __init__(self, repository: BicicletaRepositoryInterface):
        self.repository = repository
    def execute(self, bicicleta_id: int, novo_status: StatusBicicleta) -> Bicicleta:
        bicicleta = self.repository.buscar_por_id(bicicleta_id)
        if not bicicleta:
            raise ValueError(ERRO_BICICLETA_NAO_ENCONTRADA)
        bicicleta.status = novo_status
        bicicleta_atualizada = self.repository.salvar(bicicleta)
        return bicicleta_atualizada
    
class IntegrarBicicletaNaRedeUseCase:
    def __init__(self, bicicleta_repo: BicicletaRepositoryInterface, tranca_repo: TrancaRepositoryInterface):
        self.bicicleta_repo = bicicleta_repo
        self.tranca_repo = tranca_repo

    def execute(self, bicicleta_id: int, tranca_id: int) -> Tranca: 
        bicicleta = self.bicicleta_repo.buscar_por_id(bicicleta_id)
        tranca = self.tranca_repo.buscar_por_id(tranca_id) 

        if not bicicleta: 
            raise ValueError(ERRO_BICICLETA_NAO_ENCONTRADA)
        if not tranca:
            raise ValueError(ERRO_TRANCA_NAO_ENCONTRADA)

        if bicicleta.status not in [StatusBicicleta.NOVA, StatusBicicleta.EM_REPARO]: 
            raise ValueError(f"Bicicleta com status '{bicicleta.status.value}' não pode ser integrada.")

        if tranca.status != StatusTranca.LIVRE: 
            raise ValueError("Tranca não está livre.")
        
        bicicleta.status = StatusBicicleta.DISPONIVEL 
        tranca.status = StatusTranca.OCUPADA
        tranca.bicicleta_id = bicicleta.id

        self.bicicleta_repo.salvar(bicicleta) 
        tranca_atualizada = self.tranca_repo.salvar(tranca)

        return tranca_atualizada 
    

class RetirarBicicletaDaRedeUseCase: 
    def __init__(self, bicicleta_repo: BicicletaRepositoryInterface, tranca_repo: TrancaRepositoryInterface):
        self.bicicleta_repo = bicicleta_repo
        self.tranca_repo = tranca_repo

    def execute(self, bicicleta_id: int, tranca_id: int, status_final: StatusBicicleta) -> Bicicleta: 
        bicicleta = self.bicicleta_repo.buscar_por_id(bicicleta_id)
        tranca = self.tranca_repo.buscar_por_id(tranca_id)

        if not bicicleta: 
            raise ValueError(ERRO_BICICLETA_NAO_ENCONTRADA)
        if not tranca:
            raise ValueError(ERRO_TRANCA_NAO_ENCONTRADA)

        if tranca.bicicleta_id != bicicleta.id: 
            raise ValueError("A bicicleta informada não está na tranca especificada.")
        
        if tranca.status != StatusTranca.OCUPADA: 
            raise ValueError("A tranca não está ocupada.")

        if status_final not in [StatusBicicleta.EM_REPARO, StatusBicicleta.APOSENTADA]: 
            raise ValueError(f"Status de destino '{status_final.value}' é inválido para esta operação.")

        bicicleta.status = status_final 
        tranca.status = StatusTranca.LIVRE
        tranca.bicicleta_id = None

        bicicleta_atualizada = self.bicicleta_repo.salvar(bicicleta) 
        self.tranca_repo.salvar(tranca)

        return bicicleta_atualizada 
 
# ======================================================
# --- Casos de Uso para Tranca ---
# ======================================================

class CadastrarTrancaUseCase:
    def __init__(self, repository: TrancaRepositoryInterface):
        self.repository = repository
    def execute(self, dados_tranca: Dict[str, Any]) -> Tranca: 
        nova_tranca = Tranca(
            numero=dados_tranca["numero"],
            localizacao=dados_tranca["localizacao"],
            ano_de_fabricacao=dados_tranca["ano_de_fabricacao"],
            modelo=dados_tranca["modelo"],
            status=StatusTranca.NOVA,
        )
        return self.repository.salvar(nova_tranca)

class ListarTrancasUseCase:
    def __init__(self, repository: TrancaRepositoryInterface):
        self.repository = repository
    def execute(self) -> List[Tranca]:
        return self.repository.listar_todas()
        
class BuscarTrancaPorIdUseCase:
    def __init__(self, repository: TrancaRepositoryInterface):
        self.repository = repository
    def execute(self, tranca_id: int) -> Optional[Tranca]:
        return self.repository.buscar_por_id(tranca_id)

class DeletarTrancaUseCase:
    def __init__(self, repository: TrancaRepositoryInterface):
        self.repository = repository
    def execute(self, tranca_id: int) -> None:
        self.repository.deletar(tranca_id)

class AlterarStatusTrancaUseCase: 
    def __init__(self, repository: TrancaRepositoryInterface):
        self.repository = repository

    def execute(self, tranca_id: int, novo_status: StatusTranca) -> Tranca: 
        tranca = self.repository.buscar_por_id(tranca_id)

        if not tranca: 
            raise ValueError(ERRO_TRANCA_NAO_ENCONTRADA)
 
        if novo_status == StatusTranca.OCUPADA:
            raise ValueError(f"Status '{novo_status.value}' não pode ser definido diretamente. Use a operação de trancar com uma bicicleta.")
        
        if tranca.status == StatusTranca.OCUPADA and novo_status == StatusTranca.LIVRE: 
            raise ValueError("Não é possível liberar uma tranca ocupada. Use a operação de destrancar ou retirar bicicleta.")

        tranca.status = novo_status 

        return self.repository.salvar(tranca) 
    
class ListarTrancasPorTotemUseCase: 
    def __init__(self, totem_repo: TotemRepositoryInterface, tranca_repo: TrancaRepositoryInterface):
        self.totem_repo = totem_repo
        self.tranca_repo = tranca_repo
    
    def execute(self, totem_id: int) -> List[Tranca]: 
        totem = self.totem_repo.buscar_por_id(totem_id)
        if not totem:
            raise ValueError(ERRO_TOTEM_NAO_ENCONTRADO)

        return self.tranca_repo.buscar_por_totem_id(totem_id)

class IntegrarTrancaNoTotemUseCase: 
    def __init__(self, tranca_repo: TrancaRepositoryInterface, totem_repo: TotemRepositoryInterface):
        self.tranca_repo = tranca_repo
        self.totem_repo = totem_repo

    def execute(self, tranca_id: int, totem_id: int) -> Tranca: 
        tranca = self.tranca_repo.buscar_por_id(tranca_id)
        totem = self.totem_repo.buscar_por_id(totem_id)

        if not tranca: 
            raise ValueError(ERRO_TRANCA_NAO_ENCONTRADA)
        if not totem:
            raise ValueError(ERRO_TOTEM_NAO_ENCONTRADO)
        
        if tranca.totem_id is not None: 
            raise ValueError(f"Tranca já está integrada ao totem {tranca.totem_id}.")
        
        if tranca.status not in [StatusTranca.NOVA, StatusTranca.EM_REPARO]: 
            raise ValueError(f"Tranca com status '{tranca.status.value}' não pode ser integrada.")

        tranca.totem_id = totem.id 
        tranca.status = StatusTranca.LIVRE 
        
        tranca_atualizada = self.tranca_repo.salvar(tranca) 

        return tranca_atualizada
         
# ======================================================
# --- Casos de Uso para Totem ---
# ======================================================

class CadastrarTotemUseCase:
    def __init__(self, repository: TotemRepositoryInterface):
        self.repository = repository
    def execute(self, dados_totem: Dict[str, Any]) -> Totem: 
        novo_totem = Totem(
            localizacao=dados_totem["localizacao"],
            descricao=dados_totem["descricao"],
        )
        return self.repository.salvar(novo_totem)

class ListarTotensUseCase:
    def __init__(self, repository: TotemRepositoryInterface):
        self.repository = repository
    def execute(self) -> List[Totem]:
        return self.repository.listar_todos()

class BuscarTotemPorIdUseCase:
    def __init__(self, repository: TotemRepositoryInterface):
        self.repository = repository
    def execute(self, totem_id: int) -> Optional[Totem]:
        return self.repository.buscar_por_id(totem_id)

class DeletarTotemUseCase:
    def __init__(self, repository: TotemRepositoryInterface):
        self.repository = repository
    def execute(self, totem_id: int) -> None:
        self.repository.deletar(totem_id)


class AtualizarBicicletaUseCase: 
    def __init__(self, repository: BicicletaRepositoryInterface):
        self.repository = repository

    def execute(self, bicicleta_id: int, dados_atualizacao: dict) -> Bicicleta: 
        bicicleta = self.repository.buscar_por_id(bicicleta_id)
        if not bicicleta:
            raise ValueError(ERRO_BICICLETA_NAO_ENCONTRADA)

        bicicleta.marca = dados_atualizacao.get("marca", bicicleta.marca) 
        bicicleta.modelo = dados_atualizacao.get("modelo", bicicleta.modelo)
        bicicleta.ano = dados_atualizacao.get("ano", bicicleta.ano)
        bicicleta.numero = dados_atualizacao.get("numero", bicicleta.numero)
        
        return self.repository.salvar(bicicleta) 


class AtualizarTrancaUseCase: 
    def __init__(self, repository: TrancaRepositoryInterface):
        self.repository = repository

    def execute(self, tranca_id: int, dados_atualizacao: dict) -> Tranca:
        tranca = self.repository.buscar_por_id(tranca_id)
        if not tranca:
            raise ValueError(ERRO_TRANCA_NAO_ENCONTRADA)

        tranca.numero = dados_atualizacao.get("numero", tranca.numero)
        tranca.localizacao = dados_atualizacao.get("localizacao", tranca.localizacao)
        tranca.ano_de_fabricacao = dados_atualizacao.get("ano_de_fabricacao", tranca.ano_de_fabricacao)
        tranca.modelo = dados_atualizacao.get("modelo", tranca.modelo)
        
        return self.repository.salvar(tranca)


class AtualizarTotemUseCase: 
    def __init__(self, repository: TotemRepositoryInterface):
        self.repository = repository

    def execute(self, totem_id: int, dados_atualizacao: dict) -> Totem:
        totem = self.repository.buscar_por_id(totem_id)
        if not totem:
            raise ValueError(ERRO_TOTEM_NAO_ENCONTRADO)

        totem.localizacao = dados_atualizacao.get("localizacao", totem.localizacao)
        totem.descricao = dados_atualizacao.get("descricao", totem.descricao)

        return self.repository.salvar(totem)
    
class BuscarBicicletaEmTrancaUseCase: 
    def __init__(self, tranca_repo: TrancaRepositoryInterface, bicicleta_repo: BicicletaRepositoryInterface):
        self.tranca_repo = tranca_repo
        self.bicicleta_repo = bicicleta_repo

    def execute(self, tranca_id: int) -> Optional[Bicicleta]: 
        tranca = self.tranca_repo.buscar_por_id(tranca_id)

        if not tranca: 
            raise ValueError(ERRO_TRANCA_NAO_ENCONTRADA)
        
        if tranca.bicicleta_id is None:
            return None

        bicicleta = self.bicicleta_repo.buscar_por_id(tranca.bicicleta_id) 
        
        if not bicicleta: 
             raise ValueError(f"Inconsistência de dados: Bicicleta com ID {tranca.bicicleta_id} associada à tranca, mas não encontrada no repositório.")

        return bicicleta
    
class ListarBicicletasPorTotemUseCase: 
    def __init__(self, totem_repo: TotemRepositoryInterface, tranca_repo: TrancaRepositoryInterface, bicicleta_repo: BicicletaRepositoryInterface):
        self.totem_repo = totem_repo
        self.tranca_repo = tranca_repo
        self.bicicleta_repo = bicicleta_repo

    def execute(self, totem_id: int) -> List[Bicicleta]: 
        if not self.totem_repo.buscar_por_id(totem_id):
            raise ValueError(ERRO_TOTEM_NAO_ENCONTRADO)
        
        trancas_do_totem = self.tranca_repo.buscar_por_totem_id(totem_id) 
        if not trancas_do_totem:
            return []

        ids_de_bicicletas = [ 
            tranca.bicicleta_id for tranca in trancas_do_totem 
            if tranca.bicicleta_id is not None
        ]
        if not ids_de_bicicletas:
            return []

        return self.bicicleta_repo.buscar_por_ids(ids_de_bicicletas) 
    
class RetirarTrancaDoTotemUseCase: 
    def __init__(self, tranca_repo: TrancaRepositoryInterface, totem_repo: TotemRepositoryInterface):
        self.tranca_repo = tranca_repo
        self.totem_repo = totem_repo

    def execute(self, tranca_id: int, totem_id: int, status_final: StatusTranca) -> Tranca: 
        tranca = self.tranca_repo.buscar_por_id(tranca_id)
        totem = self.totem_repo.buscar_por_id(totem_id)

        if not tranca: 
            raise ValueError(ERRO_TRANCA_NAO_ENCONTRADA)
        if not totem:
            raise ValueError(ERRO_TOTEM_NAO_ENCONTRADO)

        if tranca.totem_id != totem.id: 
            raise ValueError("Tranca não pertence ao totem informado.")

        if tranca.status == StatusTranca.OCUPADA: 
            raise ValueError("Não é possível retirar uma tranca que está ocupada por uma bicicleta.")
        
        if status_final not in [StatusTranca.EM_REPARO, StatusTranca.APOSENTADA]: 
            raise ValueError(f"Status de destino '{status_final.value}' é inválido para esta operação.")
        
        tranca.status = status_final 
        tranca.totem_id = None

        return self.tranca_repo.salvar(tranca) 

class TrancarTrancaUseCase: 
    def __init__(self, tranca_repo: TrancaRepositoryInterface, bicicleta_repo: BicicletaRepositoryInterface):
        self.tranca_repo = tranca_repo
        self.bicicleta_repo = bicicleta_repo

    def execute(self, tranca_id: int, bicicleta_id: int) -> Tranca: 
        tranca = self.tranca_repo.buscar_por_id(tranca_id)
        bicicleta = self.bicicleta_repo.buscar_por_id(bicicleta_id)

        if not tranca: raise ValueError(ERRO_TRANCA_NAO_ENCONTRADA)
        if not bicicleta: raise ValueError(ERRO_BICICLETA_NAO_ENCONTRADA)

        if tranca.status != StatusTranca.LIVRE: 
            raise ValueError("A tranca não está livre para receber uma bicicleta.")
        
        if bicicleta.status != StatusBicicleta.EM_USO: 
            raise ValueError("A bicicleta não está em uso para ser devolvida.")

        tranca.status = StatusTranca.OCUPADA 
        tranca.bicicleta_id = bicicleta.id
        bicicleta.status = StatusBicicleta.DISPONIVEL

        self.bicicleta_repo.salvar(bicicleta) 
        return self.tranca_repo.salvar(tranca)


class DestrancarTrancaUseCase: 
    def __init__(self, tranca_repo: TrancaRepositoryInterface, bicicleta_repo: BicicletaRepositoryInterface):
        self.tranca_repo = tranca_repo
        self.bicicleta_repo = bicicleta_repo

    def execute(self, tranca_id: int) -> Bicicleta: 
        tranca = self.tranca_repo.buscar_por_id(tranca_id)

        if not tranca: raise ValueError(ERRO_TRANCA_NAO_ENCONTRADA)

        if tranca.status != StatusTranca.OCUPADA: 
            raise ValueError("A tranca não está ocupada.")
        if tranca.bicicleta_id is None:
            raise ValueError("Inconsistência: Tranca ocupada mas sem bicicleta associada.")
        
        bicicleta = self.bicicleta_repo.buscar_por_id(tranca.bicicleta_id) 
        if not bicicleta:
             raise ValueError(f"Inconsistência: Bicicleta com ID {tranca.bicicleta_id} não foi encontrada.")

        tranca.status = StatusTranca.LIVRE 
        tranca.bicicleta_id = None
        bicicleta.status = StatusBicicleta.EM_USO

        self.tranca_repo.salvar(tranca) 
        return self.bicicleta_repo.salvar(bicicleta)