import sys
import json
import os
import threading
import time
import pywhatkit

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit, QFileDialog,
    QMessageBox, QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QIcon, QPixmap


class Sinais(QObject):
    log = Signal(str)
    finalizado = Signal()


sinais = Sinais()

mensagens_salvas = []
imagens_anexadas = []
numeros = []
falhas = []
executando = False

pausa_envios = threading.Event()
pausa_envios.set()

ARQUIVO_MENSAGENS = "mensagens.json"


STYLE = """
QMainWindow, QWidget {
    background-color: #0f1117;
    color: #e8eaf0;
    font-family: 'Segoe UI', sans-serif;
}

#sidebar {
    background-color: #161b27;
    border-right: 1px solid #1e2535;
    min-width: 230px;
    max-width: 230px;
}

#sidebar_title {
    color: #5b8dee;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 2px;
    padding: 18px 16px 10px 16px;
}

#msg_btn {
    background-color: transparent;
    color: #c5cae0;
    border: none;
    border-radius: 6px;
    padding: 8px 10px;
    text-align: left;
    font-size: 13px;
}

#msg_btn:hover {
    background-color: #1e2535;
    color: #ffffff;
}

#del_btn {
    background-color: transparent;
    color: #455070;
    border: none;
    border-radius: 6px;
    font-size: 15px;
    padding: 4px 8px;
    min-width: 28px;
    max-width: 28px;
}

#del_btn:hover {
    background-color: #3d1a1a;
    color: #ff6b6b;
}

#main_panel {
    background-color: #0f1117;
}

#section_title {
    color: #5b8dee;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 2px;
    margin-top: 4px;
}

#app_title {
    color: #e8eaf0;
    font-size: 22px;
    font-weight: 700;
}

#app_subtitle {
    color: #455070;
    font-size: 12px;
    letter-spacing: 1px;
}

QLineEdit, QTextEdit {
    background-color: #161b27;
    color: #e8eaf0;
    border: 1px solid #1e2535;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: #2a4494;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #3d5fc4;
    background-color: #181d2e;
}

#btn_primary {
    background-color: #1e2535;
    color: #c5cae0;
    border: 1px solid #2a3550;
    border-radius: 8px;
    padding: 9px 16px;
    font-size: 12px;
    font-weight: 600;
}

#btn_primary:hover {
    background-color: #263045;
    color: #e8eaf0;
    border-color: #3a4a6a;
}

#btn_start {
    background-color: #1a3a2a;
    color: #4ecca3;
    border: 1px solid #2a5a40;
    border-radius: 8px;
    padding: 9px 20px;
    font-size: 12px;
    font-weight: 700;
}

#btn_start:hover {
    background-color: #1f4a34;
    color: #6eeebb;
}

#btn_start:disabled {
    background-color: #151f18;
    color: #2a4a38;
    border-color: #1a3028;
}

#btn_pause {
    background-color: #3a331a;
    color: #ffd166;
    border: 1px solid #6a5620;
    border-radius: 8px;
    padding: 9px 20px;
    font-size: 12px;
    font-weight: 700;
}

#btn_pause:hover {
    background-color: #4a4020;
    color: #ffe08a;
}

#btn_pause:disabled {
    background-color: #1f1c15;
    color: #4a4028;
    border-color: #2a261a;
}

#btn_stop {
    background-color: #3a1a1a;
    color: #ff6b6b;
    border: 1px solid #5a2a2a;
    border-radius: 8px;
    padding: 9px 20px;
    font-size: 12px;
    font-weight: 700;
}

#btn_stop:hover {
    background-color: #4a2020;
    color: #ff8888;
}

#btn_stop:disabled {
    background-color: #1f1515;
    color: #3a2828;
    border-color: #2a1a1a;
}

#config_frame {
    background-color: #161b27;
    border: 1px solid #1e2535;
    border-radius: 10px;
}

#config_label {
    color: #6b7a9e;
    font-size: 12px;
}

#preview_frame {
    background-color: #161b27;
    border: 1px solid #1e2535;
    border-radius: 10px;
}

#img_container {
    background-color: transparent;
}

#img_del_btn {
    background-color: #2a1a1a;
    color: #ff6b6b;
    border: none;
    border-radius: 4px;
    font-size: 10px;
    padding: 2px;
}

#img_del_btn:hover {
    background-color: #3d1a1a;
}

#log_box {
    background-color: #0a0d14;
    color: #7b8ab8;
    border: 1px solid #1e2535;
    border-radius: 10px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    padding: 10px;
}

#numeros_label {
    color: #6b7a9e;
    font-size: 11px;
}

QScrollArea {
    border: none;
    background: transparent;
}

QScrollBar:vertical {
    background: #0f1117;
    width: 6px;
    border-radius: 3px;
}

QScrollBar::handle:vertical {
    background: #2a3550;
    border-radius: 3px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #3d5fc4;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background: #0f1117;
    height: 6px;
    border-radius: 3px;
}

QScrollBar::handle:horizontal {
    background: #2a3550;
    border-radius: 3px;
}

QScrollBar::handle:horizontal:hover {
    background: #3d5fc4;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

QFrame[frameShape="4"], QFrame[frameShape="5"] {
    color: #1e2535;
}
"""


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        self.setWindowTitle("Automatizador de Mensagens")
        self.setMinimumSize(1090, 800)
        self.resize(1090, 750)

        sinais.log.connect(self._append_log)
        sinais.finalizado.connect(self._on_finalizado)

        root = QWidget()
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setCentralWidget(root)

        root_layout.addWidget(self._build_sidebar())
        root_layout.addWidget(self._build_main(), stretch=1)

        self._carregar_mensagens()
        self._log("Sistema iniciado. Importe os números e configure a mensagem.")

    def _build_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = QLabel("MENSAGENS SALVAS")
        title.setObjectName("sidebar_title")
        layout.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.sidebar_content = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar_content)
        self.sidebar_layout.setContentsMargins(8, 8, 8, 8)
        self.sidebar_layout.setSpacing(2)
        self.sidebar_layout.addStretch()

        scroll.setWidget(self.sidebar_content)
        layout.addWidget(scroll, stretch=1)

        return sidebar

    def _build_main(self):
        panel = QWidget()
        panel.setObjectName("main_panel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 20, 24, 12)
        layout.setSpacing(10)

        header = QVBoxLayout()
        header.setSpacing(2)

        title = QLabel("Editor de Mensagens")
        title.setObjectName("app_title")

        subtitle = QLabel("For WhatsApp")
        subtitle.setObjectName("app_subtitle")

        header.addWidget(title)
        header.addWidget(subtitle)
        layout.addLayout(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)

        layout.addWidget(self._section("MENSAGEM"))

        self.nome_entry = QLineEdit()
        self.nome_entry.setPlaceholderText("Título da mensagem")
        layout.addWidget(self.nome_entry)

        self.textbox = QTextEdit()
        self.textbox.setPlaceholderText("Digite aqui o conteúdo da mensagem...")
        self.textbox.setFixedHeight(140)
        layout.addWidget(self.textbox)

        dica = QLabel("Use {nome} em qualquer lugar da mensagem para inserir o nome do cliente.")
        dica.setStyleSheet("background-color: transparent; border: none; color: #455070; font-size: 11px;")
        layout.addWidget(dica)

        layout.addWidget(self._section("CONFIGURAÇÕES DE ENVIO"))
        layout.addWidget(self._build_config())

        layout.addWidget(self._build_buttons())

        self.numeros_label = QLabel("Nenhum número carregado")
        self.numeros_label.setObjectName("numeros_label")
        layout.addWidget(self.numeros_label)

        layout.addWidget(self._section("IMAGENS ANEXADAS"))
        layout.addWidget(self._build_preview(), 0)

        layout.addWidget(self._section("INFORMAÇÕES"))

        self.log_box = QTextEdit()
        self.log_box.setObjectName("log_box")
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box, 1)

        return panel

    def _section(self, texto):
        lbl = QLabel(texto)
        lbl.setObjectName("section_title")
        return lbl

    def _build_config(self):
        frame = QWidget()
        frame.setObjectName("config_frame")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        lbl1 = QLabel("Quantidade de Mensagens:")
        lbl1.setStyleSheet("background-color: transparent; border: none; color: #6b7a9e;")

        self.entry_bloco = QLineEdit()
        self.entry_bloco.setText("20")
        self.entry_bloco.setFixedWidth(45)

        lbl2 = QLabel("Pausa (minutos):")
        lbl2.setStyleSheet("background-color: transparent; border: none; color: #6b7a9e;")

        self.entry_pausa = QLineEdit()
        self.entry_pausa.setText("30")
        self.entry_pausa.setFixedWidth(45)

        layout.addWidget(lbl1)
        layout.addWidget(self.entry_bloco)
        layout.addSpacing(16)
        layout.addWidget(lbl2)
        layout.addWidget(self.entry_pausa)
        layout.addStretch()

        return frame

    def _build_buttons(self):
        frame = QWidget()

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        def btn(texto, obj, slot):
            b = QPushButton(texto)
            b.setObjectName(obj)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(slot)
            return b

        layout.addWidget(btn("Salvar Mensagem", "btn_primary", self._salvar_texto))
        layout.addWidget(btn("Anexar Imagens", "btn_primary", self._anexar_imagens))
        layout.addWidget(btn("Importar Números (.txt)", "btn_primary", self._importar_numeros))
        layout.addStretch()

        self.btn_start = btn("Começar Envios", "btn_start", self._iniciar_envios)
        self.btn_pause = btn("Pausar Envios", "btn_pause", self._alternar_pausa)
        self.btn_stop = btn("Parar", "btn_stop", self._parar_envios)

        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)

        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_pause)
        layout.addWidget(self.btn_stop)

        return frame

    def _build_preview(self):
        container = QWidget()
        container.setObjectName("preview_frame")
        container.setFixedHeight(115)
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.preview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.preview_scroll.setFrameShape(QFrame.NoFrame)
        self.preview_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.preview_scroll.setFixedHeight(113)

        self.preview_widget = QWidget()
        self.preview_widget.setObjectName("img_container")

        self.preview_layout = QHBoxLayout(self.preview_widget)
        self.preview_layout.setContentsMargins(8, 6, 8, 6)
        self.preview_layout.setSpacing(10)
        self.preview_layout.addStretch()

        self.preview_scroll.setWidget(self.preview_widget)
        container_layout.addWidget(self.preview_scroll)

        return container

    def _log(self, texto):
        self.log_box.append(texto)

    def _append_log(self, texto):
        self.log_box.append(texto)

    def _salvar_mensagens_json(self):
        with open(ARQUIVO_MENSAGENS, "w", encoding="utf-8") as f:
            json.dump(mensagens_salvas, f, ensure_ascii=False, indent=4)

    def _carregar_mensagens(self):
        global mensagens_salvas

        if os.path.exists(ARQUIVO_MENSAGENS):
            with open(ARQUIVO_MENSAGENS, "r", encoding="utf-8") as f:
                mensagens_salvas = json.load(f)

            self._atualizar_lista_mensagens()

    def _atualizar_lista_mensagens(self):
        while self.sidebar_layout.count() > 1:
            item = self.sidebar_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for indice, item in enumerate(mensagens_salvas):
            linha = QWidget()

            linha_layout = QHBoxLayout(linha)
            linha_layout.setContentsMargins(0, 0, 0, 0)
            linha_layout.setSpacing(2)

            btn_nome = QPushButton(item["nome"])
            btn_nome.setObjectName("msg_btn")
            btn_nome.setCursor(Qt.PointingHandCursor)
            btn_nome.clicked.connect(lambda _, i=indice: self._carregar_texto(i))

            btn_del = QPushButton("🗑")
            btn_del.setObjectName("del_btn")
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.clicked.connect(lambda _, i=indice, n=item["nome"]: self._confirmar_apagar(i, n))

            linha_layout.addWidget(btn_nome, stretch=1)
            linha_layout.addWidget(btn_del)

            self.sidebar_layout.insertWidget(self.sidebar_layout.count() - 1, linha)

    def _carregar_texto(self, indice):
        self.textbox.setText(mensagens_salvas[indice]["texto"])
        self._log("Mensagem carregada.")

    def _confirmar_apagar(self, indice, nome):
        resp = QMessageBox.question(
            self,
            "Confirmar exclusão",
            f'Tem certeza que deseja apagar a mensagem "{nome}"?',
            QMessageBox.Yes | QMessageBox.No
        )

        if resp == QMessageBox.Yes:
            mensagens_salvas.pop(indice)
            self._salvar_mensagens_json()
            self._atualizar_lista_mensagens()
            self._log(f"🗑 Mensagem '{nome}' apagada.")

    def _salvar_texto(self):
        texto = self.textbox.toPlainText().strip()
        nome = self.nome_entry.text().strip()

        if not texto:
            QMessageBox.warning(self, "Aviso", "Digite uma mensagem para salvar.")
            return

        if not nome:
            QMessageBox.warning(self, "Aviso", "Digite um título para a mensagem.")
            return

        mensagens_salvas.append({"nome": nome, "texto": texto})
        self._salvar_mensagens_json()
        self._atualizar_lista_mensagens()
        self._log(f"Mensagem '{nome}' salva.")

    def _importar_numeros(self):
        global numeros

        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            "Selecione o arquivo .txt com os números",
            "",
            "Arquivo de texto (*.txt)"
        )

        if not arquivo:
            return

        numeros = []

        with open(arquivo, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()

                if not linha:
                    continue

                partes = linha.split()
                numero = partes[0].lstrip("+")
                nome = partes[1].capitalize() if len(partes) > 1 else ""

                numeros.append({"numero": numero, "nome": nome})

        self.numeros_label.setText(f"✔  {len(numeros)} números carregados")
        self.numeros_label.setStyleSheet("color: #4ecca3; font-size: 11px; font-weight: 600;")
        self._log(f"📋 {len(numeros)} números importados de: {os.path.basename(arquivo)}")

        for item in numeros[:5]:
            self._log(f"   → +{item['numero']} ({item['nome']})")

        if len(numeros) > 5:
            self._log(f"   ... e mais {len(numeros) - 5} número(s).")

    def _anexar_imagens(self):
        arquivos, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecionar imagens",
            "",
            "Imagens (*.png *.jpg *.jpeg)"
        )

        if not arquivos:
            return

        for arq in arquivos:
            if arq not in imagens_anexadas:
                imagens_anexadas.append(arq)

        self._atualizar_preview()
        self._log(f"{len(imagens_anexadas)} imagem(ns) anexada(s) no total.")

    def _remover_imagem(self, caminho):
        nome = os.path.basename(caminho)

        imagens_anexadas.remove(caminho)
        self._atualizar_preview()
        self._log(f"Imagem '{nome}' removida.")

    def _atualizar_preview(self):
        while self.preview_layout.count() > 1:
            item = self.preview_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for caminho in imagens_anexadas:
            try:
                container = QWidget()
                container.setObjectName("img_container")

                c_layout = QVBoxLayout(container)
                c_layout.setContentsMargins(0, 0, 0, 0)
                c_layout.setSpacing(2)

                pixmap = QPixmap(caminho).scaled(
                    80,
                    80,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                img_label = QLabel()
                img_label.setPixmap(pixmap)
                img_label.setFixedSize(80, 80)
                img_label.setAlignment(Qt.AlignCenter)

                btn_del = QPushButton("✕ remover")
                btn_del.setObjectName("img_del_btn")
                btn_del.setCursor(Qt.PointingHandCursor)
                btn_del.setFixedWidth(80)
                btn_del.clicked.connect(lambda _, c=caminho: self._remover_imagem(c))

                c_layout.addWidget(img_label)
                c_layout.addWidget(btn_del)

                self.preview_layout.insertWidget(self.preview_layout.count() - 1, container)

            except Exception as e:
                self._log(f"Erro preview: {e}")

    def _iniciar_envios(self):
        global executando

        if not numeros:
            QMessageBox.warning(self, "Aviso", "Importe a lista de números primeiro.")
            return

        mensagem = self.textbox.toPlainText().strip()

        if not mensagem and not imagens_anexadas:
            QMessageBox.warning(self, "Aviso", "Digite uma mensagem ou anexe imagens.")
            return

        msgs_por_bloco = int(self.entry_bloco.text()) if self.entry_bloco.text().isdigit() else 20
        pausa_minutos = int(self.entry_pausa.text()) if self.entry_pausa.text().isdigit() else 30

        executando = True
        pausa_envios.set()

        self.btn_start.setEnabled(False)
        self.btn_pause.setText("Pausar Envios")
        self.btn_pause.setEnabled(True)
        self.btn_stop.setEnabled(True)

        threading.Thread(
            target=_enviar_mensagens,
            args=(mensagem, list(imagens_anexadas), msgs_por_bloco, pausa_minutos, list(numeros)),
            daemon=True
        ).start()

    def _parar_envios(self):
        global executando

        executando = False
        pausa_envios.set()

        self._log("⛔ Envios interrompidos.")
        self.btn_start.setEnabled(True)
        self.btn_pause.setText("Pausar Envios")
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)

    def _alternar_pausa(self):
        if not executando:
            return

        if pausa_envios.is_set():
            pausa_envios.clear()
            self.btn_pause.setText("Continuar Envios")
            self._log("⏸ Envios pausados.")
        else:
            pausa_envios.set()
            self.btn_pause.setText("Pausar Envios")
            self._log("▶ Retomando envios do ponto atual.")

    def _on_finalizado(self):
        pausa_envios.set()

        self.btn_start.setEnabled(True)
        self.btn_pause.setText("Pausar Envios")
        self.btn_pause.setEnabled(False)
        self.btn_stop.setEnabled(False)


def _aguardar_se_pausado():
    while executando and not pausa_envios.is_set():
        time.sleep(0.2)

    return executando


def _sleep_com_controle(segundos):
    for _ in range(segundos * 5):
        if not executando:
            return False

        if not _aguardar_se_pausado():
            return False

        time.sleep(0.2)

    return True


def _enviar_mensagens(mensagem, imagens, msgs_por_bloco, pausa_minutos, numeros_lista):
    global falhas, executando

    falhas = []
    total = len(numeros_lista)

    sinais.log.emit(f"▶ Iniciando envio para {total} números.")
    sinais.log.emit(f"   Bloco: {msgs_por_bloco} msgs | Pausa: {pausa_minutos} min")

    for i, item in enumerate(numeros_lista):
        numero = item["numero"]
        nome = item["nome"]
        mensagem_personalizada = mensagem.replace("{nome}", nome)

        if not executando:
            sinais.log.emit("⛔ Processo interrompido.")
            sinais.finalizado.emit()
            return

        if not _aguardar_se_pausado():
            sinais.log.emit("⛔ Processo interrompido.")
            sinais.finalizado.emit()
            return

        if i > 0 and i % msgs_por_bloco == 0:
            sinais.log.emit(f"⏸ Pausa de {pausa_minutos} minuto(s) ({i}/{total} enviados)...")

            if not _sleep_com_controle(pausa_minutos * 60):
                sinais.log.emit("⛔ Interrompido durante a pausa.")
                sinais.finalizado.emit()
                return

            sinais.log.emit("▶ Retomando envios.")

        try:
            sinais.log.emit(f"Enviando para +{numero} - {nome} ({i + 1}/{total})...")

            if imagens:
                pywhatkit.sendwhats_image(
                    receiver=f"+{numero}",
                    img_path=imagens[0],
                    caption=mensagem_personalizada if mensagem_personalizada else "",
                    wait_time=20,
                    tab_close=True,
                    close_time=5
                )

                for img_extra in imagens[1:]:
                    if not executando or not _aguardar_se_pausado():
                        sinais.log.emit("⛔ Processo interrompido.")
                        sinais.finalizado.emit()
                        return

                    if not _sleep_com_controle(8):
                        sinais.log.emit("⛔ Processo interrompido.")
                        sinais.finalizado.emit()
                        return

                    pywhatkit.sendwhats_image(
                        receiver=f"+{numero}",
                        img_path=img_extra,
                        caption="",
                        wait_time=20,
                        tab_close=True,
                        close_time=5
                    )
            else:
                pywhatkit.sendwhatmsg_instantly(
                    phone_no=f"+{numero}",
                    message=mensagem_personalizada,
                    wait_time=20,
                    tab_close=True,
                    close_time=5
                )

            sinais.log.emit(f"✔  Enviado para +{numero} - {nome}")

            if not _sleep_com_controle(5):
                sinais.log.emit("⛔ Processo interrompido.")
                sinais.finalizado.emit()
                return

        except Exception as erro:
            falhas.append(f"{numero} ({nome})")
            sinais.log.emit(f"X ERRO em +{numero} - {nome}: {erro}")

    executando = False

    sinais.log.emit("─" * 50)
    sinais.log.emit("✔ Processo finalizado.")

    if falhas:
        sinais.log.emit(f"⚠ {len(falhas)} número(s) com falha:")
        for n in falhas:
            sinais.log.emit(f"   → +{n}")
    else:
        sinais.log.emit("Nenhuma falha durante os envios.")

    sinais.finalizado.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())