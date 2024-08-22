export const nodeRelationships = `
  {% for edge, relNode in relationships %}
    <div class="data-div">
      <div class="key-link">
        <a
          title="Selecionar relação"
          href="#edge/{{ edge.id }}"
          class="action-select-edge"
          data-edge-id="{{ edge.id }}"
          data-ref-node="{{ node.id }}"
        >
          {{ edge.label }}
        </a>
      </div>
      <div class="content-link">
        <a
          title="Selecionar objeto"
          href="#node/{{ relNode.id }}"
          class="action-select-node"
          data-node-id="{{ relNode.id }}"
          data-ref-node="{{ node.id }}"
        >
            {% if relNode.textLabel %}
                {{ relNode.textLabel | safe }}
            {% else %}
                {{ relNode.label|safe }}
            {% endif %}
        </a>
      </div>
    </div>
  {% endfor %}

  {% for edge, relNode in unexistingEdges %}
    <div class="data-div">
      <div class="key-link">
        <a
          title="Selecionar relação"
          href="#edge/{{ edge.id }}"
          class="action-expand-unexisting-edge"
          data-edge-id="{{ edge.id }}"
          data-ref-node="{{ node.id }}"
        >
          {{ edge.label }}*
        </a>
      </div>
      <div class="content-link">
        <a
          title="Selecionar objeto"
          href="#node/{{ relNode.id }}"
          class="action-expand-unexisting-node"
          data-node-id="{{ relNode.id }}"
          data-ref-node="{{ node.id }}"
        >
            {% if relNode.textLabel %}
                {{ relNode.textLabel | safe }}
            {% else %}
                {{ relNode.label|safe }}
            {% endif %}
        </a>
      </div>
    </div>
  {% endfor %}
`
