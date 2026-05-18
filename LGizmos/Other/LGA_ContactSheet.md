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
Burnin_0  Burnin_1  Burnin_2 ...      (Text2, uno por input)
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
3. Cablea el `ContactSheet` interno: input `j` del ContactSheet = `Burnin_j`,
   solo para las ramas conectadas. Asi el input 1 del grupo va al input 1 del
   ContactSheet (no se cruzan).
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

El checkbox **Vertical Layout for 2 Inputs** fuerza solo el caso de dos inputs
a `rows = 2` y `columns = 1`. Para cualquier otra cantidad de inputs se usa el
auto-grid normal.

## Burn-in

Cada `Burnin` (Text2) tiene su knob `disable` con la expresion
`1-parent.filename_burnin`:

- Checkbox **OFF** -> `disable = 1` -> el Text pasa la imagen sin tocar.
- Checkbox **ON** -> `disable = 0` -> el Text dibuja el nombre de archivo.

El mensaje usa `parent topnode`: `[file tail [value [topnode parent.inputN].file]]`.
`topnode` a secas se queda en el nodo `Input` interno del grupo; con
`parent.inputN`, arranca desde el input externo del grupo.

El color, el tamano y la posicion del texto se controlan desde knobs del grupo.
`Text Offset` es relativo al box original del burn-in: `0, 0` mantiene la
posicion actual; valores positivos mueven el texto hacia la derecha y abajo.
El `global_font_scale` queda fijo en `0.505`, como el script original.

## Tab Settings

Identico al de ContactSheetAuto mas el knob nuevo:

- `Resolution Multiplier` (`resMult`) - igual que el original.
- `Filename Burn-in` (`filename_burnin`) - checkbox nuevo.
- `Vertical Layout for 2 Inputs` (`vertical_two_inputs`) - con dos inputs,
  los apila verticalmente en vez de ponerlos lado a lado.
- `Text Color` (`text_color`) - color del burn-in.
- `Text Font Size` (`text_font_size`) - tamano de fuente del burn-in.
- `Text Offset` (`text_offset`) - desplazamiento X/Y relativo a la posicion
  original del texto.

## Limitaciones conocidas

- Conviene conectar y desconectar los inputs **desde el final**. Si se
  desconecta un input del medio, `sync()` cuenta los conectados contiguos
  desde 0 y puede borrar ramas que estaban mas arriba.
