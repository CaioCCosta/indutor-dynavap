# Caixa 3D — indutor Dynavap (A14) **v1 fechada**

**v1 fechada (set/2026).** OpenSCAD em `caixa-3d/`, [dimensions.json](../maquetes/dimensions.json) **v1.0** (92×58×65 mm + tampa 8 mm), ímã Ø12×3 em **X=−14**. Mesma caixa, **duas variantes oficiais** de acabamento tribal.

| Variante | Pasta | Uso |
|---|---|---|
| **Lisa** | [`print/v1-lisa/`](print/v1-lisa/) | Sem tribal; corpo + pads |
| **Relevo AMS** | [`print/v1/`](print/v1/) | Duas cores no Orca (Assemble) |
| **Cavas + cola** | [`print/v1-cavas/`](print/v1-cavas/) | Casca cavada 0,6 mm; inserts 0,5 mm colados |

Não misture os dois packs no mesmo Assemble.

## Arquivos — relevo AMS

Pasta: [`print/v1/`](print/v1/)

| Arquivo | O que é | Filamento Orca/Bambu AMS |
|---|---|---|
| [`corpo_cor1.stl`](print/v1/corpo_cor1.stl) | Casca do corpo + 4 pads | **1** PETG escuro |
| [`corpo_cor2.stl`](print/v1/corpo_cor2.stl) | Relevo tribal (5 faces) | **2** PETG claro |
| [`tampa_cor1.stl`](print/v1/tampa_cor1.stl) | Casca da tampa | **1** PETG escuro |
| [`tampa_cor2.stl`](print/v1/tampa_cor2.stl) | Relevo tribal do topo | **2** PETG claro |

Fallback **uma cor / lisa:** preferir [`print/v1-lisa/`](print/v1-lisa/) (`corpo_liso.stl` + `tampa_lisa.stl`). Alternativa unida com relevo: [`stl/box_body.stl`](stl/box_body.stl) · [`stl/box_lid.stl`](stl/box_lid.stl).

### OrcaSlicer / Bambu X1 Carbon

Imprima **corpo e tampa em placas separadas** (ou as duas na cama se couber).

1. **Add** `*_cor1.stl` e `*_cor2.stl` da mesma peça.
2. Selecione os dois → clique direito → **Assemble** (um objeto, duas partes).
3. Parte casca → **Filament 1**; parte relevo → **Filament 2**.
4. Perfil: **PETG**, camada **0,2 mm**, bico **0,4 mm**, infill **15–25 %**, sem suportes.
5. Orientação: corpo **piso no bed**; tampa **face plana no bed** (pocket, collarinho e relevo para cima).
6. O relevo tem **0,8 mm** = **4 camadas** de cor 2. Flush AMS no padrão.

Não use os STL unidos (`box_body.stl` / `box_lid.stl`) se quiser duas cores.

## Arquivos — cavas + cola

Pasta: [`print/v1-cavas/`](print/v1-cavas/) · [LEIA-ME](print/v1-cavas/LEIA-ME.md)

Cava **0,6 mm**; inserts **0,5 mm** deitados (`decais.stl` ou `decal_*.stl`). Imprime casca e tribal em placas **separadas** e cola.

## Gerar / regenerar STL

```powershell
cd caixa-3d
.\export.ps1
```

Pipeline: OpenSCAD gera `*_base.stl` → `assemble_embossed.py` gera `print/v1-lisa/`, `print/v1/` (AMS) e `print/v1-cavas/`.

Requer: [OpenSCAD](https://openscad.org/), Python com `trimesh`, `manifold3d`, `scikit-image`, `Pillow`.

| Arquivo | Função |
|---|---|
| `box_params.scad` | Medidas (corpo, furos, tubo, ímã, EMBOSS_H) |
| `box_body.scad` / `box_lid.scad` | Casca base imprimível |
| `box_emboss.scad` | Referência de layout do relevo (assembly em Python) |
| `decals/vectorize_decals.py` | JPG → STL de relevo 0,8 mm |
| `assemble_embossed.py` | Une base + decals (v1); difference cavas + inserts (`print/v1-cavas`) |
| `export.ps1` | Compila tudo |

## Decals tribais (alto relevo)

| Face | Decal | Arquivo |
|---|---|---|
| Laterais (frente, trás, esq., dir.) | **1** — asa horizontal | `decals/tribal_1_*` |
| Tampa (topo) | **2** — preenche a área livre (sem o bocal); ímã no centro | `decals/tribal_2_*` |
| Base (fundo) | **3** — chama no eixo longo | `decals/tribal_3_*` + **4 pads** 1,0 mm na casca (cor 1) |

- Altura do relevo: **0,8 mm** (`EMBOSS_H`)
- Keepouts: furos do painel, jack, fusível, vents, pocket ímã, collarinho, parafusos M3
- Regenerar só os relevos: `python decals/vectorize_decals.py` depois `python assemble_embossed.py`

### Cavidade do ímã

- Posição: **centro da área livre** da tampa (`X≈−14`), longe do tubo (`X≈28`)
- Pocket: **Ø12,6 × 3,2 mm** (ímã Ø12×3 + folga/cola)
- Fundo fechado — cola cianoacrilato ou epóxi 5 min
- Para ímã **12×6**: em `box_params.scad` defina `MAGNET_H = 6` e reexporte (gera boss local)

## Ímã de descanso (Dynavap upright)

Segura o M7 pelo cap metálico entre sessões. **Não** é a trava de profundidade do tubo (essa é o fundo de vidro).

| Exemplo | Spec | Nota | Link |
|---|---|---|---|
| VapOven Cooling Magnet | **12×3** N52 **diametral** (ou 12×6) | Referência Dynavap | [vapoven.com](https://vapoven.com/product/vapoven-cooling-magnet/) |
| DynaMag oficial | **12,6×1,5** diametral | Cabe no pocket com cola | [dynavap.com](https://www.dynavap.com/products/the-dynamag) |
| MadMag | **14×2** | Mais forte; mude `MAGNET_D=14` | [madheaters](https://madheaters.co.uk/products/madmag) |
| BR (axial) | **12×3 N35** ~1–2,5 kg tração ideal | Sobra p/ ~30 g do M7 | [Polo Magnético](https://www.polomagnetico.com.br/ima-de-neodimio/disco/ima-de-neodimio-12-x-3-mm-n35) · [Lorben](https://www.lorben.com.br/10-pecas-ima-neodimio-12x3mm-disco-pastilha-super-forte) |

**Preferir diametral** (cap centra e fica em pé). Axial funciona no peso, mas tombear é mais fácil. Não aqueça o ímã acima de **~80 °C**.

## Impressão sugerida (OrcaSlicer / X1 Carbon)

| Parâmetro | Valor |
|---|---|
| Material | **PETG** mínimo; **ASA/ABS** melhor perto do tubo |
| Camada | 0,2 mm |
| Preenchimento | 15–25 % |
| Corpo | Base no bed (Z=piso); pads 1 mm nos cantos (cor 1) |
| Tampa | Face plana no bed; pocket, collarinho e relevo para cima |
| Suportes | Desnecessário na cavidade ≤3,2 mm |
| Relevo tribal | Filamento **2**; nozzle **0,4 mm**; pontas finas podem arredondar |
| Parafusos | M3 nos 4 cantos (furos 3,4 mm; posts com piloto Ø2,4) |

## Encaixe com o BOM

Furos do painel (frente → traseira), alinhados à lista A5–A9 / A15:

| Item | Peça | Furo / rasgo |
|---|---|---|
| A7 | Gangorra redonda KCD1-106N | **Ø20,2 mm** |
| A5 | Pot B10K WH148 | **Ø7,6 mm** |
| A6 | Botão momentâneo 19 mm | **Ø19,2 mm** |
| A9 | LED 5 mm (×2) | **Ø5,2 mm** |
| A15 | Jack DC-022 P4 | **Ø8,2 mm** (traseira) |
| A8 | Porta-fusível 5×20 | **Ø13,2 mm** (traseira) |

- Tubo ensaio 16×42 (de 16×100) + cama cerâmica 24×24 sob o fundo
- Bobina + O-ring 15×3 no collarinho
- ZVS + MOSFET + Nano + pot + botão + rocker nos furos do painel
- Ventilação traseira 4×10×4 mm — não feche hermético
- Ímã colado na cavidade da tampa
- Fonte 12 V 10 A **fora** da caixa (só o jack entra)

## Alternativas (legado)

Se quiser partir de um design comunitário e editar:

- [acsdog — Printables](https://www.printables.com/model/1067938-dynavap-induction-heater-box-with-pwm) (domínio público, FreeCAD)
- [jnico — Thingiverse](https://www.thingiverse.com/thing:4171627)

A caixa paramétrica deste repo já inclui o layout v3.2 + ímã; prefira ela.

## Visualizar

[Viewer 3D](../maquetes/viewer.html) · [MONTAGEM.md](../maquetes/MONTAGEM.md)
