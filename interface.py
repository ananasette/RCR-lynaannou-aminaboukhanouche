import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QListWidget, QTextEdit, QGroupBox, QMessageBox,
                               QFileDialog, QInputDialog)
from PySide6.QtGui import QPixmap, QPainter, QCursor, QFont, QFontDatabase, QColor, QPen
from PySide6.QtCore import QTimer, Qt, QPoint, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

# On importe les fonctions du backend de ton binôme
from formulas import lire_formule, afficher_formule
from defaults import Theory, Default
from reasoning import est_coherent, consequence, formules_incoherentes
from extensions import extensions, consequence_credulous, consequence_sceptique
from theoremes import audit, reparations  # <-- Corrigé : theoremes.py
from surprise import est_secret, surprise

class Personnage(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True) # pour le dépôt de fichiers
        self.setFixedSize(400, 200)
        
        self.img_corps = QPixmap("assets/corps.png")
        self.img_yeux = QPixmap("assets/yeux.png")
        self.setAttribute(Qt.WA_TranslucentBackground)
                
        if self.img_corps.isNull():
            self.img_corps = QPixmap(150, 150)
            self.img_corps.fill(Qt.transparent)
        if self.img_yeux.isNull():
            self.img_yeux = QPixmap(40, 20)
            self.img_yeux.fill(Qt.transparent)

        self.pos_souris = QPoint(0, 0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.maj_souris)
        self.timer.start(30)

    def maj_souris(self):
        self.pos_souris = self.mapFromGlobal(QCursor.pos())
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, False)

        x_corps = (self.width() - self.img_corps.width()) // 2
        y_corps = (self.height() - self.img_corps.height()) // 2
        painter.drawPixmap(x_corps, y_corps, self.img_corps)

        dx = self.pos_souris.x() - (x_corps + self.img_corps.width() // 2)
        dy = self.pos_souris.y() - (y_corps + self.img_corps.height() // 3)
        
        max_offset = 6
        offset_x = max(-max_offset, min(max_offset, dx / 15))
        offset_y = max(-max_offset, min(max_offset, dy / 15))

        base_x_yeux = x_corps + (self.img_corps.width() - self.img_yeux.width()) // 2
        base_y_yeux = y_corps + (self.img_corps.height() // 3)

        painter.drawPixmap(int(base_x_yeux + offset_x), int(base_y_yeux + offset_y), self.img_yeux)

class MainWindow(QMainWindow):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#E0F2FE"))
        pen = QPen(QColor("#BAE6FD"))
        pen.setWidth(1)
        painter.setPen(pen)
        for x in range(0, self.width(), 40):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), 40):
            painter.drawLine(0, y, self.width(), y)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logique des Défauts - 90s Edition")
        self.resize(1100, 850)
        
        self.theorie = Theory()

        font_id = QFontDatabase.addApplicationFont("assets/VT323-Regular.ttf")
        if font_id != -1:
            self.setFont(QFont("VT323", 14))
        else:
            self.setFont(QFont("Courier New", 12))

        menu = self.menuBar()
        menu.setStyleSheet("background-color: #c3e9fd; color: #333;")
        menu.addAction("Nouveau", self.nouveau)
        menu.addAction("Ouvrir", self.ouvrir)
        menu.addAction("Enregistrer", self.enregistrer)
        menu.addAction("Exemples", self.charger_exemple)
        menu.addAction("Son ON/OFF", self.toggle_musique)
        menu.addAction("Surprise", self.ouvrir_surprise)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.perso = Personnage()
        main_layout.addWidget(self.perso, alignment=Qt.AlignCenter)

        saisie_layout = QHBoxLayout()
        
        groupe_w = QGroupBox("MONDE W")
        layout_w = QVBoxLayout()
        self.input_formule = QLineEdit()
        self.input_formule.setPlaceholderText("Ex: p -> o, ~v")
        layout_w.addWidget(self.input_formule)
        
        btn_layout_w = QHBoxLayout()
        btn_add_w = QPushButton("Ajouter formule")
        btn_add_w.clicked.connect(self.ajouter_formule)
        btn_del_w = QPushButton("Supprimer")
        btn_del_w.clicked.connect(self.supprimer_formule)
        btn_layout_w.addWidget(btn_add_w)
        btn_layout_w.addWidget(btn_del_w)
        layout_w.addLayout(btn_layout_w)
        
        self.liste_w = QListWidget()
        layout_w.addWidget(self.liste_w)
        groupe_w.setLayout(layout_w)
        
        groupe_d = QGroupBox("DÉFAUTS D")
        layout_d = QVBoxLayout()
        self.input_prerequis = QLineEdit()
        self.input_prerequis.setPlaceholderText("Prérequis")
        self.input_just = QLineEdit()
        self.input_just.setPlaceholderText("Justifications")
        self.input_conseq = QLineEdit()
        self.input_conseq.setPlaceholderText("Conséquent")
        
        layout_d.addWidget(QLabel("Prérequis :"))
        layout_d.addWidget(self.input_prerequis)
        layout_d.addWidget(QLabel("Justifications :"))
        layout_d.addWidget(self.input_just)
        layout_d.addWidget(QLabel("Conséquent :"))
        layout_d.addWidget(self.input_conseq)
        
        btn_layout_d = QHBoxLayout()
        btn_add_d = QPushButton("Ajouter défaut")
        btn_add_d.clicked.connect(self.ajouter_defaut)
        btn_del_d = QPushButton("Supprimer")
        btn_del_d.clicked.connect(self.supprimer_defaut)
        btn_layout_d.addWidget(btn_add_d)
        btn_layout_d.addWidget(btn_del_d)
        layout_d.addLayout(btn_layout_d)
        
        self.liste_d = QListWidget()
        layout_d.addWidget(self.liste_d)
        groupe_d.setLayout(layout_d)

        saisie_layout.addWidget(groupe_w)
        saisie_layout.addWidget(groupe_d)
        main_layout.addLayout(saisie_layout)

        action_layout = QHBoxLayout()
        btn_coherence = QPushButton("Vérifier la cohérence de W")
        btn_coherence.clicked.connect(self.verifier_coherence)
        
        btn_extensions = QPushButton("Générer les extensions")
        btn_extensions.clicked.connect(self.generer_extensions)
        
        btn_sceptique = QPushButton("Sceptique ?")
        btn_sceptique.clicked.connect(self.tester_sceptique)
        
        btn_credule = QPushButton("Crédule ?")
        btn_credule.clicked.connect(self.tester_credule)
        
        # Séparation de l'audit et de la réparation
        btn_audit = QPushButton("Audit des théorèmes")
        btn_audit.clicked.connect(self.lancer_audit)
        
        btn_reparation = QPushButton("Réparations")
        btn_reparation.clicked.connect(self.lancer_reparation)
        
        action_layout.addWidget(btn_coherence)
        action_layout.addWidget(btn_extensions)
        action_layout.addWidget(btn_sceptique)
        action_layout.addWidget(btn_credule)
        action_layout.addWidget(btn_audit)
        action_layout.addWidget(btn_reparation)
        main_layout.addLayout(action_layout)

        self.resultats = QTextEdit()
        self.resultats.setReadOnly(True)
        self.resultats.setObjectName("terminal")
        main_layout.addWidget(self.resultats)

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.setSource(QUrl.fromLocalFile("assets/music.mp3"))
        self.player.setLoops(QMediaPlayer.Infinite)
        self.player.play()

        self.setStyleSheet("""
            QMainWindow { background: transparent; }
            QMenuBar { background-color: rgba(255, 255, 255, 200); border-bottom: 3px solid #F9C6D3; color: #333; }
            QGroupBox { border: 4px solid #c3e9fd; border-radius: 15px; margin-top: 15px; font-weight: bold; background-color: #FFFFFF; color: #333; }
            QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 0 5px 0 5px; color: #F9C6D3; font-size: 18px; }
            QPushButton { background-color: #F9C6D3; border: 3px solid #FFFFFF; border-radius: 8px; padding: 8px; color: #333; font-weight: bold; }
            QPushButton:hover { background-color: #FFD1DC; border: 3px solid #c3e9fd; }
            QPushButton:pressed { background-color: #c3e9fd; }
            QLineEdit, QListWidget { border: 2px solid #D4E9F2; border-radius: 8px; padding: 5px; background-color: #FAFAFA; color: #333; }
            QTextEdit#terminal { background-color: #2D2D2D; color: #00FF00; font-family: "VT323", "Courier New", monospace; font-size: 22px; border: 4px solid #F9C6D3; border-radius: 15px; padding: 10px; }
        """)

    def dragEnterEvent(self, event):
        # Vérifie si ce qu'on glisse est bien un fichier texte
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        # Quand on lâche le fichier
        for url in event.mimeData().urls():
            fichier = url.toLocalFile()
            if fichier.endswith('.txt') or fichier.endswith('.json'):
                self.charger_fichier_par_chemin(fichier)
                break

    def ajouter_formule(self):
        texte = self.input_formule.text().strip()
        if texte:
            try:
                self.theorie.ajouter_fait(texte)
                self.liste_w.addItem(texte)
                self.input_formule.clear()
            except ValueError as e:
                QMessageBox.warning(self, "Erreur de syntaxe", str(e))

    def supprimer_formule(self):
        row = self.liste_w.currentRow()
        if row >= 0:
            self.liste_w.takeItem(row)
            del self.theorie.faits[row]
            del self.theorie._src_faits[row]

    def ajouter_defaut(self):
        p = self.input_prerequis.text().strip()
        j = self.input_just.text().strip()
        c = self.input_conseq.text().strip()
        texte_defaut = f"{p} : {j} / {c}"
        
        try:
            avertissements = self.theorie.ajouter_defaut(texte_defaut)
            self.liste_d.addItem(texte_defaut)
            self.input_prerequis.clear()
            self.input_just.clear()
            self.input_conseq.clear()
            if avertissements:
                QMessageBox.warning(self, "Avertissement", "\n".join(avertissements))
                for a in avertissements:
                    self.resultats.append(f"> ATTENTION : {a}")
                self.resultats.append("")
        except ValueError as e:
            QMessageBox.warning(self, "Erreur de syntaxe", str(e))

    def supprimer_defaut(self):
        row = self.liste_d.currentRow()
        if row >= 0:
            self.liste_d.takeItem(row)
            del self.theorie.defauts[row]
            del self.theorie._src_defauts[row]

    def verifier_coherence(self):
        self.resultats.append("> Vérification de la cohérence de W...")
        if est_coherent(self.theorie.faits):
            self.resultats.append("W est cohérent.\n")
        else:
            self.resultats.append("W est incohérent !")
            for f in formules_incoherentes(self.theorie.faits):
                self.resultats.append(f"  Formule contradictoire : {afficher_formule(f)}")
            self.resultats.append("")

    def generer_extensions(self):
        self.resultats.append("> Génération des extensions...")
        try:
            exts = extensions(self.theorie)
            if not exts:
                self.resultats.append("Aucune extension trouvée.\n")
                return
            self.resultats.append(f"{len(exts)} extension(s) trouvée(s) :")
            for i, E in enumerate(exts, 1):
                formules_str = ", ".join(afficher_formule(f) for f in E.base)
                litteraux = ", ".join(afficher_formule(l) for l in E.litteraux()) or "(aucun)"
                self.resultats.append(f"  E{i} = Th({{{formules_str}}})")
                self.resultats.append(f"      littéraux : {litteraux}")
                self.resultats.append(f"      défauts appliqués : {E.noms or '(aucun)'}")
            self.resultats.append("")
        except Exception as e:
            self.resultats.append(f"Erreur lors du calcul : {e}\n")

    def tester_sceptique(self):
        formule, ok = QInputDialog.getText(self, "Test Sceptique", "Entrez la formule phi :")
        if ok and formule.strip():
            try:
                res = consequence_sceptique(self.theorie, lire_formule(formule))
                self.resultats.append(f"> Sceptique ? {formule} : {res}\n")
            except ValueError as e:
                QMessageBox.warning(self, "Erreur", f"Formule invalide : {e}")

    def tester_credule(self):
        formule, ok = QInputDialog.getText(self, "Test Crédule", "Entrez la formule phi :")
        if ok and formule.strip():
            try:
                res = consequence_credulous(self.theorie, lire_formule(formule))
                self.resultats.append(f"> Crédule ? {formule} : {res}\n")
            except ValueError as e:
                QMessageBox.warning(self, "Erreur", f"Formule invalide : {e}")

    def lancer_audit(self):
        self.resultats.append("> Lancement de l'audit de la théorie...")
        try:
            rapport = audit(self.theorie)
            for nom, statut, commentaire in rapport:
                self.resultats.append(f"  [{statut}] {nom}")
                if commentaire:
                    self.resultats.append(f"      -> {commentaire}")
            self.resultats.append("")
        except Exception as e:
            self.resultats.append(f"Erreur lors de l'audit : {e}\n")

    def lancer_reparation(self):
        self.resultats.append("> Recherche de réparations...")
        try:
            reps = reparations(self.theorie)
            if reps:
                self.resultats.append("> Réparations suggérées (supprimer ces défauts) :")
                for r in reps:
                    self.resultats.append(f"  - {', '.join(r)}")
            else:
                self.resultats.append("Aucune réparation nécessaire (la théorie a des extensions).")
            self.resultats.append("")
        except Exception as e:
            self.resultats.append(f"Erreur lors de la réparation : {e}\n")

    def nouveau(self):
        self.theorie = Theory()
        self.liste_w.clear()
        self.liste_d.clear()
        self.resultats.clear()

    def enregistrer(self):
        fichier, _ = QFileDialog.getSaveFileName(self, "Enregistrer la théorie", "", "Fichiers texte (*.txt)")
        if fichier:
            try:
                self.theorie.sauvegarder(fichier)
                self.resultats.append(f"> Théorie sauvegardée dans {fichier}\n")
            except Exception as e:
                QMessageBox.warning(self, "Erreur", f"Impossible de sauvegarder : {e}")

    def ouvrir(self):
        # La fenêtre classique de sélection de fichier
        fichier, _ = QFileDialog.getOpenFileName(self, "Ouvrir une théorie", "", "Fichiers texte (*.txt)")
        if fichier:
            self.charger_fichier_par_chemin(fichier)

    def charger_fichier_par_chemin(self, fichier):
        # Cette fonction fait le vrai travail de chargement
        try:
            self.theorie = Theory.charger(fichier)
            self.nouveau()
            self.theorie = Theory.charger(fichier)
            
            for f in self.theorie._src_faits:
                self.liste_w.addItem(f)
            for d in self.theorie._src_defauts:
                self.liste_d.addItem(d)
                
            self.resultats.append(f"> Théorie chargée depuis {fichier}\n")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger : {e}")

    def charger_exemple(self):
        self.nouveau()
        try:
            self.theorie.ajouter_fait("oiseau(tweety)")
            self.theorie.ajouter_defaut("oiseau(tweety) : vole(tweety) / vole(tweety)")
            self.liste_w.addItem("oiseau(tweety)")
            self.liste_d.addItem("oiseau(tweety) : vole(tweety) / vole(tweety)")
            self.resultats.append("> Exemple Tweety chargé.\n")
        except Exception as e:
            self.resultats.append(f"Erreur exemple : {e}\n")

    def toggle_musique(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.resultats.append("> Musique en pause.\n")
        else:
            self.player.play()
            self.resultats.append("> Musique reprise.\n")

    def ouvrir_surprise(self):
        code, ok = QInputDialog.getText(self, "Easter Egg", "Entrez un mot-clé (ex: 'reiter', 'nixon', 'theory', '67', '13') :")
        if ok and code.strip():
            if est_secret(code):
                s = surprise(code)
                self.resultats.append(f"\n*** {s.type} : {s.titre} ***")
                self.resultats.append(f"Énoncé : {s.enonce}")
                self.resultats.append(f"Explication : {s.explication}")
                self.resultats.append(f"Exemple : {s.exemple}")
                self.resultats.append(f"Source : {s.source}\n")
            else:
                QMessageBox.information(self, "Oups", "Ce n'est pas le bon code secret. Cherche encore !")

if __name__ == "__main__":
    import traceback
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print("\n--- CRASH DÉTECTÉ ---")
        traceback.print_exc()
        input("Appuie sur Entrée pour fermer...")