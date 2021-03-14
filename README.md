# global_p2t
przełanczanie mikrofona klawiszami ni

## Budowanie ze źródła
### Wymagany jest `pyinstaller`.
Przed zbudowaniem aplikacji zainstaluj wszystkie zależności:

**Windows:**
```cmd
pip install pyinstaller
pip install -r requirements.txt
pip install pyaudio
```
Dodatkowo wymagane jest narzędzie SoundVolumeView, które można pobrać ze [strony producenta](https://www.nirsoft.net/utils/sound_volume_view.html).

**Linux:**
```bash
pip install pyinstaller
pip install -r requirements.txt
sudo apt install python3-pyaudio
```

Tryb jednego folderu (**rekomendowane**) - przenosi wszystkie biblioteki razem z plikiem wykonywalnym do folderu `./dist/main`
```bash
pyinstaller --onedir main.spec
```
Tryb jednego pliku (**może nie działać**) - tworzy jeden plik wykonywalny, w którym zapakowane są wszystkie zależności
```bash
pyinstaller --onefile main.spec
```
