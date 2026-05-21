<p>
  <span style="font-size:1.6em;font-weight:700;line-height:1;">LGA NODE PACK</span><br>
  <span style="font-style:italic;line-height:1;">Lega | v1.44</span><br>
</p>

**LGA Node Pack** es una coleccion simple de nodos para Nuke: gizmos,
groups y toolsets reunidos en un solo lugar para tenerlos disponibles desde el
menu **Nodes**.

Es una libreria de nodos de uso diario: algunos vienen de recursos publicos,
otros estan levemente modificados, otros son toolsets rapidos, y otros son
nodos propios.

La parte importante del pack es que no hace falta editar `menu.py` cada vez que
se agrega un nodo. El cargador recorre automaticamente las carpetas y
subcarpetas del repositorio, replica esa estructura en el menu **Nodes** de
Nuke y agrega cada archivo compatible que encuentra:

- Los `.gizmo` aparecen como nodos normales y se crean con `nuke.createNode()`.
- Los `.nk` aparecen en el menu y se cargan como toolsets.
- Las carpetas tambien se agregan al plugin path, asi los gizmos quedan
  disponibles sin registrar cada uno a mano.
- Si una carpeta ya trae su propio `menu.py` o `init.py`, como `pixelfudger3`
  o `spin_tools`, el pack la deja manejar su propia carga.

En la practica, para sumar un gizmo, un group guardado como `.nk` o un toolset,
solo hay que copiarlo dentro de la categoria correspondiente. Al reiniciar
Nuke, aparece automaticamente en el menu siguiendo la estructura de carpetas.

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
- **Spin Tools**: set de gizmos creado por el estudio SPIN VFX
  Keying.

El menu se arma automaticamente a partir del contenido real de las carpetas.

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

Los nodos que empiezan con **`LGA_`** son nodos propios o versiones creadas
para resolver necesidades mas especificas.

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

