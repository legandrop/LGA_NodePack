<p>
  <span style="font-size:1.6em;font-weight:700;line-height:1;">LGA NODE PACK</span><br>
  <span style="font-style:italic;line-height:1;">Lega | v1.32</span><br>
</p>

**LGA Node Pack** es una coleccion simple de nodos para Nuke: gizmos,
groups y toolsets reunidos en un solo lugar para tenerlos disponibles desde el
menu **Nodes**.

Es una libreria de nodos de uso diario: algunos vienen de recursos publicos,
otros estan levemente modificados, otros son toolsets rapidos, y otros son
nodos propios.

## Instalacion

Copiar la carpeta **LGA_NodePack** a **%USERPROFILE%/.nuke** y agregar en el
`init.py` principal de Nuke:

```python
nuke.pluginAddPath('./LGA_NodePack')
```

Estructura esperada:

```
.nuke/
`-- LGA_NodePack/
    |-- init.py
    |-- menu.py
    |-- LGizmos/
    |-- pixelfudger3/
    `-- spin_tools/
```

## Que aparece en Nuke

El pack agrega menus al panel **Nodes**:

- **LGizmos**: la coleccion principal, organizada por categorias.
- **Pixelfudger3**: pack original de Xavier Bourque, con menu propio.
- **Spin Tools**: set de gizmos organizado por 3D, Color, Comp, Effects y
  Keying.

El menu se arma automaticamente. Si se agrega un `.gizmo` o `.nk` dentro de una
carpeta cargada, aparece en Nuke siguiendo la estructura de carpetas.

## Tipos de nodos

### Nodos recopilados

La mayor parte del pack esta formada por nodos utiles encontrados, guardados y
ordenados por categoria. Muchos conservan su nombre original para mantener
referencia del autor o del recurso de donde salieron.

### Nodos modificados

Algunos nodos externos tienen pequenos cambios para adaptarlos al uso del pack.
Cuando aplica, el nombre termina con **`_LGA`**.

Ejemplos:

- `apColorSampler_LGA`
- `DropShadow_LGA`
- `Fractal_Blur_LGA`
- `PSDMerge_LGA`
- `Vanishing Point_LGA`

### Toolsets rapidos

Los nodos que empiezan con **`LGAt_`** son setups simples guardados como
toolsets. No buscan reemplazar herramientas grandes; son atajos para crear
estructuras de nodos que se usan seguido.

Ejemplos:

- `LGAt_CopyCat_2`
- `LGAt_CopyCat_3`
- `LGAt_Freq Sep`
- `LGAt_HSV_Sandwich`
- `LGAt_OCIO_Sandwich`
- `LGAt_SmartVector`
- `LGAt_mocha_stab_precomp`

### Nodos propios

Los nodos que empiezan con **`LGA_`** son nodos hechos o armados por Lega para
resolver necesidades mas especificas.

Ejemplos:

- `LGA_ContactSheet`
- `LGA_Film_Projector`
- `LGA_Film_Projector_Real`
- `LGA_iCard3D`
- `LGA_Paralax2D`
- `LGA_chromAB`
- `LGA_VenetianBlinds`

Algunos tienen documentacion propia dentro del pack:

- `LGizmos/Other/LGA_ContactSheet.md`
- `LGizmos/Other/LGA_Film_Projector_Real.md`
- `LGizmos/Distort/LGA_iCard3D.md`

## Categorias principales

La carpeta **LGizmos** esta ordenada por uso:

- **3D**: relight, cam tools, shaders y utilidades 3D.
- **Aberration**: aberracion cromatica, moire, glitch y efectos opticos.
- **Animation**: shake, parallax y motion blur desde transforms.
- **Clean_and_Beauty**: cleanplates, CopyCat, paint y reconstruccion.
- **ColorGrading**: relight, deflicker, glow y setups de color.
- **Defocus-Sharp**: blur, defocus, sharpen y separacion de frecuencias.
- **Despill**: despill, unspill y spill replace.
- **Distort**: STMap, PowerPin, iTransform, SmartVector y deformaciones.
- **Edges**: edge extend, edge fill, roughen y herramientas de bordes.
- **Generate**: elementos generativos y efectos.
- **Keying**: keyers, alpha clean, lightwrap y gradients.
- **Other**: nodos varios como contact sheets, projector, drop shadow y PSD.
- **Rebuild_frames**: reconstruccion de frames.
- **Track**: reference pin y estabilizado/precomp.
- **Utilities**: utilidades chicas.

## Para mantener el pack

- Agregar gizmos o toolsets dentro de la categoria correspondiente.
- Usar prefijo **`LGA_`** para nodos propios.
- Usar prefijo **`LGAt_`** para toolsets simples.
- Usar sufijo **`_LGA`** cuando sea una modificacion de un nodo externo.
- Mantener las carpetas con `menu.py` propio, como Pixelfudger o Spin Tools,
  separadas.
- Si un nodo necesita explicacion larga, agregar un `.md` al lado del `.nk` o
  `.gizmo` en vez de inflar este README.

## Resumen

Este repositorio es una caja de nodos para comp: liviana, directa y facil de
extender. El valor esta en tener los nodos ordenados, disponibles desde el menu
de Nuke y con una convencion minima para distinguir que es propio, que es un
toolset rapido y que viene de otro lado con modificaciones.
