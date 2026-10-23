> **Regla de documentacion**: este archivo describe el estado actual del codigo. No es un historial de cambios, changelog ni bitacora temporal.
> **Regla de documentacion**: este archivo debe incluir una seccion de referencias tecnicas con rutas completas a los archivos mas importantes relacionados, y para cada archivo nombrar las funciones, clases o metodos clave vinculados a este tema.

# LGA_BlurFusion

Nodo `Group` (se distribuye como `.nk`, editable por dentro) que estima el **color del frente** en los bordes
semitransparentes (pelo, motion blur) a partir del Plate y un matte, sin placa limpia: el color del fondo se estima del
mismo Plate. Así, al componer el sujeto sobre otra cosa, el fondo original no se trasluce en el borde. Es el método de
*Approximate Fast Foreground Colour Estimation* (Marco Forte y François Pitié, ICIP 2021), armado con nodos nativos.

Menú: **LGizmos > Edges > LGA_BlurFusion** (se pega con `nuke.loadToolset`, como los demás `.nk` del pack).

## Inputs

- **Source** (0) — el Plate; se usa su rgb.
- **Matte** (1) — el matte en su **alpha**. Sin conectar, se usa el alpha del Source. Un matte que viene en rgb (un PNG
  gris) hay que pasarlo antes a alpha.

## Fórmula

Todo en el espacio de trabajo del script (luz lineal en un proyecto normal). `I` = Plate, `a` = matte recortado a [0, 1]
y elevado a `alpha gamma`. Una pasada, con un blur de caja de ancho `r` (filtro `box` del Blur):

```
F^ = blur(Fsrc · a) / (blur(a) + eps)              color medio del frente cercano
B^ = blur(Bsrc · (1 − a)) / (blur(1 − a) + eps)    color medio del fondo cercano
F  = F^ + a · (I − a · F^ − (1 − a) · B^)          corrección por la ecuación de mezcla
```

- Pasada 1: `Fsrc = Bsrc = I`, `r = large size` (90).
- Pasada 2: `Fsrc` = F de la pasada 1, `Bsrc` = B^ de la pasada 1, `r = small size` (6).
- Salida: rgb = F de la pasada 2 premultiplicado por `a`, alpha = `a`. Con `premultiply` apagado sale F sin
  premultiplicar.

Es el esquema del código de referencia de los autores (`FB_blur_fusion_foreground_estimator_2`). Diferencias
deliberadas: la caja del Blur de Nuke es simétrica (ancho `r`, medio peso en los extremos); numerador y denominador se
recortan al formato con negro afuera para que el promedio quede normalizado en el borde del cuadro (por eso el fondo se
divide por `blur(1 − a)` y no por `1 − blur(a)`); y en vez de recortar F a [0, 1] sólo se llevan a cero los negativos,
porque en lineal los brillos pasan de 1. Los Blur fuerzan `quality` por encima del tamaño: con la de fábrica (15) Nuke
calcula las cajas grandes a menor resolución.

## Controles

| Knob | Default | Qué hace |
|---|---|---|
| `large size` | 90 | Ancho de la caja de la pasada 1. |
| `small size` | 6 | Ancho de la caja de la pasada 2. |
| `alpha gamma` | 1 | `a' = a^gamma` antes de Blur-Fusion y en el alpha de salida; 0 y 1 no cambian. |
| `premultiply` | on | Salida premultiplicada por el matte. |
| `clamp negatives` | on | Negativos a cero (no recorta arriba). |
| `epsilon` | 1e-5 | Se suma a los divisores. |

Los tooltips están en castellano.

### Alpha gamma

Al componer en luz lineal, un fondo mucho más brillante que el sujeto (cielo detrás de pelo a contraluz) entra en
proporción al alpha. Si el matte marca más cobertura de la que hay en el pelo ralo, ese exceso se ve como un velo claro
aunque Blur-Fusion corrija el color. Subir `alpha gamma` afina los semitransparentes y saca el velo. Medido en un plano
de pelo a contraluz con un matte de video: con 2.0 el pelo total baja al 96 % y el de la franja semitransparente al 72 %,
y el temblor del alpha entre cuadros no cambia en valor absoluto. Entre 1.6 y 2.0 es un buen rango para ese caso; más
arriba se pierde pelo suelto. Con un matte que ya es fiel en lineal, dejarlo en 1.

## Rendimiento

Todo CPU (Blur, Expression, MergeExpression, Copy, Crop, Premult). En UHD (3840×2160), Nuke 17 en modo terminal: unos
0,23 s por cuadro con cajas 90/6, contra 0,19 s de un Read + Premult + Write del mismo cuadro.

## Verificación

- Contra una implementación numpy de las mismas fórmulas, sobre una imagen sintética de 640×400: diferencia máxima 7e-7
  (premultiplicado, sin premultiplicar y con el matte por el input Matte) y 3e-7 con `alpha gamma` 2.
- El `.nk` cargado con `loadToolset` da exactamente lo mismo que el Group de origen, en la imagen sintética y en un
  cuadro UHD real.

## Referencias técnicas

- `C:\Users\leg4-pc\.nuke\LGA_NodePack\LGizmos\Edges\LGA_BlurFusion.nk` — el Group (toolset), con los nodos internos
  `image_and_matte` (clamp y gamma del matte), `weight_*`, `crop_*`, `blur_*`, `mean_*` (medias locales),
  `rest_*` y `fg_*` (corrección), `clamp_*`, `premult` y `crop_output`.
- `C:\Users\leg4-pc\.nuke\LGA_NodePack\menu.py` — `load_files_in_directory()`: agrega cada `.nk` de `LGizmos/<carpeta>`
  al menú de nodos con `nuke.loadToolset`.
- `C:\Users\leg4-pc\.nuke\LGA_NodePack\+Building_Blocks\BlurFusion\build_LGA_BlurFusion.py` — generador del `.nk`
  (no se publica; lo respalda el repo `.nuke`): `build_group()`, `_build_internals()`, `_pass()`, `_local_mean()`,
  `export()`. Se corre con `Nuke -t -i build_LGA_BlurFusion.py`.
