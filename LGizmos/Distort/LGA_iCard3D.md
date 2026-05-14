# LGA_iCard3D

Variante del gizmo `iTransform_ae` (Aitor Echeveste, 2021) que reemplaza el `Transform` 2D interno por un `Card3D`. Permite aplicar una transformación 3D de tipo Card3D **únicamente dentro de la región definida por una máscara**, con falloff suave si la máscara está blureada.

Se distribuye como `.nk` con bloque `Group { ... }` (no `Gizmo`), por lo que el usuario puede entrar al grupo y modificar el contenido.

## Inputs

- **img** (0) — imagen a deformar.
- **crtlMask** (1) — control mask (alpha = 1 zonas afectadas, 0 zonas intactas). El usuario suele poner aquí la máscara *binaria* (sin blur) cuando `smart mask` está activo.
- **mask** (2) — máscara opcional usada por el STMap como filtro de blending (con blur, define el falloff).

> Nota: en el gizmo original, los inputs eran `crtlMask`, `mask`, `img`. Se mantiene el mismo orden / nombres.

## Idea de funcionamiento

Un Transform/Card3D 2D directo aplicado a una capa enmascarada produce una transición *abrupta* en el borde del alpha. Si se quiere una transición suave (mask con blur → transformación gradual hacia los bordes) hay que aplicar la deformación en **espacio UV** y luego *remapear* la imagen vía `STMap`.

Pipeline:

1. Se construye un `STMap identidad`: una imagen donde `R = (x+0.5)/width`, `G = (y+0.5)/height`. Eso describe "para cada pixel, leé de su misma posición".
2. Se aplica el `Card3D` interno (`inCard3D1`) sobre esa imagen identidad. El resultado es un STMap deformado: cada pixel ahora apunta a la coordenada que le corresponde en el render del card.
3. Con un `Keymix` y la máscara, se mezcla el STMap deformado con el STMap identidad. Donde alpha=1 → coords deformadas. Donde alpha=0 → coords originales. **Donde el alpha está blureado → coords interpoladas linealmente, lo que da una deformación que decae suavemente**.
4. Un `STMap` final usa ese mapa híbrido para resamplear la imagen de entrada.

El nodo `inCard3D2` está desconectado: existe sólo como **contenedor de los knobs** que el usuario edita; `inCard3D1` lee esos valores con expresiones `parent.inCard3D2.<knob>`.

## Knobs expuestos

Tab **iCard3D**:

- `channels` — canales a procesar (link al STMap final).
- `black outside before` — `BlackOutside` antes del crop expandido.
- `translate / rotate / scaling / uniform_scale / skew` — transform 3D del card.
- `pivot translate / pivot rotate` — pivot del card.
- `focal length / haperture / card z` — parámetros de la cámara interna del Card3D y distancia del card.
- `filter` — filtro común; se propaga al Card3D real.
- `mb samples / shutter` — motion blur del Card3D.
- `crop to format` — recorta el output al formato.
- `black outside after` — BlackOutside al final.
- `addpixels` — padding extra para el crop dinámico (calculado a partir del bbox del input vs. bbox de la máscara).
- `mix` — interpola entre el resultado y el STMap identidad (mix=0 ⇒ sin deformación).
- `smart mask` — alterna entre usar la máscara *binarizada* (`no_filter`, default) o la máscara cruda (`mask`) como key del STMap. Cambia el input 2 del STMap vía `knobChanged`.

## Diferencias respecto a `iTransform_ae`

| | `iTransform_ae` | `LGA_iCard3D` |
|---|---|---|
| Definición | `Group` (file `.gizmo`) | `Group` (file `.nk`) |
| Nodo deformador | `Transform` (2D) | `Card3D` (3D) |
| Holder de knobs | `inTransform2` | `inCard3D2` |
| Knobs expuestos | translate / rotate / scale / skewX / skewY / center / skewOrder | translate / rotate / scaling / uniform_scale / skew / pivot_translate / pivot_rotate / focal / haperture / z / mb |
| Resto de la pipeline | igual | igual (Crop, Expression UV, Keymix×2, STMap, Crop dinámico, Reformat, BlackOutside) |

## Hallazgos / decisiones

- **Card3D necesita renderear con un formato.** Toma el formato del input (la imagen UV expandida por `Crop1`), por lo que rinde en project format y no rompe el STMap.
- **Card3D con knobs por defecto = identidad** (translate 0, rotate 0, z 0, scaling 1). Si en algún proyecto Card3D no rindiera idéntico al input cuando los controles están en cero, habría que ajustar `lens_in_focal` y `lens_in_haperture` para que el card cubra exactamente el frame. Por eso se exponen ambos.
- Se exponen los knobs con `addUserKnob {41 ...}` linkeados al `inCard3D2`. Esto preserva animaciones, expresiones y el panel nativo de Card3D para cada knob.
- El `Card3D` real (`inCard3D1`) usa expresiones por componente (`.x .y .z`) en `translate / rotate / scaling / skew / pivot_translate / pivot_rotate` porque Nuke no acepta linkear vec3 enteros con un único `{{parent.x}}` sin perder las curvas individuales.
- `set_center` y `skewOrder` del original no aplican a Card3D (tiene su propio pivot y orden de transform). Reemplazados por `pivot_translate` / `pivot_rotate`.
- El `knobChanged` y `onCreate` se mantienen análogos al original; `onCreate` ya no setea `center` (no existe en Card3D) — sólo marca el flag `create`.

## Ubicación

`C:\Users\leg4-pc\.nuke\LGA_NodePack\LGizmos\Distort\LGA_iCard3D.nk`
