# Todo-Listen-App

Eine kleine **REST-API** für Todo-Listen und Einträge (Flask, In-Memory-Daten). Dazu gibt es ein separates **Web-Frontend** zum Verwalten der Listen.

---

## Links


|                     |                                                                                                                    |
| ------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **Frontend (live)** | [todo-list-frontend-eight-omega.vercel.app](https://todo-list-frontend-eight-omega.vercel.app/)                    |
| **Repository**      | [github.com/jakobschltr/bbs-jakob-schlueter-todo-app](https://github.com/jakobschltr/bbs-jakob-schlueter-todo-app) |


---

## Projektüberblick

- **Backend:** Python mit Flask — Endpoints für Listen und Todo-Einträge; die Schnittstelle ist in `todolistenverwaltung_openapi.yaml` beschrieben.
- **Frontend:** Web-App auf Vercel — Oberfläche für Todo-Sammlungen und Listen (Link siehe oben).

---

## Backend lokal starten

**Abhängigkeit:** [Flask](https://flask.palletsprojects.org/)

```bash
pip3 install flask
python3 app.py
```

Der Server läuft standardmäßig unter **[http://127.0.0.1:5000](http://127.0.0.1:5000)** (`host=0.0.0.0`, Port **5000**, Debug-Modus aktiv).

---

*LF9 / BBS Brinkstraße*