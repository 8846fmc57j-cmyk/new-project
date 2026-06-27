# MVP Web Prototype

This is a lightweight browser prototype for the MVP flow. It connects to the local Mock API and is meant for product and engineering validation before a Unity or Cocos implementation.

Run both services from the repository root:

```bash
python3 Tools/run_mvp_demo.py
```

Or run the Mock API manually:

```bash
python3 Server/mock_api.py
```

Run the prototype from the repository root:

```bash
python3 -m http.server 8080
```

Open:

```text
http://127.0.0.1:8080/Client/web-prototype/
```

Supported flow:

- Guest login
- Game sync
- Idle reward claim
- Main quest claim
- Tutorial completion
- Antique appraisal
- Battle start and finish
- Equipment equip
- Realm breakthrough
- Demo reset

Smoke test:

```bash
python3 Tools/test_web_prototype.py
```
