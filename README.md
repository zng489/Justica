# Sniper Frontend

Esse repositório contém o frontend do [projeto
Sniper](https://www.cnj.jus.br/tecnologia-da-informacao-e-comunicacao/justica-4-0/sniper/), que é baseado no [frontend
de referência da PDPJ](https://git.cnj.jus.br/pdpj/frontends/referencia) e utiliza como backend o projeto
[sniper-backend](https://git.cnj.jus.br/pdpj/negocio/sniper-backend/).


## Desenvolvimento

O desenvolvimento é feito utilizando [docker compose](https://docs.docker.com/compose/) e, para que o frontend funcione
corretamente, você precisa de toda a pilha do backend (incluindo bases de dados e sistema de autenticação). Para
executar o backend, veja a documentação de [sniper-backend](https://git.cnj.jus.br/pdpj/negocio/sniper-backend/).

Para construir os containers, rodar os serviços e ver os logs, execute:

```sh
make build start logs
```

Execute `make help` para ver outros comandos úteis.
