# Hardware Troubleshooting Guide

## Current Status (2026-02-06 04:15 GMT)
❌ All compute devices offline:
- Mac Mini M4 (192.168.154.44) - Unreachable
- Kali Box (192.168.154.193) - Unreachable  
- Jetson Nano (192.168.154.124) - Unreachable

## Likely Causes
1. **Power outage** - Devices need manual restart
2. **Network change** - Router restart changed DHCP assignments
3. **WiFi issues** - Devices disconnected from network

## Quick Fixes

### 1. Check Network
```bash
# Scan for devices on network
nmap -sn 192.168.154.0/24
# Or try other common ranges:
nmap -sn 192.168.1.0/24
nmap -sn 192.168.0.0/24
```

### 2. Power Cycle Devices
- **Mac Mini M4**: Press power button, wait for boot
- **Kali Box**: Check power LED, restart if needed
- **Jetson Nano**: Unplug/replug power adapter

### 3. Router Check
- Did the router restart and change DHCP range?
- Are devices getting new IP addresses?

## Once Online
1. Mac Mini: Start Ollama with `OLLAMA_HOST=0.0.0.0 ollama serve &`
2. Jetson: Try `deepseek/jetson_orin` credentials 
3. Deploy optimized OpenClaw config

## Emergency Fallback
If hardware stays offline, we can still optimize:
- Use Gemini Pro for cheaper bulk work
- Set up Bedrock Claude (potentially cheaper)
- Add smart routing in current config