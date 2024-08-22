export const NodeLabel = ` {{ node.label | safe }}
  {%- if node.extra.aeronave -%}
  <b> \uf072 </b>
  {%- endif -%}
  {%- if node.extra.embarcacao -%}
  <b> \uf13d </b>
  {%- endif -%}
  {%- if node.extra.sancao -%}
  <i> \uf05e </i>
  {%- endif -%}
  {% set regExpSC = r/^(Situação cadastral.*)/ %}
  {%- if node.group in ['company', 'company_expanded'] -%}
    {%- for key, value in node.properties -%}
        {%- if regExpSC.test(key) and value != 'Ativa' -%}
        <code> \uf071 </code>
        {%- elif key === "País" and value not in ['BRASIL', 'BRASIL (AFRETAMENTO)'] -%}
        <code> \uf57d </code>
        {%- endif -%}
    {%- endfor -%}
  {%- elif node.group in ['person', 'person_expanded'] -%}
    {%- for key, value in node.properties -%}
      {%- if key === "Ano do óbito" -%}
      <code> \uf654 </code>
      {%- elif regExpSC.test(key) and value != 'Regular' and not node.properties["Ano do óbito"] -%}
      <code> \uf071 </code>
      {%- elif key === "País de residência" and value != 'BRASIL' -%}
      <code> \uf57d </code>
      {%- endif -%}
    {%- endfor -%}
  {%- endif -%}
`;
