# Changelog

## v1.47
- El instalador dejaba el `init.py` roto en cualquier equipo que tuviera sus `pluginAddPath` adentro de un bloque `if` —por ejemplo para discriminar por version de Nuke— y ademas reportaba exito. Al reordenar los paths se llevaba tambien las lineas indentadas, dejando el bloque sin cuerpo, y Nuke no arrancaba con un `IndentationError`. Ahora solo toca las lineas en columna 0 y respeta las indentadas donde estan. Suma ademas deduplicacion de paths repetidos, preservacion del BOM del archivo original y una validacion del resultado: si el `init.py` quedaria invalido, no lo modifica y aborta la instalacion. [ NodePack - Corregir el manejo del init.py del instalador ]

## v1.46
- El instalador ordena `~/.nuke/init.py` de forma canónica en Windows y macOS: recolecta todos los bloques `pluginAddPath` de LGA, los reordena según el orden oficial (Layout, ToolPack-B, ToolPack, NodePack, OpenInNukeX, Defaults, CollectedTools), elimina duplicados y deja intactos los paths ajenos. Antes cada plataforma resolvía el orden de una manera distinta y macOS simplemente agregaba al final. [ NodePack - Unificar el orden del init.py ]

- Se incorpora instalación transaccional para Windows y macOS, con backup de la carpeta previa, actualización idempotente del `init.py` global y restauración ante fallos. El generador de release pasa a usar `VERSION` y este changelog como fuentes canónicas, e incluye ambos instaladores sin depender del inventario de ZIPs. [ NodePack - Agregar instaladores y versionado canónico ]

- LGA_BouncePos: restaura los controles de Delay Random y Effective Delay conectandolos al nuevo `Bounce_Impulse.g` sin modificar la formula optimizada de `Bounce_Raw`, y actualiza el texto visible del gizmo a v0.9 en dos lineas. [ LGA_BouncePos - Restaurar delay random ]

- LGA_BouncePos: elimina el readout live "Bounce Offset" (el knob de display y el nodo interno `Bounce_Output`) que reevaluaba toda la expresion del rebote una segunda vez en cada refresco del panel, para acelerar la interaccion mientras se ajustan los controles. [ LGA_BouncePos - Quitar readout live ]

## v1.45
- LGA_BouncePos: optimiza la evaluacion live del rebote gateando los impulsos historicos dentro del ternario de `Bounce Length` y elimina el label dinamico del nodo interno para evitar reevaluaciones en redraw del DAG. [ LGA_BouncePos - Optimizar evaluacion live ]

## v1.44
- Changelog inicial creado para alinear la repo con la version actual visible en `README.MD`. [ NodePack - Crear changelog inicial ]
