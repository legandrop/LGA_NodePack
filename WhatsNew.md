---
product: LGA NodePack
release_repo: legandrop/LGA_NodePack
tech_changelog: CHANGELOG.md
version_heading: "## v{v}"
platforms: [win, mac]
---
# What's new in LGA NodePack
<!-- Editable while a version is unpublished. NOT append-only. Published versions are frozen. -->

## Unreleased

## v1.49
- [new] LGA_BlurFusion, in LGizmos > Edges, cleans the colour of soft edges such as hair from a plate and its matte, so the original background no longer shows through when you comp the subject over something else; its alpha gamma control thins the edge when a bright background still glows through.
- [new] LGA_LightFromPlate, in LGizmos > ColorGrading, gives a render the lighting of the original plate while keeping the render's detail; it works on the whole frame with just the render and the plate, or inside optional masks, and can composite the result over the plate.
- [fixed] EdgeFromAlpha no longer throws a "Nothing is named red" error when you add it to a comp; comps saved earlier keep the old error until you replace the node with a fresh copy.
