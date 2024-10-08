import sys
import markdown
from pathlib import Path
from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QFileDialog, QLabel, QTextEdit, QDialog, QLineEdit, QComboBox, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QBrush, QPalette, QIcon
from back.colorimetry import colorimetric_fusion
from back.PCA import pca_fusion
from deep_translator import GoogleTranslator


ROOT_DIR = Path(__file__).resolve().parent.parent
STYLESHEET_PATH = ROOT_DIR / "front" / "static" / "css" / "style.css"
TUTORIAL_PATH = ROOT_DIR / "front" / "static" / "md" / "tutorial.md"
BACKGROUND_IMAGE_PATH = ROOT_DIR / "front" / "static" / "img" / "Background2.png"
ICON_IMAGE_PATH = ROOT_DIR / "front" / "static" / "img" / "imported.png"
error_string = 'Ocorreu um erro!'
translator = GoogleTranslator(source='en', target='pt')


class MainWindow(QMainWindow):
    def __init__(self, api_function):
        super().__init__()
        self.api_function = api_function
        self.output_path = ''
        self.setWindowTitle("Janela Principal")

        # Dimensões da janela
        self.setMaximumSize(400, 400)
        self.resize(400, 400)

        # Carregando a imagem de fundo
        background_image = QPixmap(str(BACKGROUND_IMAGE_PATH))

        # Ajustando o tamanho da imagem de fundo para o tamanho da janela
        scaled_background_image = background_image.scaled(self.size())

        # Configurando a paleta de cores para incluir transparência
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(scaled_background_image))
        self.setPalette(palette)

        # Configurando os botões principais
        self.open_tutorial_button = QPushButton("Abrir Tutorial")
        self.open_tutorial_button.setObjectName("OpenTutorialButton")
        self.open_tutorial_button.clicked.connect(self.open_tutorial)
        self.open_tutorial_button.setFixedSize(150, 50)

        self.open_api_setup_button = QPushButton("Configurar API")
        self.open_api_setup_button.setObjectName("ApiSetupButton")
        self.open_api_setup_button.clicked.connect(self.open_api_setup)
        self.open_api_setup_button.setFixedSize(150, 50)

        # Configurando o botão de saída de imagem
        self.output_folder_button = QPushButton("Selecione o diretório de saída")
        self.output_folder_button.setObjectName("OutputFolderButton")
        self.output_folder_button.clicked.connect(self.select_output_folder)

        # Configurando os botões de importação
        self.import_multispectral_button = QPushButton("Importar MultiS")
        self.import_multispectral_button.setObjectName("MultiSpectralButton")
        self.import_multispectral_button.clicked.connect(self.import_multispectral)
        self.import_multispectral_button.setFixedSize(150, 50)
        self.import_multispectral_button.setIcon(QIcon(str(ICON_IMAGE_PATH)))

        self.import_panc_button = QPushButton("Importar Pan")
        self.import_panc_button.setObjectName("PanCButton")
        self.import_panc_button.clicked.connect(self.import_panc)
        self.import_panc_button.setFixedSize(150, 50)
        self.import_panc_button.setIcon(QIcon(str(ICON_IMAGE_PATH)))

        # Configurando os botões de métodos de fusão
        self.pca_method_button = QPushButton("Fusão PCA")
        self.pca_method_button.setObjectName("PCAFusionButton")
        self.pca_method_button.clicked.connect(self.open_pca_method)

        self.colorimetric_method_button = QPushButton("Fusão Colorimétrica")
        self.colorimetric_method_button.setObjectName("ColorimetricFusionButton")
        self.colorimetric_method_button.clicked.connect(self.open_colorimetric_method)    

        # Configurando o layout principal
        self.layout = QVBoxLayout()

        # Criando um layout vertical para os botões principais
        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.open_tutorial_button, alignment=Qt.AlignmentFlag.AlignCenter)
        buttons_layout.addWidget(self.open_api_setup_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Adicionando o botão de saída de imagem
        buttons_layout.addWidget(self.output_folder_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Criando um layout horizontal para os botões de importação
        import_buttons_layout = QHBoxLayout()
        import_buttons_layout.addWidget(self.import_multispectral_button)
        import_buttons_layout.addWidget(self.import_panc_button)

        # Adicionando os layouts ao layout principal
        self.layout.addLayout(buttons_layout)
        self.layout.addLayout(import_buttons_layout)

        # Criando layout horizontal para os botões de métodos de fusão
        methods_layout = QHBoxLayout()
        methods_layout.addWidget(self.pca_method_button)
        methods_layout.addWidget(self.colorimetric_method_button)
        self.layout.addLayout(methods_layout)

        # Configurando o widget central
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def open_tutorial(self):
        with open(TUTORIAL_PATH, "r", encoding='utf-8') as file:
            tutorial_content = file.read()

        html_content = markdown.markdown(tutorial_content)

        self.tutorial_dialog = TutorialDialog(html_content)
        self.tutorial_dialog.show()

    def open_api_setup(self):
        self.api_setup_window = SetUpAPIWindow(self.api_function)
        self.api_setup_window.show()

    def import_multispectral(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Selecione o arquivo multiespectral:", "", "Tif files (*.tif)")
        if file_path:
            self.multiespectral_path = file_path

    def import_panc(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Selecione o arquivo pancromático:", "", "Tif files (*.tif)")
        if file_path:
            self.panchromatic_path = file_path

    def select_output_folder(self):
        folder_dialog = QFileDialog()
        folder_path = folder_dialog.getExistingDirectory(self, "Selecione o diretório de saída")
        if folder_path:
            self.output_path = folder_path

    def open_pca_method(self):
        if self.output_path != '':
            try:
                colorimetric_fusion(
                self.multiespectral_path,
                self.panchromatic_path,
                self.output_path
            )
                success_message = QMessageBox()
                success_message.setIcon(QMessageBox.Icon.Information)
                success_message.setWindowTitle("Sucesso")
                success_message.setText("Fusão realizada com sucesso!")
                success_message.setStandardButtons(QMessageBox.StandardButton.Ok)
                success_message.exec()

            except Exception as e:
                error_message = QMessageBox()
                error_message.setIcon(QMessageBox.Icon.Critical)
                error_message.setWindowTitle("Erro")
                error_message.setText(error_string)
                translated_error = translator.translate(str(e))
                error_message.setInformativeText(translated_error)
                error_message.setStandardButtons(QMessageBox.StandardButton.Ok)
                error_message.exec()
        else:
            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Icon.Critical)
            error_message.setWindowTitle("Erro")
            error_message.setText(error_string)
            error_message.setInformativeText("Por favor, insira um diretório de saída.")
            error_message.setStandardButtons(QMessageBox.StandardButton.Ok)  
            error_message.exec()
                

    def open_colorimetric_method(self):
        if self.output_path != '':
            try:
                pca_fusion(
                    self.multiespectral_path,
                    self.panchromatic_path,
                    self.output_path
                )
                success_message = QMessageBox()
                success_message.setIcon(QMessageBox.Icon.Information)
                success_message.setWindowTitle("Sucesso")
                success_message.setText("Fusão realizada com sucesso!")
                success_message.setStandardButtons(QMessageBox.StandardButton.Ok)
                success_message.exec()

            except Exception as e:
                error_message = QMessageBox()
                error_message.setIcon(QMessageBox.Icon.Critical)
                error_message.setWindowTitle("Erro")
                error_message.setText(error_string)
                translated_error = translator.translate(str(e))
                error_message.setInformativeText(translated_error)
                error_message.setStandardButtons(QMessageBox.StandardButton.Ok)
                error_message.exec()
        else:
            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Icon.Critical)
            error_message.setWindowTitle("Erro")
            error_message.setText(error_string)
            error_message.setInformativeText("Por favor, insira um diretório de saída.")
            error_message.setStandardButtons(QMessageBox.StandardButton.Ok)
            error_message.exec()
        

class TutorialDialog(QDialog):
    def __init__(self, content):
        super().__init__()
        self.setWindowTitle("Tutorial de Uso")

        # Configurando o layout principal
        self.layout = QVBoxLayout()

        # Adicionando um QTextEdit para exibir o conteúdo do tutorial
        self.text_edit = QTextEdit()
        self.text_edit.setHtml(content)
        self.text_edit.setReadOnly(True)
        self.layout.addWidget(self.text_edit)

        # Adicionando o botão de fechar
        self.close_button = QPushButton("Fechar")
        self.close_button.setObjectName("CloseButton")
        self.close_button.clicked.connect(self.close)
        self.layout.addWidget(self.close_button)

        # Configurando o layout do widget
        self.setLayout(self.layout)

        self.setMinimumSize(500, 300)


class SetUpAPIWindow(QWidget):
    def __init__(self, funcao):
        super().__init__()
        self.funcao = funcao
        self.setWindowTitle("Configuração de API")

        # Configurando o layout principal
        self.layout = QVBoxLayout()

        # Criando os campos de entrada
        self.account_field = QLineEdit()
        self.account_field.setPlaceholderText("Conta")
        self.layout.addWidget(self.account_field)

        self.api_file_button = QPushButton("Selecione o arquivo de API")
        self.api_file_button.setObjectName("ApiFileButton")
        self.api_file_button.clicked.connect(self.select_api_file)
        self.api_file_label = QLabel("Nenhum arquivo selecionado")
        self.layout.addWidget(self.api_file_button)
        self.layout.addWidget(self.api_file_label)

        # Criar e adicionar o QComboBox para satélites
        self.satellite_field = QComboBox()
        self.satellite_field.addItems(["CBERS 04A", "Landsat"])
        self.layout.addWidget(self.satellite_field)

        # Criar e adicionar o QComboBox para coleções (inicialmente vazio)
        self.collection_field = QComboBox()
        self.layout.addWidget(self.collection_field)

        # Conectar o sinal de mudança de seleção do QComboBox
        self.satellite_field.currentIndexChanged.connect(self.update_collections)

        # Inicializar as coleções
        self.update_collections()

        self.id_field = QLineEdit()
        self.id_field.setPlaceholderText("ID")
        self.layout.addWidget(self.id_field)

        self.area_of_interest_field = QLineEdit()
        self.area_of_interest_field.setPlaceholderText("Área de interesse")
        self.layout.addWidget(self.area_of_interest_field)

        # Criando o botão de execução
        self.execute_button = QPushButton("Confirmar")
        self.execute_button.setObjectName("ExecuteButton")
        self.execute_button.clicked.connect(self.execute)
        self.layout.addWidget(self.execute_button)

        # Configurando o layout do widget
        self.setLayout(self.layout)

        self.setMinimumSize(500, 300)

    def select_api_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Selecione o arquivo da API:", "", "JSON files (*.json)")

        if file_path:
            self.api_file_label.setText(f"Arquivo selecionado: {file_path}")
        else:
            self.api_file_label.setText("Nenhum arquivo selecionado")


    def execute(self):
        # Chamando a função de API com os parâmetros necessários
        try:
            self.funcao(
                self.account_field.text(),
                self.api_file_label.text().replace("Arquivo selecionado: ", ""),
                self.satellite_field.currentText(),
                self.collection_field.currentText(),
                self.id_field.text(),
                self.area_of_interest_field.text(),
            )
        except Exception as e:
            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Icon.Critical)
            error_message.setWindowTitle("Erro")
            error_message.setText(error_string)
            translated_error = translator.translate(str(e))
            error_message.setInformativeText(translated_error)
            error_message.setStandardButtons(QMessageBox.StandardButton.Ok)
            error_message.exec()

    def update_collections(self):
        # Limpar as opções atuais
        self.collection_field.clear()

        if self.satellite_field.currentText() == "Landsat":
            self.collection_field.addItems(["C01", "C02"])