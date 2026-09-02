# Afinação da bobina e segurança

Alvo desta v1: clique em **5–8 s** com **~60–70 W** (cerca de 5–6 A em 12 V com o cap inserido). Clique abaixo de 3 s costuma super-extrair; acima de 12 s a bobina está frouxa ou o duty está baixo demais.

Firmware e pinos: [indutor_dynavap.ino](firmware/indutor_dynavap.ino) e [BOM_E_FIACAO.md](BOM_E_FIACAO.md).

---

## Bobina: duas formas válidas

A bobina de fábrica do ZVS 120 W vem com ~23–28 mm de diâmetro interno. O cap Dynavap fica longe do cobre e o clique atrasa ou fica irregular. **Não corte o fio** se for só remodelar o comprimento original — o tanque LC precisa dessa indutância.

### A) Apertar a bobina original (VapOven)

1. Use o tubo de 16 mm como mandril.
2. Feche para **~5 espiras** justas no vidro.
3. O restante do fio fica dobrado para o lado, **inteiro**, até os bornes.
4. Soldar a bobina na placa. Bornes de plástico derretem com o uso.

### B) Rebobinar 16 AWG (Printables / acsdog)

1. Fio esmaltado 16 AWG. Raspé as pontas até o cobre aparecer.
2. Enrolar **8–10 espiras** no tubo de 16 mm (ou num gabarito do mesmo diâmetro).
3. Espiras apertadas, sem sobrepor isolamento danificado (curto entre voltas mata o ZVS).
4. Mesmo número de voltas da bobina original se você medi-las antes de desmontar — ponto de partida mais seguro.
5. Soldar na placa.

O tubo de vidro fica **dentro** da bobina. O-ring 15×3 mm trava o tubo na caixa. A trava (cavilha, cortiça ou cerâmica) vai no **fundo** do tubo e define a profundidade do cap.

---

## Profundidade (YLL + FuckCombustion)

O campo é uma banda quente no **centro** das espiras. Mais cap dentro da bobina = mais cobre “vendo” metal = clique mais rápido.

| Objetivo | Trava |
|---|---|
| Primeiro teste | Cap **inteiro** na bobina |
| Clique < 3 s | Subir a trava (menos cap no centro) ou abrir um pouco as espiras / baixar o pot |
| Clique > 12 s | Descer a trava, apertar espiras ou subir o pot |
| Sabor / terpenos | Um pouco menos fundo, duty menor (pulso) |
| Nuvem | Cap inteiro, duty alto, ainda na faixa 60–70 W |

Marque a posição boa com uma fita no tubo. A repetibilidade é o motivo de existir IH.

---

## Procedimento de afinação

Faça com a caixa aberta, multímetro em série no positivo (escala 10 A DC) se possível, e o interruptor geral à mão.

1. **Bobina no ar, sem cap.** Pulso curto. Corrente ociosa baixa (cerca de 1–2 A nos ZVS bem comportados). Fonte não pode piscar nem cair abaixo de ~11,5 V.
2. **Pot no mínimo** (sentido do sketch = potência cheia). Inserir o Dynavap até a trava. Contar até o clique.
3. Alvo **5–8 s**. Anotar corrente com o cap dentro.
4. Potência elétrica ≈ `12 V × corrente`. Ajustar pot e/ou bobina para **~5–6 A (60–72 W)**. Não persiga o 10 A nominais do módulo.
5. Se a fonte entrar em proteção: espiras demais / diâmetro pequeno demais / cap enfiado demais. Abra a bobina ou suba a trava.
6. Se o clique não vem: cap de vidro/cerâmica, bobina frouxa, polaridade do MOSFET, ou TRIG invertido (`MOSFET_ACTIVE_HIGH`).
7. Com o TMP36 no dissipador, segure o botão: em ≥ 60 °C o LED status pisca rápido e o ZVS corta. Solte e espere cair de 55 °C. Serial `Ts=0` significa sensor ausente ou leitura absurda — o corte térmico fica desligado até o TMP36 estar no dissipador.
8. Segure 60 s de propósito: o firmware corta (pisca lento). Solte o botão para rearmar.

Módulos ZVS nacionais pedem pausa depois de ~5 min contínuos. O timeout de 60 s cobre o uso real; não use o IH como fogão.

---

## Potenciómetro no firmware

| Posição | Comportamento |
|---|---|
| Quase todo aberto (ADC baixo) | ZVS contínuo enquanto o botão estiver apertado |
| Meio / fechado | Pulso lento, período 500 ms, “on” de ~500 ms até 120 ms |

Isso é o slowCook do VapOven / PULSE do Hackster: o ZVS **arranca e oscila** em cada pulso. PWM de kHz não dá tempo de oscilar e queima MOSFET.

---

## Checklist de segurança

Faça na ordem. Qualquer “não” = não aquece o cap.

- [ ] Fonte é **12 V 10 A** (ou 12 A), não 6 A
- [ ] ZVS é o de **5–12 V / 120 W**, não o de 1800 W
- [ ] Fusível **10 A** no positivo, depois do interruptor, antes do MOSFET
- [ ] MOSFET comuta o **12 V do ZVS**; botão só no D2
- [ ] GND comum: fonte, MOSFET, ZVS, Nano
- [ ] Polaridade da fonte conferida no jack
- [ ] Bobina soldada; isolamento entre espiras intacto; **fio original não cortado** se for o método A
- [ ] Dissipadores do ZVS com ar; caixa não é fechada hermética
- [ ] TMP36 no dissipador, não flutuando no ar da caixa
- [ ] Timeout e corte térmico testados **sem** cap na primeira vez
- [ ] Não usar Dynavap **G3 de vidro** (nem cap de vidro/cerâmica/plástico)
- [ ] Cap sai quente; o vidro isola a **bobina**, não o cap
- [ ] Não deixar o botão preso e sair da sala — o timeout é backup, não babysitter
- [ ] Sem LiPo. v2 de bateria: só 18650/21700 high-drain ≥ 20 A e BMS ≥ 15 A

---

## Sintomas comuns

| Sintoma | Causa mais provável |
|---|---|
| Fonte pisca / desliga | Bobina curta, diâmetro pequeno demais, fonte < 10 A |
| MOSFETs do ZVS queimam na hora | Tensão < 12 V, ZVS não oscilou, PWM rápido no TRIG |
| Clique instantâneo | Bobina apertada demais ou cap no centro; subir trava |
| Demora demais | Bobina de estoque larga; reenrolar ou apertar |
| LED status pisca rápido | Corte térmico 60 °C |
| LED status pisca lento com botão preso | Timeout 60 s — solte o botão |
| Nada aquece, Serial `zvs=0` com `btn=1` | `lock=1`, `to=1`, ou TRIG invertido |
| Nano reseta quando o ZVS liga | Fios de potência longos / GND ruim — encurtar e estreitar o loop |

---

## v2 (não misturar com a primeira solda)

Só depois que a v1 clicar estável em 5–8 s:

- 3S 18650 **ou** 2S 21700 high-drain (≥ 20 A contínuos)
- BMS ≥ 15 A, holder rígido, indicador de carga
- **Nunca LiPo** de drone
- Carregar com fonte 12,6 V adequada ao pack, ou USB-C num módulo de carga decente

Até lá, a tomada é o modo mais seguro e o que o VapOven comercial usa em 12 V 10 A.
