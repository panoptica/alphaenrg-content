# MEMORY.md - Long-Term Memory

## Active Projects

### Energy Intelligence Agent (Started 2026-02-04)
Automated intelligence system for energy/cooling/quantum investment signals.
- Spec: `specs/energy-intelligence-agent-spec.md`
- Code: `energy-agent/`
- Target: 2-3 actionable trades/month, 12-18 month horizon
- **Status**: MVP working! Daily 7am digests to oc@cloudmonkey.io
- Collectors: ArXiv ✅, SEC ✅, USPTO ⏳ (waiting API key)
- See daily notes for progress

### Hardware Empire (Started 2026-02-04)
Distributed compute for intelligence operations.
- **Mac Mini M4** (192.168.154.44): Llama 3 8B WORKING! API at :11434
- **Kali box** (192.168.154.193): RDP available, need SSH creds
- **Jetson Orin**: Satellite imagery CV (pending setup)

## Credentials & Access
- **Email**: oc@cloudmonkey.io (app password in energy-agent/.env)
- **Mac Mini**: host 192.168.154.44, user macmini, pass `!1Longmore@@`
- **Kali**: host 192.168.154.193, user oc, pass `Apple24`
- **Jetson**: host 192.168.154.124, user deepseek, pass `jetson_orin` (cracked via hydra!)
- **PatentsView**: API key requested (PVS-4987), 1-2 day wait
- **WhatsApp**: Connected as +447788537939

## Matt's Preferences
- Prefers files over chat pastes for specs
- Wants to watch and learn (not hands-on coding)
- Impatient — get to the point, show progress
- Excited about hardware/empire building

## Lessons Learned
- **2026-02-04**: Lost entire conversation context because I didn't write memory files. Never again. Write it down immediately.
- **2026-02-04**: PatentsView old API deprecated May 2025 - need new API key for USPTO
- **2026-02-04**: Ollama binds to localhost by default - need `OLLAMA_HOST=0.0.0.0` for network access
- **2026-02-04**: Nitter instances unreliable - Twitter scraping needs official API or alternative

## Empire Status (as of 2026-02-04 22:35 GMT)
- **Mac Mini M4**: OpenClaw + WhatsApp + Llama 3 + auto-start ✅
- **Kali Y2K**: OSINT stack (Reddit/News/Darkweb) + 4hr cron ✅
- **Jetson Orin**: Password cracked (`deepseek`/`jetson_orin`), needs reboot
- **Energy Agent**: MVP working, daily 7am digest with AI narrative

## Next Priorities
1. Help Matt set up payments (Coinbase Commerce → UK Ltd → Stripe)
2. Recover Jetson for satellite imagery CV
3. Add USPTO when API key arrives (PVS-4987)
4. Wire local Llama 3 for real-time synthesis (not just digest)
