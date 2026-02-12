# Permanent Connection Setup Options

## Option 1: Tailscale (Recommended) 
**Pros**: Secure, zero-config, works from anywhere
**Setup**: 
```bash
# On Mac Mini M4
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Enable in OpenClaw config
"tailscale": {
  "mode": "on",
  "resetOnExit": false
}
```

## Option 2: SSH Reverse Tunnel
**Pros**: Uses existing SSH, no additional software
**Setup**:
```bash
# From Mac Mini, create persistent reverse tunnel
ssh -R 2222:localhost:22 -N -f your-vps-server

# I connect via: ssh -p 2222 macmini@your-vps-server
```

## Option 3: OpenClaw Gateway Bridge
**Pros**: Native OpenClaw integration
**Setup**: Enable gateway binding to network interface:
```json
"gateway": {
  "bind": "0.0.0.0",  // Instead of "loopback"
  "port": 18789
}
```

## Option 4: VPN Server on Mac Mini
**Pros**: Full network access to entire 192.168.154.x range
**Setup**: Install WireGuard server on Mac Mini

## Recommendation: Start with Tailscale
- Most secure and user-friendly
- Zero network config needed  
- Works from anywhere
- Can add other devices to same Tailscale network