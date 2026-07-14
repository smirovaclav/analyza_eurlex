# Analýza vlivu evropské legislativy na německý finanční trh

Tento projekt byl vytvořen v rámci předmětu Projektový seminář 4IZ503 a jeho autorem je Václav Šmíro. Projekt zkoumá vazby mezi legislativními akty Evropské unie a dynamikou německé výnosové křivky, která slouží jako evropský benchmark. Cílem je ověřit hypotézu o zvýšené citlivosti institucionálních investorů na změny právního rámce nesoucí budoucí ekonomické náklady a strukturální rizika. 

---

## Popis projektu

Celý analytický proces je rozdělen do dvou hlavních částí:

* **Zpracování legislativy:** Python skript iteruje přes zdrojový dataset, stahuje HTML texty legislativy z portálu EUR-Lex a pomocí LLM (Mistral API) vrací strukturovaný JSON.
* **Extrahované dimenze:** Systém u každého dokumentu určuje primární sektor, intenzitu dopadu, přísnost, časový horizont a komplexitu.
* **Finanční analýza:** Pomocí analýzy hlavních komponent (PCA) se z denních dat Bundesbank extrahují faktory úrovně, sklonu a zakřivení výnosové křivky.
* **Data mining:** Nástroj Clever Miner (konkrétně 4ftMiner) následně v datech identifikuje statisticky významné vzorce chování trhu v okamžicích zveřejnění legislativy.

---

## Struktura souborů a datové cesty

> Způsob uložení dat a přesné lokální cesty pro datové vstupy jsou zobrazeny v souboru `Screenshot 2026-07-14 at 09.44.12.png`. 

V rámci kódu se pracuje s následujícími soubory:

| Soubor | Popis |
| :--- | :--- |
| `vysledek.csv` | Vstupní tabulka obsahující základní atributy legislativy, jako je Celexové číslo, datum dokumentu a forma. |
| `result_full.csv` | Výstupní soubor z první fáze zpracování, který kromě metadat obsahuje LLM vygenerované ekonomické a právní klasifikace. Slouží jako vstup pro navazující Jupyter notebook. |
| `vdax.csv` | Historická tržní data indexu volatility VDAX. |
| `EUR_USD.csv` | Historická data uzavíracích cen měnového páru EUR/USD. |
| `final.csv` | Finální datová sada obsahující očištěná, kategorizovaná a propojená data z trhů i legislativy, připravená pro algoritmus Clever Miner. |

---

## Postup zpracování (Pipeline)

1. **Načtení legislativy:** Načtení legislativních záznamů ze souboru `vysledek.csv`.
2. **LLM Extrakce:** Odeslání textů legislativy do LLM pro vytěžení požadovaných kvantitativních dimenzí a uložení do `result_full.csv` po každých 250 záznamech.
3. **PCA Transformace:** Načtení historických křivek úrokových sazeb z databáze Bundesbank a jejich transformace přes PCA.
4. **Zpracování tržních dat:** Kategorizace makroekonomických parametrů a výpočet procentuálních změn tržních dat (DAX, VDAX, EUR/USD).
5. **Sloučení datových sad:** Sloučení legislativních výstupů s finančními daty na základě data vydání dokumentu a uložení do tabulky `final.csv`.
6. **Data Mining:** Tvorba asociačních pravidel nad kategorizovanými proměnnými pro nalezení vztahů mezi aktem EU a reakcí trhu.
