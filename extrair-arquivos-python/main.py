import os
import zipfile
import shutil

origin_folder = "C:\\Users\\yuri_\\Downloads\\arquivosbaixados\\"
destination_folder = "C:\\Users\\yuri_\\Downloads\\arquivosmovidos\\"


if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

if not os.path.exists(origin_folder):
    os.makedirs(origin_folder)

def processar_arquivos():
    
    for arquivo in os.listdir(origin_folder):
        file_name, ext = os.path.splitext(arquivo)

        if ext == ".zip" and os.path.exists(f'{origin_folder}{file_name}.pdf'):
            arquivo_zip = zipfile.ZipFile(os.path.join(origin_folder, arquivo))
            arquivo_zip.extractall(origin_folder)
            um_nome = arquivo_zip.namelist()
            um_nome = um_nome[0]
            arquivo_zip.close()
            os.remove(os.path.join(origin_folder, arquivo))

            file_count = checkIsUnique(file_name)

            if file_count > 0:
                file_count += 1
                enviar_xml(um_nome , f'{nome_arquivo}-{file_count}')
                enviar_pdf(file_name, f'{file_name}-{file_count}')
            else: 
                enviar_xml(um_nome, file_name)
                enviar_pdf(file_name)
        elif(ext in "zip"):
            print("Nao achou o zip e pdf")

def checkIsUnique(file_name):
    sameItemCount = 0
    global nome_arquivo
    for nome_arquivo in os.listdir(destination_folder):
        if(file_name in nome_arquivo and 'xml' in nome_arquivo):
            sameItemCount += 1
            nome_arquivo = file_name
            print(nome_arquivo)

    return sameItemCount

def enviar_xml(um_nome, file_name):
    if os.path.exists(f'{origin_folder}{um_nome}'):
        shutil.move(f'{origin_folder}{um_nome}', f'{destination_folder}{file_name}.xml')
        print("moveu o xml")
    else:
        print("Nao achou o XML")

def enviar_pdf(um_nome, file_name = None):
    if os.path.exists(f'{origin_folder}{um_nome}.pdf'):       

        if(file_name):
            shutil.move(f'{origin_folder}{um_nome}.pdf', f'{destination_folder}{file_name}.pdf')
        else: 
            shutil.move(f'{origin_folder}{um_nome}.pdf', f'{destination_folder}{um_nome}.pdf')

        print("moveu o pdf")
    else:
        print("Nao achou o PDF")
        
        
    
processar_arquivos()

