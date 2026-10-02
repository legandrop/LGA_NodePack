"""
____________________________________________________________________

  LGA_NodePack_WhatsNew v1.00 | Lega

  Ventana "What's new" de NodePack: las notas para el usuario de
  cada version del pack, de la mas nueva a la mas vieja. NodePack no
  tiene menu propio en la barra de Nuke: la entrada va al final del
  menu LGizmos de la barra de nodos, y la agrega menu.py.

  Lee whats_new.json de la raiz instalada del pack. Ese archivo lo
  genera el script de release (build_whats_new) y viaja en el zip:
  en el repo no existe hasta el proximo release, y en ese caso la
  ventana avisa que las notas van a aparecer con la proxima version.

  Solo se lee al abrir la ventana. El menu registra la entrada y
  nada mas, asi que el JSON nunca se toca al arrancar Nuke.

  Vive en la raiz del pack y no en una subcarpeta: menu.py convierte
  cada subcarpeta en un menu de la barra de nodos.

  La logica (leer, validar, filtrar) no importa Qt: se puede probar
  con cualquier Python. Qt se importa recien al armar la ventana.

  Log de cada apertura: DebugPy_LGA_NodePack_WhatsNew.log, suelto en
  la raiz del pack (una subcarpeta seria un menu mas).

  v1.00: Version inicial.
____________________________________________________________________
"""

import json
import os
import re
import sys
import time

PACK_ROOT = os.path.dirname(os.path.realpath(__file__))
NOTES_PATH = os.path.join(PACK_ROOT, "whats_new.json")
DEFAULT_NAME = "LGA NodePack"

# Formato que escribe build_whats_new. Otro numero es un formato que esta
# version del pack no conoce: se trata como "sin notas" antes que mostrar
# algo mal interpretado.
SCHEMA_VERSION = 1

# Orden y titulo de los grupos dentro de cada version. Un kind que no este
# aca se ignora: no hay donde mostrarlo.
KINDS = (("new", "New"), ("improved", "Improved"), ("fixed", "Fixed"))

# Este pack no tiene ediciones (Studio/Client): no se filtra por edicion.
EDITION = None

EMPTY_MESSAGE = "Release notes will appear here starting with the next update."
NO_CHANGES_MESSAGE = "No user-facing changes in this version."

DEBUG = False
# El log va suelto en la raiz y no en logs/: menu.py convierte cada
# subcarpeta del pack en un menu de la barra de nodos, y una carpeta logs/
# aparecia ahi como un menu vacio despues de abrir esta ventana una vez.
LOG_PATH = os.path.join(PACK_ROOT, "DebugPy_LGA_NodePack_WhatsNew.log")

_log_lines = []
_window = None


# ----------------------------------------------------------------------
# Log: una apertura = una corrida, el .log se pisa en cada una
# ----------------------------------------------------------------------
def _log(message):
    _log_lines.append(message)
    if DEBUG:
        print("LGA_NodePack_WhatsNew: %s" % message)


def _flush_log():
    """Escribe el log de la corrida. Nunca rompe la ventana."""
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("Fecha: %s\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
            handle.write("\n".join(_log_lines) + "\n")
    except Exception:
        pass
    del _log_lines[:]


# ----------------------------------------------------------------------
# Logica: leer, validar y filtrar. Sin Qt.
# ----------------------------------------------------------------------
def current_platform():
    """La plataforma con los nombres del WhatsNew.md: win, mac o linux."""
    if sys.platform.startswith("win"):
        return "win"
    if sys.platform == "darwin":
        return "mac"
    return "linux"


def load_notes(path=None):
    """
    El contenido de whats_new.json, o None si no hay notas que mostrar.

    None cubre todo lo que no sea un archivo valido: que no exista (el caso
    normal en el repo), que no se pueda leer, que el JSON este roto o que el
    schemaVersion no sea el que esta version conoce. Nunca levanta: un
    archivo de notas roto no puede tirarle una excepcion a Nuke.
    """
    path = path or NOTES_PATH
    if not os.path.isfile(path):
        _log("sin archivo de notas: %s" % path)
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception as error:
        # Exception y no solo ValueError: un JSON muy anidado tira
        # RecursionError, y un disco que falla, OSError.
        _log("no se pudo leer %s: %s" % (path, error))
        return None
    if not isinstance(data, dict):
        _log("el JSON no es un objeto")
        return None
    schema = data.get("schemaVersion")
    # type() y no isinstance(): True == 1 en Python, y un "schemaVersion":
    # true no es el formato 1.
    if type(schema) is not int or schema != SCHEMA_VERSION:
        _log("schemaVersion desconocido: %r" % (schema,))
        return None
    if not isinstance(data.get("versions"), list):
        _log("el JSON no trae una lista de versiones")
        return None
    return data


def product_name(data):
    """Nombre del producto para el titulo; el del pack si el JSON no lo trae."""
    if isinstance(data, dict):
        name = data.get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    return DEFAULT_NAME


def _allowed(item, key, value):
    """
    Si el item se muestra para ese valor de plataforma o edicion.

    Un item sin la clave vale para todos. value None significa que esa
    dimension no se filtra (un pack sin ediciones muestra todo).
    """
    if value is None:
        return True
    allowed = item.get(key)
    if allowed is None:
        return True
    if isinstance(allowed, str):
        allowed = [allowed]
    if not isinstance(allowed, list):
        return False
    return value in allowed


def _version_key(version):
    """2.66 -> (2, 66), para ordenar por numero y no alfabeticamente."""
    return tuple(int(part) for part in re.findall(r"\d+", version))


def visible_versions(data, platform, edition=None):
    """
    Las versiones a mostrar, de la mas nueva a la mas vieja.

    Cada una es {"version", "date", "groups"}, con groups una lista de
    (titulo, [textos]) en el orden New / Improved / Fixed. Los items de
    otra plataforma o edicion se descartan; una version que se queda sin
    items se muestra igual, con groups vacio. Lo que venga mal formado se
    saltea sin cortar el resto.
    """
    if not isinstance(data, dict) or not isinstance(data.get("versions"), list):
        return []
    result = []
    for entry in data["versions"]:
        if not isinstance(entry, dict):
            continue
        version = entry.get("version")
        if not isinstance(version, str) or not version.strip():
            continue
        items = entry.get("items")
        if not isinstance(items, list):
            items = []
        items = [
            item
            for item in items
            if isinstance(item, dict)
            and isinstance(item.get("text"), str)
            and item["text"].strip()
            and _allowed(item, "platform", platform)
            and _allowed(item, "edition", edition)
        ]
        groups = []
        for kind, title in KINDS:
            texts = [item["text"].strip() for item in items if item.get("kind") == kind]
            if texts:
                groups.append((title, texts))
        date = entry.get("date")
        result.append(
            {
                "version": version.strip(),
                "date": date.strip() if isinstance(date, str) else "",
                "groups": groups,
            }
        )
    result.sort(key=lambda entry: _version_key(entry["version"]), reverse=True)
    return result


# ----------------------------------------------------------------------
# Qt y estilo propios
# ----------------------------------------------------------------------
# NodePack son gizmos y toolsets: no tiene adapter de Qt ni modulo de estilo,
# y no puede importarlos de otro pack porque cada pack se instala solo. Lo
# minimo que necesita esta ventana vive aca.
#
# Los valores son COPIA de LGA_UI_Style_ToolPack v1.29 (Color.WINDOW, TEXT,
# TEXT_STRONG, TEXT_DIM, BORDER, SURFACE_RAISED, SURFACE_HOVER, BORDER_STRONG,
# BORDER_HOVER; Metric.WINDOW_MARGIN, SPACING, RADIUS, BUTTON_HEIGHT,
# FORM_FONT_SIZE, DIALOG_MIN_WIDTH; las hojas FORM, BTN_SECONDARY y
# SCROLLBAR), para que la ventana se lea igual que las de los ToolPacks. Si el
# modulo de estilo cambia esos tokens, se actualizan aca a mano.
_WINDOW = "#212121"
_TEXT = "#A7A7A7"
_TEXT_STRONG = "#E8E8E8"
_TEXT_DIM = "#6E6E6E"
_BORDER = "#333333"
_RAISED = "#2E2E2E"
_HOVER = "#383838"
_BORDER_STRONG = "#444444"
_BORDER_HOVER = "#555555"

_WINDOW_MARGIN = 16
_SPACING = 10
_RADIUS = 5
_BUTTON_HEIGHT = 30
_FONT_SIZE = 14
_DIALOG_MIN_WIDTH = 460
_SCROLLBAR_WIDTH = 10


def _qt():
    """QtWidgets, QtCore y QtGui: PySide6 en Nuke 16+, PySide2 antes."""
    try:
        from PySide6 import QtCore, QtGui, QtWidgets
    except ImportError:
        from PySide2 import QtCore, QtGui, QtWidgets
    return QtWidgets, QtCore, QtGui


def _families():
    """
    (familia, familia_semibold) de Inter si ya esta cargada en esta sesion.

    NodePack no trae fuentes. Si otro pack LGA ya registro Inter, se usa
    (sin importar nada de ese pack: solo se le pregunta a Qt); si no, queda
    la fuente del host, al tamano del pack.
    """
    _, _, QtGui = _qt()
    try:
        available = set(QtGui.QFontDatabase.families())
    except TypeError:
        available = set(QtGui.QFontDatabase().families())
    family = "Inter" if "Inter" in available else ""
    semibold = "Inter SemiBold" if "Inter SemiBold" in available else ""
    return family, semibold


def _semibold_css(semibold_family):
    # La SemiBold de Inter puede vivir en su propia familia: si existe se la
    # nombra, porque `font-weight: 600` sobre "Inter" devuelve la Bold.
    if semibold_family:
        return "font-family: '%s'; font-weight: normal;" % semibold_family
    return "font-weight: 600;"


def _stylesheet(semibold_family):
    return """
QDialog, QWidget { background-color: %(window)s; color: %(text)s; }
QLabel { background: transparent; color: %(text)s; }
QLabel[lgaTitle="true"] { color: %(strong)s; font-weight: bold; font-size: 11pt; }
QLabel[lgaVersion="true"] { color: %(strong)s; %(semibold)s }
QLabel[lgaDim="true"] { color: %(dim)s; }
QFrame[frameShape="4"] { background-color: %(border)s; border: none; max-height: 1px; }
QPushButton {
    background-color: %(raised)s;
    border: 1px solid %(border_strong)s;
    color: %(strong)s;
    padding: 7px 18px;
    border-radius: %(radius)dpx;
    %(semibold)s
}
QPushButton:hover { background-color: %(hover)s; border-color: %(border_hover)s; }
QScrollBar:vertical {
    background: %(window)s; width: %(sb)dpx; margin: 0px; border-radius: %(sb_radius)dpx;
}
QScrollBar::handle:vertical {
    background: %(border_strong)s; min-height: 30px; border-radius: %(sb_radius)dpx;
}
QScrollBar::handle:vertical:hover { background: %(border_hover)s; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0px; height: 0px; background: none; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }
""" % {
        "window": _WINDOW,
        "text": _TEXT,
        "strong": _TEXT_STRONG,
        "dim": _TEXT_DIM,
        "border": _BORDER,
        "raised": _RAISED,
        "hover": _HOVER,
        "border_strong": _BORDER_STRONG,
        "border_hover": _BORDER_HOVER,
        "radius": _RADIUS,
        "sb": _SCROLLBAR_WIDTH,
        "sb_radius": _SCROLLBAR_WIDTH // 2,
        "semibold": _semibold_css(semibold_family),
    }


def _apply_font(widget, family):
    """Familia y tamano del pack en la ventana y en cada hijo.

    Uno por uno y no por herencia: con hoja de estilo, Qt le fija a cada hijo
    su propia fuente y deja de heredar la del padre.
    """
    QtWidgets, _, _ = _qt()
    for target in [widget] + widget.findChildren(QtWidgets.QWidget):
        font = target.font()
        if family:
            font.setFamily(family)
        font.setPixelSize(_FONT_SIZE)
        target.setFont(font)


# ----------------------------------------------------------------------
# Ventana
# ----------------------------------------------------------------------
def _escape(text):
    """El texto va en rich text: un & o un < de una nota no es marcado."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _dim_label(text):
    QtWidgets, _, _ = _qt()
    label = QtWidgets.QLabel(text)
    label.setProperty("lgaDim", True)
    return label


def _version_header(entry):
    QtWidgets, _, _ = _qt()
    row = QtWidgets.QHBoxLayout()
    row.setSpacing(_SPACING)
    version = QtWidgets.QLabel("v%s" % entry["version"])
    version.setProperty("lgaVersion", True)
    row.addWidget(version)
    if entry["date"]:
        row.addWidget(_dim_label(entry["date"]))
    row.addStretch(1)
    return row


def _item_row(text):
    """Una nota con su vineta. La vineta va aparte para que las lineas
    siguientes de una nota larga queden alineadas con el texto y no con
    la vineta."""
    QtWidgets, QtCore, _ = _qt()
    Qt = QtCore.Qt
    row = QtWidgets.QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(6)
    bullet = _dim_label("\u2022")
    label = QtWidgets.QLabel(_escape(text))
    label.setTextFormat(Qt.RichText)
    label.setWordWrap(True)
    label.setTextInteractionFlags(Qt.TextSelectableByMouse)
    row.addWidget(bullet, 0, Qt.AlignTop)
    row.addWidget(label, 1)
    return row


def _version_block(entry):
    QtWidgets, _, _ = _qt()
    block = QtWidgets.QVBoxLayout()
    block.setContentsMargins(0, 0, 0, 0)
    block.setSpacing(4)
    block.addLayout(_version_header(entry))
    if not entry["groups"]:
        block.addWidget(_dim_label(NO_CHANGES_MESSAGE))
        return block
    for title, texts in entry["groups"]:
        block.addSpacing(_SPACING // 2)
        block.addWidget(_dim_label(title))
        for text in texts:
            block.addLayout(_item_row(text))
    return block


def build_window(name, versions, parent=None):
    """Arma la ventana. versions vacio muestra el aviso de 'sin notas'."""
    QtWidgets, QtCore, _ = _qt()
    Qt = QtCore.Qt
    family, semibold_family = _families()

    dialog = QtWidgets.QDialog(parent)
    dialog.setObjectName("LGA_NodePack_WhatsNew")
    dialog.setWindowTitle("What's new in %s" % name)
    dialog.setStyleSheet(_stylesheet(semibold_family))

    root = QtWidgets.QVBoxLayout(dialog)
    root.setContentsMargins(*([_WINDOW_MARGIN] * 4))
    root.setSpacing(_SPACING)

    title = QtWidgets.QLabel("What's new in %s" % name)
    title.setProperty("lgaTitle", True)
    root.addWidget(title)

    if versions:
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content = QtWidgets.QWidget()
        column = QtWidgets.QVBoxLayout(content)
        # Aire a la derecha para que la scrollbar no se apoye en el texto.
        column.setContentsMargins(0, 0, _SPACING, 0)
        column.setSpacing(_SPACING)
        for index, entry in enumerate(versions):
            if index:
                line = QtWidgets.QFrame()
                line.setFrameShape(QtWidgets.QFrame.HLine)
                column.addWidget(line)
            column.addLayout(_version_block(entry))
        column.addStretch(1)
        scroll.setWidget(content)
        root.addWidget(scroll, 1)
    else:
        message = QtWidgets.QLabel(EMPTY_MESSAGE)
        message.setWordWrap(True)
        root.addWidget(message)
        root.addStretch(1)

    buttons = QtWidgets.QHBoxLayout()
    buttons.addStretch(1)
    close = QtWidgets.QPushButton("Close")
    # Close no es una accion: va en el gris del boton secundario de los
    # ToolPacks y la ventana no tiene ningun violeta.
    close.setFixedHeight(_BUTTON_HEIGHT)
    close.setDefault(True)
    close.clicked.connect(dialog.close)
    buttons.addWidget(close)
    root.addLayout(buttons)

    # Ultimo paso del armado: recorre los hijos que ya existen.
    _apply_font(dialog, family)
    if versions:
        dialog.resize(640, 560)
    else:
        dialog.resize(_DIALOG_MIN_WIDTH, dialog.sizeHint().height())
    return dialog


def _host_window():
    """La ventana principal activa, para que el dialogo quede encima de Nuke."""
    try:
        QtWidgets, _, _ = _qt()
        return QtWidgets.QApplication.activeWindow()
    except Exception:
        return None


def show_whats_new(parent=None, notes_path=None):
    """Abre la ventana. Es lo que llama la entrada What's new del menu."""
    global _window
    _log("pack: %s" % PACK_ROOT)
    platform = current_platform()
    try:
        data = load_notes(notes_path)
        versions = visible_versions(data, platform, EDITION) if data else []
        _log(
            "plataforma %s, %d versiones a mostrar" % (platform, len(versions))
        )
        if _window is not None:
            try:
                _window.close()
                _window.deleteLater()
            except Exception:
                pass
            _window = None
        _window = build_window(
            product_name(data), versions, parent or _host_window()
        )
        _window.show()
        _window.raise_()
        _window.activateWindow()
    except Exception as error:
        _log("error al abrir la ventana: %s" % error)
        print("LGA_NodePack_WhatsNew: no se pudo abrir la ventana: %s" % error)
    finally:
        _flush_log()
