import { tableReport } from "./includes/table-report";

export const ReportGenericTemplate = `
    <!DOCTYPE html>
    <html>
        <head>
            <title>Sniper - Mapa de relações</title>
            <style type="text/css">
                :root {
                  --color-img-bg: #f5f5f5;
                }
                .dark {
                  --color-img-bg: #363636;
                }

                html,
                body {
                    font-family: 'Roboto', sans-serif;
                    color: #212427;
                }

                h1 {
                    font-size: x-large;
                    padding-bottom: 0;
                    margin-bottom: 0;
                }

                h2 {
                    padding-top: 0;
                    margin-top: 0;
                    font-size: large;
                }

                .subtitle {
                    padding-top: 0;
                    margin-top: 0;
                    margin-bottom: 25px;
                    font-size: x-small;
                }

                h3 {
                    font-size: medium;
                    margin-top: 0;
                    margin-bottom: 0;
                }

                h4 {
                    font-size: small;
                }

                .graph {
                    display: flex;
                    justify-content: center;
                    margin: 25px 0;
                }

                img {
                    width: 70%;
                    border: 1px solid rgb(245, 245, 245);
                    background-color: var(--color-img-bg);
                }

                table {
                    margin: 20px 2px;
                    width: 100%;
                    font-size: small;
                }

                .table-base {
                    border: .8pt solid #212427;
                }

                .table-base,
                .table-base th,
                .table-base td {
                    padding: 3px;
                    border-collapse: collapse;
                    border: .5pt solid #212427;
                    font-family: 'Roboto Mono', monospace;
                }

                .table-striped tbody tr:nth-of-type(even) {
                    background-color: rgb(245, 245, 245);
                }

                .total-value {
                    border: solid 1pt;
                    margin-top: 12px;
                    background-color: #f5f5f5;
                    padding: 10px;
                    border-radius: 0.35rem;
                    text-align: center;
                }

                .total-value h2 {
                    font-size: 1.2em;
                    margin: 0;
                }

                .total-value p {
                    margin: 0;
                    font-weight: 400;
                    font-size: 0.7em;
                }

                .details {
                    background-color: var(--ugb-color-info-table-even);
                    border: 1pt solid;
                    border-radius: 0.2rem;
                    padding: 1rem;
                    margin: 1rem 0;
                }

                .details-title span {
                    font-size: 0.7em;
                }

                .details-title h1 {
                    font-size: .9em;
                    margin-top: 0;
                    margin-bottom: 1rem;
                }

                .details-cell {
                  width: 200px
                  word-break: break-all;
                }

                .details-key {
                    font-size: 0.7em;
                    margin-bottom: 0.3rem;
                }

                .details-value {
                    font-size: 0.9em
                }

                section {
                    display: flex;
                    flex-wrap: wrap;
                    color: var(--ugb-color-text);
                    gap: .5rem 1rem;
                }

                .bottom-message {
                  font-size: 0.8rem;
                }

                .table-many-columns {
                    border-color: #212427;
                }

                .table-many-columns td {
                    padding: 3px 6px;
                }

                .table-border-dotted {
                    border-style: dotted;
                    border-width: 2pt;
                }

                .table-border {
                    border-style: solid;
                    border-width: 2pt;
                }

                @media print {
                    @page {
                        size: A4;
                        orphans: 0 !important;
                        widows: 0 !important;
                    }

                    td {
                        position: static;
                    }
                }
            </style>
        </head>
        <body>
            <h1>SNIPER</h1>
            <h2 class="subtitle">Sistema Nacional de Investigação Patrimonial e Recuperação de Ativos</h2>

            {% if imageData %}
                <h3>Representação das relações</h3>
                <hr>
                <div class="graph">
                    <img id="graph-image" src="{{ imageData }}">
                </div>
            {% endif %}

            {% if node %}
                <h3>Detalhes do objeto</h3>
                <hr>

                <div class="details">
                    <div class="details-title">
                        <span>Objeto</span>
                        <h1>
                            {{ node.label | safe }}
                        </h1>
                    </div>

                    <section>
                        {% for key, value in node.properties %}
                            <div class="details-cell">
                                <div class="details-key">
                                    {{ key }}
                                </div>
                                <div class="details-value">
                                    {% if value %}
                                        {{ value }}
                                    {% else %}
                                        <span><i>(vazio)</i></span>
                                    {% endif %}
                                </div>
                            </div>
                        {% endfor %}
                    </section>
                    {% if person %}
                        <hr>
                        <div class="details-title">
                            <span>Indivíduo Relacionado</span>
                            <h1>
                                {{ person.label }}
                            </h1>
                        </div>
                        <section>
                            {% for key, value in person.properties %}
                                <div class="details-cell">
                                    <div class="details-key">{{ key }}</div>
                                    <div class="details-value">
                                        {% if value %}
                                            {{ value }}
                                        {% else %}
                                            <span><i>(vazio)</i></span>
                                        {% endif %}
                                    </div>
                                </div>
                            {% endfor %}
                        </section>
                    {% endif %}
                </div>
            {% endif %}

            {% if results | length > 0 %}
              {% for data in results %}
                {% set fields = data.fields  %}
                {% set result = data.result  %}
                {% set title = data.title  %}
                ${tableReport}
              {% endfor %}
            {% else %}
                ${tableReport}
            {% endif %}
            <p class="bottom-message">{{ bottom_message }}</p>
            {% if total %}
                <div class="modal-footer border-top">
                  <div class="total-value">
                    <h2>{{ total }}<h2>
                    <p>Valor total</p>
                  </div>
                </div>
            {% endif %}
        </body>
    </html>
`;
