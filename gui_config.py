#gui_config.py
from PyQt6.QtWidgets import QVBoxLayout, QTextEdit, QComboBox, QPushButton, QMenu, QMenuBar, QSpinBox, QDialog, QFormLayout, QLabel, QHBoxLayout
from PyQt6.QtGui import QIcon, QCursor
import config
from PyQt6.QtCore import QSettings, QPoint
from PyQt6.QtWidgets import QApplication

def get_stylesheet(cls, theme_sombre=False, theme=None):
    """Charge la feuille de style en fonction du thème."""
    # Dictionnaire des thèmes
    themes = {
        "Sombre": {
            "BACKGROUND_COLOR": "#2E2E2E",
            "TEXT_COLOR": "white",
            "TEXTEDIT_BACKGROUND": "#3A3A3A",
            "BUTTON_BACKGROUND": "#444444",
            "BUTTON_HOVER": "#555555"
        },
        "Clair": {
            "BACKGROUND_COLOR": "#FFFFFF",
            "TEXT_COLOR": "black",
            "TEXTEDIT_BACKGROUND": "#F5F5F5",
            "BUTTON_BACKGROUND": "#DDDDDD",
            "BUTTON_HOVER": "#CCCCCC"
        },
        "Bleu": {
            "BACKGROUND_COLOR": "#ADD8E6",
            "TEXT_COLOR": "#00008B",
            "TEXTEDIT_BACKGROUND": "#B0E2FF",
            "BUTTON_BACKGROUND": "#87CEFA",
            "BUTTON_HOVER": "#6495ED"
        },
         "Vert": {
            "BACKGROUND_COLOR": "#90EE90",
            "TEXT_COLOR": "#006400",
            "TEXTEDIT_BACKGROUND": "#98FB98",
            "BUTTON_BACKGROUND": "#3CB371",
            "BUTTON_HOVER": "#2E8B57"
        }
    }

    with open("style.css", "r") as f:
        style = f.read()

    # Remplacer les couleurs en fonction du thème
    if theme in themes:
        selected_theme = themes[theme]
    elif theme_sombre:
        selected_theme = themes["Clair"]
    else:
        selected_theme = themes["Sombre"]

    style = style.replace("BACKGROUND_COLOR", selected_theme["BACKGROUND_COLOR"])
    style = style.replace("TEXT_COLOR", selected_theme["TEXT_COLOR"])
    style = style.replace("TEXTEDIT_BACKGROUND", selected_theme["TEXTEDIT_BACKGROUND"])
    style = style.replace("BUTTON_BACKGROUND", selected_theme["BUTTON_BACKGROUND"])
    style = style.replace("BUTTON_HOVER", selected_theme["BUTTON_HOVER"])

    return style

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Paramètres")
        self.setGeometry(100, 100, 400, 200)

        # Obtenir l'écran où se trouve la souris à ce moment
        screen = QApplication.screenAt(QCursor.pos())
        if screen is None:
            screen = QApplication.primaryScreen()

        # Centrer la fenêtre sur l'écran actuel
        if screen:
            screen_geometry = screen.geometry()
            window_geometry = self.geometry()
            x = (screen_geometry.width() - window_geometry.width()) // 2 + screen_geometry.x()
            y = (screen_geometry.height() - window_geometry.height()) // 2 + screen_geometry.y()
            self.move(x, y)

        layout = QFormLayout(self)

        # Font Size Settings
        self.font_size_label = QLabel("Taille de la police :")
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(8, 24)

        # Theme Selection
        self.theme_label = QLabel("Sélection du thème:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Sombre", "Clair", "Bleu", "Vert"])

        # Load settings
        settings = QSettings("TraducteurApp", "Settings")
        default_font_size = settings.value("font_size", 12, type=int)
        self.font_size_spinbox.setValue(default_font_size)

        default_theme = settings.value("theme", "Sombre", type=str)
        self.theme_combo.setCurrentText(default_theme)

        layout.addRow(self.font_size_label, self.font_size_spinbox)
        layout.addRow(self.theme_label, self.theme_combo)

        # Create Save and Cancel buttons
        self.save_button = QPushButton("Sauvegarder")
        self.cancel_button = QPushButton("Annuler")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        # Add buttons to the layout
        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)

        layout.addRow(buttons_layout)

        self.setLayout(layout)


def setup_ui(self, traducteur_instance):
    """Configure l'interface utilisateur."""
    self.setWindowTitle(config.TITRE_FENETRE)
    self.setWindowIcon(QIcon(config.ICONE_FENETRE))

   # Get the screen where the mouse is currently located
    # Get the screen where the mouse is currently located
    mouse_position = QPoint(0,0)  # Initialise à (0, 0) par défaut

    # Obtient la position globale de la souris (fonctionne uniquement si l'application est active)
    global_pos = QCursor.pos()
    screen = QApplication.screenAt(global_pos)

    # If there's no screen at the mouse position, fallback to the primary screen
    if screen is None:
        screen = QApplication.primaryScreen()

    screen_geometry = screen.geometry()
    # Définir la géométrie de la fenêtre par rapport à l'écran principal
    window_width, window_height = 800, 400  # Largeur et hauteur souhaitées de la fenêtre
    x = (screen_geometry.width() - window_width) // 2 + screen_geometry.x()
    y = (screen_geometry.height() - window_height) // 2 + screen_geometry.y()
    self.setGeometry(x, y, window_width, window_height)  # x, y, largeur, hauteur

    layout = QVBoxLayout()

    # Menu Bar
    menu_bar = QMenuBar()
    settings_menu = QMenu("Paramètres", self)

    # Settings Action
    settings_action = settings_menu.addAction("Ouvrir les paramètres")
    settings_action.triggered.connect(traducteur_instance.open_settings)

    menu_bar.addMenu(settings_menu)
    layout.setMenuBar(menu_bar)

    # Zone de texte pour l'entrée
    self.entry_text = QTextEdit()
    layout.addWidget(self.entry_text)

    # Layout horizontal pour les ComboBox des langues
    langues_layout = QHBoxLayout()

    # Liste déroulante pour la langue source
    # self.langues_source = ["Détection automatique"] + list(config.LANGUES.values())
    self.langues_source = list(config.LANGUES.values())
    self.langue_source_var = QComboBox()
    self.langue_source_var.addItems(self.langues_source)
    langues_layout.addWidget(self.langue_source_var)

    # Liste déroulante pour la langue de destination
    self.langues_destination = list(config.LANGUES.values())
    self.langue_destination_var = QComboBox()
    self.langue_destination_var.addItems(self.langues_destination)
    langues_layout.addWidget(self.langue_destination_var)

    # Ajouter le layout des langues au layout principal
    layout.addLayout(langues_layout)

    # Layout horizontal pour les boutons
    boutons_layout = QHBoxLayout()

    # Bouton de traduction
    self.bouton_traduire = QPushButton(QIcon(config.ICONE_TRADUIRE), "Traduire")
    self.bouton_traduire.clicked.connect(traducteur_instance.traduire_texte)
    self.bouton_traduire.setEnabled(False)
    boutons_layout.addWidget(self.bouton_traduire)

    # Bouton Lire
    self.bouton_lire = QPushButton("Lire")
    self.bouton_lire.clicked.connect(traducteur_instance.lire_texte_traduit)
    self.bouton_lire.setEnabled(False)  # Désactiver initialement
    boutons_layout.addWidget(self.bouton_lire)

    # Ajouter le layout des boutons au layout principal
    layout.addLayout(boutons_layout)

    # Zone de texte pour la traduction
    self.entry_traduit = QTextEdit()
    self.entry_traduit.setReadOnly(True) # Lecture seule
    layout.addWidget(self.entry_traduit)

    self.setLayout(layout)

     # Stockez les références aux widgets DANS l'instance Traducteur
    traducteur_instance.entry_text = self.entry_text
    traducteur_instance.entry_traduit = self.entry_traduit
    traducteur_instance.langue_source_var = self.langue_source_var
    traducteur_instance.langue_destination_var = self.langue_destination_var
    traducteur_instance.bouton_traduire = self.bouton_traduire
    traducteur_instance.bouton_lire = self.bouton_lire  # Stocker la référence du bouton lire