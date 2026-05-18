"""
___________________________________________________________________________________________

  LGA_ContactSheet_tools v1.0 - Lega Pugliese

  Logica de inputs dinamicos y burn-in para el Group LGA_ContactSheet.
  Ver LGA_ContactSheet.md para la descripcion completa del diseno.
___________________________________________________________________________________________

"""

import nuke
import traceback

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


def _ensure_group_knobs(group):
    if "vertical_two_inputs" not in group.knobs():
        knob = nuke.Boolean_Knob("vertical_two_inputs", "Vertical Layout for 2 Inputs")
        knob.setFlag(nuke.STARTLINE)
        group.addKnob(knob)


def _sync_contactsheet_layout_knobs(cs):
    cs["rows"].setExpression(AUTO_ROWS_EXPR)
    cs["columns"].setExpression(AUTO_COLUMNS_EXPR)


def _burnin_name(index):
    return "Burnin_%d" % index


def _burnin_message(index):
    return "[file tail [value [topnode parent.input%d].file]]\n" % index


def _set_burnin_style(t, index):
    t["message"].setValue(_burnin_message(index))
    t["box"].setValue([131.0625, 85.6875, 1820.9375, 158.3125])
    t["global_font_scale"].setValue(0.505)
    t["font_size"].setValue(154)
    t["color"].setValue([0.0, 1.0, 0.0, 0.0])
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
