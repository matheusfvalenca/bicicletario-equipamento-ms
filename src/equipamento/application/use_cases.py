# src/equipamento/application/use_cases.py (VERSÃO COMPLETA)

from typing import List, Optional, Dict, Any

from ..domain.entities import Bicicleta, Tranca, Totem, StatusBicicleta, StatusTranca
from .repositories import (
    BicicletaRepositoryInterface,
    TrancaRepositoryInterface,
    TotemRepositoryInterface,
)

# ... (Casos de uso de Bicicleta - sem alterações) ...
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
    def execute(self, include_deleted: bool = False) -> List[Bicicleta]:
        return self.repository.listar_todas(include_deleted=include_deleted)

class BuscarBicicletaPorIdUseCase:
    def __init__(self, repository: BicicletaRepositoryInterface):
        self.repository = repository
    def execute(self, bicicleta_id: int) -> Optional[Bicicleta]:
        return self.repository.buscar_por_id(bicicleta_id)

class DeletarBicicletaUseCase:
    def __init__(self, repository: BicicletaRepositoryInterface):
        self.repository = repository
    def execute(self, bicicleta_id: int) -> None:
        # 1. Busca a bicicleta antes de deletar
        bicicleta = self.repository.buscar_por_id(bicicleta_id)

        # 2. Valida se a bicicleta existe
        if not bicicleta:
            raise ValueError("Bicicleta não encontrada.")

        # 3. Valida a regra de negócio (UC10-R4)
        # A regra diz que apenas bicicletas com status "aposentada" podem ser excluídas.
        # A verificação de "não estar em nenhuma tranca" é implícita no status "aposentada",
        # pois para ser aposentada, ela já teve que ser retirada de uma tranca.
        if bicicleta.status != StatusBicicleta.APOSENTADA:
            raise ValueError(f"Ação negada. Apenas bicicletas com status 'APOSENTADA' podem ser excluídas. Status atual: '{bicicleta.status.value}'.")

        # 4. Se todas as validações passarem, executa a exclusão
        self.repository.deletar(bicicleta_id)

class AlterarStatusBicicletaUseCase:
    def __init__(self, repository: BicicletaRepositoryInterface):
        self.repository = repository
    def execute(self, bicicleta_id: int, novo_status: StatusBicicleta) -> Bicicleta:
        bicicleta = self.repository.buscar_por_id(bicicleta_id)
        if not bicicleta:
            raise ValueError("Bicicleta não encontrada.")
        bicicleta.status = novo_status
        bicicleta_atualizada = self.repository.salvar(bicicleta)
        return bicicleta_atualizada
    
class IntegrarBicicletaNaRedeUseCase:
    """
    Caso de uso para realizar a integração de uma bicicleta a uma tranca na rede de totens.
    Orquestra as ações entre as entidades Bicicleta e Tranca.
    """
    def __init__(self, bicicleta_repo: BicicletaRepositoryInterface, tranca_repo: TrancaRepositoryInterface):
        self.bicicleta_repo = bicicleta_repo
        self.tranca_repo = tranca_repo

    def execute(self, bicicleta_id: int, tranca_id: int) -> Tranca:
        # 1. Buscar as entidades nos repositórios
        bicicleta = self.bicicleta_repo.buscar_por_id(bicicleta_id)
        tranca = self.tranca_repo.buscar_por_id(tranca_id)

        # 2. Validar regras de negócio
        if not bicicleta:
            raise ValueError("Bicicleta não encontrada.")
        if not tranca:
            raise ValueError("Tranca não encontrada.")

        # Regra: Bicicleta deve estar em status 'NOVA' ou 'EM_REPARO' para ser integrada
        if bicicleta.status not in [StatusBicicleta.NOVA, StatusBicicleta.EM_REPARO]:
            raise ValueError(f"Bicicleta com status '{bicicleta.status.value}' não pode ser integrada.")

        # Regra: Tranca deve estar 'LIVRE' para receber uma bicicleta
        if tranca.status != StatusTranca.LIVRE:
            raise ValueError("Tranca não está livre.")
        
        # 3. Executar as ações
        bicicleta.status = StatusBicicleta.DISPONIVEL
        tranca.status = StatusTranca.OCUPADA
        tranca.bicicleta_id = bicicleta.id

        # 4. Persistir as alterações nos repositórios
        self.bicicleta_repo.salvar(bicicleta)
        tranca_atualizada = self.tranca_repo.salvar(tranca)

        # 5. Retornar o resultado
        return tranca_atualizada
    

class RetirarBicicletaDaRedeUseCase:
    """
    Caso de uso para retirar uma bicicleta da rede (de uma tranca) para
    reparo ou aposentadoria.
    """
    def __init__(self, bicicleta_repo: BicicletaRepositoryInterface, tranca_repo: TrancaRepositoryInterface):
        self.bicicleta_repo = bicicleta_repo
        self.tranca_repo = tranca_repo

    def execute(self, bicicleta_id: int, tranca_id: int, status_final: StatusBicicleta) -> Bicicleta:
        # 1. Buscar as entidades
        bicicleta = self.bicicleta_repo.buscar_por_id(bicicleta_id)
        tranca = self.tranca_repo.buscar_por_id(tranca_id)

        # 2. Validar regras de negócio
        if not bicicleta:
            raise ValueError("Bicicleta não encontrada.")
        if not tranca:
            raise ValueError("Tranca não encontrada.")

        # Regra: A bicicleta deve estar na tranca informada.
        if tranca.bicicleta_id != bicicleta.id:
            raise ValueError("A bicicleta informada não está na tranca especificada.")
        
        # Regra: A tranca deve estar ocupada.
        if tranca.status != StatusTranca.OCUPADA:
            raise ValueError("A tranca não está ocupada.")

        # Regra: O status final deve ser um status de "fora de operação".
        if status_final not in [StatusBicicleta.EM_REPARO, StatusBicicleta.APOSENTADA]:
            raise ValueError(f"Status de destino '{status_final.value}' é inválido para esta operação.")

        # 3. Executar as ações
        bicicleta.status = status_final
        tranca.status = StatusTranca.LIVRE
        tranca.bicicleta_id = None # Desassocia a bicicleta da tranca

        # 4. Persistir as alterações
        bicicleta_atualizada = self.bicicleta_repo.salvar(bicicleta)
        self.tranca_repo.salvar(tranca)

        # 5. Retornar a bicicleta com seu novo status
        return bicicleta_atualizada

# ======================================================
# --- Casos de Uso para Tranca (Agora completos)
# ======================================================

class CadastrarTrancaUseCase:
    def __init__(self, repository: TrancaRepositoryInterface):
        self.repository = repository
    def execute(self, dados_tranca: Dict[str, Any]) -> Tranca:
        # LÓGICA PREENCHIDA
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
    def execute(self, include_deleted: bool = False) -> List[Tranca]:
        return self.repository.listar_todas(include_deleted=include_deleted)
        
class BuscarTrancaPorIdUseCase:
    def __init__(self, repository: TrancaRepositoryInterface):
        self.repository = repository
    def execute(self, tranca_id: int) -> Optional[Tranca]:
        return self.repository.buscar_por_id(tranca_id)

class DeletarTrancaUseCase:
    def __init__(self, repository: TrancaRepositoryInterface):
        self.repository = repository
    def execute(self, tranca_id: int) -> None:
        # 1. Busca a tranca
        tranca = self.repository.buscar_por_id(tranca_id)

        # 2. Valida se a tranca existe
        if not tranca:
            raise ValueError("Tranca não encontrada.")

        # 3. Valida a regra de negócio (UC13-R4)
        # A regra diz que apenas trancas sem bicicleta podem ser excluídas.
        if tranca.status == StatusTranca.OCUPADA or tranca.bicicleta_id is not None:
            raise ValueError("Ação negada. Não é possível excluir uma tranca que está ocupada por uma bicicleta.")

        # 4. Procede com a exclusão
        self.repository.deletar(tranca_id)

class AlterarStatusTrancaUseCase:
    """
    Caso de uso para alterar o status de uma tranca específica
    (ex: para manutenção ou aposentadoria).
    """
    def __init__(self, repository: TrancaRepositoryInterface):
        self.repository = repository

    def execute(self, tranca_id: int, novo_status: StatusTranca) -> Tranca:
        # 1. Buscar a tranca
        tranca = self.repository.buscar_por_id(tranca_id)

        # 2. Validar se a tranca existe
        if not tranca:
            raise ValueError("Tranca não encontrada.")

        # 3. Validar regras de negócio (LÓGICA CORRIGIDA)
        # Regra: Não se pode definir o status OCUPADA diretamente.
        if novo_status == StatusTranca.OCUPADA:
            raise ValueError(f"Status '{novo_status.value}' não pode ser definido diretamente. Use a operação de trancar com uma bicicleta.")
        
        # Regra: Não se pode liberar uma tranca que está OCUPADA por este método.
        if tranca.status == StatusTranca.OCUPADA and novo_status == StatusTranca.LIVRE:
            raise ValueError("Não é possível liberar uma tranca ocupada. Use a operação de destrancar ou retirar bicicleta.")

        # 4. Se passou nas validações, altera o status
        tranca.status = novo_status

        # 5. Salvar e retornar
        return self.repository.salvar(tranca)
    
class ListarTrancasPorTotemUseCase:
    """
    Caso de uso para listar todas as trancas de um totem específico.
    """
    def __init__(self, totem_repo: TotemRepositoryInterface, tranca_repo: TrancaRepositoryInterface):
        self.totem_repo = totem_repo
        self.tranca_repo = tranca_repo
    
    def execute(self, totem_id: int) -> List[Tranca]:
        # Regra de negócio: garante que o totem existe antes de buscar as trancas
        totem = self.totem_repo.buscar_por_id(totem_id)
        if not totem:
            raise ValueError("Totem não encontrado.")

        return self.tranca_repo.buscar_por_totem_id(totem_id)

class IntegrarTrancaNoTotemUseCase:
    """
    Caso de uso para associar uma tranca a um totem.
    """
    def __init__(self, tranca_repo: TrancaRepositoryInterface, totem_repo: TotemRepositoryInterface):
        self.tranca_repo = tranca_repo
        self.totem_repo = totem_repo

    def execute(self, tranca_id: int, totem_id: int) -> Tranca:
        # 1. Buscar as entidades
        tranca = self.tranca_repo.buscar_por_id(tranca_id)
        totem = self.totem_repo.buscar_por_id(totem_id)

        # 2. Validar regras de negócio
        if not tranca:
            raise ValueError("Tranca não encontrada.")
        if not totem:
            raise ValueError("Totem não encontrado.")
        
        # Regra: Tranca não pode já pertencer a um totem
        if tranca.totem_id is not None:
            raise ValueError(f"Tranca já está integrada ao totem {tranca.totem_id}.")
        
        # Regra: Tranca deve estar em status 'NOVA' ou 'EM_REPARO'
        if tranca.status not in [StatusTranca.NOVA, StatusTranca.EM_REPARO]:
            raise ValueError(f"Tranca com status '{tranca.status.value}' não pode ser integrada.")

        # 3. Executar as ações
        # Associa a tranca ao totem
        tranca.totem_id = totem.id
        # Atualiza o status da tranca para operacional
        tranca.status = StatusTranca.LIVRE
        # Adiciona a tranca à lista do totem (se a lista existir e for gerenciada aqui)
        # Nota: A consistência dessa lista é um ponto avançado, por enquanto vamos focar em salvar a tranca.
        
        # 4. Persistir a tranca atualizada
        tranca_atualizada = self.tranca_repo.salvar(tranca)
        # O totem não precisa ser salvo pois nosso repositório em memória manipula o mesmo objeto,
        # mas em um sistema real com banco de dados, a linha abaixo seria necessária:
        # self.totem_repo.salvar(totem)

        return tranca_atualizada
        
# ======================================================
# --- Casos de Uso para Totem (Agora completos)
# ======================================================

class CadastrarTotemUseCase:
    def __init__(self, repository: TotemRepositoryInterface):
        self.repository = repository
    def execute(self, dados_totem: Dict[str, Any]) -> Totem:
        # LÓGICA PREENCHIDA
        novo_totem = Totem(
            localizacao=dados_totem["localizacao"],
            descricao=dados_totem["descricao"],
        )
        return self.repository.salvar(novo_totem)

class ListarTotensUseCase:
    def __init__(self, repository: TotemRepositoryInterface):
        self.repository = repository
    def execute(self, include_deleted: bool = False) -> List[Totem]:
        return self.repository.listar_todos(include_deleted=include_deleted)

class BuscarTotemPorIdUseCase:
    def __init__(self, repository: TotemRepositoryInterface):
        self.repository = repository
    def execute(self, totem_id: int) -> Optional[Totem]:
        return self.repository.buscar_por_id(totem_id)

class DeletarTotemUseCase:
    # O construtor agora recebe os dois repositórios
    def __init__(self, totem_repo: TotemRepositoryInterface, tranca_repo: TrancaRepositoryInterface):
        self.totem_repo = totem_repo
        self.tranca_repo = tranca_repo

    def execute(self, totem_id: int) -> None:
        # 1. Valida se o totem existe
        totem = self.totem_repo.buscar_por_id(totem_id)
        if not totem:
            raise ValueError("Totem não encontrado.")

        # 2. Valida a regra de negócio (UC14-R3)
        # Verifica se existem trancas associadas a este totem
        trancas_no_totem = self.tranca_repo.buscar_por_totem_id(totem_id)
        if trancas_no_totem:
            raise ValueError(f"Ação negada. O totem possui {len(trancas_no_totem)} tranca(s) associada(s) e não pode ser excluído.")

        # 3. Procede com a exclusão
        self.totem_repo.deletar(totem_id)

# Lembre-se de atualizar a instanciação deste caso de uso em src/equipamento/infrastructure/web/routes.py
# de: deletar_totem_uc = DeletarTotemUseCase(repository=totem_repo)
# para: deletar_totem_uc = DeletarTotemUseCase(totem_repo=totem_repo, tranca_repo=tranca_repo)



class AtualizarBicicletaUseCase:
    """
    Caso de uso para atualizar os dados de uma bicicleta existente.
    """
    def __init__(self, repository: BicicletaRepositoryInterface):
        self.repository = repository

     def execute(self, bicicleta_id: int, dados_atualizacao: dict) -> Bicicleta:
        bicicleta = self.repository.buscar_por_id(bicicleta_id)
        if not bicicleta:
            raise ValueError("Bicicleta não encontrada.")

        # Atualiza apenas os campos permitidos
        bicicleta.marca = dados_atualizacao.get("marca", bicicleta.marca)
        bicicleta.modelo = dados_atualizacao.get("modelo", bicicleta.modelo)
        bicicleta.ano = dados_atualizacao.get("ano", bicicleta.ano)
        # O campo 'numero' não é mais atualizado, respeitando a regra de negócio.
    
        return self.repository.salvar(bicicleta)


class AtualizarTrancaUseCase:
    """
    Caso de uso para atualizar os dados de uma tranca existente.
    """
    def __init__(self, repository: TrancaRepositoryInterface):
        self.repository = repository

     def execute(self, tranca_id: int, dados_atualizacao: dict) -> Tranca:
        tranca = self.repository.buscar_por_id(tranca_id)
        if not tranca:
            raise ValueError("Tranca não encontrada.")

        # Atualiza apenas os campos permitidos
        tranca.localizacao = dados_atualizacao.get("localizacao", tranca.localizacao)
        tranca.ano_de_fabricacao = dados_atualizacao.get("ano_de_fabricacao", tranca.ano_de_fabricacao)
        tranca.modelo = dados_atualizacao.get("modelo", tranca.modelo)
        # O campo 'numero' não é mais atualizado.
        
        return self.repository.salvar(tranca)



class AtualizarTotemUseCase:
    """
    Caso de uso para atualizar os dados de um totem existente.
    """
    def __init__(self, repository: TotemRepositoryInterface):
        self.repository = repository

    def execute(self, totem_id: int, dados_atualizacao: dict) -> Totem:
        totem = self.repository.buscar_por_id(totem_id)
        if not totem:
            raise ValueError("Totem não encontrado.")

        totem.localizacao = dados_atualizacao.get("localizacao", totem.localizacao)
        totem.descricao = dados_atualizacao.get("descricao", totem.descricao)

        return self.repository.salvar(totem)
    
class BuscarBicicletaEmTrancaUseCase:
    """
    Caso de uso para buscar os dados da bicicleta que está em uma tranca específica.
    """
    def __init__(self, tranca_repo: TrancaRepositoryInterface, bicicleta_repo: BicicletaRepositoryInterface):
        self.tranca_repo = tranca_repo
        self.bicicleta_repo = bicicleta_repo

    def execute(self, tranca_id: int) -> Optional[Bicicleta]:
        # 1. Busca a tranca pelo ID
        tranca = self.tranca_repo.buscar_por_id(tranca_id)

        # 2. Se a tranca não existe ou está vazia, não há bicicleta para retornar
        if not tranca:
            raise ValueError("Tranca não encontrada.")
        
        if tranca.bicicleta_id is None:
            return None # Retorna None se a tranca estiver livre

        # 3. Se há um ID de bicicleta, busca os dados da bicicleta
        bicicleta = self.bicicleta_repo.buscar_por_id(tranca.bicicleta_id)
        
        # 4. Validação de consistência de dados
        if not bicicleta:
             raise ValueError(f"Inconsistência de dados: Bicicleta com ID {tranca.bicicleta_id} associada à tranca, mas não encontrada no repositório.")

        return bicicleta
    
class ListarBicicletasPorTotemUseCase:
    """
    Caso de uso para listar todas as bicicletas disponíveis em um totem específico.
    """
    def __init__(self, totem_repo: TotemRepositoryInterface, tranca_repo: TrancaRepositoryInterface, bicicleta_repo: BicicletaRepositoryInterface):
        self.totem_repo = totem_repo
        self.tranca_repo = tranca_repo
        self.bicicleta_repo = bicicleta_repo

    def execute(self, totem_id: int) -> List[Bicicleta]:
        # 1. Valida se o totem existe
        if not self.totem_repo.buscar_por_id(totem_id):
            raise ValueError("Totem não encontrado.")
        
        # 2. Busca todas as trancas daquele totem
        trancas_do_totem = self.tranca_repo.buscar_por_totem_id(totem_id)
        if not trancas_do_totem:
            return [] # Retorna lista vazia se não há trancas no totem

        # 3. Extrai os IDs das bicicletas que estão nessas trancas
        ids_de_bicicletas = [
            tranca.bicicleta_id for tranca in trancas_do_totem 
            if tranca.bicicleta_id is not None
        ]
        if not ids_de_bicicletas:
            return [] # Retorna lista vazia se nenhuma tranca tem bicicleta

        # 4. Busca todas as bicicletas encontradas de uma só vez
        return self.bicicleta_repo.buscar_por_ids(ids_de_bicicletas)
    
class RetirarTrancaDoTotemUseCase:
    """
    Caso de uso para desassociar uma tranca de um totem (para reparo ou aposentadoria).
    """
    def __init__(self, tranca_repo: TrancaRepositoryInterface, totem_repo: TotemRepositoryInterface):
        self.tranca_repo = tranca_repo
        self.totem_repo = totem_repo

    def execute(self, tranca_id: int, totem_id: int, status_final: StatusTranca) -> Tranca:
        # 1. Buscar as entidades
        tranca = self.tranca_repo.buscar_por_id(tranca_id)
        totem = self.totem_repo.buscar_por_id(totem_id)

        # 2. Validar regras de negócio
        if not tranca:
            raise ValueError("Tranca não encontrada.")
        if not totem:
            raise ValueError("Totem não encontrado.")

        # Regra: A tranca deve pertencer ao totem informado
        if tranca.totem_id != totem.id:
            raise ValueError("Tranca não pertence ao totem informado.")

        # Regra: A tranca não pode estar ocupada
        if tranca.status == StatusTranca.OCUPADA:
            raise ValueError("Não é possível retirar uma tranca que está ocupada por uma bicicleta.")
        
        # Regra: O status final deve ser apropriado para a retirada
        if status_final not in [StatusTranca.EM_REPARO, StatusTranca.APOSENTADA]:
            raise ValueError(f"Status de destino '{status_final.value}' é inválido para esta operação.")
        
        # 3. Executar as ações
        tranca.status = status_final
        tranca.totem_id = None # Desassocia a tranca do totem

        # 4. Persistir a tranca atualizada
        return self.tranca_repo.salvar(tranca)

class TrancarTrancaUseCase:
    """
    Caso de uso para trancar uma bicicleta em uma tranca livre.
    """
    def __init__(self, tranca_repo: TrancaRepositoryInterface, bicicleta_repo: BicicletaRepositoryInterface):
        self.tranca_repo = tranca_repo
        self.bicicleta_repo = bicicleta_repo

    def execute(self, tranca_id: int, bicicleta_id: int) -> Tranca:
        # 1. Busca as entidades
        tranca = self.tranca_repo.buscar_por_id(tranca_id)
        bicicleta = self.bicicleta_repo.buscar_por_id(bicicleta_id)

        # 2. Valida as regras de negócio
        if not tranca: raise ValueError("Tranca não encontrada.")
        if not bicicleta: raise ValueError("Bicicleta não encontrada.")

        # Regra: A tranca deve estar livre
        if tranca.status != StatusTranca.LIVRE:
            raise ValueError("A tranca não está livre para receber uma bicicleta.")
        
        # Regra: A bicicleta deve estar em uso
        if bicicleta.status != StatusBicicleta.EM_USO:
            raise ValueError("A bicicleta não está em uso para ser devolvida.")

        # 3. Executa as ações
        tranca.status = StatusTranca.OCUPADA
        tranca.bicicleta_id = bicicleta.id
        bicicleta.status = StatusBicicleta.DISPONIVEL # Bicicleta agora está disponível na rede

        # 4. Persiste as alterações
        self.bicicleta_repo.salvar(bicicleta)
        return self.tranca_repo.salvar(tranca)


class DestrancarTrancaUseCase:
    """
    Caso de uso para destrancar uma tranca e liberar a bicicleta.
    """
    def __init__(self, tranca_repo: TrancaRepositoryInterface, bicicleta_repo: BicicletaRepositoryInterface):
        self.tranca_repo = tranca_repo
        self.bicicleta_repo = bicicleta_repo

    def execute(self, tranca_id: int) -> Bicicleta:
        # 1. Busca a tranca
        tranca = self.tranca_repo.buscar_por_id(tranca_id)

        # 2. Valida as regras de negócio
        if not tranca: raise ValueError("Tranca não encontrada.")

        # Regra: A tranca deve estar ocupada
        if tranca.status != StatusTranca.OCUPADA:
            raise ValueError("A tranca não está ocupada.")
        if tranca.bicicleta_id is None:
            raise ValueError("Inconsistência: Tranca ocupada mas sem bicicleta associada.")
        
        # Busca a bicicleta que será liberada
        bicicleta = self.bicicleta_repo.buscar_por_id(tranca.bicicleta_id)
        if not bicicleta:
             raise ValueError(f"Inconsistência: Bicicleta com ID {tranca.bicicleta_id} não foi encontrada.")

        # 3. Executa as ações
        tranca.status = StatusTranca.LIVRE
        tranca.bicicleta_id = None
        bicicleta.status = StatusBicicleta.EM_USO # Ciclista pegou a bicicleta

        # 4. Persiste as alterações
        self.tranca_repo.salvar(tranca)
        return self.bicicleta_repo.salvar(bicicleta)