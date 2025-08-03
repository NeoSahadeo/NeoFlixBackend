# NeoFlix-Backend

The backend account handler for [NeoFlixWeb](https://github.com/NeoSahadeo/NeoFlixWeb)
and `NeoFlixMobile`

# Getting Started

### Get TMDB Api Key

---

__Start Backend__

```bash
fastapi dev src/main.py
```

__Generate New Secret Key__

```bash
openssl rand -hex 32
```


# Project Roadmap

- [x] Create database models
- [ ] Create database functions for api
- [-] Build database encryption
- [ ] Link api calls to database functions
- [x] Setup authentication
- [ ] <strike>Setup 2fa and secure endpoints</strike>
- [ ] Setup tmdb access grants
- [ ] Setup Logs

# Possible Changes

- [ ] Switch Peewee models to inherit from Pydantic

---

# Authors

@ NeoSahadeo
