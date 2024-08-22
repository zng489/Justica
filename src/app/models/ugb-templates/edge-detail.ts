export const EdgeDetail = `
    <style>
        .graph-container .graph-info .graph-info-content .graph-icon {
            margin-left: 15px;
        }
        .graph-container .graph-info .graph-info-content .graph-icon .graph-relation {
            border-radius: 0;
            border: 2px solid #fff;
        }
        .graph-container .graph-info .graph-info-content h1 {
            margin-left: 15px;
            padding: 0;
        }
        .graph-container .graph-info .graph-info-content .graph-info-buttons {
            justify-content: initial;
            margin-left: 15px;
        }
        .graph-container .graph-info .graph-info-content .graph-icon .graph-relation i {
            top: 50%;
        }
    </style>
    <button class="graph-infobar-toggle-button" title="Esconder informações">
        <i class="fas fa-chevron-right"></i>
    </button>
    <span class="graph-icon">
        <div class="graph-relation" style="background-color: {{ fromBackgroundColor }}">
            <i class="fa fa-sm" style="color: {{ fromIconColor }}">{{ fromIcon }}</i>
        </div>
        <div class="graph-relation-arrow">
            <i class="fas fa-arrows-alt-h info-icon"></i>
        </div>
        <div class="graph-relation" style="background-color: {{ toBackgroundColor }}">
            <i class="fa fa-sm" style="color: {{ toIconColor }}">{{ toIcon }}</i>
        </div>
    </span>

    <h1 class="graph-info-label">{{ node.textLabel | safe }}</h1>

    <div class="graph-info-buttons">
        <button class="action-center-graph-on-edge" data-edge-id="{{ node.id }}" title="Centralizar grafo nessa relação">
        <i class="fas fa-compress-arrows-alt"></i>
        </button>
    </div>

    <h2 class="data-title">Relações</h2>
    <div class="data-div">
        <span class="key">De</span>
        <div title="Selecionar objeto" class="content-link">
        <a href="#node/{{ fromNode.id }}" class="action-select-node" data-node-id="{{ fromNode.id }}">{{ fromNode.textLabel | safe }}</a>
        </div>
    </div>

    <div class="data-div">
        <span class="key">Para</span>
        <div title="Selecionar objeto" class="content-link">
        <a href="#node/{{ toNode.id }}" class="action-select-node" data-node-id="{{ toNode.id }}">{{ toNode.textLabel | safe }}</a>
        </div>
    </div>

    {% for key, value in node.properties %}
        <div class="data-div">
            <div class="key">{{ key }}</div>
                <div class="content">
                    {% if value %}{{ value }}{% else %}<span class="data-empty"><em>(vazio)</em></span>{% endif %}
                </div>
            </div>
        </div>
    {% endfor %}
`;
