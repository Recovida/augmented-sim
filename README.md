# Augmented SIM

<!-- ABOUT:BEGIN -->

Este programa lê um conjunto de tabelas (CSV ou DBF) com dados de óbitos
codificados de acordo com o *Sistema de Informação sobre Mortalidade* (SIM)
e, a partir das informações disponíveis nas colunas já existentes,
cria um único arquivo contendo todos os dados após o acréscimo de algumas
colunas. Para instruções de instalação e uso, veja o arquivo
[README_INSTALL.md](https://gitlab.com/recovida/augmented-sim/-/blob/master/README_INSTALL.md).
Para informações sobre o projeto do qual este
programa faz parte, consulte o
[repositório de índice](https://gitlab.com/recovida/index).

O programa salva um único arquivo no formato CSV (*comma-separated values*),
que pode ser aberto por diversos programas que tratam de dados tabulados,
tais como
[R](https://www.r-project.org/),
[Microsoft Excel](https://www.microsoft.com/en/microsoft-365/excel),
[LibreOffice](https://www.libreoffice.org/),
[SAS](https://www.sas.com/),
[Stata](https://www.stata.com/) e
[MiniTab](https://www.minitab.com/).

<!-- ABOUT:END -->

**Importante:**

- Se algum dos arquivos de entrada contiver mais de uma coluna com o mesmo
  nome, **apenas uma** será mantida. Isto é uma consequência do funcionamento dos
  parsers.
- Se algum dos arquivos de entrada possuir alguma coluna com o mesmo nome de
  uma das colunas a serem inseridas por este programa,
  a coluna original será **substituída**.

Seguem as colunas que este programa insere. Note que não são inseridas colunas
que dependem da existência de colunas que não
estão presentes nos arquivos de entrada.

- `DIA`, `MES` e `ANO`:
  representam o dia, o mês e o ano do falecimento,
  a partir da coluna `DTOBITO`.

- `SEMANAEPI` e `ANOEPI`:
  representam o número da
  [semana epidemiológica](https://portalsinan.saude.gov.br/calendario-epidemiologico)
  à qual pertence o dia de falecimento obtido na coluna `DTOBITO`, e o ano
  correspondente (que pode não ser igual ao valor de `ANO`).

- `IDADEGERAL`, `IDADECAT1` e `IDADECAT2`:
  representam, respectivamente, a idade em anos e as categorias descritas
  na tabela abaixo.

<table>
<thead>
  <tr>
    <th>Intervalo de <code>IDADEGERAL</code></th>
    <th><code>IDADECAT1</code></th>
    <th><code>IDADECAT2</code></th>
  </tr>
</thead>
<tbody>
  <tr>
    <td align="center">menos de 1 ano</td>
    <td align="center">1</td>
    <td align="center" rowspan="2">1</td>
  </tr>
  <tr>
    <td align="center">1 a 4 anos</td>
    <td align="center">2</td>
  </tr>
  <tr>
    <td align="center">5 a 9 anos</td>
    <td align="center">3</td>
    <td align="center" rowspan="3">2</td>
  </tr>
  <tr>
    <td align="center">10 a 14 anos</td>
    <td align="center">4</td>
  </tr>
  <tr>
    <td align="center">15 a 19 anos</td>
    <td align="center">5</td>
  </tr>
  <tr>
    <td align="center">20 a 24 anos</td>
    <td align="center">6</td>
    <td align="center" rowspan="4">3</td>
  </tr>
  <tr>
    <td align="center">25 a 29 anos</td>
    <td align="center">7</td>
  </tr>
  <tr>
    <td align="center">30 a 34 anos</td>
    <td align="center">8</td>
  </tr>
  <tr>
    <td align="center">35 a 39 anos</td>
    <td align="center">9</td>
  </tr>
  <tr>
    <td align="center">40 a 44 anos</td>
    <td align="center">10</td>
    <td align="center" rowspan="4">4</td>
  </tr>
  <tr>
    <td align="center">45 a 49 anos</td>
    <td align="center">11</td>
  </tr>
  <tr>
    <td align="center">50 a 54 anos</td>
    <td align="center">12</td>
  </tr>
  <tr>
    <td align="center">55 a 59 anos</td>
    <td align="center">13</td>
  </tr>
  <tr>
    <td align="center">60 a 64 anos</td>
    <td align="center">14</td>
    <td align="center" rowspan="2">5</td>
  </tr>
  <tr>
    <td align="center">65 a 69 anos</td>
    <td align="center">15</td>
  </tr>
  <tr>
    <td align="center">70 a 74 anos</td>
    <td align="center">16</td>
    <td align="center" rowspan="2">6</td>
  </tr>
  <tr>
    <td align="center">75 a 79 anos</td>
    <td align="center">17</td>
  </tr>
  <tr>
    <td align="center">80 a 84 anos</td>
    <td align="center">18</td>
    <td align="center" rowspan="2">7</td>
  </tr>
  <tr>
    <td align="center">85 a 89 anos</td>
    <td align="center">19</td>
  </tr>
  <tr>
    <td align="center">90 anos ou mais</td>
    <td align="center">20</td>
    <td align="center">8</td>
  </tr>
</tbody>
</table>

- `AREARENDA`: representa a renda do bairro de residência obtido a partir
  da coluna `CODBAIRES`, de acordo com os valores abaixo.

<table>
  <thead>
    <tr>
      <th>Renda do bairro de código <code>CODBAIRES</code><br></th>
      <th><code>AREARENDA</code></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center">Alta</td>
      <td align="center">1</td>
    </tr>
    <tr>
      <td align="center">Intermediária</td>
      <td align="center">2</td>
    </tr>
    <tr>
      <td align="center">Baixa</td>
      <td align="center">3</td>
    </tr>
  </tbody>
</table>

- `GARBAGECODE`:
  indica o nível da
  [Causa Global de Morbidade (GBD)](https://www.healthdata.org/gbd/)
  correspondente à causa básica obtida na coluna `CAUSABAS`
  quando é um *garbage code*, entre 1 e 4, ou 0 em caso contrário
  (segundo a *Appendix Table 3* do *Supplementary appendix 1* que acompanha
    o artigo
    [*Global, regional, and national age-sex specific mortality for 264 causes
    of death, 1980–2016: a systematic analysis for the Global Burden of
    Disease Study 2016*](https://doi.org/10.1016/S0140-6736(17)32152-9)).

- `CAPCID`:
  indica o número do capítulo da [CID-10](https://icd.who.int/browse10/)
  que contém a causa básica obtida na coluna `CAUSABAS`, ou "\*\*" caso o
  valor da coluna seja inválido.

- `COVID`:
  representa a possibilidade de a causa obtida na coluna
  `CAUSABAS` indicar um óbito causado pela COVID-19, conforme tabela abaixo.

<table>
<thead>
  <tr>
    <th><code>CAUSABAS</code></th>
    <th></th>
    <th><code>COVID</code></th>
  </tr>
</thead>
<tbody>
  <tr>
    <td align="center">U04</td>
    <td align="center">Suspeita</td>
    <td align="center">2</td>
  </tr>
  <tr>
    <td align="center">B34.2</td>
    <td align="center">Sim</td>
    <td align="center">1</td>
  </tr>
  <tr>
    <td align="center">Ausente</td>
    <td align="center" rowspan="2">Sem informação</td>
    <td align="center" rowspan="3">0</td>
  </tr>
  <tr>
    <td align="center">Inválida</td>
  </tr>
  <tr>
    <td align="center">Outra</td>
    <td align="center">Não</td>
  </tr>
</tbody>
</table>

- `CIDBR`: indica o código da
  [CID-BR-10](http://tabnet.saude.mg.gov.br/Notas_tecnicas/Mortalidade_CID-10_Lista_CID-BR.pdf)
   correspondente à causa básica da coluna `CAUSABAS`.

- `DCOR`, `OUTCOR`, `AVC`, `GRIPE`, `PNEUMONIA`, `DPOCASMA`, `GPP`, `PERI`,
  `ACTRANS`, `QUEDAFOGINT`, `SUIC`, `HOMIC`, `EXTIND`, `INTLEG` e
  `OUTEXT`: indicam
  o tipo da causa obtida na coluna `CAUSABAS`, de acordo com a tabela abaixo.
  Essas colunas têm valor 0 se a causa não estiver no intervalo.
  Quando a causa está no intervalo, o valor dessas colunas é 1,
  com exceção das colunas `GPP` e `PERI`, que variam de 1 a 5 conforme
  o código CID-BR varia de 88 a 92 e de 93 a 97, respectivamente.

<table>
  <thead>
    <tr>
      <th>CID-BR</th>
      <th>Coluna</th>
      <th>Nome (segundo CID-BR-10)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center">68</td>
      <td align="center"><code>DCOR</code></td>
      <td align="center">Doenças isquêmicas do coração</td>
    </tr>
    <tr>
      <td align="center">69</td>
      <td align="center"><code>OUTCOR</code></td>
      <td align="center">Outras doenças cardíacas</td>
    </tr>
    <tr>
      <td align="center">70</td>
      <td align="center"><code>AVC</code></td>
      <td align="center">Doenças cerebrovasculares</td>
    </tr>
    <tr>
      <td align="center">73</td>
      <td align="center"><code>GRIPE</code></td>
      <td align="center">Influenza (gripe)</td>
    </tr>
    <tr>
      <td align="center">74 e 75</td>
      <td align="center"><code>PNEUMONIA</code></td>
      <td align="center">Pneumonia; Outras infecções agudas das vias aéreas inferiores</td>
    </tr>
    <tr>
      <td align="center">76</td>
      <td align="center"><code>DPOCASMA</code></td>
      <td align="center">Doenças crônicas das vias aéreas inferiores [incl. DPOC e asma]</td>
    </tr>
    <tr>
      <td align="center">88 a 92</td>
      <td align="center"><code>GPP</code></td>
      <td align="center">Gravidez, parto e puerpério</td>
    </tr>
    <tr>
      <td align="center">93 a 97</td>
      <td align="center"><code>PERI</code></td>
      <td align="center">Algumas afecções originadas no período perinatal</td>
    </tr>
    <tr>
      <td align="center">104</td>
      <td align="center"><code>ACTRANS</code></td>
      <td align="center">Acidentes de transporte</td>
    </tr>
    <tr>
      <td align="center">105 até 108</td>
      <td align="center"><code>QUEDAFOGINT</code></td>
      <td align="center">Quedas; Afogamentos e submersões acidentais; Exposição à fumaça, ao fogo e às chamas; Envenenamento acidental por e exposição a substâncias nocivas </td>
    </tr>
    <tr>
      <td align="center">109</td>
      <td align="center"><code>SUIC</code></td>
      <td align="center">Lesões autoprovocadas voluntariamente</td>
    </tr>
    <tr>
      <td align="center">110</td>
      <td align="center"><code>HOMIC</code></td>
      <td align="center">Agressões</td>
    </tr>
    <tr>
      <td align="center">111</td>
      <td align="center"><code>EXTIND</code></td>
      <td align="center">Eventos (fatos) cuja intenção é indeterminada</td>
    </tr>
    <tr>
      <td align="center">112</td>
      <td align="center"><code>INTLEG</code></td>
      <td align="center">Intervenções legais e operações de guerra</td>
    </tr>
    <tr>
      <td align="center">113</td>
      <td align="center"><code>OUTEXT</code></td>
      <td align="center">Outras causas externas</td>
    </tr>
  </tbody>
  </table>



## Projeto Recovida

Este repositório e os demais repositórios deste grupo fazem parte do projeto
**Recovida**
(*Reavaliação da Mortalidade por Causas Naturais no Município de São Paulo
durante a Pandemia da COVID-19*),
da
[Faculdade de Medicina da Universidade de São Paulo](https://www.fm.usp.br/),
sob responsabilidade do
[Prof. Dr. Paulo Andrade Lotufo](https://uspdigital.usp.br/especialistas/especialistaObter?codpub=F7A214F0B89F),
e com a atuação da [Dra. Ana Carolina de Moraes Fontes Varella](https://bv.fapesp.br/en/pesquisador/690479/ana-carolina-de-moraes-fontes-varella/) como supervisora de dados.

Sob a orientação de Paulo Lotufo e a supervisão de Ana Varella,
o desenvolvimento está sendo feito por:

- Débora Lina Nascimento Ciriaco Pereira (bolsista de dez/2020 a set/2021);
- Vinícius Bitencourt Matos (bolsista de dez/2020 a set/2021).


## Apoio

Agradecemos à iniciativa [Todos pela Saúde](https://www.todospelasaude.org/),
da [Fundação Itaú para Educação e Cultura](https://fundacaoitau.org.br/),
pelo financiamento deste projeto. 

Agradecemos também à
[Secretaria Municipal da Saúde da Prefeitura da Cidade de São Paulo](https://www.prefeitura.sp.gov.br/cidade/secretarias/saude/)
pela parceria durante a execução do projeto. 
