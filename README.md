# Extrator Guiado por Esquema

> Este projeto foi gerado automaticamente por IA e revisado por um agente automatizado, nao por uma pessoa. Leia o codigo antes de usar.

## Descrição

MVP de linha de comando para extrair dados estruturados de um texto a partir de um esquema JSON simplificado. Em execução remota, o programa solicita ao modelo uma resposta JSON com dados e evidências. Em seguida, valida os dados e verifica se os trechos de evidência informados ocorrem literalmente no texto-fonte.

Também há um modo local que valida uma resposta JSON previamente salva, sem chamar o modelo.

## Objetivo

Transformar texto livre em um relatório JSON auditável, contendo:

- `extracted_data`: os dados retornados na chave `data`;
- `evidence`: as evidências retornadas na chave `evidence`;
- `errors`: problemas no contrato da resposta, na validação do esquema ou nas evidências;
- `warnings`: avisos sobre evidências vazias ou associadas a campos desconhecidos.

## Como funciona

1. A CLI lê um arquivo de texto UTF-8 e um arquivo de esquema JSON.
2. O esquema é restringido e validado antes do processamento.
3. Se `--response` for informado, a resposta JSON desse arquivo é usada localmente.
4. Caso contrário, o programa lê `OPENAI_API_KEY`, determina o modelo por `--model` ou `OPENAI_MODEL`, cria um cliente OpenAI e solicita uma resposta JSON.
5. A resposta deve ser um objeto com as chaves `data` e `evidence`.
6. Os dados em `data` são validados com o esquema recebido.
7. Cada evidência é validada como uma lista de textos. Para campos conhecidos e presentes em `data`, evidências não vazias devem ocorrer literalmente no texto original.
8. O relatório é gravado no caminho indicado por `--output`.

A execução termina com código `0` quando não há erros de validação, `1` quando o relatório contém erros e `2` para erros de operação, leitura, esquema ou extração.

## Arquitetura

- `requirements.txt`: arquivo de dependências do projeto.
- `src/schema_guided_extractor/__init__.py`: define a versão do pacote.
- `src/schema_guided_extractor/__main__.py`: permite a execução com `python -m schema_guided_extractor`.
- `src/schema_guided_extractor/cli.py`: interpreta os argumentos, lê arquivos, coordena os modos local e remoto e grava o relatório.
- `src/schema_guided_extractor/schema.py`: valida o subconjunto de esquema aceito.
- `src/schema_guided_extractor/extractor.py`: monta o prompt, lê a configuração da extração remota, cria o cliente OpenAI e interpreta a resposta JSON.
- `src/schema_guided_extractor/validator.py`: valida o envelope `data`/`evidence`, aplica a validação de esquema e confere as evidências.
- `tests/conftest.py`: configuração compartilhada dos testes.
- `tests/test_cli.py`: testes da interface de linha de comando.
- `tests/test_extractor.py`: testes da construção e interpretação da extração.
- `tests/test_schema.py`: testes da validação do esquema simplificado.
- `tests/test_validator.py`: testes da validação de respostas e evidências.

## Tecnologias

- Python 3.11+;
- `openai`, usado para o cliente da extração remota;
- `jsonschema`, usado com `Draft202012Validator` para validar os dados extraídos;
- `pytest, fornecido pelo ambiente de execução`, para executar os testes.

## Instalação

O projeto requer Python 3.11 ou superior. Instale as dependências declaradas no arquivo `requirements.txt` com:

```bash
python -m pip install -r requirements.txt
```

O pacote está em `src/` e o projeto não possui arquivo de instalação. Por isso, é necessário incluir `src/` no `PYTHONPATH` ao executar o pacote:

- Linux/macOS:

```bash
PYTHONPATH=src python -m schema_guided_extractor
```

- Windows (PowerShell):

```powershell
$env:PYTHONPATH="src"; python -m schema_guided_extractor
```

Sem `PYTHONPATH=src`, a execução por módulo não encontra o pacote.

## Configuração

A extração remota lê as seguintes variáveis de ambiente:

| Variável | Uso | Valor padrão |
| --- | --- | --- |
| `OPENAI_API_KEY` | Chave necessária para criar o cliente OpenAI na extração remota. | Não possui; a ausência gera erro. Configure com `<sua-chave-aqui>`. |
| `OPENAI_MODEL` | Modelo usado quando `--model` não é informado. | Não possui; a ausência gera erro na extração remota. |

A opção `--model` tem prioridade sobre `OPENAI_MODEL`.

O modo `--response` não usa essas variáveis, pois não realiza chamada remota.

## Uso

A CLI exige os argumentos `--text`, `--schema` e `--output`:

```text
python -m schema_guided_extractor --text <arquivo-texto> --schema <arquivo-esquema> --output <arquivo-relatorio>
```

Para validação local, informe também `--response`:

```text
python -m schema_guided_extractor --text <arquivo-texto> --schema <arquivo-esquema> --response <arquivo-resposta> --output <arquivo-relatorio>
```

Para extração remota, informe `--model` ou configure `OPENAI_MODEL`:

```text
python -m schema_guided_extractor --text <arquivo-texto> --schema <arquivo-esquema> --output <arquivo-relatorio> --model <nome-do-modelo>
```

Execute com o `PYTHONPATH` adequado:

```bash
# Linux/macOS
PYTHONPATH=src python -m schema_guided_extractor --text texto.txt --schema esquema.json --response resposta.json --output relatorio.json
```

```powershell
# Windows (PowerShell)
$env:PYTHONPATH="src"; python -m schema_guided_extractor --text texto.txt --schema esquema.json --response resposta.json --output relatorio.json
```

O esquema aceito deve ter `type` igual a `object`, `properties` como objeto e, opcionalmente, `required` como lista de nomes de propriedades. Propriedades aceitam os tipos `string`, `number`, `integer`, `boolean` e `array`; arrays devem declarar `items` com um tipo escalar suportado. As chaves permitidas na raiz são `type`, `properties`, `required` e `description`.

## Exemplos

Um arquivo `esquema.json` válido pode conter:

```json
{
  "type": "object",
  "properties": {
    "nome": {"type": "string"},
    "idade": {"type": "integer"},
    "interesses": {
      "type": "array",
      "items": {"type": "string"}
    }
  },
  "required": ["nome"]
}
```

Considerando um arquivo `texto.txt` com o conteúdo:

```text
Ana tem 31 anos e gosta de cinema e música.
```

Uma resposta local em `resposta.json` pode ser:

```json
{
  "data": {
    "nome": "Ana",
    "idade": 31,
    "interesses": ["cinema", "música"]
  },
  "evidence": {
    "nome": ["Ana"],
    "idade": ["31 anos"],
    "interesses": ["cinema", "música"]
  }
}
```

Execute a validação local no Linux ou macOS com:

```bash
PYTHONPATH=src python -m schema_guided_extractor --text texto.txt --schema esquema.json --response resposta.json --output relatorio.json
```

O relatório produzido preserva os dados e as evidências e inclui listas de erros e avisos. Evidências vazias geram aviso; um trecho não localizado literalmente no texto gera erro.

## Testes

Execute os testes com:

```bash
python -m pytest
```

Os testes não acessam a rede. As interações com a API são dubladas e os cenários usam arquivos locais quando necessário.

## Limitações

- O esquema suporta somente um objeto na raiz, campos escalares e arrays de itens escalares.
- Não são aceitos objetos aninhados, arrays de objetos, referências, composição ou chaves fora do subconjunto validado.
- A evidência é conferida por presença literal no texto. Essa verificação não comprova que o valor extraído foi interpretado semanticamente de forma correta.
- A evidência não é exigida para todos os campos: a validação verifica as entradas de `evidence` que forem fornecidas.
- A extração remota depende de `OPENAI_API_KEY`, de um modelo informado por `--model` ou `OPENAI_MODEL` e da disponibilidade da chamada ao modelo.
- O modo local valida uma resposta já salva, mas não realiza extração.

## O que foi aprendido

O experimento demonstra a separação entre duas responsabilidades: geração de uma resposta estruturada por um modelo e validação determinística posterior. O esquema simplificado limita o formato aceito, enquanto o relatório preserva dados, evidências, erros e avisos para inspeção. A validação literal das evidências acrescenta uma camada de rastreabilidade sem tentar inferir a correção semântica da extração.

## Possível aplicação na FOX

O padrão pode ser avaliado em fluxos que precisem converter textos em campos estruturados e manter trechos de apoio para revisão, como triagem de conteúdo textual ou preparação de informações extraídas de documentos. A validação local permite revisar respostas previamente obtidas sem realizar uma nova chamada remota.

## Status

O relatório de testes recebido informa que a execução passou: 10 testes foram coletados e os 10 testes passaram.
