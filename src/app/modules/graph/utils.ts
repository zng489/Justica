export const nodeLinks = (node: {
  group: string;
  properties: {
    CPF: string;
    Nome: string;
    CNPJ: string;
  };
}) => {
  const links = [];

  // Portal da Transparência
  const label = 'Buscar no Portal da Transparência';
  const title =
    'Verifique se esse objeto aparece nos datasets do Governo Federal, como: gastos, despesas, beneficiários e servidores';
  const urlPJ = 'https://transparencia.gov.br/busca?termo=';
  const urlPF = 'https://transparencia.gov.br/busca?termo=';

  if (['person', 'person_expanded'].includes(node.group)) {
    const cpf = node.properties.CPF || undefined;
    const searchTerm = cpf
      ? node.properties.CPF.replace(/\D/g, '')
      : node.properties.Nome;
    links.push({ title, label, url: urlPF + encodeURI(searchTerm) });
  } else if (['company', 'company_expanded'].includes(node.group)) {
    links.push({
      title,
      label,
      url: urlPJ + node.properties.CNPJ.replace(/\D/g, ''),
    });
  }

  return links;
}

export const firstLetterUpperCase = (word: string): string => {
  if (word[0].toUpperCase() !== word[0]) {
    word = word.charAt(0).toUpperCase() + word.slice(1);
  }

  return word;
}


function formataProcesso(processo: string) {
    processo = processo.replace('.', '');
    processo = processo.replace('-', '');
    let tam = processo.length;
    let quant = 20 - tam;
    for ( let j = 0; j < quant; j++ ) {
        processo = "0" + processo;
    }

    return processo.slice(0, 7)+"-"+processo.slice(7, 9)+"."+processo.slice(9, 13)+"."+
        processo.slice(13,14)+"."+processo.slice(14, 16)+"."+processo.slice(16, 20);
}


export const formatColumnRow = (
  columns: Array<{ title: string }>,
  rows: Array<object>
) => {
  const result = [];

  for (const el of rows) {
    const row = {};
    // Set title: value to show titles in mobile table layout
    for (let j = 0; j < columns.length; j++) {
          if (columns[j].title.indexOf( 'mero') != -1 ) {
            row[columns[j].title] = formataProcesso(el[j]);
           } else {
            // Translate to text if boolean values
            row[columns[j].title] =
              el[j] === true ? "Sim" : el[j] === false ? "Não" : el[j];
           }

    }
    result.push(row);
  }

  return result;
}

export const brReal = Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
});

export const deepCopy = (arr: Array<any>) => {
  let copy = [];
  arr.forEach(elem => {
    if(Array.isArray(elem)){
      copy.push(deepCopy(elem))
    }else{
      if (typeof elem === 'object') {
        copy.push(deepCopyObject(elem))
    } else {
        copy.push(elem)
      }
    }
  })
  return copy;
}

// Helper function to deal with Objects
export const deepCopyObject = (obj: {}) => {
  let tempObj = {};
  for (let [key, value] of Object.entries(obj)) {
    if (Array.isArray(value)) {
      tempObj[key] = deepCopy(value);
    } else {
      if (typeof value === 'object') {
        tempObj[key] = deepCopyObject(value);
      } else {
        tempObj[key] = value
      }
    }
  }
  return tempObj;
}

// Convert link in button
export const linkAsButton = (data: any) => {
  if (typeof data !== "string") {
    return data;
  }

  const isUrl = data.startsWith("http://") || data.startsWith("https://");
  let result: string|object = data;

  if (isUrl) {
    result = {
      buttons: [
        {
          icon: 'fa-link',
          title: `Abrir link: ${data}.`,
          url: data
        },
      ],
    }
  }

  return result;
}


export const formatRowModal = (
  rows: Array<string>
) => {
  const result = [];

  for (const row of rows) {
    const rowResult = [];
    for (const el of row) {
      rowResult.push(linkAsButton(el));
    }
    result.push(rowResult);
  }

  return result;
}
