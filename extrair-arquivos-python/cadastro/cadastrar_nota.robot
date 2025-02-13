*** Settings ***
Library    SeleniumLibrary
Library    OperatingSystem
Library    JSONLibrary
Library    Collections
Variables    ${CURDIR}${/}variaveis_sp.py

*** Keywords ***
Show Screenshot
    Run Keyword And Ignore Error    Capture Page Screenshot    ${SCREENSHOT_NAME}
    Run Keyword And Ignore Error    Remove File    ${SCREENSHOT_NAME}

Cadastrar CPF
    [Arguments]    ${CPF}
    Input Text      xpath=//input[@id='cnpj' and contains(@class, 'bling-item-form')]    ${CPF}
    Show Screenshot

Cadastrar CNPJ
    [Arguments]    ${CNPJ}      ${INSCRICAO_ESTADUAL}
    Click Element    xpath=//select[@id='tipo']
    Show Screenshot
    Press Keys       xpath=//select[@id='tipo']     UP
    Show Screenshot
    Press Keys       xpath=//select[@id='tipo']     ENTER
    Input Text      xpath=//input[@id='cnpj' and contains(@class, 'bling-item-form')]    ${CNPJ}
    Show Screenshot
    Run Keyword If    '${INSCRICAO_ESTADUAL}' != '' and '${INSCRICAO_ESTADUAL}' != 'None'
    ...    Input Text    xpath=//input[@id='ie' and contains(@class, 'bling-item-form')]    ${INSCRICAO_ESTADUAL}

Fazer Login
    [Arguments]    ${USERNAME}      ${PASSWORD}
    Wait Until Element Is Visible   id=username   timeout=10s
    Input Text      id=username    ${USERNAME}
    Show Screenshot
    Input Text      xpath=//input[@type='password']    ${PASSWORD}
    Show Screenshot
    Click Button    xpath=//button[@type='submit']

Novo Cadastro
    Wait Until Element Is Visible   id=btn-incluir    timeout=10s
    Show Screenshot
    Click Button    id=btn-incluir
    Show Screenshot

Inserir Novo Cliente
    Wait Until Element Is Visible   xpath=//a[@title='Adicionar novo']   timeout=10s
    Show Screenshot

Nome Cliente
    [Arguments]    ${NOME}
    Wait Until Element Is Visible   id=nome   timeout=10s
    Show Screenshot
    Input Text      id=nome    ${NOME}
    Show Screenshot

Cadastrar CPF_CNPJ
    [Arguments]       ${CPF_CNPJ}        ${INSCRICAO_ESTADUAL}
    ${CPF_LENGHT}=    Get Length                    ${CPF_CNPJ}
    Run Keyword If    ${CPF_LENGHT} == 11     Cadastrar CPF       ${CPF_CNPJ}
    ...    ELSE       Cadastrar CNPJ            ${CPF_CNPJ}        ${INSCRICAO_ESTADUAL}

    Run Keyword If    '${INSCRICAO_ESTADUAL}' == 'ISENTO' or '${INSCRICAO_ESTADUAL}' == '' or '${INSCRICAO_ESTADUAL}' == 'None'
    ...    Select From List By Value    xpath=//select[@id='indIEDest']    9

Endereco cliente
    [Arguments]    ${CEP}  ${SIGLA_ESTADO}   ${CIDADE}    ${BAIRRO}    ${RUA}    ${NUMERO}

    #CEP
    Input Text      xpath=//input[@id='cep' and contains(@class, 'bling-item-form')]    ${CEP}
    Show Screenshot

    #UF
    Select From List By Value    xpath=//select[@id='uf' and contains(@class, 'InputDropdown-select')]    ${SIGLA_ESTADO}
    Show Screenshot

    #CIDADE
    Input Text    xpath=//input[@id='cidade']    ${CIDADE}
    Sleep    3s
    Press Keys    None    DOWN
    Press Keys    None    ENTER
    Show Screenshot

    #BAIRRO
    Input Text    xpath=//input[@id='bairro' and contains(@class, 'bling-item-form')]    ${BAIRRO}
 
    #RUA
    Input Text      xpath=//input[@id='endereco' and contains(@class, 'bling-item-form')]    ${RUA}

    #NUMERO DA CASA
    Input Text      xpath=//input[@id='enderecoNro' and contains(@class, 'bling-item-form')]    ${NUMERO}


Salvar dados Cliente
    [Arguments]    ${CPF_CNPJ}
    Click Button    id=salvar-contato-rapido
    ${sumiu}=    Run Keyword And Return Status    Wait Until Element Is Not Visible    id=salvar-contato-rapido    timeout=3s
    IF    not ${sumiu}
        Click Button    xpath=//button[@type='button' and contains(@class, 'ui-button ui-corner-all ui-widget ui-button-icon-only ui-dialog-titlebar-close')]
        Wait Until Element Is Visible    xpath=//input[@id='contato' and contains(@class, 'input_text ui-autocomplete-input tipsyOff')]    timeout=3s
        Input Text    xpath=//input[@id='contato' and contains(@class, 'input_text ui-autocomplete-input tipsyOff')]    ${CPF_CNPJ}
        Press Keys    xpath=//input[@id='contato' and contains(@class, 'input_text ui-autocomplete-input tipsyOff')]    DOWN
        Press Keys    xpath=//input[@id='contato' and contains(@class, 'input_text ui-autocomplete-input tipsyOff')]    ENTER
    END

Novo Cliente
    [Arguments]    ${NOME}      ${CPF_CNPJ}      ${INSCRICAO_ESTADUAL}     ${CEP}      ${SIGLA_ESTADO}   ${CIDADE}     ${BAIRRO}       ${RUA}        ${NUMERO}
    Inserir Novo Cliente
    Click Element    xpath=//a[@title='Adicionar novo']
    Nome Cliente    ${NOME}
    Cadastrar CPF_CNPJ    ${CPF_CNPJ}       ${INSCRICAO_ESTADUAL}
    Endereco cliente     ${CEP}      ${SIGLA_ESTADO}     ${CIDADE}    ${BAIRRO}    ${RUA}    ${NUMERO}
    Salvar dados Cliente      ${CPF_CNPJ}   
    Run Keyword And Ignore Error    Wait Until Element Is Visible    xpath=//div[contains(@class, 'toast-message')]    timeout=3s
    Run Keyword And Ignore Error    Click Element    xpath=//div[contains(@class, 'toast-message')]
    
Novo Produto
    [Arguments]    ${PRODUTO}      ${UN}     ${QUANTIDADE}      ${VALOR}       ${NCM}
    Wait Until Element Is Visible   id=produto   timeout=10s
    Wait Until Element Is Enabled   id=produto   timeout=10s
    Show Screenshot
    Input Text       id=produto    ${PRODUTO}
    Show Screenshot
    Press Keys    id=un    ${UN}
    Show Screenshot
    Press Keys       id=quantidade         ${QUANTIDADE}
    Show Screenshot
    Execute JavaScript    document.getElementById('precounitario').value = "${VALOR}";
    Show Screenshot
    Input Text       id=cf    ${NCM}
    Show Screenshot
    Click Element    xpath=//a[@id='aNovaLinhaItem' and contains(@class, 'link-action plus-sign has-shortcut')]
    Show Screenshot

Salvar nota
    Wait Until Element Is Visible      xpath=//button[@id='botaoSalvar' and contains(@class, 'call-to-action')]   timeout=10s
    Click Element    xpath=//button[@id='botaoSalvar' and contains(@class, 'call-to-action')]
    #Click Element    xpath=//button[@id='botaoCancelar' and contains(@value, 'Cancelar')]
    Show Screenshot

*** Variables ***
${CHROME_DRIVER_PATH}    C:\chromedriver-win64\chromedriver.exe
${URL}                   https://www.bling.com.br/notas.fiscais.php#list
${SCREENSHOT_NAME}       ${CURDIR}${/}..${/}screenshot.png

*** Test Cases ***
Cadastro Bling
    ${chrome_options} =     Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
    Create WebDriver    Chrome    options=${chrome_options}

    Go To       ${URL}
    Maximize Browser Window

    Fazer Login       ${USERNAME}      ${PASSWORD}

    FOR    ${i}    IN RANGE    ${CADASTROS_NUMBER}
        ${cadastro_key} =    Set Variable    Cadastro_${i + 1}
        ${cadastro} =    Get From Dictionary    ${dicionario_cadastros}    ${cadastro_key}
        Novo Cadastro
        Novo Cliente    ${cadastro['nome']}      ${cadastro['cpf_cnpj']}      ${cadastro['inscricao_estadual']}     ${cadastro['cep']}      ${cadastro['uf']}     ${cadastro['cidade']}      ${cadastro['bairro']}      ${cadastro['rua']}      ${cadastro['numero']}
        Novo Produto    ${cadastro['produto']}      ${cadastro['un']}     ${cadastro['quantidade']}      ${cadastro['valor']}       ${cadastro['ncm']}
        Salvar nota
    END