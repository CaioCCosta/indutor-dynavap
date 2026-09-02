# Caixa 3D — indutor Dynavap (A14)

**Recomendado para este projeto:** [acsdog — Dynavap Induction Heater Box With PWM](https://www.printables.com/model/1067938-dynavap-induction-heater-box-with-pwm) (domínio público).

## Por que este

| Critério | acsdog (Printables) | jnico (Thingiverse) | PM_ME / ABV Storage |
|---|---|---|---|
| ZVS 120 W + bobina | Sim | Sim | Sim |
| MOSFET 15 A 400 W | Sim (pensado para isso) | Sim | Sim |
| Pot / PWM no painel | Sim (módulo PWM na foto) | Não | Não |
| Gabarito de bobina (coil chuck) | **Sim** — útil se rebobinar 16 AWG | Não | Não |
| Arquivos editáveis | FreeCAD inclusos | STL | STL |
| Licença | Domínio público | CC (Thingiverse) | CC |
| Observação | Nosso firmware substitui o PWM de kHz | Fonte original **6 A** — **não** use 6 A; use **10 A** | Mais “mesa + pote ABV”; layout maior |

**Não baixe caixa de kit VapOven a bateria** ([I＜I](https://www.printables.com/model/548213-dynavap-induction-heater-enclosure)) — é para portátil/baterias, não para a v1 de mesa 12 V.

## Como baixar (1 clique)

1. Abra: https://www.printables.com/model/1067938-dynavap-induction-heater-box-with-pwm  
2. Clique **Download** → baixa ZIP com:
   - `box_body.stl`
   - `box-Lid001.stl`
   - `coil chuck-Coil Chuck.stl`
   - FreeCAD (`.fcstd`) se quiser furar Nano / pot / LEDs
3. Alternativa clássica: https://www.thingiverse.com/thing:4171627 (jnico) → **Download all files**

## Impressão sugerida

| Parâmetro | Valor |
|---|---|
| Material | **PETG** (preferível perto do ZVS); PLA aguenta se não esquentar a caixa demais |
| Camada | 0,2 mm |
| Preenchimento | 15–25 % |
| Suportes | Só se o slicer pedir (tampa/corpo costumam imprimir sem) |
| Furos | 3,4 mm — M3/M4; use parafuso cabeça botão ou arruela |

## Encaixe com o nosso BOM

- Bobina + tubo de vidro Ø ~16 mm no topo (O-ring 15×3).
- ZVS + MOSFET + Nano + pot + botão + rocker dentro — se o Nano / TMP36 não couberem nos furos do acsdog, fure ou edite o FreeCAD.
- **Ventilação:** não feche hermético; dissipadores do ZVS precisam de ar.
- **Trava de altura** (cortiça/cavilha) no fundo do tubo — não vem no STL.

## O que NÃO é B2

O tubo de vidro (B2) é a **câmara do aquecedor**, não o Dynavap. Você enfia o **M7** (que você já tem) **dentro** desse tubo. Sem o tubo, a bobina não tem guia nem isolamento.
