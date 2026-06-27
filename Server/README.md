# Mock API Server

Local MVP API server for early client integration.

Run:

```bash
python3 Server/mock_api.py
```

Optional custom port:

```bash
MOCK_API_PORT=18787 python3 Server/mock_api.py
```

Base URL:

```text
http://127.0.0.1:8787
```

Supported MVP endpoints:

- `GET /health`
- `GET /config/latest`
- `POST /auth/guest-login`
- `GET /game/sync`
- `POST /quest/claim`
- `POST /tutorial/complete`
- `POST /equipment/equip`
- `POST /realm/breakthrough`
- `POST /idle/claim`
- `POST /antique/appraise`
- `POST /battle/start`
- `POST /battle/finish`

This server uses in-memory state and resets when restarted.
