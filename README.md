# global_p2t
przełanczanie mikrofona klawiszami ni

## Budowanie ze źródła
### Wymagany jest `pyinstaller` (`pip install pyinstaller`).
Tryb jednego folderu - przenosi wszystkie biblioteki razem z plikiem wykonywalnym do folderu `./dist/main`
```bash
pyinstaller --onedir main.spec
```
Tryb jednego pliku (**rekomendowane**) - tworzy jeden plik wykonywalny, w którym zapakowane są wszystkie zależności
```bash
pyinstaller --ondefile main.spec
```

### Na razie program jest kompatybilny jedynie z systemem PulseAudio, więc nie zadziała natywnie na innych platformach niż Linux.
