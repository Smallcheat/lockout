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
- Referenssimalli: jokaisella riippuvuudella ja kyvykkyydellä on oltava perustelu, joka nojaa todelliseen käytäntöön tai tapaukseen (`docs/reference-model.md`, osio "Dependency justifications"). Perustelu erottaa "raportti sanoo" (lähde `docs/sources.md`:ssä) ja "malli olettaa". Mallia ei muuteta eikä täydennetä tulosteen siistimiseksi tai demon näkyvyyden vuoksi. Perustelemattomat kohdat listataan osioon "Not yet justified".
- Mallinnus: vian leviäminen CrowdStrike-tyyppisissä tapauksissa mallinnetaan solmujen `tags`-kentällä ja skenaarion vikajoukon tagivalitsimella, ei uudella kaarityypillä (ADR-0001).

## v0.1:n PR-lista
PR 1–4 on tehty (scaffold, arkkitehtuuri ja ADR-0001, skeema/loader/referenssimalli, graafi ja analyysit). Jäljellä olevat PR:t:

| PR | Haara | Sisältö |
|---|---|---|
| 5 | `feat/05-redundancy-groups` | redundanssiryhmien analyysi: jaettu riippuvuus tekee ryhmästä näennäisen (single point of failure), ryhmän tila vikajoukossa (`min_available`), näkyy `analyze`- ja `simulate`-tulosteessa |
| 6 | `feat/06-reports-ci-gate` | JSON/Markdown/HTML-raportit, golden-testit, NIS2/CSF-koukut, CLI `check`, `model-gate.yml`, poikkeustiedosto, `bad-cycle`-esimerkki |
| 7 | `docs/07-reference-model-justification` | jokainen referenssimallin riippuvuus ja kyvykkyys luokitellaan: (1) lähteistetty tapaus tai dokumentti, (2) yleinen käytäntö yleisellä viitteellä (esim. Microsoftin Entra-hätäkäyttötiliohje, NIST, CIS), (3) eksplisiittinen oletus synteettisestä ympäristöstä. Luokka on pakollinen, lähteistys ei kaikelle. Perustelemattomat poistetaan tai perustellaan ennen v0.1:tä. Mekanismi (kenttä mallissa tai erillinen tiedosto) ja mahdollinen lint-sääntö päätetään PR:ssä |
| 8 | `feat/08-meta-replay` | Meta-replay-malli, skenaario, odotettujen löydösten testi, `docs/replays/meta-2021.md`, `sources.md`-merkinnät |
| 9 | `feat/09-api-ui-docker` | vain lukeva FastAPI, staattinen graafi-UI, Dockerfile, compose, e2e-savutesti |
| 10 | `docs/10-readme-release-v0.1` | README, assumptions-and-limitations, demo-script, `sources.md` valmiiksi, CHANGELOG, versio, lisenssitarkistus. Käyttäjä luo tagin v0.1.0 ja demo-GIF:n |

Jos PR ylittää 800 rivin rajan, sen saa jakaa kahtia kysymättä (ks. Työskentely).
