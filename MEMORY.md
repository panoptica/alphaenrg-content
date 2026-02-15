# MEMORY.md - Long-Term Memory

## Infrastructure

### Mac Mini M4 — PRIMARY 24/7 HUB
- Netbird: 100.87.48.20 | User: macmini | Password: see secrets/.credentials
- OpenClaw Gateway :18789 | Ollama :11434 | Telegram connected
- Primary model: google/gemini-2.5-flash (1M ctx) | Fallback: claude-sonnet | Heartbeats: llama3.1:8b
- Ollama binary: /usr/local/bin/ollama | OpenClaw: /opt/homebrew/bin/openclaw
- 16GB RAM, MPS GPU, needs LaunchDaemon for auto-start

### MacBook Air — Dev/Remote Client
- Netbird: 100.87.78.214
- Primary: anthropic/claude-sonnet-4-20250514 | Fallback: google/gemini-2.5-flash
- This instance — for dev, testing, mobile work

### Kali Y2K — OSINT Node
- Netbird: 100.87.231.197 | User: panoptica | see secrets/.credentials
- OSINT collectors (Reddit/News/Darkweb) + 4hr cron
- SSH key setup pending

### Jetson Orin — CONNECTED ✅
- Netbird: 100.87.171.38 | User: panoptica | Password: see secrets/.credentials
- OS: Ubuntu 22.04 | Target: satellite imagery CV
- Status: Connected to Netbird mesh network

## Credentials
All secrets in `secrets/.credentials`. Key refs:
- Email: oc@cloudmonkey.io (app pass in energy-agent/.env)
- PatentsView API: in .env
- X/Twitter OAuth2: in energy-agent/.env | Handle: @AlphaENRG
- Bybit API: in Mac Mini crypto-scalper/.env
- WhatsApp: +447788537939 (disabled, Telegram primary)

## Active Projects

### Energy Agent — MVP Running
- Code: `energy-agent/` | Spec: `specs/energy-intelligence-agent-spec.md`
- Daily 7am digest to oc@cloudmonkey.io
- Collectors: ArXiv ✅, SEC ✅, USPTO ⚠️ (fixed Feb 13 - company-based search only), Lens ⚠️ (needs testing)
- Email may be broken (Gmail app password issue Feb 9)

### Crypto Scalper — BINNED 2026-02-12
- Project cancelled (going nowhere). Process stopped and disabled on Mac Mini.
- Virtual capital remains unspent. Strategy failed to prove 1-3% daily target.

### LFC Social Agent — BINNED 2026-02-12
- Project cancelled. Not producing results.
- 7 scheduled LaunchAgents disabled on Mac Mini.
- Code archived to ~/binned/lfc-agent.

### AlphaEnergy / @AlphaENRG
- ~1,100 followers | Substack: alphaenergy.substack.com
- Auto-publisher needs Substack cookies from Matt
- Editorial: UK English, no m-dashes, no emoji, lowercase subtitles (NEVER Title Case), WHY not HOW, sound human not AI

### Companion App — Specced
- Spec: specs/companion-app-spec.md | Brand shortlist: Ember, Muse, Reverie, Velvet, Bloom
- Revenue: free/£9.99/£19.99 + virtual gifts
- Status: needs brand decision + MVP build

### Polymarket Bot — Scoped
- Cross-ref AlphaEnergy signals with Polymarket odds
- Needs Polygon wallet + USDC from Matt

## GitHub
- Repo: https://github.com/panoptica/empire (private)
- gh CLI, HTTPS, panoptica account
- Branches: main → dev → agent/* / infra/* / feat/* / exp/*
- Worktrees: ~/.openclaw/trees/{dev,energy,lfc,experiments}

## Matt
- Prefers files over chat pastes
- Wants to watch, not hands-on code
- Impatient — show progress fast
- HL portfolio — PRIVATE, never share in groups
- Target: £50k+ this year
- Earnings crons set (VRT, CVX, MU, TSLA, INTC, PLTR)

## Lessons (Hard-Won)
- ALWAYS use Tailscale IPs, never LAN
- 8B models too weak for OpenClaw agent — use 2.5 Flash / Sonnet minimum
- Write memory immediately — "mental notes" don't survive sessions
- Custom Ollama providers need "apiKey": "ollama" dummy value
- Mac Mini paths: export PATH when SSHing
- Two independent configs (MacBook Air + Mac Mini) — don't confuse them
- ALWAYS grep .env files + secrets/.credentials before claiming something is missing — Matt has given creds multiple times
- Use X API (bearer token), don't scrape x.com
- **CRITICAL: Service reliability is core competency** — Working solutions must not rot (Feb 13, 2026)
- **State maintenance failure pattern** — Matt's feedback: "You simply cannot maintain state" and "It's poor and won't scale"
- OpenClaw services crash frequently on Mac Mini — investigate LaunchDaemon setup for auto-restart
- USPTO API changed from api.patentsview.org to search.patentsview.org — only supports exact equality matches
- **Netbird Migration Complete (Feb 15, 2026)** — Migrated entire infrastructure from broken Tailscale to reliable Netbird P2P mesh. All SSH and workspace sync now via Netbird IPs only.
- **Final Netbird IPs**: MacBook Air 100.87.78.214, Mac Mini 100.87.48.20, Y2K 100.87.231.197, Jetson Orin 100.87.171.38
- **Infrastructure lesson**: Replace unreliable systems entirely rather than fighting with them
- **AlphaEnergy cron job model errors** — Fixed broken "google/gemini-2.5-flash" model references in isolated session jobs

## Next Priorities  
1. **Complete SSH key setup** — Fix authentication for workspace sync via Netbird
2. **Complete Lens API integration** — Test and debug Lens collector hanging issues
3. Get Substack cookies → test auto-publisher
4. Jetson Orin: NVMe boot, Tailscale, OpenClaw
5. Build Polymarket bot (needs wallet from Matt)
6. Companion app: brand decision → MVP
7. Fix energy agent email (Gmail app password)
