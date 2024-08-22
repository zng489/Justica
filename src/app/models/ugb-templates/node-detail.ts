import { nodeRelationships } from "./includes/node-relationships";

export const NodeDetail = `
    <style>
        .graph-container .graph-info .graph-info-content .graph-info-search {
            justify-content: initial;
            margin-left: 15px;
        }
        .graph-container .graph-info .graph-info-content .graph-info-search form input {
            margin-top: 15px;
            box-shadow: none;
        }
        .graph-container .graph-info .graph-info-content .graph-icon {
            margin-bottom: 0;
            margin-left: 15px;
        }
        .graph-container .graph-info .graph-info-content h1 {
            margin-left: 15px;
            padding: 0;
        }
        .graph-container .graph-info .graph-info-content .graph-info-buttons {
            justify-content: initial;
            margin: 0 15px;
        }
        .graph-container .graph-info .graph-info-content .graph-info-search .container-search-input-icons {
            margin-top: 1rem;
        }
        #vis .graph-container .graph-info .hidden-input {
            top: 1.8rem;
        }
    </style>
    <button class="graph-infobar-toggle-button" title="Esconder informações">
        <i class="fas fa-chevron-right"></i>
    </button>

    <div class="graph-icon" style="background-color: {{ nodeBackgroundColor }}">
        <span class="fa fa-2x" style="color: {{ nodeIconColor }}">{{ nodeIcon }}</span>
        {% if description %}
            <div title="Descrição" class="infobar-entity-description" data-entity="{{ entity }}">
                <i class="fas fa-info-circle"></i>
            </div>
        {% endif %}
    </div>

    <h1>{{ node.textLabel | safe }}</h1>

    <div class="graph-info-buttons">
        <section>
            <button class="action-center-zoom-on-node" data-node-id="{{ node.id }}" title="Centralizar no objeto atual">
                <i class="fas fa-compress-arrows-alt"></i>
            </button>
            <button class="action-expand-all-neighbors" data-node-id="{{ node.id }}" data-depth="1" title="Expandir objetos vizinhos">
                <i class="fas fa-plus"></i>
            </button>
            {% if node.graph.edges.length <= 5 %}
                <button class="action-expand-all-neighbors" data-node-id="{{ node.id }}" data-depth="2" title="Expandir objetos vizinhos em até 2 graus">
                    <i class="fas fa-users"></i>
                </button>
            {% endif %}
        </section>
    </div>

    {% if infoSearchField %}
        <div class="graph-info-search">
        <form class="clearable-input">
            <input type="search" autocomplete="off" data-from-node-id="{{ node.id }}" title="Busque o menor caminho entre esse e outro objeto" placeholder="Busque o menor caminho">
            {% if anonymousSearchField %}
                <div class="hidden-input"></div>
            {% endif %}
            <div class="container-search-input-icons">
                <div class="search-input-icons">
                    <span data-clear-input>
                        <i class="fas fa-times"></i>
                    </span>
                    <span type="submit">
                        <i class="fas fa-search"></i>
                    </span>
                </div>
            </div>
        </form>
        </div>
    {% endif %}

    <h2 class="data-title">Dados</h2>

    {% for key, value in node.properties %}
        <div class="data-div">
            <div class="key">{{ key }}</div>
            <div class="content">
                {% if value %}
                    {{ value }}
                    {% if key === "Endereço" %}
                        <a href="https://www.google.com/maps/search/{{value}}" title="Clique para buscar" target="_blank">
                            <i class="fa-solid fa-up-right-from-square"></i>
                        </a>
                    {% endif %}
                {% else %}
                    <span class="data-empty">
                        <em>(vazio)</em>
                    </span>
                {% endif %}
            </div>
        </div>
    {% endfor %}

    {% if
        node.extra.aeronave or
        node.extra.embarcacao or
        node.extra.sancao or
        node.group in ['candidacy', 'candidacy_expanded', 'person', 'person_expanded', 'company', 'company_expanded'] or
        links.length
    %}
        <h2 class="data-title">Dados Complementares</h2>

        <div class="links">
            {% for key, value in node.extra %}
                {% if value %}
                    <div class="data-div">
                        <div class="content-link-only">
                            <a
                                title="Clique para ver a lista"
                                class="action-modal-details complementary-dataset"
                                data-node-id="{{ node.id }}"
                                data-link-label="{{ key }}"
                            >
                                {{
                                    key
                                    | replace("aeronave", "Aeronaves")
                                    | replace("embarcacao", "Embarcações")
                                    | replace("sancao", "Sanções")
                                    | capitalize
                                }}
                            </a>
                        </div>
                    </div>
                {% endif %}
            {% endfor %}
            {% if node.group in ['person', 'person_expanded', 'company', 'company_expanded']  %}
                    {% if enabledIntegrations.CABECALHO_PROCESSUAL %}
                    <div class="data-div">
                        <div class="content-link-only">
                            <a
                                title="Clique para ver a lista"
                                class="action-modal-details law-suits" data-node-id="{{ node.id }}" data-link-label="processos"
                            >
                                Lista de processos DATAJUD
                            </a>
                        </div>
                    </div>
                    {% endif %}
                    {% if enabledIntegrations.SISBAJUD_CONTAS %}
                    <div class="data-div">
                        <div class="content-link-only">
                            <a
                                title="Clique para ver a lista"
                                class="action-modal-details financial-accounts" data-node-id="{{ node.id }}" data-link-label="financial-accounts"
                            >
                                Contas em instituições financeiras
                            </a>
                        </div>
                    </div>
                    {% endif %}
            {% endif %}
            {% if
                node.group == "candidacy" or
                node.group == "candidacy_expanded"
            %}
            <div class="data-div">
                <div class="content-link-only">
                    <a
                        title="Bens declarados"
                        class="action-modal-details complementary-dataset"
                        data-node-id="{{ node.id }}"
                        data-link-label="bem-declarado"
                    >
                        Bens declarados
                    </a>
                </div>
            </div>
            {% endif %}
            {% for link in links %}
                <div class="data-div">
                    <div class="content-link-only">
                        <a title="{{ link.title }}" href="{{ link.url }}" target="_blank">
                          {{ link.label }}
                          <i class="fa-solid fa-up-right-from-square"></i>
                        </a>
                    </div>
                </div>
            {% endfor %}
        </div>
    {% endif %}

    {% if relationshipsFrom.length + relationshipsTo.length + unexistingEdgesFrom.length + unexistingEdgesTo.length > 50 %}
      <p class="info-text">Esse objeto possui muitas relações, <a class="action-expand-node" data-node-id="{{ node.id }}" href="#">clique aqui</a> para visualizá-las.</p>
    {% else %}
      {% if relationshipsTo.length or unexistingEdgesTo.length %}
          <h2 class="data-title">Relações de entrada</h2>
          <div class="relations">
              {% set relationships = relationshipsTo %}
              {% set unexistingEdges = unexistingEdgesTo %}
              ${nodeRelationships}
          </div>
      {% endif %}

      {% if relationshipsFrom.length or unexistingEdgesFrom.length %}
          <h2 class="data-title">Relações de saída</h2>
          <div class="relations">
              {% set relationships = relationshipsFrom %}
              {% set unexistingEdges = unexistingEdgesFrom %}
              ${nodeRelationships}
          </div>
      {% endif %}

      {% if unexistingEdgesFrom.length or unexistingEdgesTo.length %}
          <p class="info-text">
              Relações marcadas com * existem no banco de dados mas não estão presentes no grafo atual.
              <a class="action-expand-node" data-node-id="{{ node.id }}" href="#">Expandir todas</a>
          </p>
      {% endif %}
    {% endif %}
`;
