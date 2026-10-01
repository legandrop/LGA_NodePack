<p align="right"><b>English</b> · <a href="README_ES.md">Español</a></p>

<p>
  <span style="font-size:1.6em;font-weight:700;line-height:1;">LGA NODE PACK</span><br>
  <span style="font-style:italic;line-height:1;">Lega | v1.48</span><br>
</p>

**LGA Node Pack** is a simple collection of nodes for Nuke: gizmos,
groups and toolsets gathered in one place, all available from the
**Nodes** menu.

It is a library of everyday nodes: some come from public resources,
some are slightly modified, some are quick toolsets, and some are
my own nodes.

The key point of the pack is that you don't need to edit `menu.py` every time
you add a node. The loader automatically walks through the folders and
subfolders of the repository, mirrors that structure in the Nuke **Nodes** menu
and adds every compatible file it finds:

- The `.gizmo` files show up as regular nodes and are created with `nuke.createNode()`.
- The `.nk` files show up in the menu and load as toolsets.
- Folders are also added to the plugin path, so gizmos are
  available without registering each one by hand.
- If a folder already ships its own `menu.py` or `init.py`, like `pixelfudger3`
  or `spin_tools`, the pack lets it handle its own loading.

In practice, to add a gizmo, a group saved as `.nk` or a toolset,
just copy it into the matching category. After restarting
Nuke, it shows up in the menu automatically, following the folder structure.

## Installation

Copy the **LGA_NodePack** folder to **%USERPROFILE%/.nuke** and add this to Nuke's main
`init.py` file:

```python
nuke.pluginAddPath('./LGA_NodePack')
```

Expected structure:

```
.nuke/
`-- LGA_NodePack/
    |-- init.py
    |-- menu.py
    |-- LGizmos/
    |-- pixelfudger3/
    `-- spin_tools/
```

## What shows up in Nuke

The pack adds menus to the **Nodes** panel:

- **LGizmos**: the main collection, organized by category.
- **Pixelfudger3**: the original pack by Xavier Bourque, with its own menu.
- **Spin Tools**: a set of gizmos made by the SPIN VFX studio
  Keying.

The menu is built automatically from the actual contents of the folders.

## Node types

### Collected nodes

Most of the pack is made of useful nodes I found, saved and
sorted by category. Many keep their original name to credit
the author or the resource they came from.

### Modified nodes

Some external nodes have small changes to fit the way the pack works.
When that applies, the name ends with **`_LGA`**.

Examples:

- `apColorSampler_LGA`
- `DropShadow_LGA`
- `Fractal_Blur_LGA`
- `PSDMerge_LGA`
- `Vanishing Point_LGA`

### Quick toolsets

Nodes that start with **`LGAt_`** are simple setups saved as
toolsets. They are not meant to replace larger tools; they are shortcuts to build
node structures that get used often.

Examples:

- `LGAt_CopyCat_2`
- `LGAt_CopyCat_3`
- `LGAt_Freq Sep`
- `LGAt_HSV_Sandwich`
- `LGAt_OCIO_Sandwich`
- `LGAt_SmartVector`
- `LGAt_mocha_stab_precomp`

### Own nodes

Nodes that start with **`LGA_`** are my own nodes, or versions made
to solve more specific needs.

Examples:

- `LGA_ContactSheet`
- `LGA_Film_Projector`
- `LGA_Film_Projector_Real`
- `LGA_iCard3D`
- `LGA_Paralax2D`
- `LGA_chromAB`
- `LGA_VenetianBlinds`

Some of them have their own documentation inside the pack:

- `LGizmos/Other/LGA_ContactSheet.md`
- `LGizmos/Other/LGA_Film_Projector_Real.md`
- `LGizmos/Distort/LGA_iCard3D.md`

## Main categories

The **LGizmos** folder is organized by use:

- **3D**: relight, cam tools, shaders and 3D utilities.
- **Aberration**: chromatic aberration, moire, glitch and optical effects.
- **Animation**: shake, parallax and motion blur from transforms.
- **Clean_and_Beauty**: cleanplates, CopyCat, paint and reconstruction.
- **ColorGrading**: relight, deflicker, glow and color setups.
- **Defocus-Sharp**: blur, defocus, sharpen and frequency separation.
- **Despill**: despill, unspill and spill replace.
- **Distort**: STMap, PowerPin, iTransform, SmartVector and distortions.
- **Edges**: edge extend, edge fill, roughen and edge tools.
- **Generate**: generative elements and effects.
- **Keying**: keyers, alpha clean, lightwrap and gradients.
- **Other**: assorted nodes such as contact sheets, projector, drop shadow and PSD.
- **Rebuild_frames**: frame reconstruction.
- **Track**: reference pin and stabilize/precomp.
- **Utilities**: small utilities.

