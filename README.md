# Didelių kalbos modelių (DKM) generuoto edukacinio turinio vertinimas
Šioje repozitorije pateikiami bakalauro darbo metu surinktas duomenų rinkinys, metodikų implementacijos ir sukaupti bei įvertinti duomenys

## Failai
1. `sources` direktorijoje yra naudojamas duomenų rinkinys.
2. `data.xlsx` yra tyrimo metu sukaupti ir įvertinti duomenys.
3. `generate_questionnaires_excel.py` kodas atliekantis klausimynų generavimą.
4. `generate_answers_excel.py` kodas atliekantis pradinių atsakymų generavimą, naudojamas tik pradiniams duomenimis surinkti kurie buvo redaguoti prieš kitą žingsnį.
5. `evaluate_answers_excel.py` kodas atliekantis atsakymų vertinimą.
6. `methods` direktorijoje stovi darbo metu įgyvendintos metodikos

## Paleidimas
### Reikalavimai
1. Python 3.12.6+
2. OpenAI ir Alibaba API raktai

### Aplinkos paruošimo instrukcijos
1. Nusiklonuoti šią repozitoriją.
2. Sukurti naują python aplinka paleidžiant `python -m venv .venv` komandą repozitorijos direktorijoje.
3. Aktyvuoti aplinką paleidžiant `.\.venv\Scripts\activate` per powershell, kaikurios IDE gali tai padaryti automatiškai.
4. Įrašyti naudojamas bibliotekas su `pip install -r requirements.txt` komanda.
5. Sukurti `.env` failą, pagal `.env.example` ir užpildyti API raktų parametrus.
6. Paleisti norimą python failą su komanda `python <failo pavadinimas>`
