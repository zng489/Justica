export const tableReport = `
    <h3>{{ title }}</h3>
    <hr>
    {% if manyColumns %}
        {% for element in result %}
            <table
                class="
                    table-result table-striped
                    {% if loop.index % 2 != 0 %}
                        table-border-dotted
                    {% else %}
                        table-border
                    {% endif %}
                "
            >
                {% for key, value in element %}
                    <tr>
                        {% if value %}
                            <td><b>{{ key }}</b></td>
                            <td>{{ value }}</td>
                        {% else %}
                            <td><b>{{ key }}</b></td>
                            <td><i>(vazio)</i></td>
                        {% endif %}
                    </tr>
                {% endfor %}
            </table>
        {% endfor %}
    {% else %}
        <table class="table-base table-striped">
            <thead>
                <tr>
                    {% for field in fields %}
                    <th {% if field.description %} title="{{ field.description }}" {% endif %}>
                        {{ field.title }}
                    </th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
              {% if result | length > 0 %}
                  {% for element in result %}
                      <tr>
                          {% for key, value in element %}
                              <td data-label="{{ key }}">
                                {% if value %}
                                    {{ value }}
                                {% else %}
                                    <i>(vazio)</i>
                                {% endif %}
                              </td>
                          {% endfor %}
                      </tr>
                  {% endfor %}
              {% else %}
                  <tr>
                    <td colspan="3">Nenhum objeto foi encontrado.</td>
                  </tr>
              {% endif %}
            </tbody>
        </table>
    {% endif %}
`
