# src/equipamento/infrastructure/web/routes.py

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel

from ..repositories.mem_repository import (
    MemBicicletaRepository,
    MemTrancaRepository, 
    MemTotemRepository
)
from ...application.use_cases import ( 
    CadastrarBicicletaUseCase,
    ListarBicicletasUseCase,
    BuscarBicicletaPorIdUseCase,
    DeletarBicicletaUseCase,
    AlterarStatusBicicletaUseCase,
    IntegrarBicicletaNaRedeUseCase,
    RetirarBicicletaDaRedeUseCase,
    AtualizarBicicletaUseCase,
    CadastrarTrancaUseCase,
    ListarTrancasUseCase,
    BuscarTrancaPorIdUseCase,
    DeletarTrancaUseCase,
    AlterarStatusTrancaUseCase,
    IntegrarTrancaNoTotemUseCase,
    RetirarTrancaDoTotemUseCase,
    AtualizarTrancaUseCase,
    ListarTrancasPorTotemUseCase,
    BuscarBicicletaEmTrancaUseCase,
    TrancarTrancaUseCase,
    DestrancarTrancaUseCase,
    CadastrarTotemUseCase,
    ListarTotensUseCase,
    BuscarTotemPorIdUseCase,
    DeletarTotemUseCase,
    AtualizarTotemUseCase,
    ListarBicicletasPorTotemUseCase,
    RestaurarDadosUseCase,
)
from ...domain.entities import StatusBicicleta, StatusTranca 

# ===================================================================
# Constantes
# ===================================================================
INCLUDE_DELETED_DESCRIPTION = "Incluir itens deletados na lista"

# ===================================================================
# Pydantic Models
# ===================================================================

class BicicletaCreate(BaseModel): 
    marca: str
    modelo: str
    ano: str
    numero: int

class BicicletaResponse(BaseModel):
    id: int
    marca: str
    modelo: str
    ano: str
    numero: int
    status: StatusBicicleta
    is_deleted: bool

class IntegrarBicicletaRequest(BaseModel):
    idBicicleta: int
    idTranca: int

class RetirarBicicletaRequest(BaseModel):
    idBicicleta: int
    idTranca: int
    statusAcaoReparador: StatusBicicleta

class TrancaCreate(BaseModel): 
    numero: int
    localizacao: str
    ano_de_fabricacao: str
    modelo: str

class TrancaResponse(BaseModel):
    id: int
    numero: int
    localizacao: str
    ano_de_fabricacao: str
    modelo: str
    status: StatusTranca
    bicicleta_id: Optional[int] = None
    is_deleted: bool

class IntegrarTrancaRequest(BaseModel):
    idTranca: int
    idTotem: int
    idFuncionario: int

class RetirarTrancaRequest(BaseModel):
    idTranca: int
    idTotem: int
    statusAcaoReparador: StatusTranca

class AcaoBicicletaRequest(BaseModel):
    bicicleta: int

class TotemCreate(BaseModel): 
    localizacao: str
    descricao: str

class TotemResponse(BaseModel):
    id: int
    localizacao: str
    descricao: str
    tranca_ids: List[int] = []
    is_deleted: bool

# ===================================================================
# Montagem das dependências (Wiring)
# ===================================================================

bicicleta_repo = MemBicicletaRepository()
tranca_repo = MemTrancaRepository()
totem_repo = MemTotemRepository()

cadastrar_bicicleta_uc = CadastrarBicicletaUseCase(repository=bicicleta_repo)
listar_bicicletas_uc = ListarBicicletasUseCase(repository=bicicleta_repo)
buscar_bicicleta_uc = BuscarBicicletaPorIdUseCase(repository=bicicleta_repo)
deletar_bicicleta_uc = DeletarBicicletaUseCase(repository=bicicleta_repo)
integrar_bicicleta_uc = IntegrarBicicletaNaRedeUseCase(bicicleta_repo=bicicleta_repo, tranca_repo=tranca_repo)
retirar_bicicleta_uc = RetirarBicicletaDaRedeUseCase(bicicleta_repo=bicicleta_repo, tranca_repo=tranca_repo)
alterar_status_bicicleta_uc = AlterarStatusBicicletaUseCase(repository=bicicleta_repo) 

cadastrar_tranca_uc = CadastrarTrancaUseCase(repository=tranca_repo)
listar_trancas_uc = ListarTrancasUseCase(repository=tranca_repo)
buscar_tranca_uc = BuscarTrancaPorIdUseCase(repository=tranca_repo)
deletar_tranca_uc = DeletarTrancaUseCase(repository=tranca_repo)
alterar_status_tranca_uc = AlterarStatusTrancaUseCase(repository=tranca_repo)
listar_trancas_por_totem_uc = ListarTrancasPorTotemUseCase(totem_repo=totem_repo, tranca_repo=tranca_repo)
integrar_tranca_uc = IntegrarTrancaNoTotemUseCase(tranca_repo=tranca_repo, totem_repo=totem_repo)
buscar_bicicleta_em_tranca_uc = BuscarBicicletaEmTrancaUseCase(tranca_repo=tranca_repo, bicicleta_repo=bicicleta_repo)
retirar_tranca_uc = RetirarTrancaDoTotemUseCase(tranca_repo=tranca_repo, totem_repo=totem_repo)
trancar_tranca_uc = TrancarTrancaUseCase(tranca_repo=tranca_repo, bicicleta_repo=bicicleta_repo)
destrancar_tranca_uc = DestrancarTrancaUseCase(tranca_repo=tranca_repo, bicicleta_repo=bicicleta_repo)

cadastrar_totem_uc = CadastrarTotemUseCase(repository=totem_repo)
listar_totens_uc = ListarTotensUseCase(repository=totem_repo)
buscar_totem_uc = BuscarTotemPorIdUseCase(repository=totem_repo)
deletar_totem_uc = DeletarTotemUseCase(repository=totem_repo)
listar_bicicletas_por_totem_uc = ListarBicicletasPorTotemUseCase(
    totem_repo=totem_repo,
    tranca_repo=tranca_repo,
    bicicleta_repo=bicicleta_repo
)

restaurar_dados_uc = RestaurarDadosUseCase(
    bicicleta_repo=bicicleta_repo,
    tranca_repo=tranca_repo,
    totem_repo=totem_repo
)

atualizar_bicicleta_uc = AtualizarBicicletaUseCase(repository=bicicleta_repo)
atualizar_tranca_uc = AtualizarTrancaUseCase(repository=tranca_repo)
atualizar_totem_uc = AtualizarTotemUseCase(repository=totem_repo)

router = APIRouter()

# ===================================================================
# Rotas da API
# ===================================================================

# --- Rotas para Bicicletas ---
@router.post("/bicicleta", response_model=BicicletaResponse, status_code=status.HTTP_201_CREATED, tags=["Bicicletas"])
def cadastrar_bicicleta(data: BicicletaCreate):
    bicicleta = cadastrar_bicicleta_uc.execute(data.model_dump())
    return bicicleta

@router.get("/bicicleta", response_model=List[BicicletaResponse], tags=["Bicicletas"])
def listar_bicicletas(include_deleted: bool = Query(False, description=INCLUDE_DELETED_DESCRIPTION)):
    return listar_bicicletas_uc.execute(include_deleted=include_deleted)

@router.get("/bicicleta/{bicicleta_id}", response_model=BicicletaResponse, tags=["Bicicletas"])
def buscar_bicicleta(bicicleta_id: int):
    bicicleta = buscar_bicicleta_uc.execute(bicicleta_id)
    if not bicicleta: raise HTTPException(status.HTTP_404_NOT_FOUND, "Bicicleta não encontrada.")
    return bicicleta

@router.delete("/bicicleta/{bicicleta_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Bicicletas"])
def deletar_bicicleta(bicicleta_id: int):
    deletar_bicicleta_uc.execute(bicicleta_id)

@router.post("/bicicleta/integrarNaRede", response_model=TrancaResponse, tags=["Ações"])
def integrar_bicicleta_na_rede(data: IntegrarBicicletaRequest):
    try:
        tranca = integrar_bicicleta_uc.execute(bicicleta_id=data.idBicicleta, tranca_id=data.idTranca, funcionario_id=data.idFuncionario)
        return tranca
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
@router.post("/bicicleta/retirarDaRede", response_model=BicicletaResponse, tags=["Ações"])
def retirar_bicicleta_da_rede(data: RetirarBicicletaRequest):
    try:
        bicicleta = retirar_bicicleta_uc.execute(
            bicicleta_id=data.idBicicleta,
            tranca_id=data.idTranca,
            status_final=data.statusAcaoReparador,
            funcionario_id=data.idFuncionario
        )
        return bicicleta
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
@router.post("/bicicleta/{idBicicleta}/status/{acao}", response_model=BicicletaResponse, tags=["Bicicletas"])
def alterar_status_bicicleta(idBicicleta: int, acao: StatusBicicleta):
    """
    Altera o status de uma bicicleta específica.
    """
    try:
        bicicleta = alterar_status_bicicleta_uc.execute(
            bicicleta_id=idBicicleta,
            novo_status=acao
        )
        return bicicleta
    except ValueError as e:
        # Retorna 404 se a bicicleta não for encontrada
        if "não encontrada" in str(e):
             raise HTTPException(status_code=404, detail={"codigo": "NAO_ENCONTRADO", "mensagem": str(e)})
        # Retorna 422 para outras violações de regras de negócio
        raise HTTPException(status_code=422, detail={"codigo": "DADOS_INVALIDOS", "mensagem": str(e)})

    
@router.put("/bicicleta/{idBicicleta}", response_model=BicicletaResponse, tags=["Bicicletas"])
def atualizar_bicicleta(idBicicleta: int, data: BicicletaCreate):
    try:
        bicicleta = atualizar_bicicleta_uc.execute(idBicicleta, data.model_dump())
        return bicicleta
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# --- Rotas para Trancas ---
@router.post("/tranca", response_model=TrancaResponse, status_code=status.HTTP_201_CREATED, tags=["Trancas"])
def cadastrar_tranca(data: TrancaCreate):
    tranca = cadastrar_tranca_uc.execute(data.model_dump())
    return tranca

@router.get("/tranca", response_model=List[TrancaResponse], tags=["Trancas"])
def listar_trancas(include_deleted: bool = Query(False, description=INCLUDE_DELETED_DESCRIPTION)):
    return listar_trancas_uc.execute(include_deleted=include_deleted)

@router.get("/tranca/{idTranca}", response_model=TrancaResponse, tags=["Trancas"])
def buscar_tranca(idTranca: int):
    tranca = buscar_tranca_uc.execute(idTranca)
    if not tranca: raise HTTPException(status.HTTP_404_NOT_FOUND, "Tranca não encontrada")
    return tranca

@router.delete("/tranca/{idTranca}", status_code=status.HTTP_204_NO_CONTENT, tags=["Trancas"])
def deletar_tranca(idTranca: int):
    deletar_tranca_uc.execute(idTranca)

@router.post("/tranca/{idTranca}/status/{acao}", response_model=TrancaResponse, tags=["Trancas"])
def alterar_status_tranca(idTranca: int, acao: StatusTranca):
    try:
        tranca = alterar_status_tranca_uc.execute(idTranca=idTranca, novo_status=acao)
        return tranca
    except ValueError as e:
        if "não encontrada" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
@router.post("/tranca/integrarNaRede", response_model=TrancaResponse, tags=["Ações"])
def integrar_tranca_na_rede(data: IntegrarTrancaRequest):
    """
    Coloca uma tranca nova ou retornando de reparo de volta na rede de totens.
    """
    try:
        # O idFuncionario é recebido mas não utilizado na lógica atual deste microsserviço.
        tranca = integrar_tranca_uc.execute(
            tranca_id=data.idTranca,
            totem_id=data.idTotem,
            funcionario_id=data.idFuncionario
        )
        return tranca
    except ValueError as e:
        raise HTTPException(status_code=422, detail={"codigo": "DADOS_INVALIDOS", "mensagem": str(e)})

@router.put("/tranca/{idTranca}", response_model=TrancaResponse, tags=["Trancas"])
def atualizar_tranca(idTranca: int, data: TrancaCreate):
    try:
        tranca = atualizar_tranca_uc.execute(idTranca, data.model_dump())
        return tranca
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@router.get("/tranca/{idTranca}/bicicleta", response_model=BicicletaResponse, tags=["Trancas"])
def buscar_bicicleta_na_tranca(idTranca: int):
    try:
        bicicleta = buscar_bicicleta_em_tranca_uc.execute(idTranca)
        if not bicicleta:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Nenhuma bicicleta encontrada na tranca.")
        return bicicleta
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@router.post("/tranca/retirarDaRede", response_model=TrancaResponse, tags=["Ações"])
def retirar_tranca_do_totem(data: RetirarTrancaRequest):
    try:
        tranca = retirar_tranca_uc.execute(
            tranca_id=data.idTranca,
            totem_id=data.idTotem,
            status_final=data.statusAcaoReparador,
            funcionario_id=data.idFuncionario
        )
        return tranca
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
@router.post("/tranca/{idTranca}/trancar", response_model=TrancaResponse, tags=["Ações"])
def trancar_tranca(idTranca: int, data: AcaoBicicletaRequest):
    try:
        tranca = trancar_tranca_uc.execute(tranca_id=idTranca, bicicleta_id=data.bicicleta)
        return tranca
    except ValueError as e:
        raise HTTPException(status_code=422, detail={"codigo": "DADOS_INVALIDOS", "mensagem": str(e)})


@router.post("/tranca/{idTranca}/destrancar", response_model=TrancaResponse, tags=["Ações"])
def destrancar_tranca(idTranca: int, data: Optional[AcaoBicicletaRequest] = None):
    """
    Realiza o destrancamento de uma bicicleta de uma tranca.
    O corpo da requisição é opcional e não é utilizado pela lógica.
    """
    try:
        tranca = destrancar_tranca_uc.execute(tranca_id=idTranca)
        return tranca
    except ValueError as e:
        raise HTTPException(status_code=422, detail={"codigo": "DADOS_INVALIDOS", "mensagem": str(e)})

# --- Rotas para Totens ---
@router.post("/totem", response_model=TotemResponse, status_code=status.HTTP_201_CREATED, tags=["Totens"])
def cadastrar_totem(data: TotemCreate):
    totem = cadastrar_totem_uc.execute(data.model_dump())
    return totem

@router.get("/totem", response_model=List[TotemResponse], tags=["Totens"])
def listar_totens(include_deleted: bool = Query(False, description=INCLUDE_DELETED_DESCRIPTION)):
    return listar_totens_uc.execute(include_deleted=include_deleted)

@router.get("/totem/{idTotem}", response_model=TotemResponse, tags=["Totens"])
def buscar_totem(idTotem: int):
    totem = buscar_totem_uc.execute(idTotem)
    if not totem: raise HTTPException(status.HTTP_404_NOT_FOUND, "Totem não encontrado")
    return totem

@router.delete("/totem/{idTotem}", status_code=status.HTTP_204_NO_CONTENT, tags=["Totens"])
def deletar_totem(idTotem: int):
    deletar_totem_uc.execute(idTotem)

@router.get("/totem/{idTotem}/trancas", response_model=List[TrancaResponse], tags=["Totens"])
def listar_trancas_do_totem(idTotem: int):
    try:
        trancas = listar_trancas_por_totem_uc.execute(idTotem)
        return trancas
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@router.put("/totem/{idTotem}", response_model=TotemResponse, tags=["Totens"])
def atualizar_totem(idTotem: int, data: TotemCreate):
    try:
        totem = atualizar_totem_uc.execute(idTotem, data.model_dump())
        return totem
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@router.get("/totem/{idTotem}/bicicletas", response_model=List[BicicletaResponse], tags=["Totens"])
def listar_bicicletas_do_totem(idTotem: int):
    try:
        bicicletas = listar_bicicletas_por_totem_uc.execute(idTotem)
        return bicicletas
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@router.post("/tranca/{idTranca}/status/{acao}", response_model=TrancaResponse, tags=["Trancas"])
def alterar_status_tranca(idTranca: int, acao: StatusTranca):
    """
    Altera o status de uma tranca (ex: para NOVA, EM_REPARO, APOSENTADA).
    """
    try:
        tranca = alterar_status_tranca_uc.execute(
            tranca_id=idTranca,
            novo_status=acao
        )
        return tranca
    except ValueError as e:
        if "não encontrada" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
    
@router.get("/restaurarDados", status_code=status.HTTP_200_OK, tags=["Testes"])
def restaurar_dados():
    """
    Restaura a base de dados em memória para o estado inicial predefinido.
    Útil para garantir um estado limpo antes de executar testes automatizados.
    """
    try:
        restaurar_dados_uc.execute()
        return {"message": "Dados restaurados para o estado inicial com sucesso."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro ao restaurar os dados: {e}"
        )

