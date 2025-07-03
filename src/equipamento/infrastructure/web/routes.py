# src/equipamento/infrastructure/web/routes.py (VERSÃO COMPLETA)

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ..repositories.mem_repository import (
    MemBicicletaRepository,
    MemTrancaRepository, 
    MemTotemRepository
)
from ...application.use_cases import * # Importa todos os casos de uso
from ...domain.entities import * # Importa todas as entidades e enums

# ===================================================================
# Pydantic Models
# ===================================================================

# --- Modelos para Bicicleta ---
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

class IntegrarBicicletaRequest(BaseModel):
    idBicicleta: int
    idTranca: int

class RetirarBicicletaRequest(BaseModel):
    idBicicleta: int
    idTranca: int
    statusAcaoReparador: StatusBicicleta

# --- Modelos para Tranca ---
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

class IntegrarTrancaRequest(BaseModel):
    idTranca: int
    idTotem: int

class RetirarTrancaRequest(BaseModel):
    idTranca: int
    idTotem: int
    statusAcaoReparador: StatusTranca # Ex: "EM_REPARO" ou "APOSENTADA"

class TrancarRequest(BaseModel):
    idBicicleta: int

# --- Modelos para Totem ---
class TotemCreate(BaseModel):
    localizacao: str
    descricao: str

class TotemResponse(BaseModel):
    id: int
    localizacao: str
    descricao: str
    tranca_ids: List[int] = []

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
alterar_status_bicicleta_uc = AlterarStatusBicicletaUseCase(repository=bicicleta_repo) # type: ignore


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

atualizar_bicicleta_uc = AtualizarBicicletaUseCase(repository=bicicleta_repo)
atualizar_tranca_uc = AtualizarTrancaUseCase(repository=tranca_repo)
atualizar_totem_uc = AtualizarTotemUseCase(repository=totem_repo)

router = APIRouter()

# ===================================================================
# Rotas da API
# ===================================================================

# --- Rotas para Bicicletas ---
@router.post("/bicicletas", response_model=BicicletaResponse, status_code=status.HTTP_201_CREATED, tags=["Bicicletas"])
def cadastrar_bicicleta(data: BicicletaCreate):
    bicicleta = cadastrar_bicicleta_uc.execute(data.model_dump())
    return bicicleta

@router.get("/bicicletas", response_model=List[BicicletaResponse], tags=["Bicicletas"])
def listar_bicicletas():
    return listar_bicicletas_uc.execute()

@router.get("/bicicletas/{bicicleta_id}", response_model=BicicletaResponse, tags=["Bicicletas"])
def buscar_bicicleta(bicicleta_id: int):
    bicicleta = buscar_bicicleta_uc.execute(bicicleta_id)
    if not bicicleta: raise HTTPException(status.HTTP_404_NOT_FOUND, "Bicicleta não encontrada.")
    return bicicleta

@router.delete("/bicicletas/{bicicleta_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Bicicletas"])
def deletar_bicicleta(bicicleta_id: int):
    deletar_bicicleta_uc.execute(bicicleta_id)

@router.post("/bicicletas/integrar-na-rede", response_model=TrancaResponse, tags=["Ações"])
def integrar_bicicleta_na_rede(data: IntegrarBicicletaRequest):
    """
    Coloca uma bicicleta de volta na rede, associando-a a uma tranca livre.
    """
    try:
        tranca = integrar_bicicleta_uc.execute(
            bicicleta_id=data.idBicicleta,
            tranca_id=data.idTranca
        )
        return tranca
    except ValueError as e:
        # Se as regras de negócio do caso de uso falharem, retorna um erro 422
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    

@router.post("/bicicletas/retirar-da-rede", response_model=BicicletaResponse, tags=["Ações"])
def retirar_bicicleta_da_rede(data: RetirarBicicletaRequest):
    """
    Retira uma bicicleta da rede (de uma tranca) para reparo ou aposentadoria.
    """
    try:
        bicicleta = retirar_bicicleta_uc.execute(
            bicicleta_id=data.idBicicleta,
            tranca_id=data.idTranca,
            status_final=data.statusAcaoReparador
        )
        return bicicleta
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    

@router.post("/bicicletas/{bicicleta_id}/status/{novo_status}", response_model=BicicletaResponse, tags=["Bicicletas"])
def alterar_status_bicicleta(bicicleta_id: int, novo_status: StatusBicicleta):
    """
    Altera o status de uma bicicleta específica.
    """
    try:
        bicicleta = alterar_status_bicicleta_uc.execute(
            bicicleta_id=bicicleta_id,
            novo_status=novo_status
        )
        return bicicleta
    except ValueError as e:
        # O único ValueError que nosso caso de uso levanta é de não encontrar a bicicleta.
        # Portanto, o status 404 Not Found é o mais apropriado.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@router.put("/bicicletas/{bicicleta_id}", response_model=BicicletaResponse, tags=["Bicicletas"])
def atualizar_bicicleta(bicicleta_id: int, data: BicicletaCreate):
    try:
        bicicleta = atualizar_bicicleta_uc.execute(bicicleta_id, data.model_dump())
        return bicicleta
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# --- Rotas para Trancas ---
@router.post("/trancas", response_model=TrancaResponse, status_code=status.HTTP_201_CREATED, tags=["Trancas"])
def cadastrar_tranca(data: TrancaCreate):
    tranca = cadastrar_tranca_uc.execute(data.model_dump())
    return tranca

@router.get("/trancas", response_model=List[TrancaResponse], tags=["Trancas"])
def listar_trancas():
    return listar_trancas_uc.execute()

@router.get("/trancas/{tranca_id}", response_model=TrancaResponse, tags=["Trancas"])
def buscar_tranca(tranca_id: int):
    tranca = buscar_tranca_uc.execute(tranca_id)
    if not tranca: raise HTTPException(status.HTTP_404_NOT_FOUND, "Tranca não encontrada")
    return tranca

@router.delete("/trancas/{tranca_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Trancas"])
def deletar_tranca(tranca_id: int):
    deletar_tranca_uc.execute(tranca_id)

@router.post("/trancas/{tranca_id}/status/{novo_status}", response_model=TrancaResponse, tags=["Trancas"])
def alterar_status_tranca(tranca_id: int, novo_status: StatusTranca):
    """
    Altera o status de uma tranca (ex: para NOVA, EM_REPARO, APOSENTADA).
    """
    try:
        tranca = alterar_status_tranca_uc.execute(
            tranca_id=tranca_id,
            novo_status=novo_status
        )
        return tranca
    except ValueError as e:
        # Se o ID não for encontrado, retornamos 404.
        if "não encontrada" in str(e):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        # Para outras violações de regras de negócio, 422 é mais apropriado.
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
@router.post("/trancas/integrar-na-rede", response_model=TrancaResponse, tags=["Ações"])
def integrar_tranca_no_totem(data: IntegrarTrancaRequest):
    """
    Associa uma tranca a um totem, tornando-a operacional.
    """
    try:
        tranca = integrar_tranca_uc.execute(
            tranca_id=data.idTranca,
            totem_id=data.idTotem
        )
        return tranca
    except ValueError as e:
        # Erros de regras de negócio (ex: tranca já integrada)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
@router.put("/trancas/{tranca_id}", response_model=TrancaResponse, tags=["Trancas"])
def atualizar_tranca(tranca_id: int, data: TrancaCreate):
    try:
        tranca = atualizar_tranca_uc.execute(tranca_id, data.model_dump())
        return tranca
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@router.get("/trancas/{tranca_id}/bicicleta", response_model=BicicletaResponse, tags=["Trancas"])
def buscar_bicicleta_na_tranca(tranca_id: int):
    """
    Obtém os dados da bicicleta que está na tranca especificada.
    """
    try:
        bicicleta = buscar_bicicleta_em_tranca_uc.execute(tranca_id)
        if not bicicleta:
            # Isso acontece se a tranca existe mas está livre
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma bicicleta encontrada na tranca.")
        return bicicleta
    except ValueError as e:
        # Isso acontece se a tranca não for encontrada ou houver inconsistência
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@router.post("/trancas/retirar-da-rede", response_model=TrancaResponse, tags=["Ações"])
def retirar_tranca_do_totem(data: RetirarTrancaRequest):
    """
    Desassocia uma tranca de um totem (para reparo ou aposentadoria).
    """
    try:
        tranca = retirar_tranca_uc.execute(
            tranca_id=data.idTranca,
            totem_id=data.idTotem,
            status_final=data.statusAcaoReparador
        )
        return tranca
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
@router.post("/trancas/{tranca_id}/trancar", response_model=TrancaResponse, tags=["Ações"])
def trancar_tranca(tranca_id: int, data: TrancarRequest):
    """
    Tranca uma bicicleta em uma tranca específica.
    """
    try:
        tranca = trancar_tranca_uc.execute(tranca_id=tranca_id, bicicleta_id=data.idBicicleta)
        return tranca
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.post("/trancas/{tranca_id}/destrancar", response_model=BicicletaResponse, tags=["Ações"])
def destrancar_tranca(tranca_id: int):
    """
    Destranca uma tranca, liberando a bicicleta para uso.
    """
    try:
        bicicleta = destrancar_tranca_uc.execute(tranca_id)
        return bicicleta
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

# --- Rotas para Totens ---
@router.post("/totens", response_model=TotemResponse, status_code=status.HTTP_201_CREATED, tags=["Totens"])
def cadastrar_totem(data: TotemCreate):
    totem = cadastrar_totem_uc.execute(data.model_dump())
    return totem

@router.get("/totens", response_model=List[TotemResponse], tags=["Totens"])
def listar_totens():
    return listar_totens_uc.execute()

@router.get("/totens/{totem_id}", response_model=TotemResponse, tags=["Totens"])
def buscar_totem(totem_id: int):
    totem = buscar_totem_uc.execute(totem_id)
    if not totem: raise HTTPException(status.HTTP_404_NOT_FOUND, "Totem não encontrado")
    return totem

@router.delete("/totens/{totem_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Totens"])
def deletar_totem(totem_id: int):
    deletar_totem_uc.execute(totem_id)

@router.get("/totens/{totem_id}/trancas", response_model=List[TrancaResponse], tags=["Totens"])
def listar_trancas_do_totem(totem_id: int):
    """
    Lista todas as trancas de um totem específico.
    """
    try:
        trancas = listar_trancas_por_totem_uc.execute(totem_id)
        return trancas
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@router.put("/totens/{totem_id}", response_model=TotemResponse, tags=["Totens"])
def atualizar_totem(totem_id: int, data: TotemCreate):
    try:
        totem = atualizar_totem_uc.execute(totem_id, data.model_dump())
        return totem
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    
@router.get("/totens/{totem_id}/bicicletas", response_model=List[BicicletaResponse], tags=["Totens"])
def listar_bicicletas_do_totem(totem_id: int):
    """
    Lista todas as bicicletas que estão nas trancas de um totem específico.
    """
    try:
        bicicletas = listar_bicicletas_por_totem_uc.execute(totem_id)
        return bicicletas
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))



