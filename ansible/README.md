# OpenClaw Distributed Infrastructure

Ansible-based deployment for distributed OpenClaw network across multiple specialized systems.

## Architecture

- **Mac Mini (master)**: Primary coordinator, gateway, high-end models
- **Kali Y2K (osint)**: OSINT collection, monitoring, reconnaissance  
- **Jetson Orin (ai)**: AI/CV processing, GPU inference, satellite imagery

## Quick Start

```bash
# Test connectivity to all systems
make check

# Deploy everything
make deploy  

# Deploy individual systems
make master   # Mac Mini only
make osint    # Kali Y2K only  
make ai       # Jetson Orin only

# Dry run (check what would change)
make dry-run
```

## Prerequisites

1. **Ansible installed**: `pip install ansible`
2. **SSH keys set up**: Key-based auth to all systems as `oc` user
3. **Netbird mesh**: All systems connected (100.87.x.x network)
4. **Secrets configured**: `ansible-vault create vault.yml`

## Inventory

- **production.yml**: Live system IPs and SSH config
- **staging.yml**: Development/test systems (if needed)

## Secrets Management

```bash
# Create encrypted secrets file
ansible-vault create vault.yml

# Edit secrets
make vault-edit
```

Example vault.yml:
```yaml
vault_netbird_setup_key: "your-netbird-setup-key"
vault_openclaw_telegram_token: "your-telegram-bot-token"
vault_github_token: "your-github-pat"
```

## Role Structure

- **common**: Base system setup, users, directories
- **netbird**: Mesh network configuration
- **openclaw-core**: Core OpenClaw installation
- **openclaw-master**: Master coordinator setup
- **openclaw-osint**: OSINT collection services
- **openclaw-ai**: AI/CV processing setup
- **monitoring**: Logging, metrics, health checks

## CI/CD Integration

This structure supports automated deployment via:
- GitHub Actions
- GitLab CI
- Local development workflow

## System Requirements

### Mac Mini (Master)
- 16GB RAM, M4 chip
- Primary models: Claude Sonnet, Gemini Flash  
- Services: Gateway, Telegram, Energy Digest

### Kali Y2K (OSINT)
- 8GB+ RAM recommended
- Services: Reddit/News/Darkweb collectors
- Tools: nmap, sqlmap, subfinder

### Jetson Orin (AI)
- 8GB RAM + GPU
- CUDA toolkit, optimized power settings
- Services: Image analysis, video processing