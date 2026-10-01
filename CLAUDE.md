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
- PR:t pidetään pieninä (tavoite alle noin 400 muutettua riviä). Jos tehtävä paisuu, ehdota jakoa.
- Ei laajuuden venytystä: tee vain sen PR:n tehtävä, joka on sovittu.
- PR-checklistin kohtia ei merkitä ennen kuin ne on oikeasti varmistettu. Aja `pytest`, `ruff check .`, `ruff format --check .` ja `mypy` paikallisesti ennen pushia, älä luota pelkkään CI:hin.

## Päätökset
- Mallinnus: vian leviäminen CrowdStrike-tyyppisissä tapauksissa mallinnetaan solmujen `tags`-kentällä ja skenaarion vikajoukon tagivalitsimella, ei uudella kaarityypillä (ADR-0001).
