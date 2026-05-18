# LGA_ContactSheet

Nodo `Group` con un contact sheet automatico, inputs dinamicos y burn-in
opcional del nombre de archivo.

## Que es

Es un `Group` de Nuke (como `LGA_Film_Projector.nk`) basado en el
"ContactSheetAuto" de `contactsheet_review.nk`. Empieza con **un solo input**
y va creando inputs nuevos a medida que el usuario conecta Reads, igual que un
`ContactSheet` suelto. Adentro del grupo, cada input pasa por un nodo `Text`
que imprime el nombre del archivo del Read conectado. Un checkbox
**Filename Burn-in** prende o apaga todos esos `Text` de una sola vez.

## Archivos

| Archivo | Rol |
|---|---|
| `LGA_ContactSheet.nk` | Toolset que se inserta desde el menu Nodes. Define el `Group`. |
| `LGA_ContactSheet_tools.py` | Logica de inputs dinamicos. Importado por los callbacks del grupo. |
| `LGA_ContactSheet.md` | Este documento. |

El `.py` queda importable porque `menu.py` hace `pluginAddPath` de la carpeta
`Other`. No aparece en el menu Nodes porque su nombre no contiene `init`.

## Estructura interna del grupo

```
Input1    Input2    Input3 ...       (se ven como 1, 2, 3 en la UI)
   |         |         |
Burnin_*  Burnin_*  Burnin_* ...      (cadena de Text2, uno activo por input)
   \________ | ________/
         ContactSheet1
              |
           Output1
```

El `.nk` se entrega con una sola rama (`Input1 -> Burnin_0 -> ContactSheet1`).
El resto lo arma el callback.

## Inputs dinamicos

Un `Group` de Nuke tiene tantos inputs como nodos `Input` haya adentro, asi
que para que crezca solo hace falta agregar/sacar nodos `Input` por codigo.

El grupo tiene dos callbacks que llaman a `LGA_ContactSheet_tools`:

- `onCreate` -> `on_create()` al crear el nodo.
- `knobChanged` -> `knob_changed()`; cuando llega el evento `inputChange`
  (se conecto o desconecto un input) corre `sync()`.

`sync()` hace lo siguiente:

1. Cuenta los inputs conectados de forma contigua desde 0.
2. Mantiene adentro `conectados + 1` ramas `Input -> Burnin` (una rama libre
   extra para poder seguir conectando). Crea las que falten, borra las que
   sobren.
3. Cablea el `ContactSheet` interno al final de la cadena `Burnin` de cada
   input conectado. Asi el input 1 del grupo va al input 1 del ContactSheet
   (no se cruzan).
4. Setea primero el knob interno `number` y despues renombra los nodos como
   `Input1`, `Input2`, `Input3`, etc. Esto evita que Nuke regenere nombres
   como `Input_1` al cambiar el numero. Tambien fija el `label` visible como
   `1`, `2`, `3`. El orden interno sigue dependiendo de `number`, en base cero
   (`0`, `1`, `2`, etc.).

Hay una guarda de reentrada (`_busy`) porque agregar o borrar nodos `Input`
vuelve a disparar `knobChanged`.

## Auto-grid

El `ContactSheet` interno calcula `rows` / `columns` / `width` / `height` con
las mismas expresiones que ContactSheetAuto, leyendo su propio `[numvalue
inputs]`. Como `sync()` cablea el ContactSheet solo con las ramas conectadas,
`inputs` refleja la cantidad real y la grilla sale correcta.

## Burn-in

Cada rama tiene varios `Text2` internos para probar distintas formas de leer
el nombre del archivo desde adentro del grupo. El knob **Filename Formula**
elige cual queda activo:

- `parent topnode` - `[file tail [value [topnode parent.inputN].file]]`
- `direct parent input` - `[file tail [value [input parent N].file ""]]`
- `metadata input/filename` - `[file tail [metadata input/filename]]`
- `python parent input` - obtiene `parent().input(N)` por Python y usa
  `nuke.filename()`.

Cada `Burnin` (Text2) tiene su knob `disable` ligado a `Filename Burn-in` y a
`Filename Formula`:

- Checkbox **OFF** -> `disable = 1` -> el Text pasa la imagen sin tocar.
- Checkbox **ON** -> queda activo solo el Text de la formula elegida.

La formula por defecto es `parent topnode`, porque `topnode` a secas se queda
en el nodo `Input` interno del grupo. Con `parent.inputN`, `topnode` arranca
desde el input externo del grupo. Mismo estilo verde, `font_size` 154,
`global_font_scale` 0.505 y `box` que el script original.

## Tab Settings

Identico al de ContactSheetAuto mas el knob nuevo:

- `Resolution Multiplier` (`resMult`) - igual que el original.
- `Filename Burn-in` (`filename_burnin`) - checkbox nuevo.
- `Filename Formula` (`filename_formula`) - selector temporal para comparar
  formulas de burn-in dentro del grupo.

## Limitaciones conocidas

- Conviene conectar y desconectar los inputs **desde el final**. Si se
  desconecta un input del medio, `sync()` cuenta los conectados contiguos
  desde 0 y puede borrar ramas que estaban mas arriba.

## Futuro

Por ahora el burn-in es de estilo fijo (identico al original). Mas adelante se
agregaran controles en el panel para configurar tamano / color / posicion del
texto.
