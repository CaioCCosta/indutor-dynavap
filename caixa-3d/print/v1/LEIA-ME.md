# Pack v1 — relevo AMS (duas cores)

**v1 fechada (set/2026).** Variante de relevo. A outra variante oficial é [`../v1-cavas/`](../v1-cavas/).

Não use os STL unidos `box_body.stl` / `box_lid.stl` se quiser duas cores.

| Arquivo | Filamento |
|---|---|
| `corpo_cor1.stl` | **1** PETG escuro — casca + pads |
| `corpo_cor2.stl` | **2** PETG claro — tribal |
| `tampa_cor1.stl` | **1** PETG escuro — casca |
| `tampa_cor2.stl` | **2** PETG claro — tribal |

## OrcaSlicer / Bambu X1 Carbon

1. Importar o par da peça (`*_cor1` + `*_cor2`).
2. Selecionar os dois → **Assemble**.
3. Casca → Filament 1; relevo → Filament 2.
4. PETG, camada **0,2 mm**, bico **0,4 mm**, infill 15–25 %, sem suportes.
5. Corpo: **piso no bed**. Tampa: **face plana no bed** (pocket, collarinho e relevo para cima).
6. Relevo 0,8 mm = 4 camadas de cor 2.

Guia completo: [../README.md](../README.md)
