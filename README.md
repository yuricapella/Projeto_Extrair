## Verificação e extração de arquivos

#### No arquivo

```
main.py
```
Roda apenas o processamento dos arquivos.

resumo: 

Faz a verificação dos arquivos na pasta, se possuem o mesmo nome, pega o nome do zip e coloca no xml e após isso envia para a pasta de saída, na pasta de saída verifica se há arquivos com o mesmo nome, se houver, adiciona um contador.

#### Já no arquivo
```
main_com_app.py
```
Utilizei o PyQt5 e criei uma interface gráfica com botões onde inicia a verificação dos arquivos na pasta de entrada (Onde será colocado o arquivo pdf e zip) e assim que houver os dois arquivos com o mesmo nome, rodará o script de processamento dos arquivos.

### Botão de iniciar
Pode ser clicado ou apertando a tecla f6.

### Botão de configurações
Possui dois botões para selecionar as pastas de entrada e saída

### Botão de logs
Mostra o inicio e o fim do monitoramento, as pastas selecionadas e os arquivos que serão processados.

