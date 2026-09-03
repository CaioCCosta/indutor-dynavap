# Melhorias — v1 fechada e backlog v2

A **v1 desktop** está fechada (set/2026): caixa [lisa](../caixa-3d/print/v1-lisa/), [relevo AMS](../caixa-3d/print/v1/) ou [cavas](../caixa-3d/print/v1-cavas/), furos alinhados ao BOM, firmware lento, fonte 12 V 10 A na tomada.

O [visualizador](viewer.html) e [dimensions.json](dimensions.json) descrevem essa caixa. Não edite FreeCAD/acsdog para a v1.

---

## Já na v1 (não refazer)

- Painel: gangorra redonda Ø20,2 · pot Ø7,6 · botão Ø19,2 · LEDs Ø5,2
- Traseira: jack Ø8,2 · porta-fusível 5×20 Ø13,2 · vents 4×10×4
- Tampa: bocal à direita, ímã X=−14 no centro do tribal
- Tribal opcional: lisa · relevo AMS · cavas + cola
- TMP36 no dissipador, fios 16 AWG curtos, tubo ensaio + cama 24×24 — ver [MONTAGEM.md](MONTAGEM.md)

---

## Ainda vale na montagem (não é CAD)

| Item | Ação |
|---|---|
| Ventilação | Não colar a tampa hermética; não tape os vents |
| TMP36 | Pasta térmica no dissipador do ZVS; Serial `Ts=` plausível |
| Fios 12 V | Loop curto jack → fusível → gangorra → MOSFET → ZVS |
| LED D6 | Apontar para o tubo, não para o olho |
| Placas | Parafusar ZVS/MOSFET; Nano isolado da parede |

---

## Legado (não usar na v1)

ZIP [acsdog Printables](https://www.printables.com/model/1067938-dynavap-induction-heater-box-with-pwm) e edição FreeCAD — só referência histórica. A caixa oficial é OpenSCAD neste repo.

Coil chuck do acsdog continua **opcional** se for rebobinar 16 AWG na mesa.

---

## Backlog v2 (não entra nesta versão)

- Pack 18650/21700 + BMS adequado (≥10 A) — **não** power bank de celular
- Gangorra com LED que acenda em **12 V DC** (o kit 127/220 V AC não ilumina)
- Viewer carregando o STL real (`STLLoader`)
- Ajustes pós-impressão medidos na peça física → atualizar `dimensions.json`

Depois de montar, compare a caixa real com o viewer e anote desvios aqui.
