import { Component, AfterViewInit, ElementRef } from '@angular/core';
import {
  GraphBrowser,
  AnonymousDataSpinnerRequest,
  SpinnerRequest,
  Modal,
  CsvWriter,
  TableActions,
} from 'urlid-graph-browser';
import { HostListener } from '@angular/core';
import { Hotkey, HotkeysService } from 'angular2-hotkeys';
import { EnvService } from '../../services/env.service';
import { AvisoService } from '../../services/aviso.service';
import { GraphService } from '../../services/graph.service';
import { KeycloakService } from '../../services/keycloak.service';
import { NodeLabel } from '../../models/ugb-templates/node-label';
import { NodeDetail } from '../../models/ugb-templates/node-detail';
import { EdgeDetail } from '../../models/ugb-templates/edge-detail';
import { Legend } from '../../models/ugb-templates/legend';
import { ReportGenericTemplate } from '../../models/ugb-templates/report-generic-template';
import { nodeLinks, firstLetterUpperCase, formatColumnRow, deepCopy, brReal, formatRowModal } from './utils';
import { UserOptionsService } from '../../services/user-options.service';

@Component({
  selector: 'app-graph',
  templateUrl: './graph.component.html',
  styleUrls: ['./graph.component.scss'],
})
export class GraphComponent implements AfterViewInit {
  private graph: any;

  constructor(
    private env: EnvService,
    private aviso: AvisoService,
    private securityService: KeycloakService,
    protected hotkeysService: HotkeysService,
    private elementRef: ElementRef,
    private graphservice: GraphService,
    private userOptionService: UserOptionsService,
  ) {}

  // Show popup alert
  @HostListener('window:beforeunload', ['$event'])
  beforeunloadHandler(event) {
    return false;
  }

  async _getNodeData(nodeId: string) {
    const self = this;
    const node = await this.graph.spinner.node(nodeId);
    const result = { node, person: undefined };

    if (node.group === 'candidacy') {
      const edgeId = self.graph.network.getSelection().edges[0].split('|')[1];
      result.person = await this.graph.spinner.node(edgeId);
    }

    return result;
  }

  _printGraphData() {
    const imageData = this.graph.network.canvas.getContext().canvas.toDataURL();
    const nodes = {};
    const result = [];
    const fields = [
      { title: 'Origem' },
      { title: 'Destino' },
      { title: 'Nome' },
    ];

    // Primeiro, selecionamos os objetos que precisam entrar no relatório
    for (const nodeId of this.graph.nodes.getIds()) {
      const node = this.graph.nodes.get(nodeId);
      let obj: { tipo: string; nome: any; documento: any };

      if (
        !node.properties ||
        (!node.group.startsWith('person') && !node.group.startsWith('company'))
      ) {
        continue;
      }
      if (node.group === 'person' || node.group === 'person_expanded') {
        obj = {
          tipo: 'person',
          nome: node.properties.Nome,
          documento: node.properties.CPF,
        };
      } else if (
        node.group === 'company' ||
        node.group === 'company_expanded'
      ) {
        obj = {
          tipo: 'company',
          nome: node.properties['Razão social'],
          documento: node.properties.CNPJ,
        };
      } else {
        continue;
      }
      nodes[node.id] = obj;
    }

    // Agora, adicionamos as relações
    for (const relId of this.graph.edges.getIds()) {
      const relationship = this.graph.edges.get(relId);
      const nodeFrom = nodes[relationship.from];
      const nodeTo = nodes[relationship.to];

      if (nodeFrom === undefined || nodeTo === undefined) {
        continue;
      }
      result.push([
        `${nodeFrom.nome} (${nodeFrom.documento})`,
        `${nodeTo.nome} (${nodeTo.documento})`,
        relationship.label,
      ]);
    }

    return {
      nodes: Object.values(nodes),
      fields,
      result: formatColumnRow(fields, result),
      imageData,
      title: 'Quadro de Sócios(as)',
    };
  }

  async _printGraphComplementary() {
    const imageData = this.graph.network.canvas.getContext().canvas.toDataURL();
    const results = [];
    const selectedNode = await this.graph.network.getSelection();
    const node = await this.graph.nodes.get(selectedNode.nodes[0]);

    // If is array, there is not selected object, show toast message
    if (Array.isArray(node)) {
      this.graph.toast.info(
          "Atenção!",
          `É necessário selecionar um objeto no grafo para poder gerar esse relatório.`,
          { timeout: 5000 }
      )
      return;
    }

    // Getting selected object relations
    const [
      relFrom,
      relTo,
      relUnexistingFrom,
      relUnexistingTo
    ] = await this.graph.getNodeRelatiohipsDetails(node);
    const data = await this._getNodeData(selectedNode.nodes[0]);
    let bottom_message = "";

    // Cloning arrays
    const unexistingFrom = deepCopy(relUnexistingFrom);
    const unexistingTo = deepCopy(relUnexistingTo);

    // Adding * in unexisting graph object labels
    if (unexistingFrom.length || unexistingTo.length) {
      bottom_message = "Relações marcadas com * existem no banco de dados mão não foram expandidas no grafo atual.";
      [unexistingFrom, unexistingTo].forEach(
        arr => arr.forEach((el: Array<{ label: String }>) => el[1].label = el[1].label + "*")
      )
    }

    // Generating template variables
    const fromRelations = [...relFrom, ...unexistingFrom];
    const toRelations = [...relTo, ...unexistingTo];
    const tablesData = [];
    if (toRelations.length) {
      tablesData.push(
        {
          title: 'Relações de entrada',
          result: toRelations,
          fields: [{ title: 'Origem' }, { title: 'Relação' }]
        }
      )
    }
    if (fromRelations.length) {
      tablesData.push(
        { title: 'Relações de saída',
          result: fromRelations,
          fields: [{ title: 'Destino' }, { title: 'Relação' }]
        }
      )
    }

    // Generating edge data template variables
    for (const tableData of tablesData) {
      const rows = [];

      for (const [edge, relationship] of tableData.result) {
        rows.push([
          relationship.textLabel || relationship.label,
          edge.label
        ]);
      }
      results.push({
        title: tableData.title,
        fields: tableData.fields,
        result: formatColumnRow(tableData.fields, rows),
      })
    }

    // Returning result with node data, graph img and bottom_message
    return {
      node: data.node,
      results,
      imageData,
      bottom_message,
    };
  }

  print(template: string, data: object) {
    const winOpts =
      'left=0,top=0,width=800,height=900,toolbar=0,status=0,location=0,menubar=0,scrollbars=1,resizable=1';
    const printWin = window.open('', '_blank', winOpts);
    const templateCompiled = this.graph.compileTemplate(template);
    printWin.document.write(templateCompiled.render(data));
    printWin.document.close();

    // If contrast theme active set dark theme in print window
    const mainBody = [...this.elementRef.nativeElement.closest('body').classList];
    if (mainBody.includes('dark')){
      printWin.document.body.classList.add('dark');
    }

    printWin.onload = () => {
      printWin.focus();
      printWin.print();
    };
  }

  bindHotkeys() {
    // Setting hotkeys
    const hotkeys = [
      {
        command: 'ctrl+o',
        action: () => this.graph.triggerGraphOpenModal(),
      },
      {
        command: 'ctrl+f',
        allowIn: ['INPUT', 'SELECT', 'TEXTAREA'],
        action: () =>
          this.graph.getElement('.graph-search input[type=search]').focus(),
      },
      {
        command: 'ctrl+l',
        action: () => this.graph.clearGraphQuestion(),
      },
      {
        command: 'ctrl+s',
        allowIn: ['INPUT', 'SELECT', 'TEXTAREA'],
        action: () => this.graph.triggerGraphSave(),
      },
      {
        command: 'left',
        action: () => this.graph.triggerGraphNavigationBack(),
      },
      {
        command: 'right',
        action: () => this.graph.triggerGraphNavigationForward(),
      },
    ];
    hotkeys.forEach((element) => {
      this.hotkeysService.add(
        new Hotkey(
          element.command,
          (event: KeyboardEvent): boolean => {
            element.action();
            return false;
          },
          element.allowIn
        )
      );
    });
  }

  _authorization() {
    return this.securityService.kc
      ? `Bearer ${this.securityService.kc.token}`
      : null;
  }

  _updateToken() {
    this.graph.spinner.extraHeaders['Authorization'] = this._authorization();
  }

  _refreshToken() {
    const self = this;

    if (!this.securityService.kc.isTokenExpired()) {
      setTimeout(() => {
        self._refreshToken();
      }, 1000);
      return;
    }

    self.securityService.kc.updateToken(-1).then((refreshed) => {
      if (refreshed) {
        self._updateToken();
      }
      setTimeout(() => {
        self._refreshToken();
      }, 1000);
    });
  }

  async _modalAcceptanceTerms(
    title: string,
    content: string,
    callback: (data: { answer: string }) => void
  ) {
    const modal = new Modal('#vis');
    const template = `
      <div class="modal-body" style="padding: 1rem 2rem; text-align:justify">
        ${content}
        <br><br>
        <div style="display: flex; gap: .5rem;">
          <input id="confirmed" type="checkbox">
          <label for="confirmed" style="font-size: 0.7em; padding:0rem">
            Confirmo que li e estou de acordo com os termos acima
          </label>
        </div>
        <br>
      </div>
      <div class="modal-footer border-top">
        <button class="ma-btn" data-answer="true">Acessar</button>
      </div>`;

    await modal.showMessage(title, template, {
      html: true,
      modalSize: 'modal-large',
      callback,
      closeWhenClickOutside: false,
      onLoad: (div: any) => {
        const mainButton = div.querySelector('.ma-btn');
        const closeButton = div.querySelector('.modal-close');
        if (closeButton) {
          closeButton.remove();
        }
        mainButton.disabled = true;
        div
          .querySelector('#confirmed')
          .addEventListener('change', (e: any) => {
            mainButton.disabled = !e.target.checked;
          });
      },
    });
  }

  async termsModal() {
    const self = this;
    const template = self.graph.compileTemplate(
      self.graph.apiConfig.user.terms.template
    );
    await self._modalAcceptanceTerms(
      self.graph.apiConfig.user.terms.title,
      template.render(self.graph.apiConfig.user),
      async (data: {answer: string}) => {
        if (JSON.parse(data.answer) === true) {
          await self.graph.spinner.post('/v1/terms');
          await self.afterGraphInit();
        } else {
          self.graph.toast.error(
            'Negado!<br>',
            `Autorização <b>não concedida</b>`,
            { timeout: 5000 }
          );
          await self.termsModal();
        }

        return;
      }
    );
  }

  async unauthorizedModal(title: string, content: string) {
    const modal = new Modal('#vis');

    const template = `
      <div class="modal-body" style="padding: 1rem 2rem; text-align:justify">
        ${content}
      </div>`;
    await modal.showMessage(title, template, {
      html: true,
      modalSize: 'modal-large',
      closeWhenClickOutside: false,
    });
  }

  async _modalShowMessageCsvPrintable(
    dataset: { nodeId: string, linkLabel: string },
    data: {
      title: string;
      fields: Array<{ title: string }>;
      result: Array<object>;
      results: Array<object>;
    },
  ) {
    const self = this;
    const nodes = await self._getNodeData(dataset.nodeId);
    let title = data.title ? data.title : dataset.linkLabel.replace('-', ' ');
    title = firstLetterUpperCase(title);
    // genericListTemplate expects `result` but Sniper API returns as `results`
    if (data.results !== undefined && data.result === undefined) {
      data.result = data.results;
      data.results = undefined;
    }
    const html = self.graph.getGenericListTemplate().render({
      title,
      ...data,
      ...nodes,
    });

    self.graph.modal.showMessage(title, html, {
      modalSize: 'modal-xlarge',
      closeWhenClickOutside: true,
      html: true,
      headerExtraButtons: [
        {
          title: 'Imprimir',
          label: '<i class="fa fa-print"></i>',
          class: 'report-print',
          action: () => {
            self.print(ReportGenericTemplate, {
              title,
              ...data,
              ...nodes,
              result: formatColumnRow(data.fields, data.result),
            });
          },
        },
        {
          title: 'Baixar tabela em CSV',
          label: '<i class="fa fa-file-download"></i>',
          class: 'csv-report',
          action: () => {
            const fields = data.fields;
            const elements = data.result;
            const header = [];

            // Header
            for (const field of fields) {
              header.push(field.title);
            }

            const csvResult = new CsvWriter(header);

            // Rows
            for (const row of elements) {
              csvResult.addRow(row);
            }

            // Create anchor element pointing to CSV data and click on it
            csvResult.anchorElement(title);
          },
        },
      ],
      onLoad: async (div: HTMLElement) => {
        const table = new TableActions(div.querySelector('.generic-table'));
      },
    });
  }

  _tablePartsAsButtons(dataJson: any) {
    const self = this;
    const result = [];

    if (dataJson.error) {
      self.graph.toast.error(
        'Erro!<br>',
        `mensagem <b>${dataJson.message}</b>`,
        { timeout: 5000, html: true }
      );
      return [];
    }

    for (const object of dataJson.results) {
      if (object.partes !== undefined) {
        object.partes = {
          buttons: [
            {
              class: 'progress extra-data',
              icon: 'fa-arrow-right',
              title: 'Clique para acessar dados.',
              datasets: [
                {
                  name: 'fields',
                  data: JSON.stringify(dataJson.fields[1]),
                },
                {
                  name: 'parts',
                  data: JSON.stringify(object.partes),
                },
                {
                  name: 'title',
                  data: 'Pessoas relacionadas',
                },
                {
                  name: 'description',
                  data: object.numero ?
                          `Processo: ${object.numero}` :
                          object.codigo_ordem_judicial ?
                              `Ordem: ${object.codigo_ordem_judicial}` :
                              `Protocolo: ${object.protocolo}`,
                },
              ],
            },
          ],
        };
      }
      const values = [];
      for (const field of dataJson.fields[0]) {
        values.push(object[field.name]);
      }
      result.push(values);
    }

    return result;
  }

  async afterGraphInit() {
    const self = this;

    // Values to show or hide setup options
    const availableIntegrations = self.graph.apiConfig.integrations || {};
    self.userOptionService.setSisbajudOrdens(availableIntegrations.SISBAJUD_ORDENS === true);

    if (availableIntegrations.INFOJUD === true) {
      self.userOptionService.setInfojud(true);
      self.graph.attachExternalEventListener(
        'click',
        '.extra-data-infojud',
        async (event, closest) => {
          const dataJson = await this.graph.spinner.infojudIncomeTax(closest.dataset.document);
          const title = dataJson.title;
          let html = "";

          for (const tabName in dataJson['fields']) {
            if (tabName == "title" || tabName == "description") {
              continue;
            }
            let tab = dataJson['results'][tabName];
            const tabDiv =
              `<div id="content_${tabName}" class="tab-content" data-title="${tab.tab_name}">`;

            if (tabName === "resumo") {
              const resume = tab;
              const resumeResult = resume.result;
              const result = {};

              for (const field of resume["fields"]) {
                result[field.title] = resumeResult[field.name];
              }

              html += tabDiv;
              html += self.graph.getDetailsTemplate().render({
                node: {
                  label: `Essa é a declaração relativa ao documento:
                    ${resumeResult["documento"]}, do processo ${resumeResult["numero_processo"]}.`,
                  properties: result,
                },
                details_clean: true,
              });
              html += `</div>`;
              continue;
            }

            const results = [];
            for (const result of tab['result']) {
              const row = [];
              for (const tabField of tab['fields']){
                row.push(result[tabField['name']]);
              }
              results.push(row);
            }
            html += tabDiv;
            html +=
              self.graph.getGenericListTemplate().render({
              rowIdField: 'object_uuid',
              fields: tab['fields'],
              result: results,
              total: tab['total'] ? { label: "Total Atual", value: `${brReal.format(tab['total'])}` } : undefined,
              last_total: tab['total_anterior'] ? { label: "Total Anterior", value: `${brReal.format(tab['total_anterior'])}` } : undefined,
            });
            html+= `</div>`;
          }

          self.graph.modal.showMessage(
            title,
            html,
            {
              modalSize: 'modal-xlarge',
              extra: true,
              html: true,
              tabs: true,
              onLoad: async (div: HTMLElement) => {
                div.querySelectorAll('.generic-table').forEach((table:HTMLElement) => {
                  let tableOptions = {};

                  // if table has rowId
                  const dataset = table.querySelector("[data-row-id]")
                  if (dataset.getAttribute('data-row-id')) {
                    const rowIds = [];
                    for (const tr of Array.from(table.querySelectorAll('tbody>tr'))){
                      rowIds.push(tr['dataset']['rowId']);
                    }
                    tableOptions = {
                      checkableRows: true,
                      checkedElementsCallback: async (checked: Array<string>) => {
                        await self.graph.addNodesExpanded(checked);
                        return self.graph.nodesAlreadyInGraph(rowIds);
                      },
                      alreadyAddedElements: self.graph.nodesAlreadyInGraph(rowIds),
                      checkableButtonLabel: 'Carregar no grafo',
                    }
                  }
                  new TableActions(table, tableOptions)
                });
              },
            });
        }
      );

    }

    self.graph.addReport(
      async () => {
        const result = await self._printGraphComplementary();
        if (result) {
          self.print(ReportGenericTemplate, { ...result });
        }
      },
      {
        label: "Imprimir dados do objeto",
        title: "Dados complementares disponíveis no grafo e barra lateral",
      }
    );

    self.graph.addReport(
      async () => {
        self.print(ReportGenericTemplate, { ...self._printGraphData() });
      },
      {
        label: "Imprimir relações do objeto",
        title: "Relatório com relações dispostas no grafo",
      }
    );

    self.graph.attachExternalEventListener(
      'click',
      '.extra-data',
      async (event, closest) => {
        const result = [];
        const btnDataset = closest.closest('button').dataset;

        for (const object of JSON.parse(
          btnDataset.parts
        )) {
          const values = [];
          for (const field of JSON.parse(btnDataset.fields)) {
            values.push(object[field.name]);
          }
          result.push(values);
        }

        const html = self.graph.getGenericListTemplate().render({
          title: btnDataset.title,
          description: btnDataset.description,
          rowIdField: 'object_uuid',
          fields: JSON.parse(btnDataset.fields),
          result,
        });

        await self.graph.modal.showMessage(
          btnDataset.title,
          html,
          {
            modalSize: 'modal-xlarge',
            html: true,
            extra: true,
            onLoad: async (div: any) => {
              const table = div.querySelector('.generic-table');
              const rowIds = [];

              for (const tr of table.querySelectorAll('tbody>tr')){
                rowIds.push(tr.dataset.rowId);
              }

              const tableActions = new TableActions(table, {
                checkableRows: true,
                checkedElementsCallback: async (checked: Array<string>) => {
                  await self.graph.addNodesExpanded(checked);
                  return self.graph.nodesAlreadyInGraph(rowIds);
                },
                alreadyAddedElements: self.graph.nodesAlreadyInGraph(rowIds),
                checkableButtonLabel: 'Carregar no grafo',
              });
            },
          }
        );
      }
    );

    self.graph.attachExternalEventListener(
      'click',
      '.law-suits',
      async (event, closest) => {
        const dataset = self.graph.network.getSelection().nodes[0];
        const dataJson = await self.graph.spinner.lawSuits(dataset);
        const nodes = await self._getNodeData(dataset);
        const result = this._tablePartsAsButtons(dataJson);
        const title = dataJson.title;
        const html = self.graph.getGenericListTemplate().render({
          title,
          description: dataJson.description,
          fields: dataJson.fields[0],
          result,
          ...nodes,
        });

        self.graph.modal.showMessage(title, html, {
          modalSize: 'modal-xlarge',
          closeWhenClickOutside: true,
          html: true,
          onLoad: async (div: HTMLElement) => {
            const table = new TableActions(div.querySelector('.generic-table'));
          },
        });
      }
    );

    self.graph.attachExternalEventListener(
      'click',
      '.complementary-dataset',
      async (event: any, closest: { dataset: { linkLabel: string, nodeId: string} }) => {
        const dataset = closest.dataset;
        const data = await self.graph.spinner.objectDataset(
          dataset.linkLabel,
          dataset.nodeId
        );
        await this._modalShowMessageCsvPrintable(dataset, data);
      }
    );

    self.graph.attachExternalEventListener(
      'click',
      '.financial-accounts',
      async (event: any, closest: { dataset: { linkLabel: string, nodeId: string} }) => {
        const dataset = closest.dataset;
        const data = await self.graph.spinner.sisbajudAccounts(
          dataset.nodeId,
        );
        await this._modalShowMessageCsvPrintable(dataset, data);
      }
    );
  }

  async ordersJudgeDocInputModal() {
    const self = this;

    await self.graph.modal.askQuestion(
      "Ordens",
      "Digite o documento do juiz que deseja visualizar as ordens de quebra de sigilo.",
      {
        label: "CPF",
        placeholder: "000.000.000-00",
        callback: async (
              data: { action: string, answerResult?: [ { fields?: [ { value?: string } ] } ]}
          ) =>
          {
            if (data.action === "answered") {
              if (!data.answerResult) {
                return { closeModal: false };
              }
              const judgeId = data.answerResult[0].fields[0].value.replace(/\D/g, "").substring(0, 11);
              localStorage.setItem("judge_id", judgeId);

              await self.ordersModal(judgeId);
              return { closeModal: false }
            }
         },
         "onLoad": (div: HTMLElement) => {
          const input:HTMLInputElement = div.querySelector("input[name='ma-answer']");
          input.addEventListener("input", function () {
            let n = this.value.replace(/\D/g, "").substring(0, 11);
            this.setAttribute("data-normalized", n);
            if(n.length === 11) {
              let valid = n.split('').map(el => +el)
              const rest = (count:number) =>
              (valid.slice(0, count-12).reduce( (soma, el, index) => (soma + el * (count-index)), 0 )*10) % 11 % 10;
              if (rest(10) === valid[9] && rest(11) === valid[10] && n != "00000000000") {
                 input.style.backgroundColor = "rgba(3, 252, 11, .08)";
              } else {
                 input.style.backgroundColor = "rgba(252, 3, 3, .08)";
              }
            } else {
              input.style.backgroundColor = "";
            }
            n = n.replace(/(\d{3})(\d)/,"$1.$2")
            n = n.replace(/(\d{3})(\d)/,"$1.$2")
            n = n.replace(/(\d{3})(\d{1,2})$/,"$1-$2")
            this.value = n;
          });
         }
      }
    );
  }

  async ordersModal(judgeId: string) {
    const self = this;
    const dataJson = await this.graph.spinner.sisbajudOrders(judgeId);
    const title = dataJson.title;

    if (dataJson.error) {
      self.graph.toast.error(
          "Erro",
          dataJson.message,
      )
      // If user is not a judge send back to orders
      if (!self.graph.apiConfig.user.juiz) {
        localStorage.removeItem("judge_id");
        self.ordersJudgeDocInputModal();
      }
      return;
    }

    const result = this._tablePartsAsButtons(dataJson);
    const html = self.graph.getGenericListTemplate().render({
      title,
      description: dataJson.description,
      fields: dataJson.fields[0],
      result: formatRowModal(result),
    });

    self.graph.modal.showMessage(title, html, {
      modalSize: 'modal-xlarge',
      html: true,
      onLoad: async (div: HTMLElement) => {
        let nomeJuiz;
        try {
          nomeJuiz = JSON.parse(dataJson.nome_juiz);
        } catch (err) {
          nomeJuiz = dataJson.nome_juiz;
        }

        new TableActions(div.querySelector('.generic-table'));
        // Setting judge tag in modal if user is not a judge
        if (!self.graph.apiConfig.user.juiz) {
          const element = document.createElement("div");
          element.innerHTML = `
            <div style="
                    border: 1px solid var(--ugb-color-primary);
                    display: flex;
                    justify-content: space-between;
                    padding: .5rem 1rem;margin-bottom: .5rem;
                 "
            >
              <span><b>Juiz(a):</b> ${nomeJuiz}</span>
              <button class="ma-close remove-judge" style="cursor: pointer; background: none; border:none;" title="Remover juiz">
                <i class="fa-regular fa-circle-xmark" style="color: var(--color-darker);"></i>
              </button>
            </div>
          `;
          div.querySelector(".modal-body").insertBefore(element, div.querySelector('.ta-search'));

          div.querySelector(".remove-judge").addEventListener("click", async (e) => {
            localStorage.removeItem("judge_id");
          })
        }
      },
    });
  };

  ngAfterViewInit(): void {
    const self = this;
    this.graph = new GraphBrowser('#vis', {
      apiUrl: this.env.apiUrl,
      templateContextProcessors: {
        "nodeDetail": function nodeDetailTemplateContextProcessor(data: object) {
          return { ...data, enabledIntegrations: self.graph.apiConfig.integrations };
        }
      },
      spinnerErrorCallback: function (url: string, response:{message: string, detail: { title: string, content: string}}) {
        self.graph.toast.error(
            response.message || "Erro",
            response.detail || `Ocorreu um erro ao acessar o endereço ${url}`,
            { timeout: 5000 },
        )
      },
      SpinnerClass: class SpinnerClass extends SpinnerRequest {
        async lawSuits(objectUuid: string) {
          return await super.get(`/v1/processos/${objectUuid}`);
        }
        async sisbajudAccounts(objectUuid: string) {
          return await super.get(`/v1/sisbajud-contas/${objectUuid}`);
        }
        async sisbajudOrders(judgeId: string) {
          return await super.get(`/v1/sisbajud-ordens?cpf=${judgeId}`);
        }
        async infojudOrders() {
          return await super.get(`/v1/declaracao-renda-lista/`);
        }
        async infojudIncomeTax(document: string, year: string = "2020") { // TODO: Change, set value from real data
          const docResult = document.match(/\d+/g).join("");
          return await super.get(`/v1/declaracao-renda/${docResult}/${year}/`);
        }
      },
      AnonymousDataSpinnerClass: class AnonymousDataSpinnerClass extends AnonymousDataSpinnerRequest {
          async lawSuits(objectUuid: string) {
            const result = await super.get(`/v1/processos/${objectUuid}`);
            this.partsResultAnonimyze(result);

            return result;
          }
          partsResultAnonimyze(result) {
            for (let i = 0; i < result.results.length; i++) {
              for (const key of Object.keys(result.results[i].resumo)){
                if (result.results[i].resumo[key]) {
                  result.results[i].resumo[key] = "Exemplo data"
                }
              }
              if (result.results[i].partes) {
                for (let j = 0; j < result.results[i].partes.length; j++) {
                  for (const key of Object.keys(result.results[i].partes[j])){
                    result.results[i].partes[j][key] = "Exemplo data"
                  }
                }
              }
            }
          }
          async sisbajudAccounts(objectUuid: string) {
            const dataJson = await super.get(`/v1/sisbajud-contas/${objectUuid}`);
            const listResultElements = dataJson.results[0] ? new Array(dataJson.results[0].length).fill("Exemplo conteúdo") : undefined;
            const listResult = [];
            if (listResultElements) {
                  for (let i = 0; i < dataJson.results.length; i++) {
                      listResult.push(listResultElements);
                  }
              }
              dataJson.results = listResult;

              if (dataJson.results.total){
                 dataJson.results.total = 0;
              }
              if (dataJson.results.description) {
                  dataJson.results.description = "Os dados abaixo são exemplos: ";
              }

              return dataJson.results;
          }
          async sisbajudOrders(judgeId: string) {
            const result = await super.get(`/v1/sisbajud-ordens?cpf=${judgeId}`);
            this.partsResultAnonimyze(result);

            return result;
          }
      },
      ToastClass: class Toast {
        success(
          message: string,
          text: string,
          { timeout }: { timeout?: number } = {}
        ) {
          self.aviso.putSuccess(`<b>${message}</b><br>` + ` ${text}`, timeout ? { timeout } : undefined);
        }

        info(message: string, text: string, { timeout }: { timeout?: number } = {}) {
          self.aviso.putInfo(`<b>${message}</b><br>` + ` ${text}`, timeout ? { timeout } : undefined);
        }

        error(
          message: string,
          text: string & { title: string, content: string },
          { timeout }: { timeout?: number } = {}
        ) {
          let textResult: string;
          switch (message) {
            case 'terms-user-not-found':
            case 'terms-anonymous-user':
            case 'keycloak-forbidden':
            case 'keycloak-integration-error':
            case 'keycloak-no-token':
              textResult = 'A autenticação falhou';
              break;
            case 'terms-not-accepted':
              self.termsModal();
              break;
            case 'keycloak-profile-unauthorized':
              self.unauthorizedModal(text.title, text.content);
              break;
            default:
              textResult = text;
              break;
          }

          if (textResult){
            self.aviso.putError(`<b>${message}</b><br>` + ` ${textResult}`, timeout ? { timeout } : undefined);
          }
        }

        warning(
          message: string,
          text: string,
          { timeout }: { timeout?: number } = {}
        ) {
          self.aviso.putWarning(`<b>${message}</b><br>` + ` ${text}`, timeout ? { timeout } : undefined);
        }
      },
      extraHeaders: {
        Authorization: this._authorization(),
      },
      modalOnBody: true,
      templateStrings: {
        'node-label': NodeLabel,
        'node-detail': NodeDetail,
        legend: Legend,
        'edge-detail': EdgeDetail,
      },
      extraIcons: {
        person: [
          {
            icon: 'fa-cross',
            color: 'base',
            description: 'Falecido(a)',
          },
          { icon: 'fa-ban', color: 'warning', description: 'Possui sanções' },
          {
            icon: 'fa-anchor',
            color: 'primary',
            description: 'Proprietário(a) ou afretador(a) de embarcação(ões)',
          },
          {
            icon: 'fa-plane',
            color: 'primary',
            description: 'Proprietário(a) ou operador(a) de aeronave(es)',
          },
          {
            icon: 'fa-globe-americas',
            color: 'base',
            description: 'Reside no exterior',
          },
          {
            icon: 'fa-exclamation-triangle',
            color: 'base',
            description: 'Situação cadastral não regular',
          },
        ],
        company: [
          {
            icon: 'fa-globe-americas',
            color: 'base',
            description: 'Domiciliada no exterior',
          },

          { icon: 'fa-ban', color: 'warning', description: 'Possui sanções' },
          {
            icon: 'fa-anchor',
            color: 'primary',
            description: 'Proprietário(a) ou afretador(a) de embarcação(ões)',
          },
          {
            icon: 'fa-plane',
            color: 'primary',
            description: 'Proprietário(a) ou operador(a) de aeronave(es)',
          },
          {
            icon: 'fa-exclamation-triangle',
            color: 'base',
            description: 'Situação cadastral não ativa',
          },
        ],
      },
      nodeLinks: nodeLinks,
    });

    this.graph.init().then(async () => {
      if (self.graph.apiConfig.message &&
        self.graph.apiConfig.message === 'keycloak-profile-unauthorized') {
        return;
      } else if (
        !self.graph.apiConfig.user ||
        !self.graph.apiConfig.user.terms ||
        !self.graph.apiConfig.user.terms.accepted_at
      ) {
        await self.termsModal();
      } else {
        await self.afterGraphInit();
      }

      // Por algum motivo não foi possível deixar automaticamente o
      // refresh token do Keycloak funcionando, então checamos a cada 1s
      // se o token foi expirado e forçamos a atualização.
      // TODO: ver forma melhor de contemplar a atualização, com um
      // setTimeout mais preciso (de acordo com o tempo de expiração do
      // token, ou utilizando um callback do Keycloak).
      setTimeout(() => {
        self._refreshToken();
      }, 1000);
    });

    // Getting navbar buttons clicks user interactions
    this.graphservice.orderGraphRequest().subscribe(async () => {
      const judgeId = localStorage.getItem('judge_id') ? localStorage.getItem('judge_id') :
        self.graph.apiConfig.user.juiz ? self.graph.apiConfig.user.cpf :
        undefined;

      if (judgeId) {
        await self.ordersModal(judgeId);
        return;
      }

      await self.ordersJudgeDocInputModal()
    })

    this.graphservice.infoGraphRequest().subscribe(async () => {
      const dataJson = await self.graph.spinner.infojudOrders();
      const results = [];
      const fields = [...dataJson.fields, { name: "actions", title: "Detalhes", type: "string" }];

      for (const object of dataJson.results) {
        object.actions = {
          buttons: [
            {
              class: 'progress extra-data-infojud',
              icon: 'fa-arrow-right',
              title: 'Clique para acessar dados.',
              datasets: [
                {
                  name: "document",
                  data: object['documento'],
                },
              ],
            },
          ],
        };

        const values = [];
        for (const field of fields) {
          values.push(object[field.name]);
        }
        results.push(values);
      }

      const title = dataJson.title;
      const html = self.graph.getGenericListTemplate().render({
        title,
        description: dataJson.description,
        fields: fields,
        result: results,
      });

      self.graph.modal.showMessage(title, html, {
        modalSize: 'modal-xlarge',
        closeWhenClickOutside: true,
        html: true,
        onLoad: async (div: HTMLElement) => {
          const table = new TableActions(div.querySelector('.generic-table'));
        },
      });
    })

    this.bindHotkeys();

    // Pause and unpause hotkeys when modal is opened
    const evts = [
      {
        type: 'modalopened',
        action: () =>
          self.hotkeysService.pause([...self.hotkeysService.hotkeys]),
      },
      {
        type: 'modalclosed',
        action: () =>
          self.hotkeysService.unpause([...self.hotkeysService.pausedHotkeys]),
      },
    ];
    for (const evt of evts) {
      this.elementRef.nativeElement
        .querySelector('#vis')
        .addEventListener(evt.type, evt.action);
    }
  }
}
