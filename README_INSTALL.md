# Augmented SIM - Instruções

Seguem as instruções para a instalação deste programa a partir da versão
disponível no repositório.

#### Windows

1. Instale o interpretador [Python](https://www.python.org/downloads/windows/) na
versão 3.6 ou superior.
Se necessário, consulte a
[documentação](https://docs.python.org/pt-br/3/using/windows.html#the-full-installer).
Ao instalar, certifique-se de **deixar marcada** a
[opção *Add Python to PATH*](https://docs.python.org/pt-br/3/using/windows.html#installation-steps)
na parte inferior do instalador.

1. Faça
[download do conteúdo deste repositório](https://gitlab.com/projeto-fm-usp-mortalidade-sp/augmented-sim/-/archive/master/mortalidadesp-master.zip) e descompacte-o.

1. É possível instalar o programa ou executá-lo sem instalar:
  - Se preferir executar **da própria pasta**:
    - Clique duas vezes no script `PREPARAR` (arquivo `PREPARAR.py`).
      Este passo poderá
      levar alguns minutos, mas só será necessário
      executá-lo uma vez nesta versão do programa
      (para cada usuário de um computador).
    - Clique duas vezes no script `EXECUTAR` (arquivo `EXECUTAR`.py).
      O programa será aberto.
  - Caso queira **instalar**:
    - Clique duas vezes no script `INSTALAR` (arquivo `INSTALAR`.py).
      O programa será instalado.
    - Para executar o programa, use os atalhos no menu Iniciar ou na área
      de trabalho.

Uma interface de linha de comando estará disponível em `augmentedsim_gui`.


#### macOS e Linux


1. Instale o interpretador [Python](https://www.python.org/downloads/)
na versão 3.6 ou superior.
Se necessário, consulte a documentação para
[macOS](https://docs.python.org/pt-br/3/using/mac.html) ou
[Linux](https://docs.python.org/3/using/unix.html).
  - Após executar `python3 --version` em um terminal, caso a saída não contenha
  erros e mostre uma versão igual ou superior a 3.6, não é necessário instalar
  outra versão.
  - Diversas distribuições Linux já possuem
  uma versão recente do Python instalada automaticamente, dispensando
  este passo. Se necessário, instale o Python utilizando o gerenciador
  de pacotes de sua distribuição (`apt`, `apt-get`, `yum`, `dnf`, etc.).

1. Faça
  [download do conteúdo deste repositório](https://gitlab.com/projeto-fm-usp-mortalidade-sp/augmented-sim/-/archive/master/mortalidadesp-master.zip) e descompacte-o.
  <br/><small>Obs.:  No Safari, é possível que a extração ocorra automaticamente.</small>

1. Em um terminal, entre no diretório descompactado
   acima (usando o comando `cd`).

  - Se preferir executar **do próprio diretório**,
    sem instalar:<br>
    - Digite `python3 PREPARAR.py`
      e aperte Enter (isto instalará apenas as dependências).
      Este passo poderá
      levar alguns minutos, mas só será necessário
      executá-lo uma vez nesta versão do programa
      (para cada usuário de um computador).
    - Digite
      `python3 EXECUTAR.py` e aperte Enter para executar o programa
      com interface gráfica
      (ou `python3 ./augmented_sim/augmented_sim_gui.py`).
      Uma interface de linha de comando também estará
      disponível: `python3 ./augmented_sim/augmented_sim_cli.py`.

  - Caso queira **instalar**:<br>
    - Digite `python3 INSTALAR.py` e aperte Enter.
    - Para executar o programa com interface gráfica, utilize o atalho
      na área de trabalho e
      no menu Iniciar (ou equivalente), ou execute
      `augmentedsim_gui`. A interface de
      linha de comando estará disponível como `augmentedsim_cli`.
      - É possível que o diretório <code>\~/.local/bin</code> (Linux)
        ou
        <code>\~/Library/Python/<b>&lt;versão do Python aqui&gt;</b>/bin</code>
        (macOS) não esteja no `PATH`. Se necessário, inclua-o no PATH
        acrescentando uma linha ao final de algum arquivo que seja lido na
        inicialização do shell (geralmente `~/.bashrc` ou
        `~/.zshenv`). Observe os
        exemplos abaixo (note que há `:$PATH` **após** o diretório, para
        que os caminhos já existentes sejam mantidos):

        ```shell
        export PATH=~/Library/Python/3.9/bin:$PATH  # macOS
        export PATH=~/.local/bin:$PATH              # Linux
        ```
