> **Regla de documentacion**: este archivo describe el estado actual del codigo. No es un historial de cambios, changelog ni bitacora temporal.
> **Regla de documentacion**: este archivo debe incluir una seccion de referencias tecnicas con rutas completas a los archivos mas importantes relacionados, y para cada archivo nombrar las funciones, clases o metodos clave vinculados a este tema.

# LGA_LightFromPlate

Nodo `Group` (se distribuye como `.nk`, editable por dentro) que le devuelve a un render la **iluminación del Plate**: separa cada imagen en luz (bajas frecuencias) y detalle (altas frecuencias) y arma el resultado con la luz del Plate y el detalle del render. Sirve para un render que cambió la textura de una cara (envejecimiento, retoque, generación) y perdió la luz del plano original.

Funciona con sólo dos entradas, el render y el Plate, y en ese caso actúa sobre **todo el cuadro**. Las máscaras son opcionales: limitan dónde se mide y dónde se aplica la luz. También puede componer el resultado sobre el Plate.

## Inputs

- **render** (0) — el render al que se le corrige la luz. Es la entrada principal: sus demás canales pasan sin tocar.
- **plate** (1) — el Plate original, del mismo tamaño que el render.
- **skin** (2, opcional) — máscara de la zona donde se mide la luz (la piel). Se binariza en 0,5. Sin conectar, la luz se mide y se aplica en todo el cuadro.
- **area** (3, opcional) — zona donde se aplica el resultado. Se binariza en 0,5 y se une con `skin`. Sin conectar, la zona es la misma máscara `skin`.
- **matte** (4, opcional) — matte para componer sobre el Plate, o matte de cabeza para medir `Head width`.

Las tres máscaras se leen por alfa o por rojo, a elección. Un PNG gris entra sólo por rojo: si se elige alfa y la entrada no tiene canal alfa, el nodo usa el rojo, así una máscara gris funciona con los valores de fábrica.

## Fórmula

Todo se calcula en luz lineal, a partir de los **valores del archivo** tomados como sRGB (ver «Colorspace»). `G` = render, `P` = Plate, `S` = máscara de piel binaria (1 en todo el cuadro si no hay máscara), `a` = `Amount`, `gauss(x, s)` = desenfoque gaussiano de sigma `s`.

```
sigma  = max(1, Head width * clamp(Cutoff, 0.25, 16) / 100)

baja(X) = gauss(X * S, sigma) / max(gauss(S, sigma), 1e-4)        luz de X medida solo dentro de S
gan     = log(baja(P)) - log(baja(G))                             ganancia de luz, en logaritmo

c       = smoothstep((gauss(S, 2*sigma) - 0.3) / 0.6)             1 dentro de S, 0 lejos
relleno = gauss(gan * c, 3*sigma) / max(gauss(c, 3*sigma), 1e-4)
gan     = c * gan + (1 - c) * relleno                             la ganancia se extiende suave fuera de S

det     = (log P - log baja(P)) - (log G - log baja(G))           diferencia de detalle entre Plate y render
m_luz   = gauss(erosion(S, disco 4 px), 8)
L       = G * exp(gan + (1 - a) * m_luz * det)

m_zona  = gauss(dilatacion(area o S, disco Area grow), Area soften)
salida  = m_zona * L + (1 - m_zona) * G                           donde m_zona vale 0 sale el render sin tocar
```

Con `Amount = 1` y sin máscaras se reduce a `salida = baja(P) * G / baja(G)`: la luz del Plate con el detalle del render. En general, `salida = baja(P) * (G / baja(G))^a * (P / baja(P))^(1-a)`: con `Amount = 0` vuelve el Plate y con más de 1 se exagera el detalle del render. Todos los logaritmos se acotan por abajo en `1e-5`. El resultado se acota entre 0 y 1 en valores de archivo dentro de la zona.

Los gaussianos se calculan con el núcleo de OpenCV para imágenes float (radio `floor(rint(8*sigma + 1) / 2)`, o sea 4 sigmas, y borde repetido), con dos `Convolve` de una dimensión cada uno. El `Blur` de Nuke corta el núcleo a 3,53 sigmas y no da el mismo resultado lejos de la máscara, donde el relleno divide por pesos muy chicos. La erosión y la dilatación usan el disco de `cv2.getStructuringElement(MORPH_ELLIPSE)`.

## Controles (tab LightFromPlate)

**Light from Plate**

- **Amount** — cuánto detalle del render queda. 1 = luz del Plate con detalle del render; 0 = dentro de la piel vuelve el Plate; más de 1 exagera el detalle. Valor habitual: 1.
- **Cutoff (% head width)** — corte entre luz y detalle, en % del ancho de cabeza. Se acota entre 0,25 y 16. Valor habitual: 2.
- **Head width (px)** — ancho de la cabeza en píxeles (primera a última columna del matte de cabeza). Se escribe, se anima o se mide con el botón. Por defecto 1000.
- **Sigma (px)** *(sólo lectura)* — el sigma que resulta de `Head width` y `Cutoff`.
- **Measure from / Range / Measure head width** — mide el ancho del matte de la entrada elegida (`matte`, `skin` o `area`, umbral 0,5) en cada cuadro del rango y lo deja animado en `Head width`. El resultado de la medición queda escrito debajo del botón; no abre ningún cartel. Un cuadro con el matte vacío queda en 0 (sigma 1) y el texto dice cuántos hubo. Si el matte está vacío en todo el rango (por ejemplo, el canal elegido no tiene datos), `Head width` no se toca y el texto empieza con «not measured». El `CurveTool` que mide se crea dentro del grupo sólo mientras dura la medición y se borra al terminar: uno permanente imprimía en la consola un aviso de Nuke («Setting knob values from validate…») cada vez que algo lo validaba. Ese aviso sigue saliendo una vez al apretar el botón y no cambia la medición.

**Masks (optional)**

- **Skin mask from** — `alpha` o `red` de la entrada `skin`, o `render alpha` (el alfa del render, sin conectar nada). Con `alpha` y una entrada sin canal alfa se usa `red`; con `render alpha` y un render sin alfa no hay máscara (todo el cuadro).
- **Area mask from** — `alpha` o `red` de la entrada `area`. Con `alpha` y una entrada sin canal alfa se usa `red`.
- **Area grow (px)** — cuánto se agranda la zona antes de suavizarla (disco). Valor habitual: 6.
- **Area soften (px)** — sigma del borde suave de la zona. Valor habitual: 8.

**Colorspace**

- **Inputs are raw file values** — marcar si los `Read` están en raw. Desmarcado, el nodo convierte del espacio de trabajo a `Files colorspace`, hace la cuenta y vuelve.
- **Files colorspace** — el colorspace con el que se leyeron el render y el Plate. Tiene que ser el mismo en los dos `Read`. Por defecto `Output - Rec.709` (config ACES 1.2). Al crear el nodo o abrir el script, si el nombre guardado no existe en el config OCIO activo, se elige el rol `color_picking` (en los configs que trae Nuke es un sRGB: `sRGB` en `nuke-default`, `sRGB Encoded Rec.709 (sRGB)` en los ACES 1.3 y 2.0), así el nodo recién creado renderiza en cualquier config. Conviene igual comprobar que coincida con el de los `Read`.

**Over Plate**

- **Composite over Plate** — compone el render corregido sobre el Plate con el matte elegido. Desmarcado sale el render completo. La mezcla se hace siempre en luz lineal: sin `raw`, en el espacio de trabajo; con `raw`, sobre los valores del archivo pasados a lineal con la curva sRGB. Así el borde del matte y `Mix` se ven igual en los dos modos.
- **Matte** — `render alpha`, `matte input alpha` o `matte input red`. Con `matte input alpha` y una entrada sin canal alfa se usa el rojo; con `render alpha` y un render sin alfa, el render entero va sobre el Plate.
- **Mix** — opacidad del render sobre el Plate (multiplica al matte).

**View** — `result`, `area mask` (la zona de aplicación suave) o `light gain` (la ganancia de luz por canal; 1 = sin cambio).

## Uso

1. Leer el render y el Plate con el mismo colorspace y conectarlos a `render` y `plate`. Con eso ya funciona, sobre todo el cuadro.
2. Ajustar `Head width` al ancho de la cabeza en píxeles, o conectar un matte de cabeza a `matte` y apretar `Measure head width`.
3. Para limitar el efecto a la piel, conectar una máscara a `skin` (o elegir `render alpha`). Sin máscara la luz del Plate se aplica también al pelo, la ropa y el fondo: si el render cambió el color del pelo, las bajas frecuencias vuelven al color del Plate.
4. Para componer sobre el Plate, marcar `Composite over Plate` y elegir el matte.

## Limitaciones

- El render y el Plate tienen que tener el mismo formato y ocupar el cuadro entero.
- Con un colorspace que se invierte con tablas (por ejemplo `Output - Rec.709` del config ACES 1.2) la ida y vuelta de color de Nuke no es exacta: leer y volver a escribir un archivo sin ningún nodo ya cambia el valor. Dentro de la zona el nodo suma una ida y vuelta más. Con un colorspace de matriz y curva (`Utility - sRGB - Texture`) o con las entradas en raw la cuenta es exacta.
- `Files colorspace` guarda un nombre del config OCIO. En otro config, si el nombre no existe, el nodo toma el rol `color_picking` (ver «Colorspace»), que puede no ser el colorspace de los `Read`: hay que revisarlo. Si un config propio no tiene ese rol ni ningún sRGB conocido, hay que elegirlo a mano o marcar `raw`.
- Fuera de la zona sale el render de entrada sin tocar. El corte es `m_zona > 1e-5` y no 0 porque `Convolve` deja ruido numérico donde la máscara vale cero.
- El costo crece con el sigma: con `Cutoff` 2 tarda alrededor de medio segundo por cuadro a 2K en CPU; con `Cutoff` 16 puede tardar varios segundos.
- No usa GPU ni BlinkScript.

## Referencias técnicas

- **`C:\Users\leg4-pc\.nuke\LGA_NodePack\LGizmos\ColorGrading\LGA_LightFromPlate.nk`** — el grupo. Nodos internos clave:
  - `ToFile_render`, `ToFile_plate`, `FromFile` (`OCIOColorSpace`): ida y vuelta entre el espacio de trabajo y los valores de archivo; se desactivan con `raw`. `ToFile_plate` y `FromFile` copian el colorspace de `ToFile_render` por expresión.
  - `ToFile_render.onCreate` (función `_lga_lfp_colorspace`): si `out_colorspace` no existe en el config activo, elige `color_picking` (o el primer sRGB conocido que exista).
  - `S`, `Area_bin`, `Matte_sel`, `Measure_bin`: variables temporales `ha`/`hb` (`lsearch` sobre `channels` en TCL) que detectan si la entrada tiene canal alfa y, si no, leen el rojo.
  - `Lin_render`, `Lin_plate`, `A_sRGB` (`Expression`): curva sRGB en los dos sentidos.
  - `S` (`Expression`): máscara de piel binaria, o 1 si no hay máscara.
  - `Blur_plate_*`, `Blur_render_*`, `LowPlate`, `LowRender`: luz de cada imagen por convolución normalizada dentro de `S`.
  - `LGain`, `C`, `Blur_fill_*`, `Fill`, `LGain_ext`: ganancia de luz y su extensión fuera de `S`.
  - `S_inv_dil`, `S_erode`, `MLit_*`, `LDet`, `Exponente`, `L`: rama de detalle (sólo se evalúa si `Amount` no es 1).
  - `Area_bin`, `DiscoGrow`, `Area_dil`, `MApp_*`: zona de aplicación.
  - `Mezcla_lineal`, `Result`: mezcla y salida sin tocar fuera de la zona.
  - `Matte_sel`, `Over_lin_result`, `Over_lin_plate`, `Over_plate`, `Over_sRGB`, `Final_sel`, `Out_rgb`: composición sobre el Plate (los tres `Over_*` de curva sRGB sólo actúan con `raw`).
  - `Measure_sel`, `Measure_bin`: matte binario que mide el botón `measure`. El script del knob (función `_lga_lfp_medir`, envuelta para no dejar variables en el espacio global de Nuke) crea un `CurveTool` temporal `HeadMeasure_tmp` en Auto Crop sobre `Measure_bin`, lo ejecuta en el rango, lee `autocropdata` y lo borra.
  - `View_area`, `View_gain`, `View_sel`: vistas de control.
- **`C:\Users\leg4-pc\.nuke\LGA_NodePack\menu.py`** — `load_files_in_directory()`: agrega el `.nk` al menú `LGizmos > ColorGrading` con `nuke.loadToolset`.
