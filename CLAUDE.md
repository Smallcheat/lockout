# Lockout: projektin ohjeet agentille

Lockout on avoimen lähdekoodin portfolioprojekti: recovery-lockout- ja break-glass-validity-analyzer datakeskusten hallintatasolle. Lisenssi on Apache-2.0.

Käyttäjän yleiset ohjeet ovat kotihakemiston CLAUDE.md:ssä. Tämä tiedosto täydentää niitä, ja Lockoutia koskevat konventiot ovat alla.

## Lockout: konventiot (pakollinen)

### Yleistä
- Kieli: koodi, kommentit, docs, commitit ja PR:t englanniksi.
- Python 3.12+, src-layout, tyyppivihjeet kaikkialla, mypy läpi, ruff (lint + format) läpi.
- Funktiot puhtaita missä mahdollista: analyysit eivät lue tiedostoja eivätkä käytä verkkoa. I/O vain reunoilla (loader, cli, api).
- Ei piilotettuja lukuja: kaikki oletusluvut tulevat `assumptions/assumptions.yaml`:sta. Ei kovakoodattuja kestoja tai kustannuksia.
- Virheilmoitukset ihmisluettavia: kerro mikä malli, solmu ja kenttä on virheellinen.
- Satunnaisuus (Monte Carlo) aina siemennetty ja toistettava.
- Ei salaisuuksia repossa. Ei oikeita järjestelmiä, ei skannausta, vain synteettistä dataa.

### Faktat ja lähteet
- Jokainen ulkoinen fakta (standardit, incidentit, lait) kirjataan `docs/sources.md`:hen lähteineen ja varmistuspäivineen. Ei muistinvaraisia väitteitä.
- Replay-mallit ovat havainnollistavia: `docs/replays/` erottaa selvästi "raportti sanoo" ja "malli olettaa".
- IEC 62443:sta ja ISO-standardeista käytetään vain käsitteitä, ei lainauksia.

### Testaus
- Jokainen PR sisältää testit. Ei testejä, ei mergeä.
- Yksikkötestit: graafi-, simulaatio- ja validiusalgoritmit pienillä käsin rakennetuilla fikstuureilla (`tests/fixtures`).
- Skeema: validit ja virheelliset mallit, odotetut virheilmoitukset.
- Golden-testit: raportit (JSON/Markdown) vertailtuna tallennettuun odotettuun tulokseen. Golden-tiedostot päivitetään vain tarkoituksella ja perustellen PR:ssä.
- Skenaariotestit: replay-malleille odotetut löydökset (esim. "Meta-replay löytää valekatkaisun X").
- CI-portti: `models/examples/bad-cycle`:n pitää epäonnistua ja referenssimallin pitää mennä läpi.
- Savutesti: docker compose käynnistyy, `/health` vastaa, esimerkkiskenaario ajetaan.
- Tavoite: analyyseissä (`src/lockout/analyzers`) rivikattavuus vähintään 85 %. Tämä on ohjearvo, ei ehdoton.
- Testit eivät käytä verkkoa.

### Työskentely
- Yksi tehtävä = yksi feature-haara = yksi PR. Haaranimi `feat/<nn>-<slug>` (myös `docs/`, `chore/`, `fix/`, `build/`).
- Ei suoria pusheja mainiin. Älä yhdistä PR:ää itse: käyttäjä hyväksyy ja yhdistää (squash merge).
- Pushaa feature-haara vasta kun testit ja lint menevät läpi.
- Commit-viestit: Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
- PR-kuvaus: mitä, miksi, miten testattu, mitä jätettiin tekemättä, lähteet jos faktoja.
- Yksi PR on yksi looginen kokonaisuus, kokoraja noin 800 riviä käsin kirjoitettua koodia ja dokumentaatiota. Testit, golden-tiedostot ja generoitu JSON Schema eivät kuulu rajaan. Jos PR ylittää rajan, sen saa jakaa kahtia kysymättä, ja jako kerrotaan PR:n kuvauksessa.
- Ei laajuuden venytystä: tee vain sen PR:n tehtävä, joka on sovittu.
- PR-checklistin kohtia ei merkitä ennen kuin ne on oikeasti varmistettu. Aja `pytest`, `ruff check .`, `ruff format --check .` ja `mypy` paikallisesti ennen pushia, älä luota pelkkään CI:hin.

## Päätökset
- Mallinnus: vian leviäminen CrowdStrike-tyyppisissä tapauksissa mallinnetaan solmujen `tags`-kentällä ja skenaarion vikajoukon tagivalitsimella, ei uudella kaarityypillä (ADR-0001).

## v0.1:n PR-lista
PR 1–2 on tehty (scaffold, arkkitehtuuri ja ADR-0001). Jäljellä olevat PR:t ovat nippuja alkuperäisestä jaosta 3–16.

| PR | Haara | Sisältö |
|---|---|---|
| 3 | `feat/03-schema-loader-reference` | skeema (tagit, 4 kaarityyppiä), JSON Schema -vienti, YAML-lataus ja semanttinen lint, referenssi-DC ja sen docs |
| 4 | `feat/04-graph-analyzers` | tyypitetty graafi, bootstrap-kehät (SCC), skenaarioformaatti tagivalitsimella, lockout-simulaatio, break-glass-validius ja selitysketju, CLI `analyze` ja `simulate` |
| 5 | `feat/05-reports-ci-gate` | JSON/Markdown/HTML-raportit, golden-testit, NIS2/CSF-koukut, CLI `check`, `model-gate.yml`, poikkeustiedosto, `bad-cycle`-esimerkki, **redundanssiryhmien tarkistus** (jaettu riippuvuus tekee ryhmästä näennäisen, min_available täyttyy vikajoukossa) |
| 6 | `feat/06-meta-replay` | Meta-replay-malli, skenaario, odotettujen löydösten testi, `docs/replays/meta-2021.md`, `sources.md`-merkinnät |
| 7 | `feat/07-api-ui-docker` | vain lukeva FastAPI, staattinen graafi-UI, Dockerfile, compose, e2e-savutesti |
| 8 | `docs/08-readme-release-v0.1` | README, assumptions-and-limitations, demo-script, `sources.md` valmiiksi, CHANGELOG, versio, lisenssitarkistus. Käyttäjä luo tagin v0.1.0 ja demo-GIF:n |

Redundanssiryhmät: skeema ja lint ovat valmiina (PR 3), analyysi puuttuu. Ne otetaan käyttöön PR 5:ssä ennen v0.1:tä. Jos PR 5 ylittää 800 rivin rajan, ryhmätarkistus saa olla oma PR:nsä ennen PR 6:ta.
