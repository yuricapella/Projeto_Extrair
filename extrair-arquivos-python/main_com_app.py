import sys
import time
import os
import zipfile
import shutil
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget,QDialog, QLineEdit, QFileDialog, QTextEdit
from PyQt5.QtCore import Qt, QThread, pyqtSignal
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
    keyPressed = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def run(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    def on_press(self, key):
        try:
            if key == keyboard.Key.f6:
                self.keyPressed.emit(Qt.Key_F6)
        except AttributeError:
            pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_dialog = ConfigDialog()
        self.config_dialog.config_saved.connect(self.carregar_configuracoes)
        
        # Start logs
        self.log_dialog = LogDialog()
        self.logger = Logger(self.log_dialog)
        
        
        self.observer = None
        self.monitorando = False
        self.origin_folder = None
        self.destination_folder = None  # Inicialize esses valores como None

        # Carregar configurações antes de usar
        self.carregar_configuracoes()
        
        self.setWindowTitle("Extração app")
        layout = QVBoxLayout()
        self.extrair_title = QLabel("Extrair arquivos")
        layout.addWidget(self.extrair_title)
        
        self.iniciar_button = QPushButton("Iniciar")
        layout.addWidget(self.iniciar_button)
        
        self.config_button = QPushButton("Configurações")
        layout.addWidget(self.config_button)
        
        self.logs_button = QPushButton("Logs")
        layout.addWidget(self.logs_button)
        
        self.extrair_hint = QLabel("Deve-se parar programa o caso for alterar as pastas")
        layout.addWidget(self.extrair_hint)
        
        self.iniciar_button.clicked.connect(self.iniciar_button_function)
        self.config_button.clicked.connect(self.config_button_function)
        self.logs_button.clicked.connect(self.logs_button_function)
        
        # Principal
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Start key listener thread
        self.key_listener = KeyListener()
        self.key_listener.keyPressed.connect(self.on_key)
        self.key_listener.start()

        
    
    def iniciar_button_function(self):
        if self.monitorando:
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
        config_dialog = ConfigDialog()  # Criar uma instância de ConfigDialog
        self.log_dialog = LogDialog()
        self.logger = Logger(self.log_dialog)
        
        config_dialog.config_saved.connect(self.carregar_configuracoes)
        def verificar_e_parar_monitoramento():
            if self.iniciar_button.text() == "Parar":
                config_dialog.salvar_button.clicked.connect(self.iniciar_button_function)
        verificar_e_parar_monitoramento()
        config_dialog.carregar_configuracoes()  # Carregar configurações antes de usar
        if config_dialog.exec_():
            origin_folder = config_dialog.get_origin_folder()
            destination_folder = config_dialog.get_destination_folder()
            if origin_folder and destination_folder:
                self.origin_folder = origin_folder
                self.destination_folder = destination_folder
            else:
                self.logger.log_message("Pasta de origem ou destino não selecionada.")                

    def logs_button_function(self):
        self.log_dialog.exec_()
    
    def carregar_configuracoes(self):
        config_dialog = ConfigDialog()  # Criar uma instância de ConfigDialog
        config_dialog.carregar_configuracoes()  # Carregar configurações antes de usar
        origin_folder = config_dialog.get_origin_folder()
        destination_folder = config_dialog.get_destination_folder()
        if origin_folder and destination_folder:
            self.origin_folder = origin_folder
            self.destination_folder = destination_folder
            self.logger.log_message(f"Pasta de origem: {self.origin_folder}")
            self.logger.log_message(f"Pasta de destino: {self.destination_folder}")
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
        if key == Qt.Key_F6:
            self.iniciar_button_function()

class ConfigDialog(QDialog):
    
    config_saved = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.origin_folder = None  # Definindo como variável de classe
        self.destination_folder = None  # Definindo como variável de classe
        
        layout = QVBoxLayout()
        self.setWindowTitle("Configurações")
        
        # Label "Entrada"
        self.label_entrada = QLabel("Entrada")
        layout.addWidget(self.label_entrada)
        
        # Campo de entrada para o diretório de entrada
        self.input_label = QLabel("Digite o caminho da pasta:")
        self.input_field = QLineEdit()
        layout.addWidget(self.input_label)
        layout.addWidget(self.input_field)
        
        # Botão para selecionar pasta de entrada
        self.selecionar_entrada_button = QPushButton("Selecionar Pasta de Entrada")
        layout.addWidget(self.selecionar_entrada_button)
        
        # Label "Saída"
        self.label_saida = QLabel("Saída")
        layout.addWidget(self.label_saida)
        
        # Campo de entrada para o diretório de saída
        self.output_label = QLabel("Digite o caminho da pasta:")
        self.output_field = QLineEdit()
        layout.addWidget(self.output_label)
        layout.addWidget(self.output_field)
        
        # Botão para selecionar pasta de saída
        self.selecionar_saida_button = QPushButton("Selecionar Pasta de Saída")
        layout.addWidget(self.selecionar_saida_button)
        
        # Botões
        self.salvar_button = QPushButton("Salvar")
        layout.addWidget(self.salvar_button)
        
        # Eventos
        self.selecionar_entrada_button.clicked.connect(self.selecionar_pasta_entrada)
        self.selecionar_saida_button.clicked.connect(self.selecionar_pasta_saida)
        self.salvar_button.clicked.connect(self.salvar_configuracoes)
        
        self.setLayout(layout)
        
    def selecionar_pasta_entrada(self):
        pasta_entrada = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Entrada")
        if pasta_entrada:
            self.input_field.setText(pasta_entrada)
            self.origin_folder = pasta_entrada
    
    def selecionar_pasta_saida(self):
        pasta_saida = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Saída")
        if pasta_saida:
            self.output_field.setText(pasta_saida)
            self.destination_folder = pasta_saida
    
    def salvar_configuracoes(self):
        origin_folder = self.input_field.text()  # Obtém o texto do campo de entrada
        destination_folder = self.output_field.text()  # Obtém o texto do campo de saída

        # Salva as configurações em um arquivo JSON
        config_data = {
            "origin_folder": origin_folder,
            "destination_folder": destination_folder
        }
        with open("config.json", "w") as f:
            json.dump(config_data, f)

        # Atualiza as variáveis de classe
        self.origin_folder = origin_folder
        self.destination_folder = destination_folder
        self.config_saved.emit()
        self.close()  # Fecha o diálogo
        
    def carregar_configuracoes(self):
        # Carrega as configurações do arquivo JSON se existir
        try:
            with open("config.json", "r") as f:
                config_data = json.load(f)
                self.origin_folder = config_data.get("origin_folder", "")
                self.destination_folder = config_data.get("destination_folder", "")
                self.input_field.setText(self.origin_folder)
                self.output_field.setText(self.destination_folder)
        except FileNotFoundError:
            pass  # Se o arquivo não existir, ignora o erro

    def get_origin_folder(self):
        return self.input_field.text()

    def get_destination_folder(self):
        return self.output_field.text()
    
class LogDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logs")
        self.resize(400, 300)
        self.layout = QVBoxLayout(self)
        
        self.log_view = QTextEdit(self)
        self.log_view.setReadOnly(True)
        self.layout.addWidget(self.log_view)

    def append_log(self, message):
        self.log_view.append(message)
        
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

