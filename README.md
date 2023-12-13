# Chain2Help

### Pré-Requisitos:

- Docker
- Sunodo
- Projeto [Cartesi Rollups Examples](https://github.com/cartesi/rollups-examples)
- Yarn
- Make (Opctional)

### Passos para execução:

- Buildar os projetos `common-contracts` e `frontend-console` no projeto **Cartesi Rollups Examples** (Seguir instruções presentes em seus próprios `README.md`)
- Executar em um terminal os comandos `make build` e `make run` e aguardar até tudo estar de pé (Será exibido o endereço dos endpoints)
- Em outro terminal executar o comando `make test`

Após isso deve-se iniciar uma sequência de comandos testando todas as operações suportadas na aplicação no momento.

Caso deseje, é possível também executar essas operações individualmente pelo projeto `frontend-console`, presente no repositório do **Cartesi Rollups Examples**.

> Obs.: O projeto **Cartesi Rollups Examples** deve estar na mesma pasta que o projeto **Chain2Help**

> Obs2.: Caso não queira instalar o comando Make, pode-se executar os comandos presentes no arquivo `Makefile` em um terminal linux
