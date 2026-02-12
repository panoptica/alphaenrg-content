# Empire Heartbeat Monitor

**Keeps your compute empire online and healthy** 🦀

## Features

- **Real-time monitoring** of all compute devices
- **Auto-recovery** for common failures (Ollama restarts)
- **Network discovery** when devices change IPs
- **Web dashboard** for remote monitoring
- **Email alerts** for critical issues
- **Persistent state** tracking uptime/downtime

## Quick Start

```bash
# Install and run
cd empire-heartbeat
chmod +x install.sh status.sh
./install.sh

# Start monitoring (background)
./monitor.py &

# Check status anytime  
./status.sh

# Web dashboard (http://localhost:8888)
./dashboard.py &
```

## Monitored Devices

- **Mac Mini M4** (192.168.154.44)
  - Ping connectivity
  - SSH access (port 22)
  - Ollama API health (port 11434)
  - Auto-restart Ollama if unhealthy

- **Kali Y2K** (192.168.154.193)  
  - Ping connectivity
  - SSH access (port 22)
  - RDP access (port 3389)

- **Jetson Orin** (192.168.154.124)
  - Ping connectivity  
  - SSH access (port 22)

## Auto-Recovery Features

### Ollama Auto-Restart
If Ollama port is open but API unhealthy:
1. SSH to Mac Mini
2. Kill existing Ollama process  
3. Restart with network binding: `OLLAMA_HOST=0.0.0.0 ollama serve &`
4. Verify health after 10s

### Network Discovery
If devices go offline at known IPs:
1. Scan network ranges for moved devices
2. Identify by service signatures (Ollama, SSH banners)
3. Update IP mappings automatically
4. Alert about IP changes

### Smart Alerting
- Rate-limited emails (5min minimum between same alert)
- Critical vs warning classifications
- Persistent issue tracking

## Files

- `monitor.py` - Main monitoring daemon
- `dashboard.py` - Web interface (port 8888)
- `status.sh` - Quick CLI status check  
- `install.sh` - Setup script
- `empire-state.json` - Persistent monitoring state
- `empire-heartbeat.service` - systemd service file
- `com.openclaw.empire-heartbeat.plist` - macOS launchd service

## Integration

### OpenClaw HEARTBEAT.md
Add to your workspace `HEARTBEAT.md`:
```markdown
# Check empire health
if [ -f "empire-heartbeat/empire-state.json" ]; then
  cd empire-heartbeat && ./status.sh
else
  echo "Empire monitor not running"
fi
```

### Auto-start Options
**Linux (systemd):**
```bash
sudo cp empire-heartbeat.service /etc/systemd/system/
sudo systemctl enable empire-heartbeat
sudo systemctl start empire-heartbeat
```

**macOS (launchd):**  
```bash
launchctl load ~/Library/LaunchAgents/com.openclaw.empire-heartbeat.plist
launchctl start com.openclaw.empire-heartbeat
```

## Configuration

Edit `monitor.py` to customize:
- Device IPs and credentials
- Service endpoints  
- Alert email settings
- Check intervals
- Auto-recovery actions

## Logs

- `monitor.log` - Standard output (when run as service)
- `monitor.error.log` - Error output (when run as service)
- Console output when run manually

## Architecture

```
monitor.py (daemon)
├── Device ping checks (60s intervals)
├── Service health checks (SSH, Ollama, RDP)  
├── Auto-recovery actions (restart services)
├── Network discovery (when devices offline)
├── State persistence (empire-state.json)
├── Email alerting (rate-limited)
└── Web API (for dashboard)

dashboard.py (web interface)
├── HTTP server (port 8888)
├── Real-time status display
├── Auto-refresh every 30s
└── Mobile-friendly interface
```

This solves the scalability problem by making the empire self-healing and proactively monitored. No more wondering if hardware went offline!