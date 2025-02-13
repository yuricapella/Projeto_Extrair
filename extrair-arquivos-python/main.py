import sys
import time
import os
import zipfile
import shutil
import json
import re
import subprocess
import threading
from unidecode import unidecode
from queue import Queue

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QWidget,QDialog, 
                            QLineEdit, QFileDialog, QTextEdit, QComboBox, QMessageBox)

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint, QObject, QTimer
from pynput import keyboard

from lxml import etree
import pdfplumber
from pdf2image import convert_from_path
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

                           
class MeuHandler(FileSystemEventHandler):
    def __init__(self, origin_folder, destination_folder, process_folder, logger, log_dialog):
        super().__init__()
        self.origin_folder = origin_folder
        self.destination_folder = destination_folder
        self.process_folder = process_folder
        self.logger = logger
        self.log_dialog = log_dialog
    
    def extract_text_with_ocr(self,file_path):
        text = ''
        
        try:
            # Converte cada página do PDF em uma imagem
            images = convert_from_path(file_path)
            for i, image in enumerate(images):
                # Aplicar OCR para cada página convertida em imagem
                page_text = pytesseract.image_to_string(image)
                #print(f"Texto extraído da página {i + 1}:\n{page_text}")
                text += page_text + '\n'
            
            if not text.strip():
                text = "Erro"
        except Exception as e:
            print(f"Erro ao processar o PDF com OCR: {e}")
            text = "Erro"

        return text
       
    def extract_text_from_pdf(self, file_path):
        self.logger.log_message("-----------------------------------")
        self.logger.log_message("Iniciando a extração do nome do PDF")
        text = ''
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted_text = page.extract_text()
                    if extracted_text:
                        text += extracted_text
            if not text: 
                text = "Erro"
        except PermissionError as e:
            self.logger.log_message(f"Erro de permissão ao abrir o PDF {file_path}: {e}")
            text = "Erro"
        except Exception as e:
            self.logger.log_message(f"Erro ao extrair texto do PDF {file_path}: {e}")
            text = "Erro"
        return text

    def extract_name_from_text(self, text):
        if text == "Erro":
            return "Erro"

        # Primeiro padrão
        match = re.search(r'Nome / Razão Social CNPJ/CPF Data emissão\s*Inscrição Estadual\s*(.*?)(?:\s*\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\s*\d{3}\.\d{3}\.\d{3}-\d{2})', text, re.DOTALL)
        
        # Se houver uma correspondência, extrai o nome
        if match:
            extracted_text = match.group(1).strip()
            normalized_name = self.normalize_name(extracted_text)
            #self.logger.log_message(f"Nome extraído do PDF: {normalized_name}")
            return normalized_name
        
        # Segundo padrão
        match = re.search(r'Nome / Razão Social CNPJ/CPF Inscrição Estadual Data emissão\s*(.*?)(?:\s*\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\s*\d{3}\.\d{3}\.\d{3}-\d{2})', text, re.DOTALL)
        
        if match:
            extracted_text = match.group(1).strip()
            normalized_name = self.normalize_name(extracted_text)
            #self.logger.log_message(f"Nome extraído do PDF: {normalized_name}")
            return normalized_name
        
        match = re.search(r'N°\s*(\d+)\s*Série', text)
        
        if match:
            nf_number = match.group(1).strip()
            self.logger.log_message(f"Carta sendo movida")
            return nf_number
            
            
        self.logger.log_message("Nenhuma correspondência encontrada.")
        return "Erro"
        
    def normalize_name(self, name):
        # Remove acentuação
        name = unidecode(name)
        
        name = re.sub(r'\.', ' ', name)
        
        name = re.sub(r'[^A-Za-z0-9\s&]', '', name)
        
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name

    def extract_name_from_xml(self, file_path):
        self.logger.log_message("-----------------------------------")
        self.logger.log_message("Iniciando a extração do nome do XML")
        try:
            tree = etree.parse(file_path)
            root = tree.getroot()
            namespaces = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
            dest_elements = root.findall('.//nfe:dest', namespaces)
            
            for dest in dest_elements:
                xNome_element = dest.find('nfe:xNome', namespaces)
                if xNome_element is not None and xNome_element.text:
                    text_xml = xNome_element.text.strip()
                    normalized_name = self.normalize_name(text_xml)
                    #self.logger.log_message(f"Nome extraído do XML: {normalized_name}")
                    return normalized_name
            
            self.logger.log_message(f"Nenhum nome encontrado no XML {file_path}")
            return "Erro"
        
        except etree.XMLSyntaxError as e:
            self.logger.log_message(f"Erro de sintaxe XML no arquivo {file_path}: {e}")
            return "Erro"
        except Exception as e:
            self.logger.log_message(f"Erro ao processar o XML {file_path}: {e}")
            return "Erro"
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_name, ext = os.path.splitext(event.src_path)
        if ext.lower() in ['.pdf', '.zip', '.xml']:
            time.sleep(2)
            pdf_file = os.path.join(self.origin_folder, f"{file_name}.pdf")
            zip_file = os.path.join(self.origin_folder, f"{file_name}.zip")
            xml_file = os.path.join(self.origin_folder, f"{file_name}.xml")
            
            if os.path.exists(pdf_file) or os.path.exists(zip_file) or os.path.exists(xml_file):
                self.processar_arquivos()
                self.logger.log_message("-----------------------------------")

    def extrair_arquivos_zip(self):
        arquivos_zip = [f for f in os.listdir(self.process_folder) if f.endswith('.zip')]
        for arquivo in arquivos_zip:
            zip_path = os.path.join(self.process_folder, arquivo)
            if os.path.exists(zip_path):
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_file:
                        self.logger.log_message(f"Extraindo o arquivo ZIP")
                        zip_file.extractall(self.process_folder)
                    os.remove(zip_path)
                    self.logger.log_message(f"Arquivo ZIP removido com sucesso.")
                except zipfile.BadZipFile:
                    self.logger.log_message(f"Erro ao extrair o arquivo ZIP {arquivo}: arquivo corrompido.")
                except OSError as e:
                    self.logger.log_message(f"Erro ao remover o arquivo ZIP {arquivo}: {e}")
                except Exception as e:
                    self.logger.log_message(f"Erro inesperado ao processar o arquivo ZIP {arquivo}: {e}")
            else:
                self.logger.log_message(f"O arquivo ZIP {arquivo} já foi removido.")

    def processar_arquivos_extraidos(self):
        arquivos_processados = False
        tentativas_maximas = 1  # Número máximo de tentativas para processar arquivos
        tentativas = 0
        arquivos_removidos = []

        while tentativas < tentativas_maximas:
            arquivos_xml = [f for f in os.listdir(self.process_folder) if f.endswith('.xml')]
            arquivos_pdf = [f for f in os.listdir(self.process_folder) if f.endswith('.pdf')]

            xml_por_nome = {}
            pdf_por_nome = {}
            
            pares_encontrados = False
            
            if arquivos_xml and arquivos_pdf:
                for xml_file in arquivos_xml:
                    xml_path = os.path.join(self.process_folder, xml_file)
                    if os.path.exists(xml_path):
                        nome_xml = self.extract_name_from_xml(xml_path)
                        chave = xml_file.split('-nfe.xml')[0]  # Ajusta para chave base
                        xml_por_nome[chave] = (xml_path, nome_xml)
                        if nome_xml != "Erro":
                            self.logger.log_message(f"XML coletado: {xml_file}\n nome extraído: {nome_xml}")
                            self.logger.log_message("-----------------------------------")
                        else:
                            self.logger.log_message(f"XML corrompido ou fora do padrão: {xml_file}")
                            self.logger.log_message("-----------------------------------")

                for pdf_file in arquivos_pdf:
                    pdf_path = os.path.join(self.process_folder, pdf_file)
                    if os.path.exists(pdf_path):
                        conteudo_pdf = self.extract_text_from_pdf(pdf_path)
                        nome_pdf = self.extract_name_from_text(conteudo_pdf)
                        chave = pdf_file.replace('.pdf', '')  # Ajusta para chave base
                        pdf_por_nome[chave] = (pdf_path, nome_pdf)
                        if nome_pdf != "Erro":
                            self.logger.log_message(f"PDF coletado: {pdf_file}\n nome extraído: {nome_pdf}")
                            self.logger.log_message("-----------------------------------")
                        else:
                            self.logger.log_message(f"PDF corrompido ou fora do padrão: {pdf_file}")
                            self.logger.log_message("-----------------------------------")
                    else:
                        self.logger.log_message(f"Caminho do PDF não encontrado: {pdf_path}")

                # Processa e renomeia arquivos
                for chave in xml_por_nome.keys():
                    if chave in pdf_por_nome:
                        xml_path, nome_xml = xml_por_nome[chave]
                        pdf_path, nome_pdf = pdf_por_nome[chave]

                        if nome_xml != "Erro" and nome_pdf != "Erro":
                            # Verifica a unicidade e ajusta o nome se necessário
                            self.logger.log_message("-----------------------------------")
                            self.logger.log_message(f"Renomeando e movendo arquivos")

                            count_xml = self.checkIsUnique(nome_xml, '.xml')
                            count_pdf = self.checkIsUnique(nome_pdf, '.pdf')

                            novo_nome_xml = f"{nome_xml}-{count_xml + 1}.xml" if count_xml > 0 else f"{nome_xml}.xml"
                            novo_nome_pdf = f"{nome_pdf}-{count_pdf + 1}.pdf" if count_pdf > 0 else f"{nome_pdf}.pdf"

                            novo_caminho_xml = os.path.join(self.destination_folder, novo_nome_xml)
                            novo_caminho_pdf = os.path.join(self.destination_folder, novo_nome_pdf)

                            try:
                                # Aqui movemos os arquivos usando o primeiro elemento da tupla, que é o caminho do arquivo
                                shutil.move(xml_path, novo_caminho_xml)
                                shutil.move(pdf_path, novo_caminho_pdf)
                                self.logger.log_message(f"XML movido para pasta de destino: {novo_nome_xml}")
                                self.logger.log_message(f"PDF movido para pasta de destino: {novo_nome_pdf}")
                                self.logger.log_message("-----------------------------------")
                                pares_encontrados = True
                            except Exception as e:
                                self.logger.log_message(f"Erro ao mover arquivos: {e}")
                            
                        else:
                            # Remover arquivos corrompidos em pares
                            if nome_xml == "Erro":
                                if os.path.exists(xml_path):
                                    os.remove(xml_path)
                                # Remove o PDF correspondente se o XML estiver corrompido
                                if chave in pdf_por_nome:
                                    pdf_path, _ = pdf_por_nome[chave]
                                    if os.path.exists(pdf_path):
                                        os.remove(pdf_path)
                                        arquivos_removidos.append(nome_pdf)

                            if nome_pdf == "Erro":
                                if os.path.exists(pdf_path):
                                    os.remove(pdf_path)
                                # Remove o XML correspondente se o PDF estiver corrompido
                                if chave in xml_por_nome:
                                    xml_path, _ = xml_por_nome[chave]
                                    if os.path.exists(xml_path):
                                        os.remove(xml_path)
                                        arquivos_removidos.append(nome_xml)
                else:
                    self.logger.log_message("Nenhum par de arquivos XML e PDF encontrado.")

            time.sleep(1)
            
            if pares_encontrados:
                self.logger.log_message("Arquivos processados com sucesso.")
                arquivos_processados = True
                break
            else:
                self.logger.log_message("Nenhum par processado")
                
            tentativas += 1

        if arquivos_removidos:
            self.logger.log_message(f"Arquivos removidos: {arquivos_removidos}")

        return arquivos_processados

    def mover_arquivos_para_process(self):
        for arquivo in os.listdir(self.origin_folder):
            nome_arquivo, extensao = os.path.splitext(arquivo)
            origin_path = os.path.join(self.origin_folder, arquivo)
            process_path = os.path.join(self.process_folder, arquivo)
            destino_path = os.path.join(self.destination_folder, arquivo)

            if not os.path.exists(origin_path):
                self.logger.log_message(f"Arquivo não encontrado: {origin_path}")
                continue

            if extensao in (".xml", ".zip", ".pdf") and "file" not in nome_arquivo.lower():
                if any(term in nome_arquivo.lower() for term in [
                    "carta de correcao", "carta de correção", "c", "carta", "bling - cartas de correção"]):
                    try:
                        conteudo_pdf = self.extract_text_with_ocr(origin_path)
                        nome_pdf = self.extract_name_from_text(conteudo_pdf)
                        arquivo = f"Carta de correção - {nome_pdf}{extensao}"
                        destino_path = os.path.join(self.destination_folder, arquivo)

                        if not os.path.exists(destino_path):
                            shutil.move(origin_path, destino_path)
                            self.logger.log_message(f"Arquivo movido para pasta de destino: {arquivo}")
                        else:
                            self.logger.log_message(f"Arquivo já existe no destino: {arquivo}")
                    except Exception as e:
                        self.logger.log_message(f"Erro ao processar arquivo: {arquivo}, {e}")
                else:
                    try:
                        if not os.path.exists(process_path):
                            shutil.move(origin_path, process_path)
                            self.logger.log_message(f"Arquivo movido para pasta process: {arquivo}")
                        else:
                            self.logger.log_message(f"Arquivo já existe na pasta process: {arquivo}")
                    except Exception as e:
                        self.logger.log_message(f"Erro ao mover arquivo para pasta process: {arquivo}, {e}")

    def checkIsUnique(self, file_name, file_type):
        sameItemCount = 0
        for nome_arquivo in os.listdir(self.destination_folder):
            if nome_arquivo.startswith(file_name) and nome_arquivo.endswith(file_type):
                sameItemCount += 1
        return sameItemCount
       
    def processar_arquivos(self):
        fila_arquivos = Queue()
        for arquivo in os.listdir(self.origin_folder):
            fila_arquivos.put(arquivo)

        while not fila_arquivos.empty():
            arquivo = fila_arquivos.get()
            
            arquivos_na_origem = os.listdir(self.origin_folder)
            arquivos = [f for f in arquivos_na_origem]
            if arquivos:
                self.mover_arquivos_para_process()
            
            arquivos_na_process = os.listdir(self.process_folder)
            
            arquivos_zip = [f for f in arquivos_na_process if f.endswith('.zip')]
            if arquivos_zip:
                self.extrair_arquivos_zip()
            
            arquivos_pdf_xml = [f for f in arquivos_na_process if f.endswith('.pdf') or f.endswith('.xml')]
            if arquivos_pdf_xml:
                self.processar_arquivos_extraidos()
            
            time.sleep(1)

class KeyListener(QThread):
    keyPressed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    key_map = {
        keyboard.Key.f1: "F1",
        keyboard.Key.f2: "F2",
        keyboard.Key.f3: "F3",
        keyboard.Key.f4: "F4",
        keyboard.Key.f5: "F5",
        keyboard.Key.f6: "F6",
        keyboard.Key.f7: "F7",
        keyboard.Key.f8: "F8",
        keyboard.Key.f9: "F9",
        keyboard.Key.f10: "F10",
        keyboard.Key.f11: "F11",
        keyboard.Key.f12: "F12",
        keyboard.Key.esc: "Esc",
        keyboard.Key.enter: "Enter",
        keyboard.Key.space: "Space",
        keyboard.Key.shift: "Shift",
        keyboard.Key.ctrl: "Ctrl",
        keyboard.Key.alt: "Alt",
        keyboard.Key.tab: "Tab",
        keyboard.Key.backspace: "Backspace",
        keyboard.Key.delete: "Delete",
        keyboard.Key.up: "Up",
        keyboard.Key.down: "Down",
        keyboard.Key.left: "Left",
        keyboard.Key.right: "Right",
        keyboard.Key.home: "Home",
        keyboard.Key.end: "End",
        keyboard.Key.page_up: "PageUp",
        keyboard.Key.page_down: "PageDown",
    }
    
    def run(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    def on_press(self, key):
        try:
            if key in self.key_map:
                print(f"Tecla pressionada: {self.key_map[key]}")  # Verifica a tecla pressionada
                self.keyPressed.emit(self.key_map[key])
        except AttributeError:
            pass
    
class MainWindow(QMainWindow):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MainWindow, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        super().__init__()

        self.config_dialog = ConfigDialog()
        self.config_dialog.config_saved.connect(self.carregar_configuracoes_MainWindow)
        
        # Start logs
        self.log_dialog = LogDialog()
        self.logger = Logger(self.log_dialog)
        
        
        self.logger.log_message("Aplicação iniciada")
        
        self.observer = None
        self.monitorando = False
        self.origin_folder = None
        self.destination_folder = None
        self.process_folder = None
        self.inicialization_key = None

        #Abrir janela
        self.initialize_ui()
        # Carregar configurações antes de usar
        self.carregar_configuracoes_MainWindow()
        
    def initialize_ui(self):
        main_layout = QVBoxLayout()
        sub_layout = QHBoxLayout()
        
        self.setWindowTitle("Extração app")

        #Botões
        self.iniciar_button = QPushButton("Iniciar")
        self.config_button = QPushButton("Configurações")
        self.logs_button = QPushButton("Logs")
        self.cadastrar_nota_button = QPushButton("Cadastrar Nota")
        
        #Widgets
        main_layout.addWidget(self.iniciar_button)
        sub_layout.addWidget(self.config_button)
        sub_layout.addWidget(self.logs_button)
        main_layout.addWidget(self.cadastrar_nota_button)
        main_layout.addLayout(sub_layout)
        
        #Eventos
        self.iniciar_button.clicked.connect(self.iniciar_button_function)
        self.config_button.clicked.connect(self.config_button_function)
        self.logs_button.clicked.connect(self.logs_button_function)
        self.cadastrar_nota_button.clicked.connect(self.abrir_cadastrar_nota)
        
        # Principal
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.resize(250, 100)

        # Iniciar key listener thread
        self.key_listener = KeyListener()
        self.key_listener.keyPressed.connect(self.saved_key)
        self.key_listener.start()
        
        self.initialized = True
        
    def fechar_todas_as_janelas(self):
        print("Fechando todas as janelas...")
        fechadas = set()

        # Fechar todas as janelas de diálogo
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QDialog) and widget != self:
                if widget not in fechadas:
                    print(f"Fechando {widget.windowTitle()}.")
                    widget.close()
                    fechadas.add(widget)  # Adiciona à lista de janelas fechadas
    
    
    def closeEvent(self, event):
        self.fechar_todas_as_janelas()
        event.accept()

        
    def iniciar_button_function(self):
        if self.monitorando:
            self.parar_monitoramento()
            self.monitorando = False
            self.iniciar_button.setText("Iniciar")

            if hasattr(self, 'processing_thread') and self.processing_thread.is_alive():
                self.processing_thread.join()
            self.logger.log_message("Monitoramento parado.")
            self.logger.log_message("-----------------------------------")
        else:
            try:
                self.start_monitoring()
                self.monitorando = True
                self.iniciar_button.setText("Parar")
                self.logger.log_message("Monitoramento iniciado.")
                self.logger.log_message("-----------------------------------")
                
                if not hasattr(self, 'processing_thread') or not self.processing_thread.is_alive():
                    self.processing_thread = threading.Thread(target=self.meu_handler.processar_arquivos)
                    self.processing_thread.start()
            except Exception as e:
                self.logger.log_message(f"Erro ao iniciar monitoramento: {e}")
    
    def config_button_function(self):
            if hasattr(self, 'config_dialog_instance') and self.config_dialog_instance.isVisible():
                self.config_dialog_instance.raise_()
                self.config_dialog_instance.activateWindow()
                return

            self.config_dialog_instance = ConfigDialog()
            self.config_dialog_instance.config_saved.connect(self.carregar_configuracoes_MainWindow)
            
            def verificar_e_parar_monitoramento():
                if self.iniciar_button.text() == "Parar":
                    self.config_dialog_instance.salvar_button.clicked.connect(self.iniciar_button_function)

            verificar_e_parar_monitoramento()
            self.config_dialog_instance.carregar_configuracoes_ConfigDialog()  # Carregar configurações antes de usar
            
            # Mostrar o diálogo de configurações sem bloquear outras janelas
            self.config_dialog_instance.show()
            
            # Adiciona a lógica de carregamento de configurações após mostrar a janela
            if self.config_dialog_instance.isVisible():
                origin_folder = self.config_dialog_instance.get_origin_folder()
                destination_folder = self.config_dialog_instance.get_destination_folder()
                process_folder = self.config_dialog_instance.get_process_folder()
                inicialization_key = self.config_dialog_instance.inicialization_key

                if origin_folder and destination_folder and process_folder and inicialization_key:
                    self.origin_folder = origin_folder
                    self.destination_folder = destination_folder
                    self.process_folder = process_folder
                    self.inicialization_key = inicialization_key
                else:
                    self.logger.log_message("Pasta de origem ou destino não selecionada.")
                    
    def logs_button_function(self):
        if self.log_dialog is not None and self.log_dialog.isVisible():
            print("LogDialog já visível.")
            self.log_dialog.raise_()
            self.log_dialog.activateWindow()
        else:
            if self.log_dialog is None:
                self.log_dialog = LogDialog()
                self.logger = Logger(self.log_dialog)  # Certifique-se de que a instância de logger use essa janela
            self.log_dialog.setWindowFlags(self.log_dialog.windowFlags() | Qt.WindowStaysOnTopHint | Qt.WindowMinimizeButtonHint)
            self.log_dialog.show()
    
    def abrir_cadastrar_nota(self):
        self.cadastrar_nota_dialog = CadastrarNota()
        self.cadastrar_nota_dialog.exec_()
      
    def carregar_configuracoes_MainWindow(self):
        config_dialog = ConfigDialog()  # Criar uma instância de ConfigDialog
        config_dialog.carregar_configuracoes_ConfigDialog()  # Carregar configurações antes de usar
        origin_folder = config_dialog.get_origin_folder()
        destination_folder = config_dialog.get_destination_folder()
        process_folder = config_dialog.get_process_folder()
        inicialization_key = config_dialog.get_inicialization_key()
        if origin_folder and destination_folder:
            self.origin_folder = origin_folder
            self.destination_folder = destination_folder
            self.process_folder = process_folder
            self.inicialization_key = inicialization_key
            
            # Inicialize MeuHandler após definir as variáveis
            self.meu_handler = MeuHandler(
                self.origin_folder,
                self.destination_folder,
                self.process_folder,
                self.logger,
                self.log_dialog
            )
            self.logger.log_message(f"Configurações:")
            self.logger.log_message(f"Pasta de origem: {self.origin_folder}")
            self.logger.log_message(f"Pasta de destino: {self.destination_folder}")
            self.logger.log_message(f"Pasta process: {self.process_folder}")
            self.logger.log_message(f"Tecla de atalho: {self.inicialization_key}")
            self.logger.log_message("-----------------------------------")
            
        else:
            if hasattr(self, 'logger') and self.logger is not None:
                self.logger.log_message("Pasta de origem ou destino não selecionada.")
            else:
                print("Pasta de origem ou destino não selecionada.")
                
    def parar_monitoramento(self):
        if hasattr(self, 'observer') and self.observer is not None:
            self.observer.stop()
            self.observer.join()  # Aguarda o Observer parar completamente
    
    def start_monitoring(self):
        if self.origin_folder and self.destination_folder and self.process_folder:
            # Parar o observador e o handler antigos, se existirem
            if hasattr(self, 'observer') and self.observer is not None:
                self.parar_monitoramento()
                
            self.meu_handler = MeuHandler(self.origin_folder, self.destination_folder, self.process_folder,self.logger, self.log_dialog)
            self.observer = Observer()
            self.observer.schedule(self.meu_handler, path=self.origin_folder, recursive=True)
            self.observer.start()
            self.logger.log_message(f"Observando mudanças no diretório: {self.origin_folder}")
        else:
            self.logger.log_message("Pasta de origem ou destino não selecionada. Não é possível iniciar o monitoramento.")

    def saved_key(self, key):
        inicialization_key = self.inicialization_key
        if key == inicialization_key:
            self.iniciar_button_function()
        
        #print(f"Chave detectada: {key}")
        if key == "F8":
            if hasattr(self, 'log_dialog') and self.log_dialog is not None:
                if self.log_dialog.isVisible():
                    self.close_log_dialog()  # Fechar a janela de logs
                else:
                    self.logs_button_function()  # Abrir a janela de logs
            else:
                self.logs_button_function()  # Abrir a janela de logs
    
    def handle_log_window_closed(self):
        # Limpar a referência quando a janela de log for fechada
        self.log_dialog = None
        print("LogDialog fechado.")
        
    def close_log_dialog(self):
        if self.log_dialog and self.log_dialog.isVisible():
            print("Fechando LogDialog.")
            self.log_dialog.close()  # Solicitar o fechamento da janela
        else:
            print("LogDialog não está visível.")

class CadastrarNota(QDialog):
    
    def __init__(self, config_file="cadastro.json"):
        super().__init__()
        self.config_file = config_file
        self.username = "" 
        self.password = ""
        self.cadastro_file = None  # Arquivo de cadastro selecionado
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        self.message_label = QLabel("")
        
        self.title_label = QLabel("Cadastrar Novo Cliente")
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Username")
        self.username_input.setText(self.username)
        
        password_layout = QHBoxLayout()
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText(self.password)

        self.toggle_password_button = QPushButton("Mostrar")
        self.toggle_password_button.setCheckable(True)
        self.toggle_password_button.clicked.connect(self.toggle_password_visibility)

        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.toggle_password_button)
        self.texto_padrao = (
            "PRIMEIRO PADRAO\n\n"
            "NOME: Nome Completo\n"
            "CPF: CPF\n"
            "ENDEREÇO: Rua Número - Complemento\n"
            "CEP: 00000000\n"
            "ESTADO: Estado\n"
            "CIDADE: Cidade\n"
            "UF: UF\n"
            "PRODUTO: Descrição do Produto\n"
            "QUANTIDADE: Quantidade\n"
            "VALOR OU VALOR UNITARIO: R$Valor Unitário\n"
            "NCM: Código NCM\n"
            "UN: Tipo Unidade\n"
            "-------------------\n"
            "SEGUNDO PADRAO\n\n"
            "NOME: Nome Completo\n"
            "CNPJ: CNPJ ou CNPJ: CNPJ (ISENTO) / (CONTRIBUINTE)\n"
            "INSCRIÇÃO ESTADUAL: IE / ISENTO / SEM ESSA LINHA TAMBÉM FICA ISENTO\n"
            "ENDEREÇO: Rua Nome, Número - Complemento\n"
            "CEP: 00000000\n"
            "ESTADO: Estado\n"
            "CIDADE: Cidade\n"
            "UF: UF\n"
            "PRODUTO: Descrição do Produto\n"
            "QUANTIDADE: Quantidade\n"
            "VALOR OU VALOR UNITARIO: R$Valor Unitário\n"
            "NCM: Código NCM\n"
            "UN: Tipo Unidade"
            )

        self.cadastrar_nota_text = QTextEdit(self)
        self.cadastrar_nota_text.setPlaceholderText(
            self.texto_padrao
        )
        
        
        self.btn_sp = QPushButton("Cadastro SP")
        self.btn_sp.clicked.connect(lambda: self.load_file("SP"))
        self.btn_ms = QPushButton("Cadastro MS")
        self.btn_ms.clicked.connect(lambda: self.load_file("MS"))

        self.cadastrar_nota_button = QPushButton("Cadastrar Nota")
        self.cadastrar_nota_button.clicked.connect(self.salvar_cliente)
        
        self.exemplo_button = QPushButton("Exemplo de cadastro")
        self.exemplo_button.clicked.connect(self.exibir_exemplo)

        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.username_input)
        main_layout.addLayout(password_layout)
        main_layout.addWidget(self.btn_sp)
        main_layout.addWidget(self.btn_ms)
        main_layout.addWidget(self.message_label)
        main_layout.addWidget(self.cadastrar_nota_text)
        

        main_layout.addWidget(self.cadastrar_nota_button)
        main_layout.addWidget(self.exemplo_button)

        self.setLayout(main_layout)
        self.setWindowTitle("Cadastrar Nota")

    def load_credentials(self):
        if not os.path.exists(self.cadastro_file):
            self.create_default_credentials()
        else:
            try:
                with open(self.cadastro_file, "r") as f:
                    config_data = json.load(f)
                    self.username = config_data.get("username", "")
                    self.password = config_data.get("password", "")
                    self.cadastro = config_data.get("cadastro", "")
                    
                    self.username_input.setText(self.username)
                    self.password_input.setText(self.password)
                    self.cadastrar_nota_text.setText(self.cadastro)
                    
            except json.JSONDecodeError:
                print("Erro ao decodificar o arquivo JSON.")
                self.create_default_credentials()
                
                
    def load_file(self, tipo):
        pasta_cadastro = "cadastro"
    
        if tipo == "SP":
            self.cadastro_file = os.path.join(pasta_cadastro, "cadastro_sp.json")
        elif tipo == "MS":
            self.cadastro_file = os.path.join(pasta_cadastro, "cadastro_ms.json")
            
        self.load_credentials()    
        
        self.show_message(f"Arquivo de cadastro selecionado: {self.cadastro_file}")
    
      
    def create_default_credentials(self):
        default_data = {
            "username": "",
            "password": "",
            "cadastro": ""
        }
        with open (self.cadastro_file, "w") as f:
            json.dump(default_data, f)
        print(f"Arquivo {self.cadastro_file} criado com sucesso.")

    def toggle_password_visibility(self):
        if self.toggle_password_button.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_button.setText("Ocultar")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_button.setText("Mostrar")
            
    def show_message(self, message):
        self.message_label.setText(message)
        self.message_label.setStyleSheet("color: green;")
        self.message_label.show()

        QTimer.singleShot(1000, self.hide_message)
        
    def show_message_error(self, message):
        self.message_label.setText(message)
        self.message_label.setStyleSheet("color: red;")
        self.message_label.show()
    
        QTimer.singleShot(1000, self.hide_message)
        
    def hide_message(self):
        self.message_label.hide()
        
    def exibir_exemplo(self):
        exemplo_dialog = QDialog(self)
        exemplo_dialog.setWindowTitle("Exemplo de cadastro")

        exemplo_layout = QVBoxLayout()
        
        exemplo_text = QTextEdit(exemplo_dialog)
        exemplo_text.setPlainText(
            self.texto_padrao
        )
        exemplo_text.setReadOnly(True)
        exemplo_layout.addWidget(exemplo_text)

        exemplo_dialog.setLayout(exemplo_layout)
        exemplo_dialog.setModal(False)
        exemplo_dialog.move(self.geometry().right(), self.geometry().top())
        exemplo_dialog.show()
    

    def salvar_cliente(self):
        if not self.cadastro_file:
            self.show_message_error("Selecione um tipo de cadastro antes de salvar.")
            return

        username = self.username_input.text()
        password = self.password_input.text()
        cadastro = self.cadastrar_nota_text.toPlainText()

        cadastro_data = {
            "username": username,
            "password": password,
            "cadastro": cadastro
        }

        with open(self.cadastro_file, "w") as f:
            json.dump(cadastro_data, f, indent=4)

        self.show_message(f"Dados salvos em {self.cadastro_file}")
        self.ativar_robo()
        
        
    def ativar_robo(self):
        match = re.search(r'_(\w+)\.json$', self.cadastro_file)
        if match:
            tipo = match.group(1)
            pasta_cadastro = "cadastro/"
            variaveis_file = f"{pasta_cadastro}variaveis_{tipo}.py"

            process = subprocess.Popen(["robot", "--variablefile", variaveis_file, "cadastro/cadastrar_nota.robot"])

            try:
                process.wait()
                self.show_message("Processo de automação iniciado com sucesso.")
            except Exception as e:
                print(f"Erro ao iniciar o processo de automação: {e}")
                process.terminate()
        else:
            self.show_message_error("Erro: tipo de cadastro não encontrado no nome do arquivo.")

class ConfigDialog(QDialog):
    
    config_saved = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.origin_folder = None
        self.destination_folder = None
        self.inicialization_key = None
        
        self.key_listener = KeyListener()
        self.log_dialog = LogDialog()
        self.logger = Logger(self.log_dialog)
        self.config_ui()
        
    def config_ui(self):
        main_layout = QGridLayout()
        
        self.combobox = QComboBox(self)
        self.combobox.addItems([(str(key).split(".")[1].capitalize()) for key in self.key_listener.key_map.keys()])
        self.combobox.activated[str].connect(self.selecionar_tecla_do_combobox)
        self.combobox.hide()
        
        self.setWindowTitle("Configurações")
        
        self.title_tecla = QLabel("Selecione uma tecla para inicializar o programa: ")
        self.title_pastas = QLabel("Selecione as pastas: ")
        
        self.input_field_pasta = QLineEdit()
        self.output_field_pasta = QLineEdit()
        self.process_field_pasta= QLineEdit()
        self.input_field_tecla = QLineEdit()
        
        self.input_field_tecla.setReadOnly(True)
        
        #Botões
        self.selecionar_entrada_button = QPushButton("Selecionar Pasta de Entrada")
        self.selecionar_saida_button = QPushButton("Selecionar Pasta de Saída")
        self.selecionar_process_button = QPushButton("Selecionar Pasta process")
        self.salvar_button = QPushButton("Salvar")
        
        min_width = 300
        #Tamanhos
        self.input_field_pasta.setMinimumWidth(min_width)
        self.output_field_pasta.setMinimumWidth(min_width)
        self.process_field_pasta.setMinimumWidth(min_width)
        self.input_field_tecla.setMinimumWidth(min_width)
        
        self.selecionar_entrada_button.setMinimumWidth(min_width)
        self.selecionar_saida_button.setMinimumWidth(min_width)
        self.selecionar_process_button.setMinimumWidth(min_width)
        self.salvar_button.setMinimumWidth(min_width)
        
        #Layouts
        main_layout.addWidget(self.title_tecla, 0, 1)
        main_layout.addWidget(self.title_pastas, 0, 0)
        main_layout.addWidget(self.input_field_pasta, 1, 0)
        main_layout.addWidget(self.input_field_tecla, 1, 1)
        main_layout.addWidget(self.combobox, 1, 0, 1, 2)
        main_layout.addWidget(self.selecionar_entrada_button, 2, 0)
        main_layout.addWidget(self.output_field_pasta, 3, 0)
        main_layout.addWidget(self.selecionar_saida_button, 4, 0)
        main_layout.addWidget(self.process_field_pasta, 3, 1)
        main_layout.addWidget(self.selecionar_process_button, 4, 1)
        main_layout.addWidget(self.salvar_button, 5, 0, 1, 2)

        self.input_field_tecla.mousePressEvent = self.mostrar_combobox

        # Eventos
        self.selecionar_entrada_button.clicked.connect(self.selecionar_pasta_entrada)
        self.selecionar_saida_button.clicked.connect(self.selecionar_pasta_saida)
        self.selecionar_process_button.clicked.connect(self.selecionar_pasta_process)
        self.salvar_button.clicked.connect(self.salvar_configuracoes)
        
        self.setLayout(main_layout)
     
    def mousePressEventHandler(self, event):
        self.mostrar_combobox(event)
    
    def mostrar_combobox(self, event):
        line_edit_size = self.input_field_tecla.sizeHint()
        
        line_edit_pos = self.input_field_tecla.mapTo(self, QPoint(0, 0))
        
        # Definir a posição e largura do combobox próximo ao QLineEdit dentro da janela de configurações
        combobox_x = line_edit_pos.x()
        combobox_y = line_edit_pos.y() 
        self.combobox.setGeometry(combobox_x, combobox_y, line_edit_size.width(), self.combobox.height())
        self.combobox.showPopup()
        self.combobox.setFocus()
        
    def selecionar_tecla_do_combobox(self, key_name):
        self.input_field_tecla.setText(key_name)
        self.inicialization_key = key_name
        self.combobox.hide()
     
    def selecionar_pasta_entrada(self):
        pasta_entrada = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Entrada")
        if pasta_entrada:
            self.input_field_pasta.setText(pasta_entrada)
            self.origin_folder = pasta_entrada
    
    def selecionar_pasta_saida(self):
        pasta_saida = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Saída")
        if pasta_saida:
            self.output_field_pasta.setText(pasta_saida)
            self.destination_folder = pasta_saida
            
    def selecionar_pasta_process(self):
        pasta_process = QFileDialog.getExistingDirectory(self, "Selecionar Pasta process")
        if pasta_process:
            self.process_field_pasta.setText(pasta_process)
            self.process_folder = pasta_process
        
    def salvar_configuracoes(self):
        
        origin_folder = self.input_field_pasta.text()
        destination_folder = self.output_field_pasta.text()
        process_folder = self.process_field_pasta.text()
        inicialization_key = self.inicialization_key

        # Salva as configurações em um arquivo JSON
        config_data = {
            "origin_folder": origin_folder,
            "destination_folder": destination_folder,
            "process_folder": process_folder,
            "inicialization_key": inicialization_key
        }
        with open("config.json", "w") as f:
            json.dump(config_data, f)

        # Atualiza as variáveis de classe
        self.origin_folder = origin_folder
        self.destination_folder = destination_folder
        self.process_folder = process_folder
        self.inicialization_key = inicialization_key
        self.config_saved.emit()
        self.logger.log_message("Configurações salvas com sucesso.")
        self.close()  # Fecha o diálogo
        
    def carregar_configuracoes_ConfigDialog(self):
        # Carrega as configurações do arquivo JSON se existir
        try:
            with open("config.json", "r") as f:
                config_data = json.load(f)
                self.origin_folder = config_data.get("origin_folder", "")
                self.destination_folder = config_data.get("destination_folder", "")
                self.process_folder = config_data.get("process_folder", "")
                self.inicialization_key = config_data.get("inicialization_key", "")
                self.input_field_pasta.setText(self.origin_folder)
                self.output_field_pasta.setText(self.destination_folder)
                self.process_field_pasta.setText(self.process_folder)
                self.input_field_tecla.setText(self.inicialization_key)
                
                
        except FileNotFoundError:
            pass

    def get_origin_folder(self):
        return self.input_field_pasta.text()

    def get_destination_folder(self):
        return self.output_field_pasta.text()
    
    def get_process_folder(self):
        return self.process_field_pasta.text()
    
    def get_inicialization_key(self):
        return self.input_field_tecla.text()
    
class LogDialog(QDialog):
    closed = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logs")
        self.resize(400, 300)
        self.main_layout = QVBoxLayout(self)
        
        self.log_view = QTextEdit(self)
        self.log_view.setReadOnly(True)
        
        self.clear_button = QPushButton("Limpar logs", self)
        
        self.main_layout.addWidget(self.log_view)
        self.main_layout.addWidget(self.clear_button)
        
        self.clear_button.clicked.connect(self.clear_logs)
        
        self.setLayout(self.main_layout)

    def append_log(self, message):
        self.log_view.append(message)
        self.log_view.ensureCursorVisible()
        
    def clear_logs(self):
        self.log_view.clear()
        
    def closeEvent(self, event):
        super().closeEvent(event)
        self.closed.emit()
        
    
class Logger(QObject):
    new_log_message = pyqtSignal(str)
    
    def __init__(self, log_dialog):
        super().__init__()
        self.log_dialog = log_dialog
        self.new_log_message.connect(self.log_dialog.append_log)

    def log_message(self, message):
        self.new_log_message.emit(message)
        print(message)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())