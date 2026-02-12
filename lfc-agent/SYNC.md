# LFC Agent - Coordination File

**Last Updated:** 2026-02-05 12:30 GMT  
**Project:** @YNWA4Reds Instagram automation  
**Launch:** LFC vs Man City, Sun 9 Feb, 4:30pm

---

## 🔄 ACTIVE WORK

### Claw (OpenClaw) - Infrastructure
- [x] All code written, ready to deploy
- [ ] PostgreSQL setup on Mac Mini (waiting for Homebrew)
- [ ] Run setup script
- [ ] Test end-to-end

### Claude (Web) - Content & Strategy
- [ ] Meta Business Manager setup guidance
- [ ] Content strategy refinement
- [ ] Prompt engineering for captions
- [ ] Dashboard UI design

---

## ✅ COMPLETED

- [x] Project structure created (2026-02-05 05:54)
- [x] Spec reviewed and understood
- [x] Database schema written (`db/init_db.sql`)
- [x] Seed data: quotes + stats for City match
- [x] Fixture monitor module (`src/fixtures/monitor.py`)
- [x] Content generator module (`src/generation/generator.py`) 
- [x] Requirements.txt ready
- [x] .env.example created
- [x] Visual compositor (`src/visuals/compositor.py`)
- [x] Instagram publisher (`src/publishing/publisher.py`)
- [x] Content sourcer (`src/content/sourcer.py`)
- [x] Setup script (`scripts/setup_mini.sh`)
- [x] Mac Mini deployed & configured
- [x] PostgreSQL running, database seeded
- [x] Python venv + all packages installed
- [x] Power management: no sleep
- [x] Anthropic API key configured
- [x] Caption generator: WORKING (tested Demis post)
- [x] Visual compositor: WORKING (stat + quote graphics)

---

## 📋 PHASE STATUS

| Phase | Description | Owner | Status |
|-------|-------------|-------|--------|
| 1 | Infrastructure (DB, env) | Claw | ✅ DEPLOYED & TESTED |
| 2 | Content sourcing + Claude | Split | ✅ WORKING |
| 3 | Dashboard + Publisher | Split | ⚪ Not Started |
| 4 | Launch + Monitor | Both | ⚪ Not Started |

---

## 🤝 HANDOFF NOTES

**To Claude (Web):**
- Spec is at `specs/LFC_SOCIAL_AGENT_SPEC.md`
- I'm starting PostgreSQL setup on Mac Mini (192.168.154.44)
- Matt needs to create Meta Business Manager account + connect @YNWA4Reds
- Let me know what you need from the infrastructure side

**From Claude (Web):**
*(Add notes here when you update)*

---

## 🚫 BLOCKERS

1. **Meta API Tokens** - Need Matt to set up Business Manager
2. **Mac Mini access** - Will verify connectivity now

---

## 📁 KEY FILES

- `specs/LFC_SOCIAL_AGENT_SPEC.md` - Full technical spec
- `lfc-agent/` - Project root
- `lfc-agent/SYNC.md` - This file (coordination)
- `lfc-agent/.env` - Credentials (create locally, don't commit)

---

## 💬 COMMS

Matt is bridging between:
- **Claw** (OpenClaw) - Handles infra, code execution, file ops
- **Claude** (Web) - Handles strategy, prompts, design thinking

Update this file when you complete tasks or hit blockers!
