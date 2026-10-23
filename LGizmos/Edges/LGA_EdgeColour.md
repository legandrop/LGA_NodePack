> **Regla de documentacion**: este archivo describe el estado actual del codigo. No es un historial de cambios, changelog ni bitacora temporal.
> **Regla de documentacion**: este archivo debe incluir una seccion de referencias tecnicas con rutas completas a los archivos mas importantes relacionados, y para cada archivo nombrar las funciones, clases o metodos clave vinculados a este tema.

# LGA_EdgeColour

Nodo `Group` (se distribuye como `.nk`, editable por dentro) que limpia el **color del frente** en el borde
semitransparente (pelo, motion blur) sin tocar el alpha. En la banda del borde reemplaza el color del Plate por el
color del interior sólido del sujeto empujado hacia afuera, con la luminancia de Blur-Fusion acotada al rango local del
interior. Así el pelo suelto conserva su forma (el alpha no cambia) pero deja de llevar el color del fondo original. Es
el método «QUICK» de limpieza de color de borde, reimplementado con nodos nativos.

Menú: **LGizmos > Edges > LGA_EdgeColour** (se pega con `nuke.loadToolset`, como los demás `.nk` del pack).

## Inputs

- **Source** (0) — el Plate; se usa su rgb.
- **Matte** (1) — el matte en su **alpha**. Sin conectar, se usa el alpha del Source.

## Método

Todo en el espacio de trabajo del script (luz lineal; la luma es la de AP1, la de ACEScg). `I` = Plate, `a` = matte
recortado a [0, 1].

```
m   = interior sólido suave: smoothstep(inner low, inner high, a), erosionado `erode` px y desenfocado `inner blur` px
E   = color del interior empujado hacia afuera: blur(I·m) / blur(m) en 9 escalas (sigma 2..512 px × spread);
      de la gruesa a la fina, cada escala reemplaza a la anterior con smoothstep(0.05, 0.15) sobre su peso blur(m)
mu, m2 = lo mismo con Y y Y² (Y = luma);  sd = sqrt(max(m2 − mu², 0))
Yt  = clamp(Y(F Blur-Fusion 90/6), mu − k·sd, mu + k·sd)          k = luma range
Fq  = max(E · Yt / Y(E), 0)
wn  = cerca del fondo real: (a < background below), recortado al cuadro, dilatado (near + far)/2 y desenfocado,
      así vale 1 hasta `near` px del fondo y 0 desde `far`
w   = (1 − m) · wn · smoothstep(0.01, 0.05, alcance del empuje)
F   = I + w · (Fq − I);   salida F·a, alpha = a
```

Las tres transiciones (interior → banda, entre escalas del empuje, cerca → lejos del fondo) son suaves a propósito. Con
un interior binario (`a ≥ 0,98` erosionado), un cambio seco de escala por umbral o un corte por distancia, el borde de la
zona reemplazada sigue un contorno del matte y se ve como un arco duro dentro del pelo.

### Suavizado temporal (opcional)

Con `temporal smoothing` prendido, F se promedia con los dos cuadros anteriores y los dos siguientes, alineados al
cuadro actual con `VectorGenerator` (calculado sobre el Plate en ACEScct/0,75) e `IDistort`; los de ±2 se alinean
encadenando dos saltos de un cuadro. Peso de cada vecino:

```
exp(−d² / (2·1.2²)) · exp(−e² / (2·tol²))     d = desfasaje en cuadros, e = diferencia del gris guía ya alineado,
                                                tol = temporal tolerance (8/255)
```

Se aplica en `(1 − m) · smoothstep(0.001, 0.01, a)`: en la banda, no en el interior ni afuera. Fuera del rango del Read,
los vecinos son el cuadro retenido. `VectorGenerator` va con `useGPUIfAvailable` apagado. Con el knob apagado, un
`Switch` deja fuera toda esa rama y no se calculan vectores.

## Controles

| Knob | Default | Qué hace |
|---|---|---|
| `view` | result | `result`, `edge weight` (peso `w` del reemplazo, blanco = color reconstruido) o `extended colour` (E). |
| `erode` | 4 | Píxeles que se achica el interior antes de usarlo como fuente de color. |
| `inner softness` | 0.90 / 0.99 | Rango del alpha de la curva suave interior → banda. |
| `inner blur` | 4 | Desenfoque del borde del interior. |
| `near` | 48 | Distancia al fondo real con reemplazo completo. |
| `far` | 80 | Distancia al fondo real donde el reemplazo ya se apagó. |
| `spread` | 1 | Escala del empuje (1 = UHD; 0.5 para HD). |
| `luma range` | 1.5 | Desvíos de la luminancia del interior que puede alejarse la del borde. |
| `temporal smoothing` | off | Promedio temporal de F en la banda. |
| `premultiply` | on | Salida premultiplicada por el matte. |
| `background below` | 0.05 | Alpha por debajo del cual un píxel cuenta como fondo para `near` y `far`. |
| `temporal tolerance` | 8/255 | Diferencia del gris guía alineado a partir de la cual un vecino deja de contar. |
| `blur-fusion large` / `small` | 90 / 6 | Cajas de Blur-Fusion para la luminancia. |
| `clamp negatives`, `epsilon` | on, 1e-5 | Los de Blur-Fusion. |

Distancias en píxeles de un plano UHD; para HD, la mitad. Los tooltips están en castellano.

## Rendimiento

UHD (3840×2160), Nuke 17 en modo terminal, CPU: unos 0,63 s por cuadro sin suavizado temporal y unos 4 s con él
(cuadros en orden; `VectorGenerator` reusa lo ya calculado).

## Verificación

Plano de prueba de pelo a contraluz (25 cuadros UHD), comparado con una implementación numpy del mismo método:

- Sin suavizado temporal, la luminancia objetivo coincide con la de numpy cuadro a cuadro (diferencias de 0,02 a 0,05 en
  lineal, por la erosión suave contra la binaria).
- Con suavizado temporal, el temblor entre cuadros en la banda del borde es el mismo que el de numpy (11,1 contra 11,0 y
  9,9 contra 9,6, diferencia media de 0 a 255 en display), y menor que el del Plate por el matte (15,0 y 13,1).
- El arco duro de la versión numpy no aparece.
- El `.nk` cargado con `loadToolset` da lo mismo que el Group de origen (diferencia del orden de un EXR half), con
  `temporal smoothing` apagado y prendido.

## Referencias técnicas

- `C:\Users\leg4-pc\.nuke\LGA_NodePack\LGizmos\Edges\LGA_EdgeColour.nk` — el Group (toolset). Nodos internos:
  `image_and_matte`, `inside_curve` / `inside_erode` / `inside_soft` (interior `m`), `push_colour_*` y `push_luma_*`
  (empuje por escalas), `luma_target`, `edge_colour` (Fq), `background*` (cerca del fondo), `weight_*`, `edge_result`,
  `temporal_*` (suavizado temporal), `view_switch`, `premult`, `crop_output`.
- `C:\Users\leg4-pc\.nuke\LGA_NodePack\LGizmos\Edges\LGA_BlurFusion.md` — Blur-Fusion, de donde sale la luminancia del
  borde.
- `C:\Users\leg4-pc\.nuke\LGA_NodePack\menu.py` — `load_files_in_directory()`: agrega cada `.nk` de `LGizmos/<carpeta>`
  al menú de nodos con `nuke.loadToolset`.
- `C:\Users\leg4-pc\.nuke\LGA_NodePack\+Building_Blocks\EdgeColour\build_LGA_EdgeColour.py` — generador del `.nk`
  (no se publica; lo respalda el repo `.nuke`): `build_group()`, `_build_internals()`, `_temporal()`, `_warp()`,
  `export()`. Usa `_pass()`, `_expression()`, `_merge_expression()` y `_crop_to_format()` de
  `C:\Users\leg4-pc\.nuke\LGA_NodePack\+Building_Blocks\BlurFusion\build_LGA_BlurFusion.py`. Se corre con
  `Nuke -t -i build_LGA_EdgeColour.py`.
