export const Legend = `
    <style>
        .graph-legend-item .graph-legend-item-icon {
            border-radius: 0;
        }
        .graph-legend-small-icons {
            padding: 0.8rem 0.5rem 0.4rem 0.5rem;
            display: flex;
            flex-direction: column;
            gap: 0.2rem;
        }
        .graph-legend-container {
            border: 1px solid rgba(180, 180, 180, 0.7) !important;
            border-radius: 0.25rem;
            padding: 0.5rem;
            margin: 0.5rem 0;
        }
        .extra-icon {
            display: flex;
            align-items: center;
            font-size: 0.95em;
        }

        .extra-icon i {
            padding: 10px;
            margin-right: 30px;
        }
    </style>
    <div class="modal-body">
        {% for group in groups %}
            <div class="graph-legend-container">
                <div class="graph-legend-item">
                    <div class="graph-legend-item-icon" style="background-color: {{ group.obj.color.background }}">
                        <span class="fa" style="color: {{ group.obj.icon.color }}">{{ group.obj.icon.code }}</span>
                    </div>
                    <span class="graph-legend-item-description">
                        {{ group.obj.icon.description }}
                    </span>
                </div>
                <div class="graph-legend-item">
                    <div class="graph-legend-item-icon" style="background-color: {{ group.expanded.color.background }}">
                        <span class="fa" style="color: {{ group.expanded.icon.color }}">{{ group.expanded.icon.code }}</span>
                    </div>
                    <span class="graph-legend-item-description">
                        {{ group.expanded.icon.description }}
                    </span>
                </div>
                {% if group["extra-icons"]  %}
                    <div class="graph-legend-small-icons">
                        {% for extra in group["extra-icons"] %}
                            <div class="extra-icon">
                                <style>
                                    :root{
                                        --color-extra-internal-{{ extra['icon'] }}: {{ extra['color']['light'] }};
                                    }
                                    .dark {
                                        --color-extra-internal-{{ extra['icon'] }}: {{ extra['color']['dark'] }};
                                    }
                                </style>
                                <i class="fa {{ extra['icon'] }} fa-fw" style="color: var(--color-extra-internal-{{ extra['icon'] }})"></i> {{ extra['description'] }}
                            </div>
                        {% endfor %}
                    </div>
                {% endif %}
            </div>
        {% endfor %}
    </div>
`;
