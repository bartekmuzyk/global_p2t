# global_p2t
przełanczanie mikrofona klawiszami ni

## Budowanie ze źródła
### Wymagany jest `pyinstaller` (`pip install pyinstaller`).
Przed zbudowaniem aplikacji zainstaluj wszystkie zależności:

**Windows:**
```cmd
pip install -r requirements.txt
pip install pyaudio
```

**Linux:**
```bash
pip install -r requirements.txt
sudo apt install python3-pyaudio
```

Tryb jednego folderu - przenosi wszystkie biblioteki razem z plikiem wykonywalnym do folderu `./dist/main`
```bash
pyinstaller --onedir main.spec
```
Tryb jednego pliku (**rekomendowane**) - tworzy jeden plik wykonywalny, w którym zapakowane są wszystkie zależności
```bash
pyinstaller --onefile main.spec
```

### Na razie program jest kompatybilny jedynie z systemem PulseAudio, więc nie zadziała natywnie na innych platformach niż Linux.
