Microsserviço de Equipamento - SCB
Este microsserviço é responsável pela gestão dos equipamentos físicos, como bicicletas, totens e trancas, no Sistema de Controle de Bicicletário (SCB). Ele controla o cadastro, o estado e as interações entre esses equipamentos.

Arquitetura
Este projeto foi construído seguindo os princípios da Clean Architecture, com uma separação clara de responsabilidades em diferentes camadas, o que garante alta testabilidade e manutenibilidade. A estrutura é organizada da seguinte forma:

src/equipamento/domain/ – Contém os modelos das entidades (Bicicleta, Tranca, Totem) e as regras de negócio centrais.

src/equipamento/application/use_cases/ – Contém os casos de uso que orquestram a lógica da aplicação e as validações.

src/equipamento/infrastructure/repositories/ – Contém a implementação concreta dos repositórios de persistência (atualmente, um repositório em memória para desenvolvimento e testes).

src/equipamento/infrastructure/web/ – Camada de interface RESTful construída com FastAPI, que expõe os casos de uso para o mundo externo.

tests/ – Contém os testes automatizados (unitários e de integração) que garantem a qualidade e a cobertura do código.

Funcionalidades
Gestão de Bicicletas
POST /bicicletas — Cadastrar uma nova bicicleta.

GET /bicicletas — Listar todas as bicicletas.

GET /bicicletas/{idBicicleta} — Consultar dados de uma bicicleta específica.

PUT /bicicletas/{idBicicleta} — Alterar dados de uma bicicleta.

DELETE /bicicletas/{idBicicleta} — Remover uma bicicleta.

POST /bicicletas/{idBicicleta}/status/{novo_status} — Alterar o status de uma bicicleta (ex: para DISPONIVEL, EM_REPARO).

Gestão de Totens
POST /totens — Cadastrar um novo totem.

GET /totens — Listar todos os totens.

GET /totens/{idTotem} — Obter dados de um totem específico.

PUT /totens/{idTotem} — Atualizar dados de um totem.

DELETE /totens/{idTotem} — Remover um totem.

GET /totens/{idTotem}/trancas — Listar todas as trancas associadas a um totem.

GET /totens/{idTotem}/bicicletas — Listar todas as bicicletas que estão nas trancas de um totem.

Gestão de Trancas
POST /trancas — Cadastrar uma nova tranca.

GET /trancas — Listar todas as trancas.

GET /trancas/{idTranca} — Obter dados de uma tranca específica.

PUT /trancas/{idTranca} — Atualizar dados de uma tranca.

DELETE /trancas/{idTranca} — Remover uma tranca.

POST /trancas/{idTranca}/status/{novo_status} — Alterar o status de uma tranca (ex: para LIVRE, EM_REPARO).

GET /trancas/{idTranca}/bicicleta — Obter os dados da bicicleta que está na tranca (se houver).

Ações e Orquestração
POST /bicicletas/integrar-na-rede — Associar uma bicicleta a uma tranca livre.

POST /bicicletas/retirar-da-rede — Desassociar uma bicicleta de uma tranca para reparo ou aposentadoria.

POST /trancas/integrar-na-rede — Associar uma tranca a um totem.

POST /trancas/retirar-da-rede — Desassociar uma tranca de um totem.

POST /trancas/{idTranca}/trancar — Simular o ato de devolver uma bicicleta, trancando-a em uma tranca.

POST /trancas/{idTranca}/destrancar — Simular o ato de alugar uma bicicleta, liberando-a de uma tranca.

Como executar localmente
1. Usando Python diretamente (Recomendado para desenvolvimento)
Pré-requisitos: Python 3.9+ e pip.

# Clone o repositório
git clone [URL_DO_SEU_REPOSITORIO]
cd [NOME_DA_PASTA]

# Crie e ative um ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Execute o servidor
uvicorn main:app --reload

2. Usando Docker (Para produção ou ambiente isolado)
(Nota: Um Dockerfile precisaria ser criado para esta etapa)

# Construa a imagem Docker
docker build -t scb-equipamento .

# Execute o container
docker run -p 8000:8000 scb-equipamento

Acesso à API
API Base: http://localhost:8000/api

Documentação Interativa (Swagger): http://localhost:8000/docs

Se estiver rodando em um ambiente de nuvem (como EC2), substitua localhost pelo endereço IP público da sua instância.

Autor responsável
Matheus Ferreira Valença – responsável pelo microsserviço de Equipamento
