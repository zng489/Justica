(function (window) {
    window.__env = window.__env || {};
    window.__env.production = false;
    window.__env.nome = "Sniper";
    window.__env.descricao = "Sistema Nacional de Investigação Patrimonial e Recuperação de Ativos";
    window.__env.apiUrl = "http://localhost:5001/",
    window.__env.ssoUrl = "http://keycloak:8080/auth/",
    window.__env.realm = "pdpj",
    window.__env.clientId = "sniper-frontend",
    window.__env.redirectUri = "http://localhost:4200"
}(this));
