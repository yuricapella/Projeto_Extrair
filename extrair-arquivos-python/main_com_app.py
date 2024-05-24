import sys
import time
import os
import zipfile
import shutil
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QWidget,QDialog, 
                            QLineEdit, QFileDialog, QTextEdit, QComboBox)

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint
from pynput import keyboard
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def processar_arquivos(origin_folder, destination_folder):
    for arquivo in os.listdir(origin_folder):
        file_name, ext = os.path.splitext(arquivo)
        if ext == ".zip" and os.path.exists(os.path.join(origin_folder, f'{file_name}.pdf')):
            arquivo_zip = zipfile.ZipFile(os.path.join(origin_folder, arquivo))
            arquivo_zip.extractall(origin_folder)
            um_nome = arquivo_zip.namelist()[0]
            arquivo_zip.close()
            os.remove(os.path.join(origin_folder, arquivo))
            file_count = checkIsUnique(file_name, destination_folder)
            if file_count > 0:
                file_count += 1
                enviar_xml(um_nome, f'{file_name}-{file_count}', origin_folder, destination_folder)
                enviar_pdf(file_name, f'{file_name}-{file_count}', origin_folder, destination_folder)
            else: 
                enviar_xml(um_nome, file_name, origin_folder, destination_folder)
                enviar_pdf(file_name, None, origin_folder, destination_folder)
        elif ext == ".zip":
            print("Não encontrou o arquivo zip e pdf")

def checkIsUnique(file_name, destination_folder):
    sameItemCount = 0
    for nome_arquivo in os.listdir(destination_folder):
        if file_name in nome_arquivo and 'xml' in nome_arquivo:
            sameItemCount += 1
    return sameItemCount

def enviar_xml(um_nome, file_name, origin_folder, destination_folder):
    if os.path.exists(os.path.join(origin_folder, um_nome)):
        shutil.move(os.path.join(origin_folder, um_nome), os.path.join(destination_folder, f'{file_name}.xml'))
        print("moveu o xml")
    else:
        print("Não encontrou o XML")

def enviar_pdf(um_nome, file_name, origin_folder, destination_folder):
    if os.path.exists(os.path.join(origin_folder, f'{um_nome}.pdf')):
        if file_name:
            shutil.move(os.path.join(origin_folder, f'{um_nome}.pdf'), os.path.join(destination_folder, f'{file_name}.pdf'))
        else: 
            shutil.move(os.path.join(origin_folder, f'{um_nome}.pdf'), os.path.join(destination_folder, f'{um_nome}.pdf'))
        print("moveu o pdf")
    else:
        print("Não encontrou o PDF")

class MeuHandler(FileSystemEventHandler):
    def __init__(self, origin_folder, destination_folder, logger, log_dialog):
        super().__init__()
        self.origin_folder = origin_folder
        self.destination_folder = destination_folder
        self.logger = logger
        self.log_dialog = log_dialog

    def on_created(self, event):
        if event.is_directory:
            return
        file_name, ext = os.path.splitext(event.src_path)
        file_name_only = os.path.basename(file_name)
        if ext.lower() in ['.pdf', '.zip']:
            self.logger.log_message(f'Arquivo criado: {file_name_only}{ext}')
            time.sleep(2)
            pdf_file = os.path.join(self.origin_folder, f"{file_name}.pdf")
            zip_file = os.path.join(self.origin_folder, f"{file_name}.zip")
            if os.path.exists(pdf_file) and os.path.exists(zip_file):
                processar_arquivos(self.origin_folder, self.destination_folder)
                self.logger.log_message("Arquivos processados")
        
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
                # Emitir o sinal com o valor da tecla
                self.keyPressed.emit(self.key_map[key])
        except AttributeError:
            pass
    
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_dialog = ConfigDialog()
        self.config_dialog.config_saved.connect(self.carregar_configuracoes_MainWindow)
        
        # Start logs
        self.log_dialog = LogDialog()
        self.logger = Logger(self.log_dialog)
        
        self.observer = None
        self.monitorando = False
        self.origin_folder = None
        self.destination_folder = None  # Inicialize esses valores como None
        self.selected_key = None

        # Carregar configurações antes de usar
        self.carregar_configuracoes_MainWindow()
        main_layout = QVBoxLayout()
        sub_layout = QHBoxLayout()
        self.setWindowTitle("Extração app")

        #Botões
        self.iniciar_button = QPushButton("Iniciar")
        self.config_button = QPushButton("Configurações")
        self.logs_button = QPushButton("Logs")
        
        #Widgets
        main_layout.addWidget(self.iniciar_button)
        sub_layout.addWidget(self.config_button)
        sub_layout.addWidget(self.logs_button)
        main_layout.addLayout(sub_layout)
        
        #Eventos
        self.iniciar_button.clicked.connect(self.iniciar_button_function)
        self.config_button.clicked.connect(self.config_button_function)
        self.logs_button.clicked.connect(self.logs_button_function)
        
        # Principal
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.resize(250, 100)

        # Start key listener thread
        self.key_listener = KeyListener()
        self.key_listener.keyPressed.connect(self.on_key)
        self.key_listener.start()

    def iniciar_button_function(self):
        if self.monitorando:
            if self.observer is not None:
                self.observer.stop()
                self.observer.join()
            self.monitorando = False
            self.iniciar_button.setText("Iniciar")
            self.logger.log_message("Monitoramento parado.")
        else:
            self.start_monitoring()
            self.monitorando = True
            self.iniciar_button.setText("Parar")
            self.logger.log_message("Monitoramento iniciado.")
    
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
                selected_key = self.config_dialog_instance.selected_key

                if origin_folder and destination_folder and selected_key:
                    self.origin_folder = origin_folder
                    self.destination_folder = destination_folder
                    self.selected_key = selected_key
                else:
                    self.logger.log_message("Pasta de origem ou destino não selecionada.")
                    
    def logs_button_function(self):
        if hasattr(self,'log_dialog_instance') and self.log_dialog_instance.isVisible():
            self.log_dialog_instance.raise_()
            self.log_dialog_instance.activateWindow()
            return
        
        self.log_dialog_instance = LogDialog()
        self.log_dialog.setWindowFlags(self.log_dialog.windowFlags() | Qt.WindowStaysOnTopHint | Qt.WindowMinimizeButtonHint)
        self.log_dialog.show()
    
    def carregar_configuracoes_MainWindow(self):
        config_dialog = ConfigDialog()  # Criar uma instância de ConfigDialog
        config_dialog.carregar_configuracoes_ConfigDialog()  # Carregar configurações antes de usar
        origin_folder = config_dialog.get_origin_folder()
        destination_folder = config_dialog.get_destination_folder()
        selected_key = config_dialog.get_selected_key()
        if origin_folder and destination_folder:
            self.origin_folder = origin_folder
            self.destination_folder = destination_folder
            self.selected_key = selected_key
            
            self.logger.log_message(f"Pasta de origem: {self.origin_folder}")
            self.logger.log_message(f"Pasta de destino: {self.destination_folder}")
            self.logger.log_message(f"Tecla de atalho: {self.selected_key}")
        else:
            self.logger.log_message("Pasta de origem ou destino não selecionada.")
  
    def start_monitoring(self):
        if self.origin_folder and self.destination_folder:  # Verifica se as pastas estão definidas
            event_handler = MeuHandler(self.origin_folder, self.destination_folder,self.logger,self.log_dialog)  # Passa origin_folder e destination_folder
            self.observer = Observer()
            self.observer.schedule(event_handler, path=self.origin_folder, recursive=True)
            self.observer.start()  # Inicia o observador
            self.logger.log_message(f"Observando mudanças no diretório: {self.origin_folder}")
        else:
            self.logger.log_message("Pasta de origem ou destino não selecionada. Não é possível iniciar o monitoramento.")

    def on_key(self, key):
        selected_key = self.selected_key
        if key == selected_key:
            self.iniciar_button_function()
            
class ConfigDialog(QDialog):
    
    config_saved = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.origin_folder = None  # Definindo como variável de classe
        self.destination_folder = None  # Definindo como variável de classe
        self.selected_key = None
        
        self.key_listener = KeyListener()
        
        #Layout
        main_layout = QGridLayout()
        
        #Combo Box
        self.combobox = QComboBox(self)
        self.combobox.addItems([(str(key).split(".")[1].capitalize()) for key in self.key_listener.key_map.keys()])
        self.combobox.activated[str].connect(self.selecionar_tecla_do_combobox)
        self.combobox.hide()
        
        self.setWindowTitle("Configurações")
        
        self.title_tecla = QLabel("Selecione uma tecla de atalho: ")
        self.title_pastas = QLabel("Selecione as pastas: ")
        
        self.input_field_pasta = QLineEdit()
        self.output_field_pasta = QLineEdit()
        self.input_field_tecla = QLineEdit()
        
        self.input_field_tecla.setReadOnly(True)
        
        #Botões
        self.selecionar_entrada_button = QPushButton("Selecionar Pasta de Entrada")
        self.selecionar_saida_button = QPushButton("Selecionar Pasta de Saída")
        self.salvar_button = QPushButton("Salvar")
        
        #Layouts
        main_layout.addWidget(self.title_tecla, 0, 1)
        main_layout.addWidget(self.title_pastas, 0, 0)
        main_layout.addWidget(self.input_field_pasta, 1, 0)
        main_layout.addWidget(self.input_field_tecla, 1, 1)
        main_layout.addWidget(self.combobox, 1, 0, 1, 2)
        main_layout.addWidget(self.selecionar_entrada_button, 2, 0)
        main_layout.addWidget(self.output_field_pasta, 3, 0)
        main_layout.addWidget(self.selecionar_saida_button, 4, 0)
        main_layout.addWidget(self.salvar_button, 5, 0, 1, 3)

        # Conectar o clique do QLineEdit ao método apropriado
        #self.input_field_tecla.mousePressEvent = self.mousePressEventHandler
        self.input_field_tecla.mousePressEvent = self.mostrar_combobox

        # Eventos
        self.selecionar_entrada_button.clicked.connect(self.selecionar_pasta_entrada)
        self.selecionar_saida_button.clicked.connect(self.selecionar_pasta_saida)
        self.salvar_button.clicked.connect(self.salvar_configuracoes)
        
        self.setLayout(main_layout)
     
    def mousePressEventHandler(self, event):
        # Exibir o combobox e também iniciar o key listener
        self.mostrar_combobox(event)
    
    def mostrar_combobox(self, event):
        # Obter o tamanho sugerido do QLineEdit
        line_edit_size = self.input_field_tecla.sizeHint()
        # Obter a posição do QLineEdit relativa à janela de configurações
        line_edit_pos = self.input_field_tecla.mapTo(self, QPoint(0, 0))
        # Definir a posição e largura do combobox próximo ao QLineEdit dentro da janela de configurações
        combobox_x = line_edit_pos.x()
        combobox_y = line_edit_pos.y() 
        self.combobox.setGeometry(combobox_x, combobox_y, line_edit_size.width(), self.combobox.height())
        self.combobox.showPopup()
        self.combobox.setFocus()
        
    def selecionar_tecla_do_combobox(self, key_name):
        self.input_field_tecla.setText(key_name)  # Exibir tecla selecionada no QLineEdit
        self.selected_key = key_name
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
        
    
    def salvar_configuracoes(self):
        origin_folder = self.input_field_pasta.text()  # Obtém o texto do campo de entrada
        destination_folder = self.output_field_pasta.text()  # Obtém o texto do campo de saída
        selected_key = self.selected_key

        # Salva as configurações em um arquivo JSON
        config_data = {
            "origin_folder": origin_folder,
            "destination_folder": destination_folder,
            "selected_key": selected_key
        }
        with open("config.json", "w") as f:
            json.dump(config_data, f)

        # Atualiza as variáveis de classe
        self.origin_folder = origin_folder
        self.destination_folder = destination_folder
        self.selected_key = selected_key
        self.config_saved.emit()
        self.close()  # Fecha o diálogo
        
    def carregar_configuracoes_ConfigDialog(self):
        # Carrega as configurações do arquivo JSON se existir
        try:
            with open("config.json", "r") as f:
                config_data = json.load(f)
                self.origin_folder = config_data.get("origin_folder", "")
                self.destination_folder = config_data.get("destination_folder", "")
                self.selected_key = config_data.get("selected_key", "")
                self.input_field_pasta.setText(self.origin_folder)
                self.output_field_pasta.setText(self.destination_folder)
                self.input_field_tecla.setText(self.selected_key)
        except FileNotFoundError:
            pass  # Se o arquivo não existir, ignora o erro

    def get_origin_folder(self):
        return self.input_field_pasta.text()

    def get_destination_folder(self):
        return self.output_field_pasta.text()
    
    def get_selected_key(self):
        return self.input_field_tecla.text()
    
class LogDialog(QDialog):
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

    def append_log(self, message):
        self.log_view.append(message)
        self.log_view.ensureCursorVisible()
        
    def clear_logs(self):
        self.log_view.clear()
    
        
        
class Logger:
    def __init__(self, log_dialog):
        self.log_dialog = log_dialog

    def log_message(self, message):
        self.log_dialog.append_log(message)
        print(message)  # Também imprime no console, se necessário    

            
    
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

