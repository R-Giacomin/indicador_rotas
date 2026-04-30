## Indicador de ganho ou perda de participação da Rota


---


**Fórmula de cálculo:**

$$
I_pR = \frac{\Delta R_p - \Delta T_p}{|\Delta T_p|}
$$


Onde:

- $I_pR$ Representa o Indicador de ganho ou perda de participação da Rota/Polo/município;
- ${\Delta R_p}$ Representa a variação da produção do total de municípios da Rota em relação ao produto da Rota no período; e
- ${\Delta T_p}$ Representa a variação da produção do total de municípios em relação ao produto da Rota no período.


**Interpretação:**

Se **maior que 0**: O crescimento da produção foi maior nos municípios das Rotas
(ou caiu menos que nos demais)

Se **menor que 0**: O crescimento da produção foi menor nos municípios das Rotas (ou caiu mais que nos demais)

O indicador pode ser decomposto para cada município e para cada Polo


---

Foram apurados os indicadores de seis Rotas, incluindo os indicadores para cada Polo.

A Fonte de dados são as Pesquisas do IBGE:
- Pesquisa da Pecuária Municipal - PPM
- Produção Agrícola Municipal - PAM
- Produção da Extração Vegetal e da Silvicultura - PEVS


```
* O código requisita os dados direto do API do SIDRA do IBGE
```


```
* Observe que o indicador do ano de referência só fica disponível a partir de setembro do ano seguinte.
```