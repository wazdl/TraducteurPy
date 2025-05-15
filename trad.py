# trad.py
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox, QDialog
from PyQt6.QtGui import QCursor
import time
from transformers import MarianMTModel, MarianTokenizer, MT5ForConditionalGeneration, MT5Tokenizer
from googletrans import Translator # Commented out googletrans
from PyQt6.QtCore import QThread, pyqtSignal, QSettings, pyqtSlot
from gtts import gTTS
import pygame  # Import pygame
import os
import re
from langdetect import detect, DetectorFactory
import langdetect

# Fixe le comportement pour avoir un résultat reproductible
DetectorFactory.seed = 0  

# Initialiser pygame au démarrage
pygame.init()
pygame.mixer.init()

# Importez la fonction de configuration de l'interface et le fichier de configuration
from gui_config import setup_ui, get_stylesheet, SettingsDialog
import config

class ModelLoaderThread(QThread):
    """Thread pour charger les modèles en arrière-plan."""
    finished = pyqtSignal(float)  # Signal pour indiquer la fin du chargement et envoyer le temps

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def run(self):
        """Charge les modèles et émet des signaux de progression."""
        debut = time.time()
        try:
            # Charger les modèles et les tokenizers
            self.parent.modeles = {
                "Français-Anglais": ("Helsinki-NLP/opus-mt-fr-en", MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-fr-en"), MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-fr-en")),
                "Français-Espagnol": ("Helsinki-NLP/opus-mt-fr-es", MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-fr-es"), MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-fr-es")),
                "Français-Allemand": ("Helsinki-NLP/opus-mt-fr-de", MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-fr-de"), MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-fr-de")),
                "Français-Turc": ("google/mt5-base", MT5ForConditionalGeneration.from_pretrained("google/mt5-base"), MT5Tokenizer.from_pretrained("google/mt5-base")),  # Utiliser MT5Tokenizer
                "Anglais-Français": ("Helsinki-NLP/opus-mt-en-fr", MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-fr"), MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-fr")),
                "Anglais-Espagnol": ("Helsinki-NLP/opus-mt-en-es", MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-es"), MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-es")),
                "Anglais-Allemand": ("Helsinki-NLP/opus-mt-en-de", MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-de"), MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-de")),
                "Anglais-Turc": ("google/mt5-base", MT5ForConditionalGeneration.from_pretrained("google/mt5-base"), MT5Tokenizer.from_pretrained("google/mt5-base")),  # Utiliser MT5Tokenizer
                "Espagnol-Français": ("Helsinki-NLP/opus-mt-es-fr", MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-es-fr"), MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-es-fr")),
                "Espagnol-Anglais": ("Helsinki-NLP/opus-mt-es-en", MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-es-en"), MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-es-en")),
                "Espagnol-Allemand": ("Helsinki-NLP/opus-mt-es-de", MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-es-de"), MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-es-de")),
                "Espagnol-Turc": ("google/mt5-base", MT5ForConditionalGeneration.from_pretrained("google/mt5-base"), MT5Tokenizer.from_pretrained("google/mt5-base")),  # Utiliser MT5Tokenizer
                "Allemand-Français": ("Helsinki-NLP/opus-mt-de-fr", MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-de-fr"), MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-de-fr")),
                "Allemand-Anglais": ("Helsinki-NLP/opus-mt-de-en", MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-de-en"), MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-de-en")),
                "Allemand-Espagnol": ("Helsinki-NLP/opus-mt-de-es", MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-de-es"), MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-de-es")),
                "Allemand-Turc": ("google/mt5-base", MT5ForConditionalGeneration.from_pretrained("google/mt5-base"), MT5Tokenizer.from_pretrained("google/mt5-base")),  # Utiliser MT5Tokenizer
                "Turc-Français": ("google/mt5-base", MT5ForConditionalGeneration.from_pretrained("google/mt5-base"), MT5Tokenizer.from_pretrained("google/mt5-base")),  # Utiliser MT5Tokenizer
                "Turc-Anglais": ("google/mt5-base", MT5ForConditionalGeneration.from_pretrained("google/mt5-base"), MT5Tokenizer.from_pretrained("google/mt5-base")),  # Utiliser MT5Tokenizer
                "Turc-Espagnol": ("google/mt5-base", MT5ForConditionalGeneration.from_pretrained("google/mt5-base"), MT5Tokenizer.from_pretrained("google/mt5-base")),  # Utiliser MT5Tokenizer
                "Turc-Allemand": ("google/mt5-base", MT5ForConditionalGeneration.from_pretrained("google/mt5-base"), MT5Tokenizer.from_pretrained("google/mt5-base")),  # Utiliser MT5Tokenizer
            }
        except Exception as e:
            QMessageBox.critical(self.parent, "Erreur de Chargement", f"Erreur lors du chargement des modèles : {e}")
            return

        fin = time.time()
        temps_chargement = fin - debut
        self.finished.emit(temps_chargement)  # Émettre le signal de fin avec le temps

class Traducteur(QWidget):
    def __init__(self):
        super().__init__()

        # Configuration initiale de l'UI (rapide)
        self.theme_sombre = config.THEME_SOMBRE_DEFAUT  # Initialisez le thème avant setup_ui

        # Utiliser les langues du fichier de configuration
        self.langues = config.LANGUES
        self.langue_codes = config.LANGUES

        # Initialisation des zones de texte
        self.entry_text = None
        self.entry_traduit = None

        # Initialisation des ComboBox
        self.langue_source_var = None
        self.langue_destination_var = None

        # Initialisation des boutons
        self.bouton_traduire = None
        self.bouton_lire = None  # Initialiser le bouton ici
        
        # Ajout d'une liste pour stocker les phrases
        self.phrases = []

        # État de la lecture
        self.is_playing = False
        self.lecture_en_cours = False
        self.lecture_thread = None
        self.fichiers_audio = [] # Stocke les fichiers audio

        # Récupérer la taille de la police depuis QSettings
        self.settings = QSettings("TraducteurApp", "Settings")
        self.font_size = self.settings.value("font_size", 12, type=int)
        self.selected_theme = self.settings.value("theme", "Sombre", type=str)

        #Setup de l'UI
        setup_ui(self, self)  # Passez 'self' à setup_ui

        # Initialisation du thème (sombre par défaut)
        self.apply_theme(self.selected_theme)

        # Désactiver le bouton de traduction avant le chargement des modèles
        if self.bouton_traduire:  # Vérifiez si le bouton est initialisé
            self.bouton_traduire.setEnabled(False)

        # Désactiver le bouton de lecture avant que la traduction soit disponible
        if self.bouton_lire:
            self.bouton_lire.setEnabled(False)

        # Initialiser les modèles dans un thread séparé
        self.model_loader_thread = ModelLoaderThread(self)  # Créer une instance du thread
        self.model_loader_thread.finished.connect(self.on_models_loaded)  # Connecter le signal de fin
        self.model_loader_thread.start()  # Démarrer le thread

        # Appliquer la taille de la police initiale aux zones de texte
        self.apply_font_size(self.font_size)

        """ self.entry_text.textChanged.connect(self.detecter_langue)  # Détection continue pendant l'écriture
        self.langue_source_var.currentIndexChanged.connect(self.detecter_langue)  # Redétection si "Détection automatique" est activée """

        self.show()  # Afficher la fenêtre après la configuration initiale

    def apply_theme(self, theme):
        """Applique le thème sélectionné."""
        if theme == "Clair":
            self.theme_sombre = False
        elif theme == "Sombre":
            self.theme_sombre = True
        else:
            self.theme_sombre = False  # Pour les thèmes personnalisés, on part du thème clair

        self.setStyleSheet(get_stylesheet(self, self.theme_sombre, theme)) # Applique le thème de base (clair ou sombre)

    """ def detecter_langue(self):
        texte = self.entry_text.toPlainText().strip()

        if not self.langue_source_var.currentText().startswith("Détection automatique"):
            return  # Ne détecte que si l'option "Détection automatique" est activée

        if not texte:  
            self.langue_source_var.setItemText(0, "Détection automatique : ")
            return  

        try:
            langue_code = detect(texte)  # Détecte la langue

            if langue_code in config.LANGUES:  
                langue_detectee = config.LANGUES[langue_code]
            else:
                langue_detectee = "Inconnue"

            texte_combo = f"Détection automatique : {langue_detectee}"

            if self.langue_source_var.itemText(0) != texte_combo:
                self.langue_source_var.setItemText(0, texte_combo)

        except langdetect.lang_detect_exception.LangDetectException:
            self.langue_source_var.setItemText(0, "Détection automatique : ") """

    def apply_font_size(self, font_size):
        """Applique la taille de police aux zones de texte."""
        if self.entry_text:
            self.entry_text.setStyleSheet(f"font-size: {font_size}pt;")
        if self.entry_traduit:
            self.entry_traduit.setStyleSheet(f"font-size: {font_size}pt;")

    def on_models_loaded(self, temps_chargement):
        """Activer le bouton de traduction une fois les modèles chargés et afficher le temps."""
        self.chargement_termine = True
        if self.bouton_traduire:  # Vérifiez si le bouton est initialisé
            self.bouton_traduire.setEnabled(True)
        QMessageBox.information(self, "Chargement Terminé", "Les modèles ont été chargés avec succès.")
        print(f"Temps de chargement des modèles: {temps_chargement:.2f} secondes")  # Afficher le temps

    def traduire_texte_en_turc_googletrans(self, texte, langue_source):
        translator = Translator()
        # Utiliser le mappage pour obtenir le code de langue valide
        code_langue_source = list(self.langues.keys())[list(self.langues.values()).index(langue_source)]
        try:
            traduction = translator.translate(texte, src=code_langue_source, dest='tr')
            return traduction.text
        except Exception as e:
            QMessageBox.warning(self, "Erreur Traduction", f"Erreur googletrans: {e}")
            return ""

    def traduire_texte_de_turc_googletrans(self, texte, langue_destination):
        translator = Translator()
        # Utiliser le mappage pour obtenir le code de langue valide
        code_langue_destination = list(self.langues.keys())[list(self.langues.values()).index(langue_destination)]
        try:
            traduction = translator.translate(texte, src='tr', dest=code_langue_destination)
            return traduction.text
        except Exception as e:
            QMessageBox.warning(self, "Erreur Traduction", f"Erreur googletrans: {e}")
            return ""

    """ def traduire_texte(self):
        if not self.chargement_termine:
            QMessageBox.information(self, "Chargement en Cours", "Les modèles sont encore en cours de chargement. Veuillez patienter.")
            return

        texte_a_traduire = self.entry_text.toPlainText()
        langue_source = self.langue_source_var.currentText()
        langue_destination = self.langue_destination_var.currentText()

        # Vérifier si les langues source et destination sont identiques
        if langue_source == langue_destination:
            QMessageBox.warning(self, "Erreur de Traduction", "La langue source et la langue de destination sont identiques. Veuillez sélectionner des langues différentes.")
            self.entry_traduit.clear()
            return

        try:
            # Diviser le texte en phrases
            phrases = re.split(r'(?<=[.!?]) +', texte_a_traduire)

            # Traduire chaque phrase
            traductions = []
            for phrase in phrases:
                if phrase:  # Vérifier si la phrase n'est pas vide
                    # Déterminer le modèle à utiliser en fonction des langues source et destination
                    model_name = None
                    model = None
                    # tokenizer = None

                    if langue_source == "Français" and langue_destination == "Anglais":
                        model_name = "Français-Anglais"
                    elif langue_source == "Anglais" and langue_destination == "Français":
                        model_name = "Anglais-Français"
                    elif langue_source == "Français" and langue_destination == "Espagnol":
                        model_name = "Français-Espagnol"
                    elif langue_source == "Espagnol" and langue_destination == "Français":
                        model_name = "Espagnol-Français"
                    elif langue_source == "Anglais" and langue_destination == "Espagnol":
                        model_name = "Anglais-Espagnol"
                    elif langue_source == "Espagnol" and langue_destination == "Anglais":
                        model_name = "Espagnol-Anglais"
                    elif langue_source == "Allemand" and langue_destination == "Français":
                        model_name = "Allemand-Français"
                    elif langue_source == "Français" and langue_destination == "Allemand":
                        model_name = "Français-Allemand"
                    elif langue_source == "Allemand" and langue_destination == "Anglais":
                        model_name = "Allemand-Anglais"
                    elif langue_source == "Anglais" and langue_destination == "Allemand":
                        model_name = "Anglais-Allemand"
                    elif langue_source == "Allemand" and langue_destination == "Espagnol":
                        model_name = "Allemand-Espagnol"
                    elif langue_source == "Espagnol" and langue_destination == "Allemand":
                        model_name = "Espagnol-Allemand"
                    #Translations avec googletrans
                    elif langue_source == "Turc" and langue_destination == "Français":
                        traduction = self.traduire_texte_de_turc_googletrans(phrase, langue_destination)
                    elif langue_source == "Turc" and langue_destination == "Anglais":
                        traduction = self.traduire_texte_de_turc_googletrans(phrase, langue_destination)
                    elif langue_source == "Turc" and langue_destination == "Espagnol":
                        traduction = self.traduire_texte_de_turc_googletrans(phrase, langue_destination)
                    elif langue_source == "Turc" and langue_destination == "Allemand":
                        traduction = self.traduire_texte_de_turc_googletrans(phrase, langue_destination)
                    elif langue_source == "Français" and langue_destination == "Turc":
                        traduction = self.traduire_texte_en_turc_googletrans(phrase, langue_source)
                    elif langue_source == "Anglais" and langue_destination == "Turc":
                        traduction = self.traduire_texte_en_turc_googletrans(phrase, langue_source)
                    elif langue_source == "Espagnol" and langue_destination == "Turc":
                        traduction = self.traduire_texte_en_turc_googletrans(phrase, langue_source)
                    elif langue_source == "Allemand" and langue_destination == "Turc":
                        traduction = self.traduire_texte_en_turc_googletrans(phrase, langue_source)
                    else:
                        traduction = phrase  # Par défaut, ne pas traduire

                    # Si un modèle est trouvé, effectuer la traduction avec le modèle
                    if model_name:
                        model_name, model, tokenizer = self.modeles[model_name]
                        inputs = tokenizer(phrase, return_tensors="pt")
                        outputs = model.generate(**inputs)
                        traduction = tokenizer.decode(outputs[0], skip_special_tokens=True)

                    traductions.append(traduction)
                    
            # Combiner les traductions
            texte_traduit_complet = " ".join(traductions).replace(" . ", ". ").replace(" ? ", "? ").replace(" ! ", "! ")

            self.entry_traduit.setText(texte_traduit_complet)

            # Activer le bouton lire
            if self.bouton_lire:
                self.bouton_lire.setEnabled(True)
        except Exception as e:
            QMessageBox.warning(self, "Erreur Traduction", f"Erreur lors de la traduction : {e}")
        return """
    
    def traduire_texte(self):
        if not self.chargement_termine:
            QMessageBox.information(self, "Chargement en Cours", "Les modèles sont encore en cours de chargement. Veuillez patienter.")
            return

        texte_a_traduire = self.entry_text.toPlainText()
        langue_source = self.langue_source_var.currentText()
        langue_destination = self.langue_destination_var.currentText()

        if langue_source == langue_destination:
            QMessageBox.warning(self, "Erreur de Traduction", "La langue source et la langue de destination sont identiques. Veuillez sélectionner des langues différentes.")
            self.entry_traduit.clear()
            return

        try:
            phrases = re.split(r'(?<=[.!?]) +', texte_a_traduire)
            traductions = []

            for phrase in phrases:
                if phrase:
                    model_name = None
                    traduction = None

                    if langue_source == "Turc":
                        if langue_destination == "Français":
                            traduction = self.traduire_texte_de_turc_googletrans(phrase, langue_destination)
                        elif langue_destination == "Anglais":
                            traduction = self.traduire_texte_de_turc_googletrans(phrase, langue_destination)
                        elif langue_destination == "Espagnol":
                            traduction = self.traduire_texte_de_turc_googletrans(phrase, langue_destination)
                        elif langue_destination == "Allemand":
                            traduction = self.traduire_texte_de_turc_googletrans(phrase, langue_destination)
                    elif langue_destination == "Turc":
                        if langue_source == "Français":
                            traduction = self.traduire_texte_en_turc_googletrans(phrase, langue_source)
                        elif langue_source == "Anglais":
                            traduction = self.traduire_texte_en_turc_googletrans(phrase, langue_source)
                        elif langue_source == "Espagnol":
                            traduction = self.traduire_texte_en_turc_googletrans(phrase, langue_source)
                        elif langue_source == "Allemand":
                            traduction = self.traduire_texte_en_turc_googletrans(phrase, langue_source)
                    else:
                        # Traduction avec les modèles préchargés pour les autres langues
                        if langue_source == "Français" and langue_destination == "Anglais":
                            model_name = "Français-Anglais"
                        elif langue_source == "Anglais" and langue_destination == "Français":
                            model_name = "Anglais-Français"
                        elif langue_source == "Français" and langue_destination == "Espagnol":
                            model_name = "Français-Espagnol"
                        elif langue_source == "Espagnol" and langue_destination == "Français":
                            model_name = "Espagnol-Français"
                        elif langue_source == "Anglais" and langue_destination == "Espagnol":
                            model_name = "Anglais-Espagnol"
                        elif langue_source == "Espagnol" and langue_destination == "Anglais":
                            model_name = "Espagnol-Anglais"
                        elif langue_source == "Allemand" and langue_destination == "Français":
                            model_name = "Allemand-Français"
                        elif langue_source == "Français" and langue_destination == "Allemand":
                            model_name = "Français-Allemand"
                        elif langue_source == "Allemand" and langue_destination == "Anglais":
                            model_name = "Allemand-Anglais"
                        elif langue_source == "Anglais" and langue_destination == "Allemand":
                            model_name = "Anglais-Allemand"
                        elif langue_source == "Allemand" and langue_destination == "Espagnol":
                            model_name = "Allemand-Espagnol"
                        elif langue_source == "Espagnol" and langue_destination == "Allemand":
                            model_name = "Espagnol-Allemand"
                        else:
                            traduction = phrase  # Par défaut, ne pas traduire... # Si un modèle est trouvé, effectuer la traduction avec le modèle
                    
                    if model_name:
                        model_name, model, tokenizer = self.modeles[model_name]
                        try:
                            inputs = tokenizer(phrase, return_tensors="pt", padding=True, truncation=True, max_length=512)
                            outputs = model.generate(**inputs, max_length=512)
                            traduction = tokenizer.decode(outputs[0], skip_special_tokens=True)
                        except Exception as token_err:
                            print(f"Erreur de tokenisation : {token_err}")
                            traduction = phrase  # Use original phrase if translation fails

                        # Post-traitement spécifique pour améliorer la fluidité
                        if traduction:
                            corrections = {}
                            if langue_source == "Anglais" and langue_destination == "Français":
                                corrections = {
                                    r'\bà lire\b': 'pour lire',  # Corrige "à lire"
                                    r'\bde Python\b': 'Python',   # Simplifie "de Python"
                                    r'\bim\b': 'Je suis'       # Forme correcte
                                }
                            elif langue_source == "Français" and langue_destination == "Anglais":
                                corrections = {
                                    r'\bJe suis\b': 'I\'m',
                                    r'\btraducteur\b': 'translator',
                                    r'\bpour lire\b': 'to read'
                                }
                            for pattern, replacement in corrections.items():
                                traduction = re.sub(pattern, replacement, traduction, flags=re.IGNORECASE)

                    if traduction:
                        traductions.append(traduction)
                    else:
                        traductions.append(phrase)

            texte_traduit_complet = " ".join(traductions).replace(" . ", ". ").replace(" ? ", " ? ").replace(" ! ", " ! ")
            self.entry_traduit.setText(texte_traduit_complet)

            if self.bouton_lire:
                self.bouton_lire.setEnabled(True)

        except Exception as e:
            QMessageBox.warning(self, "Erreur Traduction", f"Erreur lors de la traduction : {e}")
        return

    def lire_texte_traduit(self):
        texte_traduit = self.entry_traduit.toPlainText()
        langue_destination = self.langue_destination_var.currentText()

        # Choisir le code de langue approprié pour gTTS
        if langue_destination == "Français":
            langue_code = 'fr'
        elif langue_destination == "Anglais":
            langue_code = 'en'
        elif langue_destination == "Espagnol":
            langue_code = 'es'
        elif langue_destination == "Allemand":
            langue_code = 'de'
        elif langue_destination == "Turc":
            langue_code = 'tr'
        else:
            QMessageBox.warning(self, "Erreur de Lecture", "Langue non supportée pour la lecture.")
            return

        try:
            # Arrêter toute lecture en cours avant d'en démarrer une nouvelle
            self.arreter_lecture()

            # Diviser le texte en phrases
            phrases = re.split(r'(?<=[.!?]) +', texte_traduit)
            self.phrases = phrases  # Stocker les phrases

            # Générer les fichiers audio
            fichiers_audio = []
            for i, phrase in enumerate(phrases):
                filename = f"traduction_{i}.mp3"
                tts = gTTS(text=phrase, lang=langue_code, slow=False)
                tts.save(filename)
                fichiers_audio.append(filename)

            # Définir les fichiers audio pour la classe entière
            self.fichiers_audio = fichiers_audio

            if not self.is_playing:
                self.is_playing = True
                self.bouton_lire.setText("Arrêter")
                self.lecture_en_cours = True

                # Lire les fichiers audio en série dans un thread
                self.lecture_thread = LectureThread(self, self.fichiers_audio)
                self.lecture_thread.finished.connect(self.fin_lecture)
                self.lecture_thread.start()
            else:
                # Arrêter la lecture en cours si elle est déjà en cours
                if self.lecture_thread is not None:
                    self.lecture_thread.stop()
                    self.lecture_thread.wait()

                self.is_playing = False
                self.bouton_lire.setText("Lire")
                self.lecture_en_cours = False

        except Exception as e:
            QMessageBox.warning(self, "Erreur de Lecture", f"Erreur lors de la lecture : {e}")


    @pyqtSlot()
    def fin_lecture(self):
        """Mets à jour l'état de la lecture et supprime les fichiers après la fin de la lecture."""
        self.is_playing = False
        self.bouton_lire.setText("Lire")
        self.lecture_en_cours = False

        # Initialiser pygame.mixer
        pygame.mixer.init()

        # Suppression des fichiers audio
        for filename in self.fichiers_audio:
            try:
                pygame.mixer.music.stop()
                time.sleep(0.1)
                os.remove(filename)
            except Exception as e:
                print(f"Erreur lors de la suppression du fichier {filename}: {e}")

        # Arrêter toute lecture en cours et décharger les ressources
        pygame.mixer.quit()

        # Vider la liste des fichiers audio et réinitialiser le thread
        self.fichiers_audio = []
        self.lecture_thread = None

    def arreter_lecture(self):
        """Arrête la lecture audio et libère les ressources."""
        if self.lecture_en_cours:
            try:
                # Arrêter la lecture en cours et décharger les ressources
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()

                self.lecture_en_cours = False

                self.fichiers_audio.clear()

            except Exception as e:
                QMessageBox.warning(self, "Erreur Arrêt", f"Erreur lors de l'arrêt: {e}")

    def open_settings(self):
        dialog = SettingsDialog(self)

        # Obtenir l'écran où se trouve la souris à ce moment
        screen = QApplication.screenAt(QCursor.pos())
        if screen is None:
            screen = QApplication.primaryScreen()

        # Obtenir la géométrie de l'écran
        if screen:
            screen_geometry = screen.geometry()
            dialog_geometry = dialog.geometry()

            x = (screen_geometry.width() - dialog_geometry.width()) // 2 + screen_geometry.x()
            y = (screen_geometry.height() - dialog_geometry.height()) // 2 + screen_geometry.y()
            dialog.move(x, y)

        dialog.font_size_spinbox.setValue(self.font_size)
        dialog.theme_combo.setCurrentText(self.selected_theme)
        result = dialog.exec()

        if result == QDialog.DialogCode.Accepted:
            self.font_size = dialog.font_size_spinbox.value()
            self.selected_theme = dialog.theme_combo.currentText()
            self.settings.setValue("font_size", self.font_size)
            self.settings.setValue("theme", self.selected_theme)
            self.apply_font_size(self.font_size)
            self.apply_theme(self.selected_theme)

# Définition de la classe LectureThread
class LectureThread(QThread):
    finished = pyqtSignal()

    def __init__(self, parent, fichiers_audio):
        super().__init__(parent)
        self.parent = parent
        self.fichiers_audio = fichiers_audio
        self.is_stopped = False

    def run(self):
        try:
            # Initialiser pygame.mixer au début du thread
            pygame.mixer.init()

            for filename in self.fichiers_audio:
                if self.is_stopped:  # Si l'utilisateur a cliqué sur "Arrêter", quittez la boucle
                    break

                try:
                    pygame.mixer.music.load(filename)
                    pygame.mixer.music.play()

                    # Attendre la fin de la lecture audio
                    while pygame.mixer.music.get_busy():
                        if self.is_stopped:
                            pygame.mixer.music.stop()
                            break
                        time.sleep(0.1)
                except pygame.error as e:
                    print(f"Erreur lors de la lecture du fichier {filename}: {e}")
                    break # Sortir de la boucle si une erreur se produit

                pygame.mixer.music.stop()  # Arrêter la musique
                pygame.mixer.music.unload()  # Décharger le fichier
        except Exception as e:
            print(f"Erreur dans le thread de lecture: {e}")
        finally:
            # S'assurer que Pygame Mixer est quitté à la fin du thread
            pygame.mixer.quit()
            self.finished.emit()  # Émition signal de fin

    def stop(self):
        """Arrête le thread de lecture."""
        self.is_stopped = True  # flag arrêt thread propre
        pygame.mixer.music.stop()  # Stopper immédiatement la musique en cours
        pygame.mixer.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    traducteur = Traducteur()
    sys.exit(app.exec())