# Verificação e Extração de Arquivos

## Descrição

O código verifica e processa arquivos nas seguintes pastas:

- **origin_folder:** Pasta de origem onde os arquivos PDF, ZIP e XML são inicialmente colocados.
- **process_folder:** Pasta onde os arquivos são movidos para processamento.
- **destination_folder:** Pasta de destino onde os arquivos renomeados e processados são movidos.

Após a extração de arquivos ZIP, o código verifica se há arquivos PDF e XML correspondentes. Arquivos sem um par correspondente (PDF ou XML) não serão processados. O código também extrai os nomes reais dos arquivos e verifica duplicatas com base em números sequenciais antes de renomear e mover os arquivos para a pasta de destino.

## Interface Gráfica

Utiliza PyQt5 para criar uma interface gráfica com os seguintes botões:

### Botão de Iniciar
- **Descrição:** Inicia o processo de monitoramento e processamento de arquivos.
- **Método de Ativação:** Pode ser clicado ou ativado por uma tecla configurada.

### Botão de Configurações
- **Descrição:** Permite configurar as pastas de entrada, processamento e saída, escolher a tecla para iniciar o processo e salvar as configurações.

### Botão de Logs
- **Descrição:** Exibe o início e o fim do monitoramento, as pastas selecionadas e os arquivos processados.
- **Recursos Adicionais:** Inclui um botão para limpar os logs e a tecla fixa "F8" para abrir e fechar a janela.

## Versão Atual: 2.1.0

### Principais Mudanças Recentes

- **Visualização de PDF de Imagem:** Suporte para conversão e extração de texto de PDFs com imagens usando `pdf2image` e `pytesseract`.
- **Renomeação de Arquivo Específico:** Arquivos com nomes específicos são processados e movidos com nomes adequados para a pasta de destino.
- **Função de Atalho para Logs:** Adicionada a função de atalho "F8" para exibir e fechar a janela de logs.
- **Ajuste de Threading:** Remoção de `self.lock` para melhorar o desempenho.
- **Correção de Bugs:**
  - **Problema de Inicialização com Arquivos Existentes:** Corrigido o travamento ao iniciar com arquivos já presentes.

## Documentação e Comentários

A documentação foi atualizada para refletir as novas funcionalidades e melhorias implementadas na versão 2.1.0.

Para detalhes completos sobre todas as alterações, consulte as notas de lançamento na seção de releases.
