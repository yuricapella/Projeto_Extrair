## Verificação e extração de arquivos

#### No arquivo

```
main.py
```

Resumo:

O código verifica os arquivos na pasta origin_folder (PDF, ZIP e XML), movendo-os para a pasta process_folder. Após a extração de arquivos ZIP, o código verifica se há arquivos PDF e XML. Se houver apenas um tipo (PDF ou XML), o arquivo não será processado. O código extrai os nomes reais dos arquivos, verifica se há duplicatas com base nos números sequenciais e renomeia os arquivos para os nomes reais antes de movê-los para a pasta destination_folder.

Utilizei o PyQt5 para criar uma interface gráfica com botões:

### Botão de iniciar
Pode ser clicado ou ativado por uma tecla configurada.

### Botão de configurações
Permite selecionar as pastas de entrada, processamento e saída, escolher a tecla para iniciar o processo, e salvar as configurações.

### Botão de logs
Exibe o início e o fim do monitoramento, as pastas selecionadas, os botões e arquivos processados. Inclui também um botão para limpar os logs. (A visualização do log foi aprimorada e alguns bugs foram corrigidos).

