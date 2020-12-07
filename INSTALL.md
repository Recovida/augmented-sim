# Augmented SIM - Instruções

## Utilizando a última versão lançada

[TO DO]

## Utilizando a versão mais recente do repositório (possivelmente instável)


#### Windows

1. Instale o interpretador [Python](https://www.python.org/downloads/windows/) na
versão 3.6 ou superior.
Se necessário, consulte a
[documentação](https://docs.python.org/pt-br/3/using/windows.html#the-full-installer).
Ao instalar, certifique-se de **deixar marcada** a
[opção *Add Python to PATH* ](https://docs.python.org/pt-br/3/using/windows.html#installation-steps)
na parte inferior do instalador.

1. Faça
[download do conteúdo deste repositório](https://gitlab.com/projeto-fm-usp-mortalidade-sp/augmented-sim/-/archive/master/mortalidadesp-master.zip) e descompacte-o.

1. Abra uma janela de um prompt de comando (CMD) ou Powershell dentro
da pasta descompactada. <small>Para fazer isso, abra a pasta no Windows,
mantenha pressionada a tecla Shift e clique com
o botão direito do mouse em um lugar vazio dentro da pasta. Escolha a opção
de abrir o prompt de comando ou o Powershell.</small><br>
Dentro da janela do prompt de comando ou Powershell:
  - Se preferir executar **do próprio diretório**,
      sem instalar:<br>
      ...
  - Caso queira **instalar**:<br>
      Digite `python setup.py install`
      e aperte Enter.
      O programa com interface gráfica poderá então ser executado chamando
      `augmentedsim_gui`, e a interface de
      linha de comando pode ser utilizada executando `augmentedsim_cli`.


#### macOS


1. Instale o interpretador [Python](https://www.python.org/downloads/mac-osx/)
na versão 3.6 ou superior.
Se necessário, consulte a
[documentação](https://docs.python.org/pt-br/3/using/mac.html).

1. Faça
[download do conteúdo deste repositório](https://gitlab.com/projeto-fm-usp-mortalidade-sp/augmented-sim/-/archive/master/mortalidadesp-master.zip) e descompacte-o.

[,,,]


#### Linux

1. Instale o interpretador [Python](https://www.python.org/downloads/)
na versão 3.6 ou superior, preferencialmente utilizando o gerenciador
de pacotes de sua distribuição (`apt`, `apt-get`, `yum`, `dnf`, etc.).
Diversas distribuições Linux já possuem
uma versão recente do Python instalada automaticamente, dispensando este passo.
Após executar `python3 --version` em um terminal, caso a saída não contenha
erros e mostre uma versão igual ou superior a 3.6, não é necessário instalar
outra versão.

1. Faça
[download do conteúdo deste repositório](https://gitlab.com/projeto-fm-usp-mortalidade-sp/augmented-sim/-/archive/master/mortalidadesp-master.zip) e descompacte-o.

1. Abra uma janela de um terminal dentro do diretório descompactado.

  - Se preferir executar **do próprio diretório**,
    sem instalar:<br>
    Digite `python3 pip install -r requirements.txt`
    e aperte Enter (isto instalará apenas as dependências).
    O programa com interface gráfica poderá então ser executado chamando
    `./src/augmented_sim/augmented_sim_gui.py`, e a interface de
    linha de comando estará
    disponível em `./src/augmented_sim/augmented.py`, ambos a partir
    deste diretório.

  - Caso queira **instalar**:<br>
    Digite `python3 setup.py install --user`
    e aperte Enter (se desejar que a instalação seja feita para todos os
    usuários, remova `--user` do comando anterior e execute-o como *root*).
    O programa com interface gráfica poderá então ser executado chamando
    `augmentedsim_gui`, e a interface de
    linha de comando pode ser utilizada executando `augmentedsim_cli`.
