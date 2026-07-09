# Changelog

## v1.46
- LGA_BouncePos: restaura los controles de Delay Random y Effective Delay conectandolos al nuevo `Bounce_Impulse.g` sin modificar la formula optimizada de `Bounce_Raw`, y actualiza el texto visible del gizmo a v0.9 en dos lineas. [ LGA_BouncePos - Restaurar delay random ]

- LGA_BouncePos: elimina el readout live "Bounce Offset" (el knob de display y el nodo interno `Bounce_Output`) que reevaluaba toda la expresion del rebote una segunda vez en cada refresco del panel, para acelerar la interaccion mientras se ajustan los controles. [ LGA_BouncePos - Quitar readout live ]

## v1.45
- LGA_BouncePos: optimiza la evaluacion live del rebote gateando los impulsos historicos dentro del ternario de `Bounce Length` y elimina el label dinamico del nodo interno para evitar reevaluaciones en redraw del DAG. [ LGA_BouncePos - Optimizar evaluacion live ]

## v1.44
- Changelog inicial creado para alinear la repo con la version actual visible en `README.MD`. [ NodePack - Crear changelog inicial ]
