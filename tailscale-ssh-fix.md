# Tailscale SSH Fix Guide

## Issue: SSH timeout to 100.97.28.29

The Mac Mini is connected to Tailscale but SSH isn't accessible. Let's diagnose:

## Step 1: Check SSH Status on Mac Mini
```bash
# SSH to Mac Mini locally first
ssh macmini@192.168.154.44

# Then run these on Mac Mini:
sudo systemsetup -getremotelogin
sudo systemsetup -setremotelogin on  # If not enabled

# Check if SSH is listening
sudo lsof -i :22
netstat -an | grep :22
```

## Step 2: Tailscale SSH Configuration  
The GUI app issue we hit earlier - need to fix this:

```bash
# On Mac Mini, check current Tailscale status
tailscale status
tailscale ip -4

# Try enabling SSH again (may work now that device is connected)
sudo tailscale up --ssh --accept-routes --reset

# If still fails due to GUI app, install CLI version:
sudo /Applications/Tailscale.app/Contents/MacOS/Tailscale down
brew install tailscale
sudo $(brew --prefix)/bin/tailscaled install-system-daemon
sudo tailscale up --ssh --accept-routes
```

## Step 3: Test Tailscale SSH From Mac Mini Itself
```bash
# On Mac Mini, test SSH to itself via Tailscale IP
ssh macmini@100.97.28.29

# If this works, problem is external routing
# If this fails, SSH over Tailscale isn't working
```

## Step 4: Firewall Check
```bash
# Check macOS firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/sbin/sshd
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/sbin/sshd
```

## Step 5: Alternative - Tailscale Serve (if SSH fails)
```bash
# On Mac Mini, create HTTP tunnel for SSH
tailscale serve --bg --https=443 tcp://localhost:22

# Then connect via: ssh macmini@100.97.28.29:443
```

## Root Cause Likely:
- **GUI Tailscale app** doesn't support SSH server (sandboxed)
- Need **CLI Tailscale** for SSH functionality
- OR **system SSH** not enabled/accessible