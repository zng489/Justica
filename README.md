python manage.py runserver 2828# Sniper - Backend

Esse repositório contém o código do backend da plataforma Sniper, desenvolvido
em Python com o framework Django.

- Para mais detalhes sobre a instalação em ambiente de desenvolvimento local,
  consulte [`docs/instalacao.md`](docs/instalacao.md).
- Para importação de dados, consulte
  [`docs/datasets.md`](docs/datasets.md).

## Acesso

O sniper pode ser acessado em:
- Homologação:
  - Frontend: https://sniper.stg.pdpj.jus.br/
  - Backend: https://sniper-api.stg.pdpj.jus.br/
- Produção:
  - Frontend: https://sniper.pdpj.jus.br/
  - Backend: https://sniper-api.pdpj.jus.br/

O Django Admin pode ser acessado para checar informações nas tabelas, progresso
de importação de dados etc. em:

- Homologação: https://sniper-api.stg.pdpj.jus.br/admin/
- Produção: https://sniper-api.pdpj.jus.br/admin/

> Nota: para ter acesso ao Django Admin você deve utilizar o sistema de
> autenticação do Django (e não o SSO do PDPJ). Caso queira redefinir a senha
> do usuário `admin`, abra um terminal no container do backend pelo Gitlab e
> execute: `python manage.py changepassword admin`
