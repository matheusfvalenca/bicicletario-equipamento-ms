# tests/infrastructure/web/test_api.py

from fastapi.testclient import TestClient
# Importamos o 'app' principal da nossa aplicação
from main import app 

# Criamos uma instância do TestClient, passando nosso app FastAPI para ele
client = TestClient(app)

def test_criar_bicicleta_api_deve_retornar_status_201_e_dados_corretos():
    # Arrange
    payload = {
        "marca": "Caloi",
        "modelo": "10",
        "ano": "1985",
        "numero": 555,
    }

    # Act
    response = client.post("/api/bicicletas", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["marca"] == payload["marca"]
    assert data["status"] == "NOVA"
    assert "id" in data
    assert "is_deleted" in data
    assert data["is_deleted"] is False

def test_listar_bicicletas_api():
    # Arrange
    client.post("/api/bicicletas", json={"marca": "A", "modelo": "A1", "ano": "2023", "numero": 1})
    client.post("/api/bicicletas", json={"marca": "B", "modelo": "B1", "ano": "2024", "numero": 2})

    # Act
    response = client.get("/api/bicicletas")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) >= 2

def test_buscar_bicicleta_por_id_api_encontrado():
    # Arrange
    payload = {"marca": "C", "modelo": "C1", "ano": "2025", "numero": 3}
    response_post = client.post("/api/bicicletas", json=payload)
    new_id = response_post.json()["id"]

    # Act
    response_get = client.get(f"/api/bicicletas/{new_id}")

    # Assert
    assert response_get.status_code == 200
    assert response_get.json()["id"] == new_id
    assert response_get.json()["marca"] == "C"

def test_buscar_bicicleta_por_id_api_nao_encontrado():
    # Act
    response = client.get("/api/bicicletas/9999")

    # Assert
    assert response.status_code == 404 

def test_atualizar_bicicleta_api():
    # Arrange
    payload = {"marca": "Antiga", "modelo": "Antigo", "ano": "2000", "numero": 4}
    response_post = client.post("/api/bicicletas", json=payload)
    new_id = response_post.json()["id"]
    
    update_payload = {"marca": "Nova", "modelo": "Novo", "ano": "2024", "numero": 5}

    # Act
    response_put = client.put(f"/api/bicicletas/{new_id}", json=update_payload)
    data = response_put.json()

    # Assert
    assert response_put.status_code == 200
    assert data["id"] == new_id
    assert data["marca"] == "Nova" 

def test_deletar_bicicleta_api():
    # Arrange
    payload = {"marca": "Para Deletar", "modelo": "Tchau", "ano": "2024", "numero": 6}
    response_post = client.post("/api/bicicletas", json=payload)
    new_id = response_post.json()["id"]

    # Act
    response_delete = client.delete(f"/api/bicicletas/{new_id}")

    # Assert
    assert response_delete.status_code == 204
    assert client.get(f"/api/bicicletas/{new_id}").status_code == 404 

    response_list_deleted = client.get("/api/bicicletas?include_deleted=true") 
    item_deletado = next((b for b in response_list_deleted.json() if b["id"] == new_id), None)
    
    assert response_list_deleted.status_code == 200
    assert item_deletado is not None
    assert item_deletado["is_deleted"] is True

def test_criar_tranca_api():
    # Arrange
    payload = {
        "numero": 101,
        "localizacao": "Totem Central",
        "ano_de_fabricacao": "2023",
        "modelo": "T-1000"
    }
    # Act
    response = client.post("/api/trancas", json=payload)
    data = response.json()
    # Assert
    assert response.status_code == 201
    assert data["numero"] == 101
    assert data["status"] == "NOVA"
    assert "id" in data
    assert data["is_deleted"] is False

def test_listar_trancas_api():
    # Arrange
    client.post("/api/trancas", json={"numero": 201, "localizacao": "A", "ano_de_fabricacao": "2023", "modelo": "M1"})
    client.post("/api/trancas", json={"numero": 202, "localizacao": "B", "ano_de_fabricacao": "2024", "modelo": "M2"})
    # Act
    response = client.get("/api/trancas")
    data = response.json()
    # Assert
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) >= 2

def test_buscar_tranca_por_id_api_encontrado():
    # Arrange
    payload = {"numero": 301, "localizacao": "C", "ano_de_fabricacao": "2025", "modelo": "M3"}
    response_post = client.post("/api/trancas", json=payload)
    new_id = response_post.json()["id"]
    # Act
    response_get = client.get(f"/api/trancas/{new_id}")
    # Assert
    assert response_get.status_code == 200
    assert response_get.json()["id"] == new_id
    assert response_get.json()["numero"] == 301

def test_buscar_tranca_por_id_api_nao_encontrado():
    # Act
    response = client.get("/api/trancas/9998")
    # Assert
    assert response.status_code == 404

def test_atualizar_tranca_api():
    # Arrange
    payload = {"numero": 401, "localizacao": "D", "ano_de_fabricacao": "2000", "modelo": "M4"}
    response_post = client.post("/api/trancas", json=payload)
    new_id = response_post.json()["id"]
    update_payload = {"numero": 402, "localizacao": "E", "ano_de_fabricacao": "2024", "modelo": "M5"}
    # Act
    response_put = client.put(f"/api/trancas/{new_id}", json=update_payload)
    data = response_put.json()
    # Assert
    assert response_put.status_code == 200
    assert data["numero"] == 402
    assert data["localizacao"] == "E"

def test_deletar_tranca_api():
    # Arrange
    payload = {"numero": 909, "localizacao": "F", "ano_de_fabricacao": "2024", "modelo": "M6"}
    response_post = client.post("/api/trancas", json=payload)
    new_id = response_post.json()["id"]
    # Act
    response_delete = client.delete(f"/api/trancas/{new_id}") 
    # Assert
    assert response_delete.status_code == 204 
    assert client.get(f"/api/trancas/{new_id}").status_code == 404 
    response_get_deleted = client.get(f"/api/trancas?include_deleted=true")
    item_deletado = next((t for t in response_get_deleted.json() if t["id"] == new_id), None)
    assert item_deletado is not None
    assert item_deletado["is_deleted"] is True

def test_criar_totem_api():
    # Arrange
    payload = {"localizacao": "Praça Central", "descricao": "Totem perto do chafariz"}
    # Act
    response = client.post("/api/totens", json=payload)
    data = response.json()
    # Assert
    assert response.status_code == 201
    assert data["localizacao"] == "Praça Central"
    assert "id" in data
    assert data["is_deleted"] is False

def test_listar_totens_api():
    # Arrange
    client.post("/api/totens", json={"localizacao": "A", "descricao": "D1"})
    # Act
    response = client.get("/api/totens")
    data = response.json()
    # Assert
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) >= 1

def test_buscar_totem_por_id_api_encontrado():
    # Arrange
    payload = {"localizacao": "B", "descricao": "D2"}
    response_post = client.post("/api/totens", json=payload)
    new_id = response_post.json()["id"]
    # Act
    response_get = client.get(f"/api/totens/{new_id}")
    # Assert
    assert response_get.status_code == 200
    assert response_get.json()["id"] == new_id

def test_atualizar_totem_api():
    # Arrange
    payload = {"localizacao": "C", "descricao": "Antiga"}
    response_post = client.post("/api/totens", json=payload)
    new_id = response_post.json()["id"]
    update_payload = {"localizacao": "C", "descricao": "Nova"}
    # Act
    response_put = client.put(f"/api/totens/{new_id}", json=update_payload)
    data = response_put.json()
    # Assert
    assert response_put.status_code == 200
    assert data["descricao"] == "Nova"

def test_deletar_totem_api():
    # Arrange
    payload = {"localizacao": "Para Deletar", "descricao": "Totem de Teste"}
    response_post = client.post("/api/totens", json=payload)
    new_id = response_post.json()["id"]
    # Act
    response_delete = client.delete(f"/api/totens/{new_id}")
    # Assert 
    assert response_delete.status_code == 204
    assert client.get(f"/api/totens/{new_id}").status_code == 404 
    response_get_deleted = client.get(f"/api/totens?include_deleted=true") 
    item_deletado = next((t for t in response_get_deleted.json() if t["id"] == new_id), None)
    assert item_deletado is not None
    assert item_deletado["is_deleted"] is True
    
def test_integrar_bicicleta_na_rede_api():
    # Arrange: Cria uma bicicleta e uma tranca novas
    bicicleta_payload = {"marca": "Final", "modelo": "Teste", "ano": "2025", "numero": 1001}
    tranca_payload = {"numero": 101, "localizacao": "Final", "ano_de_fabricacao": "2025", "modelo": "TF"}
    
    id_bicicleta = client.post("/api/bicicletas", json=bicicleta_payload).json()["id"]
    id_tranca = client.post("/api/trancas", json=tranca_payload).json()["id"]

    # Ativa a tranca, mudando seu status de NOVA para LIVRE
    client.post(f"/api/trancas/{id_tranca}/status/LIVRE")

    integracao_payload = {"idBicicleta": id_bicicleta, "idTranca": id_tranca}

    # Act: Executa a ação de integrar
    response = client.post("/api/bicicletas/integrar-na-rede", json=integracao_payload)
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data["status"] == "OCUPADA"
    assert data["bicicleta_id"] == id_bicicleta

def test_destrancar_e_trancar_api_ciclo_completo():
    # Arrange: Prepara um cenário com uma bicicleta já integrada em uma tranca
    bicicleta_payload = {"marca": "Ciclo", "modelo": "Completo", "ano": "2025", "numero": 2002}
    tranca_payload = {"numero": 202, "localizacao": "Ciclo", "ano_de_fabricacao": "2025", "modelo": "TC"}
    id_bicicleta = client.post("/api/bicicletas", json=bicicleta_payload).json()["id"]
    id_tranca = client.post("/api/trancas", json=tranca_payload).json()["id"]

    # Ativa a tranca antes de usá-la
    client.post(f"/api/trancas/{id_tranca}/status/LIVRE")
    
    # Agora integramos a bicicleta na tranca já ativada
    client.post("/api/bicicletas/integrar-na-rede", json={"idBicicleta": id_bicicleta, "idTranca": id_tranca})

    # --- Parte 1: Teste de Destrancar ---
    
    # Act
    response_destrancar = client.post(f"/api/trancas/{id_tranca}/destrancar")
    data_bike_liberada = response_destrancar.json()

    # Assert
    assert response_destrancar.status_code == 200
    assert data_bike_liberada["status"] == "EM_USO"

    # Verificação de estado
    tranca_depois_de_destrancar = client.get(f"/api/trancas/{id_tranca}").json()
    assert tranca_depois_de_destrancar["status"] == "LIVRE"

    # --- Parte 2: Teste de Trancar ---

    # Act
    response_trancar = client.post(f"/api/trancas/{id_tranca}/trancar", json={"idBicicleta": id_bicicleta})
    data_tranca_fechada = response_trancar.json()

    # Assert
    assert response_trancar.status_code == 200
    assert data_tranca_fechada["status"] == "OCUPADA"
