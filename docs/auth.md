# Autenticação

A autenticação do acesso aos recursos deste sistema é feita a partir do conceito Single Sign On (SSO) por meio da ferramenta de autenticação [keycloak](https://www.keycloak.org/).

Neste projeto, utilizamos como base para o frontend o [uikit](https://git.cnj.jus.br/uikit/uikit) que já possui integração com o keycloak. 
Com esta integração, fazemos a requisição de um token de acesso a partir do username e senha do usuário. Deste momento em diante, o token é informado a cada requisição feita à API disponível no backend.
Para mantermos o token atualizado, fazemos sua renovação de tempos em tempos também por meio da integração com keycloak.

Antes de acessar qualquer recurso, o sistema de backend checa se a requisição possui um token e verifica junto ao keycloak se este token fornecido é válido. Caso positivo o recurso é acessado com sucesso, caso contrário a resposta da API será de acesso negado e o recurso não será acessado.
