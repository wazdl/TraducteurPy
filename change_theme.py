# change_theme.py

def get_theme(theme_sombre=False):
    """
    Fonction pour obtenir la feuille de style en fonction du thème.
    :param theme_sombre: Si True, applique le thème sombre, sinon applique le thème clair.
    :return: La feuille de style correspondante au thème.
    """
    if theme_sombre:
        return """
            QWidget {
                background-color: #2E2E2E;
                color: white;
            }
            QTextEdit {
                background-color: #3A3A3A;
                color: white;
            }
            QPushButton {
                background-color: #444444;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QComboBox {
                background-color: #444444;
                color: white;
                border-radius: 5px;
            }
        """
    else:
        return """
            QWidget {
                background-color: #FFFFFF;
                color: black;
            }
            QTextEdit {
                background-color: #F5F5F5;
                color: black;
            }
            QPushButton {
                background-color: #DDDDDD;
                color: black;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #CCCCCC;
            }
            QComboBox {
                background-color: #DDDDDD;
                color: black;
                border-radius: 5px;
            }
        """
