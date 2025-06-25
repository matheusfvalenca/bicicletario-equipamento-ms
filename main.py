# main.py

import uvicorn
from fastapi import FastAPI

# Importamos o router que criamos no nosso módulo de rotas
from src.equipamento.infrastructure.web.routes import router as equipamento_router

# Criamos a instância principal da aplicação FastAPI
app = FastAPI(
    title="Microsserviço de Equipamento",
    description="API para gerenciamento de Bicicletas, Trancas e Totens.",
    version="1.0.0"
)

# Incluímos as rotas do nosso microsserviço na aplicação principal.
# O prefixo "/api" é opcional, mas é uma boa prática para organizar os endpoints.
app.include_router(equipamento_router, prefix="/api")

@app.get("/", tags=["Root"])
def read_root():
    """Endpoint raiz para verificar se a API está no ar."""
    return {"message": "Bem-vindo ao Microsserviço de Equipamento!"}

# Esta parte permite executar o app diretamente com "python main.py"
# É útil para debug, mas geralmente usamos o comando uvicorn.
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)