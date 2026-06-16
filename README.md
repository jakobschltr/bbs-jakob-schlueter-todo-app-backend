# Todo-Listen-Verwaltung – Deployment auf Raspberry Pi OS

REST-API für Todo-Listen (Python/Flask), deployed als Docker-Container auf einem
Raspberry Pi. Diese Anleitung beschreibt die komplette Einrichtung ausgehend von
einem unveränderten Raspberry Pi OS Lite (64-bit) Image.

## Repository-Inhalt

```
.
├── app.py                              # Flask-Implementierung der REST-API
├── todolistenverwaltung_openapi.yaml   # OpenAPI-Spezifikation
├── Dockerfile                          # Container-Definition
└── README.md                           # Diese Anleitung
```

> **Hinweis zu den IP-Adressen:** Alle Adressen in dieser Anleitung sind an
> unser Netzwerk angepasst. Wer die Anleitung nachvollzieht, muss eine **eigene,
> freie IP-Adresse** im jeweiligen Subnetz wählen sowie Gateway und DNS des
> eigenen Netzwerks eintragen (siehe Schritt 1).

---

## Links

- **Frontend (live):** [todo-list-frontend-eight-omega.vercel.app](https://todo-list-frontend-eight-omega.vercel.app/)
- **Frontend Repository:** [https://github.com/jakobschltr/bbs-jakob-schlueter-todo-app-frontend](https://github.com/jakobschltr/bbs-jakob-schlueter-todo-app-frontend)
- **Backend Repository:** [https://github.com/jakobschltr/bbs-jakob-schlueter-todo-app-backend](https://github.com/jakobschltr/bbs-jakob-schlueter-todo-app-backend)

Das **Backend** ist eine Python/Flask-API für Listen und Todo-Einträge; die
Schnittstelle ist in `todolistenverwaltung_openapi.yaml` beschrieben (OpenAPI). Das
**Frontend** läuft als Web-App auf Vercel und bietet die Oberfläche für
Todo-Sammlungen und Listen (Link siehe oben).

---

## 1. Statische IP-Adresse konfigurieren

Raspberry Pi OS (Bookworm) nutzt NetworkManager. Die Konfiguration erfolgt mit
`nmcli` und ist automatisch persistent.

### 1.1 Gateway und DNS ermitteln

Solange der Pi noch per DHCP verbunden ist, lassen sich Gateway und DNS-Server
des Netzwerks direkt auslesen.

**Gateway (Standardroute):**

```bash
ip route | grep default
```

Die Adresse hinter `default via` ist das Gateway:

```
default via 192.168.24.254 dev eth0 proto dhcp ...
```

**DNS-Server:**

```bash
nmcli dev show eth0 | grep DNS
```

Alle Werte (IP, Gateway, DNS) der aktuellen Verbindung auf einen Blick:

```bash
nmcli dev show eth0
```

> In unserem Netzwerk liegt das Gateway bei **`192.168.24.254`** und das Subnetz
> ist **`192.168.24.0/24`**. In einem anderen Netzwerk liefern die obigen
> Befehle entsprechend andere Adressen.

### 1.2 Statische IP setzen

Zuerst den Namen der aktiven Verbindung ermitteln:

```bash
nmcli connection show
```

Anschließend die statische IP setzen. **Wichtig:** Gateway und Adresse müssen im
gleichen Subnetz liegen (hier: `192.168.24.0/24`):

```bash
sudo nmcli connection modify "netplan-eth0" \
  ipv4.method manual \
  ipv4.addresses 192.168.24.114/24 \
  ipv4.gateway 192.168.24.254 \
  ipv4.dns "192.168.24.254"

sudo nmcli connection down "netplan-eth0"
sudo nmcli connection up "netplan-eth0"
```

> Hinweis: Bei aktiver SSH-Verbindung bricht die Sitzung an dieser Stelle ab,
> da sich die IP-Adresse ändert. Danach unter der neuen Adresse neu verbinden.

---

## 2. Benutzer anlegen

### Benutzer `willi` (ohne Administratorrechte)

```bash
sudo adduser willi
```

- Passwort setzen -> z.B. "raspberry"
- Der Eingabemaske folgen und am Ende bestätigen

### Benutzer `fernzugriff` (mit sudo-Rechten)

```bash
sudo adduser fernzugriff
```

- Passwort setzen -> z.B. "raspberry"
- Der Eingabemaske folgen und am Ende bestätigen

```bash
sudo usermod -aG sudo fernzugriff
```

---

## 3. SSH-Dienst einrichten

SSH-Dienst dauerhaft aktivieren (überlebt Neustarts) und starten:

```bash
sudo systemctl enable ssh
sudo systemctl start ssh
```

Den SSH-Zugang auf den Benutzer `fernzugriff` beschränken, damit sich kein
anderer Benutzer (z. B. `willi`) von außen anmelden kann. Dazu folgende Zeile
ans Ende von `/etc/ssh/sshd_config` anfügen:

```bash
echo "AllowUsers fernzugriff" | sudo tee -a /etc/ssh/sshd_config
sudo systemctl reload ssh
```

- "tee" -> Weitergabe der Eingabe an eine Datei
- "-a" -> Anhängen der Eingabe an die Datei und nicht überschreiben

Verbindungstest von einem anderen Rechner im Netzwerk:

```bash
ssh fernzugriff@192.168.24.114
```

---

## 4. Docker installieren

Installation über die Paketverwaltung:

```bash
sudo apt update
sudo apt install -y docker.io
```

Docker-Dienst starten und für den automatischen Start beim Booten aktivieren:

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

Installation testen:

```bash
sudo docker run hello-world
```

Optional: Benutzer zur `docker`-Gruppe hinzufügen, um `docker` ohne `sudo`
auszuführen (wirksam nach erneutem Login):

```bash
sudo usermod -aG docker fernzugriff
```

---

## 5. Projektdateien auf den Server übertragen

Per Git (Git ggf. zuerst mit `sudo apt install -y git` installieren):

```bash
git clone https://github.com/jakobschltr/bbs-jakob-schlueter-todo-app-backend.git
cd bbs-jakob-schlueter-todo-app
```

Alternativ per `scp` vom eigenen Rechner aus:

```bash
scp app.py Dockerfile fernzugriff@192.168.24.114:~/todo-app/
```

---

## 6. Container-Image bauen

Das Dockerfile basiert auf einem schlanken Alpine-Python-Image, installiert
Flask und kopiert die Anwendung in den Container:

```dockerfile
FROM python:3.11-alpine

WORKDIR /app

RUN pip install flask==3.1.3

COPY app.py /app

EXPOSE 5000

ENTRYPOINT [ "python" ]
CMD ["app.py"]
```

Image bauen (im Projektverzeichnis ausführen):

```bash
sudo docker image build -t webapp .
```

---

## 7. Container starten

```bash
sudo docker run -p 5000:5000 -d --restart unless-stopped --name todo-app webapp
```

Erläuterung der Optionen:

- `-p 5000:5000` – leitet Port 5000 des Containers auf Port 5000 des Hosts um
- `-d` – startet den Container im Hintergrund (detached)
- `--restart unless-stopped` – startet den Container nach einem Neustart des
Systems automatisch wieder (Persistenz-Anforderung)
- `--name todo-app` – fester Name für die spätere Verwaltung

Laufende Container anzeigen:

```bash
sudo docker ps
```

Die API ist anschließend erreichbar unter:

```
http://192.168.24.114:5000/todo-list
```

---

## 8. Neustart-Test

Alle Einstellungen müssen einen Neustart überstehen. Test:

```bash
sudo reboot
```

Nach dem Hochfahren prüfen:

```bash
ssh fernzugriff@192.168.24.114        # statische IP + SSH funktionieren
sudo systemctl status docker          # Docker-Dienst läuft
sudo docker ps                        # Container "todo-app" ist "Up"
```

### Funktionstest der API

Den Endpunkt `/todo-list` abfragen, der alle Listen zurückgibt:

```bash
curl http://192.168.24.114:5000/todo-list
```

Erwartete Ausgabe (die drei vordefinierten Beispiellisten aus `app.py`):

```json
[
  {
    "id": "3530b3f0-fa39-4a48-9aa9-c36533817643",
    "name": "Einkaufsliste"
  },
  {
    "id": "0881e37f-5667-44be-b22f-1d7bb70e503b",
    "name": "Arbeit"
  },
  {
    "id": "1d4204da-2563-42e0-b733-802817db44a5",
    "name": "Privat"
  }
]
```

Antwortet der Server mit diesem JSON, läuft die Web-App im Container korrekt.
Die `id`-Werte werden bei jedem Containerstart neu generiert und weichen daher
ab. Vom Netzwerk aus ist die API unter `http://192.168.24.114:5000/todo-list`
erreichbar.

---

## 9. Container im Betrieb verwalten

Sollte `docker` ohne Gruppenmitgliedschaft genutzt werden, ist den folgenden
Befehlen jeweils `sudo` voranzustellen.

**Status ansehen** — laufende Container bzw. inklusive gestoppter:

```bash
docker ps
docker ps -a
```

**Container steuern** — der Name `todo-app` stammt aus dem `--name`-Flag beim
Start (Schritt 7):

```bash
docker stop todo-app      # anhalten
docker start todo-app     # wieder starten
docker restart todo-app   # neu starten
```

**Fehlersuche** — Logs des Containers ausgeben (mit `-f` live mitlesen):

```bash
docker logs todo-app
docker logs -f todo-app
```

**Aufräumen** — Container muss vor dem Löschen gestoppt sein; das Image kann
anschließend entfernt werden:

```bash
docker rm todo-app        # Container löschen
docker images             # vorhandene Images auflisten
docker rmi webapp         # Image löschen
```

---

## Übersicht


| Benutzer      | Rechte   | SSH-Zugang |
| ------------- | -------- | ---------- |
| `willi`       | Standard | nein       |
| `fernzugriff` | sudo     | ja         |



| Dienst   | Port | Persistenz                 |
| -------- | ---- | -------------------------- |
| SSH      | 22   | `systemctl enable ssh`     |
| Docker   | –    | `systemctl enable docker`  |
| Todo-App | 5000 | `--restart unless-stopped` |


| Netzwerk-Parameter | Wert (unser Aufbau) | Ermitteln mit                     |
| ------------------ | ------------------- | --------------------------------- |
| Statische IP       | `192.168.24.114/24` | frei wählbar im Subnetz           |
| Gateway            | `192.168.24.254`    | `ip route \| grep default`        |
| DNS                | `192.168.24.254`    | `nmcli dev show eth0 \| grep DNS` |


---

*LF9 / BBS Brinkstraße Osnabrück*