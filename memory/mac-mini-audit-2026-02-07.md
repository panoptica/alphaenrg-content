# Mac Mini Security Audit - 2026-02-07

## System Info
- **Hostname:** macmini@192.168.154.44
- **OS:** macOS 26.2 (Build 25C56)
- **Disk:** 8% used (11GB/228GB), 137GB free

## Services Running
✅ **Ollama** - Port 11434 (LLM inference)
✅ **ComfyUI** - Port 8188 (Image generation)

## Security Status

### ✅ Good
- Only 2 services exposed (both needed)
- No unnecessary homebrew services
- Single user account (macmini)
- All brew packages up to date
- Recent logins only from Tailscale IPs (100.89.198.106)

### ⚠️ Needs Review (Permission Issues)
- Firewall status: Unknown (needs sudo)
- SSH config: Cannot read (needs sudo)
- Could not check password authentication settings

### 🧹 Cleanup Done
- Homebrew cache: Cleared
- Pip cache: Cleared
- Cache reduced: 2.5GB → 1.2GB
- Temp files: Clean

## Models Installed
- **Ollama:** Llama3 (local LLM)
- **ComfyUI Total:** 16.5GB
  - SDXL Base: 6.5GB
  - CLIP Vision: 5.8GB  
  - IPAdapter: 3.4GB
  - InsightFace: 415MB
  - LoRAs: 368MB

## Recommendations

### Critical
1. **Enable macOS Firewall** - Block all except 8188, 11434, 22 (SSH)
2. **SSH Hardening:**
   - Disable password auth (keys only)
   - Disable root login
   - Consider changing default port

### Optional
3. **Install OpenClaw?** - Currently NOT installed. Do we need it on compute nodes?
4. **Monitor Services** - Set up auto-restart for Ollama/ComfyUI if they crash
5. **Backups** - ComfyUI workflows and model library

### Low Priority
6. Clean up empty ComfyUI model folders
7. Consider setting up log rotation
8. Review login history weekly

## Next Actions
- [ ] Matt: Review firewall settings (requires sudo/GUI)
- [ ] Matt: Decide if OpenClaw should be on Mac Mini
- [ ] Claw: Set up service monitoring/restart scripts
