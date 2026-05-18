"""
___________________________________________________________________________________________

  LGA_ContactSheet_tools v1.0 - Lega Pugliese

  Logica de inputs dinamicos y burn-in para el Group LGA_ContactSheet.
  Ver LGA_ContactSheet.md para la descripcion completa del diseno.
___________________________________________________________________________________________

"""

import nuke
import traceback

BOX_LEFT_FACTOR = 0.025
BOX_TOP_FACTOR = 0.11
BOX_RIGHT_FACTOR = 0.975
BOX_BOTTOM_FACTOR = 0.21
BOX_AUTO_OFFSET_X_FACTOR = -0.005208
BOX_AUTO_OFFSET_Y_FACTOR = -0.138889
TEXT_SCALE_BASE = 0.5
TEXT_SCALE_BASE_WIDTH = 1920.0

AUTO_ROWS_EXPR = (
    '[value parent.vertical_two_inputs] && [numvalue inputs] == 2 ? 2 : '
    '[expr {int( (sqrt( [numvalue inputs] ) ) )} ] * '
    '[expr {int( ceil ( ([numvalue inputs] /(sqrt( [numvalue inputs] ) ) )) )} ] '
    '< [numvalue inputs]   ? [expr {int( (sqrt( [numvalue inputs] ) ) )} ] +1 : '
    '[expr {int( (sqrt( [numvalue inputs] ) ) )} ]'
)

AUTO_COLUMNS_EXPR = (
    '[value parent.vertical_two_inputs] && [numvalue inputs] == 2 ? 1 : '
    '[expr {int( ceil ( ([numvalue inputs] /(sqrt( [numvalue inputs] )) )) )} ]'
)

# Guarda contra reentrada: agregar/borrar Input nodes vuelve a disparar knobChanged.
_busy = False


def _input_name(index):
    """Nombre visible del input del grupo; el orden interno sigue usando number."""
    return "Input%d" % (index + 1)


def _set_input_identity(inp, index):
    """Fija number primero; Nuke puede renombrar el nodo al cambiar ese knob."""
    inp["number"].setValue(index)
    inp.setName(_input_name(index))
    if "label" in inp.knobs():
        inp["label"].setValue(str(index + 1))


def _ensure_default_bool(group, name, label):
    if name not in group.knobs():
        knob = nuke.Boolean_Knob(name, label)
        knob.setFlag(nuke.STARTLINE)
        knob.setValue(True)
        group.addKnob(knob)


def _ensure_group_knobs(group):
    _ensure_default_bool(group, "filename_burnin", "Filename Burn-in")
    _ensure_default_bool(group, "vertical_two_inputs", "Vertical Layout for 2 Inputs")
    if "text_color" not in group.knobs():
        knob = nuke.Color_Knob("text_color", "Text Color")
        knob.setValue([1.0, 1.0, 1.0])
        group.addKnob(knob)
    if "text_font_size" not in group.knobs():
        knob = nuke.Double_Knob("text_font_size", "Text Scale")
        knob.setRange(0.05, 5)
        knob.setValue(1.0)
        group.addKnob(knob)
    if "text_offset_x" not in group.knobs():
        knob = nuke.Double_Knob("text_offset_x", "Text Offset X")
        knob.setValue(0.0)
        group.addKnob(knob)
    if "text_offset_y" not in group.knobs():
        knob = nuke.Double_Knob("text_offset_y", "Text Offset Y")
        knob.setValue(0.0)
        group.addKnob(knob)
    if "text_offset" in group.knobs():
        group["text_offset"].setFlag(nuke.INVISIBLE)


def _sync_contactsheet_layout_knobs(cs):
    cs["rows"].setExpression(AUTO_ROWS_EXPR)
    cs["columns"].setExpression(AUTO_COLUMNS_EXPR)


def _burnin_name(index):
    return "Burnin_%d" % index


def _burnin_message(index):
    return "[file tail [value [topnode parent.input%d].file]]\n" % index


def _box_expr(factor, axis, offset_knob):
    return "input.%s * %.6f + parent.%s" % (axis, factor, offset_knob)


def _set_burnin_style(t, index):
    t["message"].setValue(_burnin_message(index))
    t["box"].setExpression(
        _box_expr(BOX_LEFT_FACTOR + BOX_AUTO_OFFSET_X_FACTOR, "width", "text_offset_x"),
        0,
    )
    t["box"].setExpression(
        _box_expr(BOX_TOP_FACTOR + BOX_AUTO_OFFSET_Y_FACTOR, "height", "text_offset_y"),
        1,
    )
    t["box"].setExpression(
        _box_expr(BOX_RIGHT_FACTOR + BOX_AUTO_OFFSET_X_FACTOR, "width", "text_offset_x"),
        2,
    )
    t["box"].setExpression(
        _box_expr(BOX_BOTTOM_FACTOR + BOX_AUTO_OFFSET_Y_FACTOR, "height", "text_offset_y"),
        3,
    )
    t["global_font_scale"].setExpression(
        "parent.text_font_size * %.3f * input.width / %.1f"
        % (TEXT_SCALE_BASE, TEXT_SCALE_BASE_WIDTH)
    )
    t["font_size"].setValue(154)
    t["color"].setExpression("parent.text_color.r", 0)
    t["color"].setExpression("parent.text_color.g", 1)
    t["color"].setExpression("parent.text_color.b", 2)
    try:
        t["color"].clearAnimated(3)
    except Exception:
        pass
    t["color"].setValue(0.0, 3)
    t["autofit_bbox"].setValue(False)
    t["disable"].setExpression("1-parent.filename_burnin")


def _make_burnin(name, index):
    """Crea un Text2 con el mismo estilo que los Text de contactsheet_review.nk."""
    t = nuke.nodes.Text2(name=name)
    _set_burnin_style(t, index)
    return t


def _ensure_burnin(index, inp):
    """Mantiene el Text interno de la rama y lo devuelve."""
    name = _burnin_name(index)
    txt = nuke.toNode(name)
    if txt is None:
        txt = _make_burnin(name, index)
    else:
        _set_burnin_style(txt, index)
    txt.setInput(0, inp)
    txt.setXYpos(index * 160, 130)
    return txt


def _connected_count(group):
    """Cantidad de inputs del grupo conectados de forma contigua desde 0."""
    n = 0
    while True:
        try:
            src = group.input(n)
        except Exception:
            break
        if src is None:
            break
        n += 1
    return n


def sync(group):
    """Sincroniza la estructura interna del grupo con los inputs conectados afuera.

    Mantiene adentro una rama Input -> Burnin (Text2) por cada input, mas una
    rama libre extra para poder seguir conectando. El ContactSheet se cablea
    solo con las ramas que corresponden a inputs realmente conectados.
    """
    global _busy
    if _busy:
        return
    _busy = True
    try:
        _ensure_group_knobs(group)
        connected = _connected_count(group)
        desired = connected + 1  # siempre una rama libre extra
        with group:
            cs = nuke.toNode("ContactSheet1")
            _sync_contactsheet_layout_knobs(cs)
            existing = {}
            for nd in nuke.allNodes("Input"):
                existing[int(nd["number"].value())] = nd

            # Crear las ramas Input -> Burnin que falten.
            for j in range(desired):
                if j in existing:
                    _set_input_identity(existing[j], j)
                    continue
                inp = nuke.nodes.Input()
                _set_input_identity(inp, j)
                inp.setXYpos(j * 160, 0)
                existing[j] = inp
            for j in range(desired):
                _ensure_burnin(j, existing[j])

            # Borrar las ramas sobrantes (inputs que ya no existen).
            for j, inp in list(existing.items()):
                if j >= desired:
                    burn = nuke.toNode(_burnin_name(j))
                    if burn is not None:
                        nuke.delete(burn)
                    nuke.delete(inp)

            # Recablear el ContactSheet: solo las ramas conectadas (min 1).
            for k in range(cs.inputs()):
                cs.setInput(k, None)
            for j in range(max(connected, 1)):
                cs.setInput(j, nuke.toNode(_burnin_name(j)))
    except Exception:
        traceback.print_exc()
    finally:
        _busy = False


def knob_changed():
    """Callback del knob 'knobChanged' del grupo. Reacciona a los cambios de input."""
    k = nuke.thisKnob()
    if k is not None and k.name() == "inputChange":
        sync(nuke.thisNode())


def on_create():
    """Callback del knob 'onCreate' del grupo. Sincroniza al crear el nodo."""
    sync(nuke.thisNode())
