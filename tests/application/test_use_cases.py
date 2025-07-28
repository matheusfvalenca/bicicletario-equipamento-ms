# tests/application/test_use_cases.py

from unittest.mock import MagicMock
import pytest

# Importando o que vamos testar
from src.equipamento.application.use_cases import *
from src.equipamento.domain.entities import Bicicleta, Tranca, Totem, StatusBicicleta, StatusTranca
from src.equipamento.application.repositories import BicicletaRepositoryInterface, TrancaRepositoryInterface, TotemRepositoryInterface

# Constantes de erro para facilitar a verificação das mensagens
ERRO_BICICLETA_NAO_ENCONTRADA = "Bicicleta não encontrada."
ERRO_TRANCA_NAO_ENCONTRADA = "Tranca não encontrada."
ERRO_TOTEM_NAO_ENCONTRADO = "Totem não encontrado."

# ###################################################################
# --- TESTES EXISTENTES (MANTIDOS CONFORME O ORIGINAL) ---
# ###################################################################

def test_cadastrar_bicicleta_deve_criar_com_status_nova_e_chamar_repositorio():
    # Arrange (Arrumar)
    
    # 1. Dados de entrada para o caso de uso
    dados_bicicleta = {
        "marca": "Caloi",
        "modelo": "Ceci",
        "ano": "1992",
        "numero": 12345,
    }

    # 2. Criamos um mock para o repositório. O MagicMock simula qualquer objeto.
    #    Usar 'spec=...' garante que o mock só aceite métodos que existem na interface real.
    mock_repo = MagicMock(spec=BicicletaRepositoryInterface)

    # 3. Definimos o comportamento do mock: quando o método 'salvar' for chamado,
    #    ele deve retornar uma bicicleta com ID e o status correto.
    bicicleta_salva_esperada = Bicicleta(
        id=1,
        status=StatusBicicleta.NOVA,
        **dados_bicicleta # Desempacota o dicionário para preencher o resto
    )
    mock_repo.salvar.return_value = bicicleta_salva_esperada
    
    # 4. Instanciamos o caso de uso, injetando nosso mock no lugar de um repositório real.
    use_case = CadastrarBicicletaUseCase(repository=mock_repo)

    # Act (Agir)
    
    # Executamos o caso de uso com os dados de entrada
    resultado = use_case.execute(dados_bicicleta)

    # Assert (Afirmar)
    
    # 1. Verificamos se o método 'salvar' do nosso mock foi chamado exatamente uma vez.
    mock_repo.salvar.assert_called_once()

    # 2. Pegamos o objeto que foi passado para o método 'salvar' para inspecioná-lo.
    bicicleta_passada_para_salvar = mock_repo.salvar.call_args[0][0]
    
    # 3. Verificamos se o caso de uso criou a entidade corretamente ANTES de salvar.
    assert isinstance(bicicleta_passada_para_salvar, Bicicleta)
    assert bicicleta_passada_para_salvar.status == StatusBicicleta.NOVA # Regra de negócio
    assert bicicleta_passada_para_salvar.marca == "Caloi"

    # 4. Verificamos se o resultado final retornado pelo caso de uso é o mesmo
    #    que o nosso mock foi configurado para retornar.
    assert resultado == bicicleta_salva_esperada
    assert resultado.id == 1 # Confirma que o ID foi atribuído

def test_integrar_bicicleta_na_rede_caminho_feliz():
    # Arrange
    # Precisamos de mocks para DOIS repositórios agora
    mock_bicicleta_repo = MagicMock(spec=BicicletaRepositoryInterface)
    mock_tranca_repo = MagicMock(spec=TrancaRepositoryInterface)

    # Cenário: uma bicicleta 'NOVA' e uma tranca 'LIVRE' existem
    bicicleta_existente = Bicicleta(id=1, marca="Teste", modelo="TS", ano="2024", numero=100, status=StatusBicicleta.NOVA)
    tranca_existente = Tranca(id=1, numero=1, localizacao="Totem 1", ano_de_fabricacao="2024", modelo="T", status=StatusTranca.DISPONIVEL)
    
    mock_bicicleta_repo.buscar_por_id.return_value = bicicleta_existente
    mock_tranca_repo.buscar_por_id.return_value = tranca_existente
    
    # O método 'salvar' da tranca deve retornar a tranca atualizada
    mock_tranca_repo.salvar.side_effect = lambda tranca: tranca
    
    use_case = IntegrarBicicletaNaRedeUseCase(
        bicicleta_repo=mock_bicicleta_repo,
        tranca_repo=mock_tranca_repo
    )

    # Act
    tranca_atualizada = use_case.execute(bicicleta_id=1, tranca_id=1)

    # Assert
    # Verifica se os métodos de busca foram chamados corretamente
    mock_bicicleta_repo.buscar_por_id.assert_called_once_with(1)
    mock_tranca_repo.buscar_por_id.assert_called_once_with(1)

    # Verifica se os métodos de salvar foram chamados para persistir as mudanças
    mock_bicicleta_repo.salvar.assert_called_once()
    mock_tranca_repo.salvar.assert_called_once()
    
    # Verifica o estado final das entidades
    assert tranca_atualizada.status == StatusTranca.OCUPADA
    assert tranca_atualizada.bicicleta_id == 1
    # O objeto bicicleta_existente foi modificado por referência dentro do caso de uso
    assert bicicleta_existente.status == StatusBicicleta.DISPONIVEL


def test_integrar_bicicleta_na_rede_deve_falhar_se_tranca_ocupada():
    # Arrange
    mock_bicicleta_repo = MagicMock(spec=BicicletaRepositoryInterface)
    mock_tranca_repo = MagicMock(spec=TrancaRepositoryInterface)

    # Cenário de erro: a tranca já está OCUPADA
    bicicleta_existente = Bicicleta(id=1, marca="Teste", modelo="TS", ano="2024", numero=100, status=StatusBicicleta.NOVA)
    tranca_ocupada = Tranca(id=1, numero=1, localizacao="Totem 1", ano_de_fabricacao="2024", modelo="T", status=StatusTranca.OCUPADA)
    
    mock_bicicleta_repo.buscar_por_id.return_value = bicicleta_existente
    mock_tranca_repo.buscar_por_id.return_value = tranca_ocupada

    use_case = IntegrarBicicletaNaRedeUseCase(
        bicicleta_repo=mock_bicicleta_repo,
        tranca_repo=mock_tranca_repo
    )

    # Act & Assert
    # Verificamos se o caso de uso levanta a exceção correta
    with pytest.raises(ValueError, match="Tranca não está livre."):
        use_case.execute(bicicleta_id=1, tranca_id=1)

    # Garante que, como a operação falhou, nada foi salvo
    mock_bicicleta_repo.salvar.assert_not_called()
    mock_tranca_repo.salvar.assert_not_called()

def test_integrar_bicicleta_na_rede_deve_falhar_se_bicicleta_nao_encontrada():
    # Arrange
    # 1. Criamos os mocks para os dois repositórios
    mock_bicicleta_repo = MagicMock(spec=BicicletaRepositoryInterface)
    mock_tranca_repo = MagicMock(spec=TrancaRepositoryInterface)

    # 2. Configuramos o cenário de erro:
    #    - A busca pela bicicleta retorna None (não encontrada).
    #    - A busca pela tranca retorna um objeto válido, pois a validação
    #      da bicicleta acontece primeiro no nosso caso de uso.
    mock_bicicleta_repo.buscar_por_id.return_value = None
    tranca_existente = Tranca(id=1, numero=1, localizacao="T", ano_de_fabricacao="2024", modelo="T1", status=StatusTranca.DISPONIVEL)
    mock_tranca_repo.buscar_por_id.return_value = tranca_existente

    # 3. Instanciamos o caso de uso com os mocks
    use_case = IntegrarBicicletaNaRedeUseCase(
        bicicleta_repo=mock_bicicleta_repo,
        tranca_repo=mock_tranca_repo
    )

    # Act & Assert
    # 4. Verificamos se a exceção correta é levantada com a mensagem esperada
    with pytest.raises(ValueError, match="Bicicleta não encontrada."):
        use_case.execute(bicicleta_id=999, tranca_id=1)

    # 5. Garantimos que nenhuma operação de escrita foi realizada
    mock_bicicleta_repo.salvar.assert_not_called()
    mock_tranca_repo.salvar.assert_not_called()

def test_integrar_bicicleta_na_rede_deve_falhar_se_status_da_bicicleta_invalido():
    # Arrange
    # 1. Mocks para os repositórios
    mock_bicicleta_repo = MagicMock(spec=BicicletaRepositoryInterface)
    mock_tranca_repo = MagicMock(spec=TrancaRepositoryInterface)

    # 2. Cenário de erro: a bicicleta existe, a tranca existe e está livre,
    #    mas o STATUS da bicicleta é EM_USO, o que não permite a integração.
    bicicleta_em_uso = Bicicleta(id=1, marca="A", modelo="B", ano="C", numero=1, status=StatusBicicleta.EM_USO)
    tranca_livre = Tranca(id=1, numero=1, localizacao="T", ano_de_fabricacao="2024", modelo="T1", status=StatusTranca.DISPONIVEL)
    
    mock_bicicleta_repo.buscar_por_id.return_value = bicicleta_em_uso
    mock_tranca_repo.buscar_por_id.return_value = tranca_livre

    # 3. Instancia o caso de uso
    use_case = IntegrarBicicletaNaRedeUseCase(
        bicicleta_repo=mock_bicicleta_repo,
        tranca_repo=mock_tranca_repo
    )

    # Act & Assert
    # 4. Verifica se a exceção ValueError é levantada com uma mensagem que
    #    corresponda à nossa regra de negócio. Usar uma parte da mensagem
    #    no 'match' torna o teste mais robusto a pequenas mudanças no texto.
    with pytest.raises(ValueError, match="não pode ser integrada"):
        use_case.execute(bicicleta_id=1, tranca_id=1)

    # 5. Garante que, como a operação falhou, nada foi salvo
    mock_bicicleta_repo.salvar.assert_not_called()
    mock_tranca_repo.salvar.assert_not_called()

def test_retirar_bicicleta_da_rede_deve_falhar_se_tranca_nao_encontrada():
    # Arrange
    # 1. Criamos os mocks para os repositórios
    mock_bicicleta_repo = MagicMock(spec=BicicletaRepositoryInterface)
    mock_tranca_repo = MagicMock(spec=TrancaRepositoryInterface)

    # 2. Configuramos o cenário de erro:
    #    - A bicicleta é encontrada.
    #    - A tranca NÃO é encontrada (retorna None).
    bicicleta_existente = Bicicleta(id=1, marca="A", modelo="B", ano="C", numero=1, status=StatusBicicleta.DISPONIVEL)
    mock_bicicleta_repo.buscar_por_id.return_value = bicicleta_existente
    mock_tranca_repo.buscar_por_id.return_value = None

    # 3. Instanciamos o caso de uso
    use_case = RetirarBicicletaDaRedeUseCase(
        bicicleta_repo=mock_bicicleta_repo,
        tranca_repo=mock_tranca_repo
    )

    # Act & Assert
    # 4. Verificamos se a exceção correta é levantada
    with pytest.raises(ValueError, match="Tranca não encontrada."):
        use_case.execute(
            bicicleta_id=1,
            tranca_id=999, # ID de uma tranca que não existe
            status_final=StatusBicicleta.EM_REPARO
        )
    
    # 5. Garantimos que nenhuma alteração foi salva
    mock_bicicleta_repo.salvar.assert_not_called()
    mock_tranca_repo.salvar.assert_not_called()

def test_retirar_bicicleta_da_rede_caminho_feliz():
    # Arrange
    mock_bicicleta_repo = MagicMock(spec=BicicletaRepositoryInterface)
    mock_tranca_repo = MagicMock(spec=TrancaRepositoryInterface)

    # Cenário: uma bicicleta está em uma tranca OCUPADA
    bicicleta_na_tranca = Bicicleta(id=1, marca="Teste", modelo="TS", ano="2024", numero=100, status=StatusBicicleta.DISPONIVEL)
    tranca_ocupada = Tranca(id=1, numero=1, localizacao="Totem 1", ano_de_fabricacao="2024", modelo="T", status=StatusTranca.OCUPADA, bicicleta_id=1)
    
    mock_bicicleta_repo.buscar_por_id.return_value = bicicleta_na_tranca
    mock_tranca_repo.buscar_por_id.return_value = tranca_ocupada
    
    # Configura os mocks para retornarem o objeto que receberam, simulando um 'save'
    mock_bicicleta_repo.salvar.side_effect = lambda bicicleta: bicicleta
    mock_tranca_repo.salvar.side_effect = lambda tranca: tranca
    
    use_case = RetirarBicicletaDaRedeUseCase(
        bicicleta_repo=mock_bicicleta_repo,
        tranca_repo=mock_tranca_repo
    )

    # Act
    # Vamos retirar a bicicleta para reparo
    bicicleta_retirada = use_case.execute(
        bicicleta_id=1,
        tranca_id=1,
        status_final=StatusBicicleta.EM_REPARO
    )

    # Assert
    # Garante que as buscas foram feitas
    mock_bicicleta_repo.buscar_por_id.assert_called_once_with(1)
    mock_tranca_repo.buscar_por_id.assert_called_once_with(1)

    # Garante que as atualizações foram salvas
    mock_bicicleta_repo.salvar.assert_called_once()
    mock_tranca_repo.salvar.assert_called_once()
    
    # Verifica o estado final das entidades
    assert bicicleta_retirada.status == StatusBicicleta.EM_REPARO
    assert tranca_ocupada.status == StatusTranca.DISPONIVEL
    assert tranca_ocupada.bicicleta_id is None


def test_retirar_bicicleta_da_rede_deve_falhar_se_bicicleta_nao_esta_na_tranca():
    # Arrange
    mock_bicicleta_repo = MagicMock(spec=BicicletaRepositoryInterface)
    mock_tranca_repo = MagicMock(spec=TrancaRepositoryInterface)

    # Cenário de erro: A tranca está ocupada, mas com OUTRA bicicleta (ID 99)
    bicicleta_a_retirar = Bicicleta(id=1, marca="Teste", modelo="TS", ano="2024", numero=100, status=StatusBicicleta.DISPONIVEL)
    tranca_com_outra_bike = Tranca(id=1, numero=1, localizacao="Totem 1", ano_de_fabricacao="2024", modelo="T", status=StatusTranca.OCUPADA, bicicleta_id=99)
    
    mock_bicicleta_repo.buscar_por_id.return_value = bicicleta_a_retirar
    mock_tranca_repo.buscar_por_id.return_value = tranca_com_outra_bike

    use_case = RetirarBicicletaDaRedeUseCase(
        bicicleta_repo=mock_bicicleta_repo,
        tranca_repo=mock_tranca_repo
    )

    # Act & Assert
    # Verificamos se a exceção correta é levantada com a mensagem esperada
    with pytest.raises(ValueError, match="A bicicleta informada não está na tranca especificada."):
        use_case.execute(
            bicicleta_id=1, # Tentando retirar a bicicleta 1
            tranca_id=1,  # Da tranca 1 (que contém a bicicleta 99)
            status_final=StatusBicicleta.EM_REPARO
        )
    
    # Garante que nada foi salvo, pois a operação falhou
    mock_bicicleta_repo.salvar.assert_not_called()
    mock_tranca_repo.salvar.assert_not_called()

def test_listar_bicicletas_deve_retornar_lista():
    # Arrange
    mock_repo = MagicMock(spec=BicicletaRepositoryInterface)
    bicicletas_esperadas = [
        Bicicleta(id=1, marca="A", modelo="A1", ano="2023", numero=10, status=StatusBicicleta.DISPONIVEL),
        Bicicleta(id=2, marca="B", modelo="B1", ano="2024", numero=20, status=StatusBicicleta.NOVA),
    ]
    mock_repo.listar_todas.return_value = bicicletas_esperadas
    use_case = ListarBicicletasUseCase(repository=mock_repo)

    # Act
    resultado = use_case.execute()

    # Assert
    assert resultado == bicicletas_esperadas
    mock_repo.listar_todas.assert_called_once()


def test_buscar_bicicleta_por_id_encontrado():
    # Arrange
    mock_repo = MagicMock(spec=BicicletaRepositoryInterface)
    bicicleta_esperada = Bicicleta(id=1, marca="A", modelo="A1", ano="2023", numero=10, status=StatusBicicleta.DISPONIVEL)
    mock_repo.buscar_por_id.return_value = bicicleta_esperada
    use_case = BuscarBicicletaPorIdUseCase(repository=mock_repo)

    # Act
    resultado = use_case.execute(bicicleta_id=1)

    # Assert
    assert resultado == bicicleta_esperada
    mock_repo.buscar_por_id.assert_called_once_with(1)


def test_buscar_bicicleta_por_id_nao_encontrado():
    # Arrange
    mock_repo = MagicMock(spec=BicicletaRepositoryInterface)
    mock_repo.buscar_por_id.return_value = None # Simula que o ID não existe
    use_case = BuscarBicicletaPorIdUseCase(repository=mock_repo)

    # Act
    resultado = use_case.execute(bicicleta_id=99)

    # Assert
    assert resultado is None
    mock_repo.buscar_por_id.assert_called_once_with(99)


def test_deletar_bicicleta_use_case():
    # Arrange
    mock_repo = MagicMock(spec=BicicletaRepositoryInterface)
    use_case = DeletarBicicletaUseCase(repository=mock_repo)
    bicicleta_id_para_deletar = 5

    # Act
    use_case.execute(bicicleta_id=bicicleta_id_para_deletar)

    # Assert
    mock_repo.deletar.assert_called_once_with(bicicleta_id_para_deletar)


def test_atualizar_bicicleta_use_case():
    # Arrange
    mock_repo = MagicMock(spec=BicicletaRepositoryInterface)
    dados_atualizacao = {"marca": "Monark", "modelo": "Barra Forte"}
    bicicleta_existente = Bicicleta(id=1, marca="Caloi", modelo="10", ano="1980", numero=123, status=StatusBicicleta.DISPONIVEL)
    
    mock_repo.buscar_por_id.return_value = bicicleta_existente
    mock_repo.salvar.side_effect = lambda bicicleta: bicicleta # Retorna a bicicleta que foi salva
    
    use_case = AtualizarBicicletaUseCase(repository=mock_repo)

    # Act
    resultado = use_case.execute(bicicleta_id=1, dados_atualizacao=dados_atualizacao)

    # Assert
    mock_repo.buscar_por_id.assert_called_once_with(1)
    mock_repo.salvar.assert_called_once()
    assert resultado.marca == "Monark" # Verifica se o campo foi atualizado
    assert resultado.modelo == "Barra Forte" # Verifica se o campo foi atualizado
    assert resultado.ano == "1980" # Verifica se o campo antigo foi mantido

def test_atualizar_bicicleta_deve_lancar_erro_se_nao_encontrada(): 
    # Arrange
    # 1. Criamos o mock do repositório
    mock_repo = MagicMock(spec=BicicletaRepositoryInterface)
    
    # 2. Configuramos o mock para simular o cenário de "não encontrado".
    #    Quando 'buscar_por_id' for chamado com qualquer ID, ele retornará None.
    mock_repo.buscar_por_id.return_value = None
    
    # 3. Instanciamos o caso de uso com o mock
    use_case = AtualizarBicicletaUseCase(repository=mock_repo)
    dados_para_atualizar = {"marca": "Inexistente"}

    # Act & Assert
    # 4. Usamos 'pytest.raises' para afirmar que uma exceção do tipo
    #    ValueError será levantada, e que a mensagem de erro corresponde ao esperado.
    with pytest.raises(ValueError, match="Bicicleta não encontrada."):
        use_case.execute(bicicleta_id=999, dados_atualizacao=dados_para_atualizar)

    # 5. Afirmamos também que, como a operação falhou, o método 'salvar'
    #    NUNCA foi chamado. Isso garante que não há efeitos colaterais indesejados.
    mock_repo.salvar.assert_not_called()

def test_retirar_bicicleta_deve_falhar_se_tranca_nao_ocupada():
    # Arrange
    mock_bicicleta_repo = MagicMock(spec=BicicletaRepositoryInterface)
    mock_tranca_repo = MagicMock(spec=TrancaRepositoryInterface)
    
    # Cenário: A tranca está LIVRE, não OCUPADA
    bicicleta = Bicicleta(id=1, marca="A", modelo="B", ano="C", numero=1, status=StatusBicicleta.DISPONIVEL)
    tranca_livre = Tranca(id=1, numero=1, localizacao="L", ano_de_fabricacao="2024", modelo="M", status=StatusTranca.DISPONIVEL, bicicleta_id=1)
    
    mock_bicicleta_repo.buscar_por_id.return_value = bicicleta
    mock_tranca_repo.buscar_por_id.return_value = tranca_livre
    
    use_case = RetirarBicicletaDaRedeUseCase(bicicleta_repo=mock_bicicleta_repo, tranca_repo=mock_tranca_repo)
    
    # Act & Assert
    with pytest.raises(ValueError, match="A tranca não está ocupada."):
        use_case.execute(1, 1, StatusBicicleta.EM_REPARO)


# ===================================================================
# == TESTES PARA CASOS DE USO DE TRANCA
# ===================================================================

def test_listar_trancas_use_case():
    # Arrange
    mock_repo = MagicMock(spec=TrancaRepositoryInterface)
    trancas_esperadas = [
        Tranca(id=1, numero=101, localizacao="A", ano_de_fabricacao="2023", modelo="T1", status=StatusTranca.DISPONIVEL),
        Tranca(id=2, numero=102, localizacao="B", ano_de_fabricacao="2024", modelo="T2", status=StatusTranca.NOVA),
    ]
    mock_repo.listar_todas.return_value = trancas_esperadas
    use_case = ListarTrancasUseCase(repository=mock_repo)

    # Act
    resultado = use_case.execute()

    # Assert
    assert resultado == trancas_esperadas
    mock_repo.listar_todas.assert_called_once()


def test_buscar_tranca_por_id_encontrado():
    # Arrange
    mock_repo = MagicMock(spec=TrancaRepositoryInterface)
    tranca_esperada = Tranca(id=1, numero=101, localizacao="A", ano_de_fabricacao="2023", modelo="T1", status=StatusTranca.DISPONIVEL)
    mock_repo.buscar_por_id.return_value = tranca_esperada
    use_case = BuscarTrancaPorIdUseCase(repository=mock_repo)

    # Act
    resultado = use_case.execute(tranca_id=1)

    # Assert
    assert resultado == tranca_esperada
    mock_repo.buscar_por_id.assert_called_once_with(1)


def test_deletar_tranca_use_case():
    # Arrange
    mock_repo = MagicMock(spec=TrancaRepositoryInterface)
    use_case = DeletarTrancaUseCase(repository=mock_repo)

    # Act
    use_case.execute(tranca_id=1)

    # Assert
    mock_repo.deletar.assert_called_once_with(1)


def test_atualizar_tranca_use_case():
    # Arrange
    mock_repo = MagicMock(spec=TrancaRepositoryInterface)
    dados_atualizacao = {"modelo": "T-800", "localizacao": "Nova Localização"}
    tranca_existente = Tranca(id=1, numero=101, localizacao="A", ano_de_fabricacao="2023", modelo="T1", status=StatusTranca.DISPONIVEL)
    
    mock_repo.buscar_por_id.return_value = tranca_existente
    mock_repo.salvar.side_effect = lambda tranca: tranca
    
    use_case = AtualizarTrancaUseCase(repository=mock_repo)

    # Act
    resultado = use_case.execute(tranca_id=1, dados_atualizacao=dados_atualizacao)

    # Assert
    assert resultado.modelo == "T-800"
    assert resultado.localizacao == "Nova Localização"
    assert resultado.numero == 101 # Campo não alterado

def test_atualizar_tranca_deve_lancar_erro_se_nao_encontrada():
    # Arrange
    mock_repo = MagicMock(spec=TrancaRepositoryInterface)
    mock_repo.buscar_por_id.return_value = None
    use_case = AtualizarTrancaUseCase(repository=mock_repo)
    dados_atualizacao = {"modelo": "Inexistente"}

    # Act & Assert
    with pytest.raises(ValueError, match="Tranca não encontrada."):
        use_case.execute(tranca_id=999, dados_atualizacao=dados_atualizacao)
    
    mock_repo.salvar.assert_not_called()

def test_atualizar_totem_deve_lancar_erro_se_nao_encontrado():
    # Arrange
    mock_repo = MagicMock(spec=TotemRepositoryInterface)
    mock_repo.buscar_por_id.return_value = None
    use_case = AtualizarTotemUseCase(repository=mock_repo)
    dados_atualizacao = {"descricao": "Inexistente"}

    # Act & Assert
    with pytest.raises(ValueError, match="Totem não encontrado."):
        use_case.execute(totem_id=999, dados_atualizacao=dados_atualizacao)
        
    mock_repo.salvar.assert_not_called()

def test_integrar_tranca_no_totem_deve_falhar_se_tranca_ja_integrada():
    # Arrange
    mock_tranca_repo = MagicMock(spec=TrancaRepositoryInterface)
    mock_totem_repo = MagicMock(spec=TotemRepositoryInterface)

    # Cenário: A tranca já tem um totem_id
    tranca_integrada = Tranca(id=1, numero=1, localizacao="L", ano_de_fabricacao="2024", modelo="M", status=StatusTranca.DISPONIVEL, totem_id=5)
    totem = Totem(id=1, localizacao="L", descricao="D")

    mock_tranca_repo.buscar_por_id.return_value = tranca_integrada
    mock_totem_repo.buscar_por_id.return_value = totem

    use_case = IntegrarTrancaNoTotemUseCase(tranca_repo=mock_tranca_repo, totem_repo=mock_totem_repo)

    # Act & Assert
    with pytest.raises(ValueError, match="Tranca já está integrada ao totem 5."):
        use_case.execute(tranca_id=1, totem_id=1, funcionario_id=123) # CORREÇÃO: Adicionado funcionario_id
    
def test_trancar_tranca_deve_falhar_se_tranca_nao_esta_livre():
    # Arrange
    mock_bicicleta_repo = MagicMock(spec=BicicletaRepositoryInterface)
    mock_tranca_repo = MagicMock(spec=TrancaRepositoryInterface)

    bicicleta = Bicicleta(id=1, marca="A", modelo="B", ano="C", numero=1, status=StatusBicicleta.EM_USO)
    tranca_ocupada = Tranca(id=1, numero=1, localizacao="L", ano_de_fabricacao="2024", modelo="M", status=StatusTranca.OCUPADA)

    mock_bicicleta_repo.buscar_por_id.return_value = bicicleta
    mock_tranca_repo.buscar_por_id.return_value = tranca_ocupada
    
    use_case = TrancarTrancaUseCase(tranca_repo=mock_tranca_repo, bicicleta_repo=mock_bicicleta_repo)

    # Act & Assert
    with pytest.raises(ValueError, match="A tranca não está livre para receber uma bicicleta."):
        use_case.execute(tranca_id=1, bicicleta_id=1)

def test_destrancar_tranca_deve_falhar_se_tranca_nao_esta_ocupada():
    # Arrange
    mock_bicicleta_repo = MagicMock(spec=BicicletaRepositoryInterface)
    mock_tranca_repo = MagicMock(spec=TrancaRepositoryInterface)

    tranca_livre = Tranca(id=1, numero=1, localizacao="L", ano_de_fabricacao="2024", modelo="M", status=StatusTranca.DISPONIVEL)
    mock_tranca_repo.buscar_por_id.return_value = tranca_livre

    use_case = DestrancarTrancaUseCase(tranca_repo=mock_tranca_repo, bicicleta_repo=mock_bicicleta_repo)

    # Act & Assert
    with pytest.raises(ValueError, match="A tranca não está ocupada."):
        use_case.execute(tranca_id=1)


# ===================================================================
# == TESTES PARA CASOS DE USO DE TOTEM
# ===================================================================

def test_listar_totens_use_case():
    # Arrange
    mock_repo = MagicMock(spec=TotemRepositoryInterface)
    totens_esperados = [
        Totem(id=1, localizacao="L1", descricao="D1"),
        Totem(id=2, localizacao="L2", descricao="D2"),
    ]
    mock_repo.listar_todos.return_value = totens_esperados
    use_case = ListarTotensUseCase(repository=mock_repo)

    # Act
    resultado = use_case.execute()

    # Assert
    assert resultado == totens_esperados
    mock_repo.listar_todos.assert_called_once()


def test_buscar_totem_por_id_encontrado():
    # Arrange
    mock_repo = MagicMock(spec=TotemRepositoryInterface)
    totem_esperado = Totem(id=1, localizacao="L1", descricao="D1")
    mock_repo.buscar_por_id.return_value = totem_esperado
    use_case = BuscarTotemPorIdUseCase(repository=mock_repo)

    # Act
    resultado = use_case.execute(totem_id=1)

    # Assert
    assert resultado == totem_esperado
    mock_repo.buscar_por_id.assert_called_once_with(1)


def test_deletar_totem_use_case():
    # Arrange
    mock_repo = MagicMock(spec=TotemRepositoryInterface)
    use_case = DeletarTotemUseCase(repository=mock_repo)

    # Act
    use_case.execute(totem_id=1)

    # Assert
    mock_repo.deletar.assert_called_once_with(1)


def test_atualizar_totem_use_case():
    # Arrange
    mock_repo = MagicMock(spec=TotemRepositoryInterface)
    dados_atualizacao = {"descricao": "Nova Descrição"}
    totem_existente = Totem(id=1, localizacao="L1", descricao="D1")
    
    mock_repo.buscar_por_id.return_value = totem_existente
    mock_repo.salvar.side_effect = lambda totem: totem
    
    use_case = AtualizarTotemUseCase(repository=mock_repo)

    # Act
    resultado = use_case.execute(totem_id=1, dados_atualizacao=dados_atualizacao)

    # Assert
    assert resultado.descricao == "Nova Descrição"
    assert resultado.localizacao == "L1" # Campo não alterado

# ###################################################################
# --- NOVOS TESTES PARA AUMENTAR A COBERTURA ---
# ###################################################################

def test_alterar_status_tranca_sucesso():
    mock_repo = MagicMock(spec=TrancaRepositoryInterface)
    tranca_existente = Tranca(id=1, numero=1, localizacao="L", ano_de_fabricacao="A", modelo="M", status=StatusTranca.NOVA)
    mock_repo.buscar_por_id.return_value = tranca_existente
    mock_repo.salvar.side_effect = lambda t: t
    use_case = AlterarStatusTrancaUseCase(repository=mock_repo)
    resultado = use_case.execute(1, StatusTranca.EM_REPARO)
    assert resultado.status == StatusTranca.EM_REPARO
    mock_repo.salvar.assert_called_once()

def test_listar_trancas_por_totem_sucesso():
    mock_totem_repo = MagicMock(spec=TotemRepositoryInterface)
    mock_tranca_repo = MagicMock(spec=TrancaRepositoryInterface)
    mock_totem_repo.buscar_por_id.return_value = Totem(id=1, localizacao="L", descricao="D")
    use_case = ListarTrancasPorTotemUseCase(totem_repo=mock_totem_repo, tranca_repo=mock_tranca_repo)
    use_case.execute(1)
    mock_tranca_repo.buscar_por_totem_id.assert_called_once_with(1)

def test_integrar_tranca_no_totem_sucesso():
    mock_tranca_repo = MagicMock(spec=TrancaRepositoryInterface)
    mock_totem_repo = MagicMock(spec=TotemRepositoryInterface)
    tranca_nova = Tranca(id=1, numero=1, localizacao="L", ano_de_fabricacao="A", modelo="M", status=StatusTranca.NOVA)
    totem_existente = Totem(id=1, localizacao="L", descricao="D")
    mock_tranca_repo.buscar_por_id.return_value = tranca_nova
    mock_totem_repo.buscar_por_id.return_value = totem_existente
    mock_tranca_repo.salvar.side_effect = lambda t: t
    use_case = IntegrarTrancaNoTotemUseCase(tranca_repo=mock_tranca_repo, totem_repo=mock_totem_repo)
    resultado = use_case.execute(1, 1, funcionario_id=123)
    assert resultado.totem_id == 1
    assert resultado.status == StatusTranca.DISPONIVEL
    mock_tranca_repo.salvar.assert_called_once()

def test_buscar_bicicleta_em_tranca_sucesso():
    mock_tranca_repo = MagicMock(spec=TrancaRepositoryInterface)
    mock_bicicleta_repo = MagicMock(spec=BicicletaRepositoryInterface)
    tranca_ocupada = Tranca(id=1, numero=1, localizacao="L", ano_de_fabricacao="A", modelo="M", status=StatusTranca.OCUPADA, bicicleta_id=5)
    bicicleta_esperada = Bicicleta(id=5, marca="T", modelo="T", ano="T", numero=1, status=StatusBicicleta.DISPONIVEL)
    mock_tranca_repo.buscar_por_id.return_value = tranca_ocupada
    mock_bicicleta_repo.buscar_por_id.return_value = bicicleta_esperada
    use_case = BuscarBicicletaEmTrancaUseCase(tranca_repo=mock_tranca_repo, bicicleta_repo=mock_bicicleta_repo)
    resultado = use_case.execute(1)
    assert resultado == bicicleta_esperada

def test_listar_bicicletas_por_totem_sucesso():
    mock_totem_repo = MagicMock(spec=TotemRepositoryInterface)
    mock_tranca_repo = MagicMock(spec=TrancaRepositoryInterface)
    mock_bicicleta_repo = MagicMock(spec=BicicletaRepositoryInterface)
    totem_existente = Totem(id=1, localizacao="L", descricao="D")
    trancas_no_totem = [
        Tranca(id=10, bicicleta_id=100, status=StatusTranca.OCUPADA, numero=1, localizacao="L", ano_de_fabricacao="A", modelo="M"),
        Tranca(id=11, bicicleta_id=101, status=StatusTranca.OCUPADA, numero=1, localizacao="L", ano_de_fabricacao="A", modelo="M")
    ]
    mock_totem_repo.buscar_por_id.return_value = totem_existente
    mock_tranca_repo.buscar_por_totem_id.return_value = trancas_no_totem
    use_case = ListarBicicletasPorTotemUseCase(totem_repo=mock_totem_repo, tranca_repo=mock_tranca_repo, bicicleta_repo=mock_bicicleta_repo)
    use_case.execute(1)
    mock_bicicleta_repo.buscar_por_ids.assert_called_once_with([100, 101])

def test_retirar_tranca_do_totem_sucesso():
    mock_tranca_repo = MagicMock(spec=TrancaRepositoryInterface)
    mock_totem_repo = MagicMock(spec=TotemRepositoryInterface)
    tranca_existente = Tranca(id=1, numero=1, localizacao="L", ano_de_fabricacao="A", modelo="M", status=StatusTranca.REPARO_SOLICITADO, totem_id=1)
    totem_existente = Totem(id=1, localizacao="L", descricao="D")
    mock_tranca_repo.buscar_por_id.return_value = tranca_existente
    mock_totem_repo.buscar_por_id.return_value = totem_existente
    mock_tranca_repo.salvar.side_effect = lambda t: t
    use_case = RetirarTrancaDoTotemUseCase(tranca_repo=mock_tranca_repo, totem_repo=mock_totem_repo)
    resultado = use_case.execute(1, 1, StatusTranca.APOSENTADA)
    assert resultado.status == StatusTranca.APOSENTADA
    assert resultado.totem_id is None

def test_trancar_tranca_sucesso():
    mock_tranca_repo = MagicMock(spec=TrancaRepositoryInterface)
    mock_bicicleta_repo = MagicMock(spec=BicicletaRepositoryInterface)
    bicicleta_em_uso = Bicicleta(id=1, marca="T", modelo="T", ano="T", numero=1, status=StatusBicicleta.EM_USO)
    tranca_livre = Tranca(id=1, numero=1, localizacao="L", ano_de_fabricacao="A", modelo="M", status=StatusTranca.DISPONIVEL)
    mock_tranca_repo.buscar_por_id.return_value = tranca_livre
    mock_bicicleta_repo.buscar_por_id.return_value = bicicleta_em_uso
    mock_tranca_repo.salvar.side_effect = lambda t: t
    use_case = TrancarTrancaUseCase(tranca_repo=mock_tranca_repo, bicicleta_repo=mock_bicicleta_repo)
    resultado = use_case.execute(1, 1)
    assert resultado.status == StatusTranca.OCUPADA
    assert bicicleta_em_uso.status == StatusBicicleta.DISPONIVEL

def test_destrancar_tranca_sucesso():
    mock_tranca_repo = MagicMock(spec=TrancaRepositoryInterface)
    mock_bicicleta_repo = MagicMock(spec=BicicletaRepositoryInterface)
    bicicleta_na_tranca = Bicicleta(id=1, marca="T", modelo="T", ano="T", numero=1, status=StatusBicicleta.DISPONIVEL)
    tranca_ocupada = Tranca(id=1, numero=1, localizacao="L", ano_de_fabricacao="A", modelo="M", status=StatusTranca.OCUPADA, bicicleta_id=1)
    mock_tranca_repo.buscar_por_id.return_value = tranca_ocupada
    mock_bicicleta_repo.buscar_por_id.return_value = bicicleta_na_tranca
    mock_tranca_repo.salvar.side_effect = lambda t: t
    use_case = DestrancarTrancaUseCase(tranca_repo=mock_tranca_repo, bicicleta_repo=mock_bicicleta_repo)
    resultado = use_case.execute(1)
    assert resultado.status == StatusTranca.DISPONIVEL
    assert bicicleta_na_tranca.status == StatusBicicleta.EM_USO
