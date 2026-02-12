#!/usr/bin/env python3
"""
Empire Heartbeat Monitor
Keeps the compute empire online and healthy
"""

import subprocess
import json
import time
import requests
import socket
from datetime import datetime, timedelta
from pathlib import Path
import smtplib
from email.mime.text import MIMEText

class EmpireMonitor:
    def __init__(self):
        self.config = {
            "devices": {
                "mac_mini": {
                    "ip": "192.168.154.44",
                    "name": "Mac Mini M4",
                    "services": {
                        "ollama": {"port": 11434, "endpoint": "/api/tags"},
                        "ssh": {"port": 22}
                    },
                    "credentials": {"user": "macmini", "pass": "!1Longmore@@"}
                },
                "kali": {
                    "ip": "192.168.154.193", 
                    "name": "Kali Y2K",
                    "services": {
                        "ssh": {"port": 22},
                        "rdp": {"port": 3389}
                    },
                    "credentials": {"user": "oc", "pass": "Apple24"}
                },
                "jetson": {
                    "ip": "192.168.154.124",
                    "name": "Jetson Orin",
                    "services": {
                        "ssh": {"port": 22}
                    },
                    "credentials": {"user": "deepseek", "pass": "jetson_orin"}
                }
            },
            "alerts": {
                "email": "oc@cloudmonkey.io",
                "min_interval": 300  # 5 min between alerts
            }
        }
        self.state_file = Path("empire-state.json")
        self.load_state()

    def load_state(self):
        """Load previous monitoring state"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                self.state = json.load(f)
        else:
            self.state = {
                "devices": {},
                "last_alerts": {},
                "uptime_stats": {}
            }

    def save_state(self):
        """Save monitoring state"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

    def ping_device(self, ip):
        """Check if device responds to ping"""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '2', ip],
                capture_output=True, timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def check_port(self, ip, port, timeout=3):
        """Check if port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False

    def check_ollama_health(self, ip, port=11434):
        """Check Ollama API health"""
        try:
            response = requests.get(f"http://{ip}:{port}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def auto_fix_ollama(self, device_name, ip):
        """Try to auto-restart Ollama service"""
        creds = self.config["devices"][device_name]["credentials"]
        try:
            # SSH command to restart Ollama
            cmd = [
                "sshpass", "-p", creds["pass"],
                "ssh", "-o", "ConnectTimeout=10",
                "-o", "StrictHostKeyChecking=no",
                f"{creds['user']}@{ip}",
                "pkill ollama; sleep 2; OLLAMA_HOST=0.0.0.0 nohup ollama serve > /tmp/ollama.log 2>&1 &"
            ]
            subprocess.run(cmd, timeout=15, capture_output=True)
            
            # Wait and check if it worked
            time.sleep(10)
            if self.check_ollama_health(ip):
                return True
        except:
            pass
        return False

    def network_scan(self, base_ip="192.168.154"):
        """Scan network to find moved devices"""
        found_devices = {}
        
        for i in [1, 44, 124, 193]:  # Check known IPs first
            ip = f"{base_ip}.{i}"
            if self.ping_device(ip):
                # Try to identify device by SSH banner or services
                device_type = self.identify_device(ip)
                if device_type:
                    found_devices[ip] = device_type
        
        return found_devices

    def identify_device(self, ip):
        """Try to identify what device this is"""
        # Check for Ollama (Mac Mini)
        if self.check_ollama_health(ip):
            return "mac_mini"
        
        # Check SSH banners or other identifying features
        for device, config in self.config["devices"].items():
            if self.check_port(ip, 22):  # SSH
                # Could try SSH banner detection here
                pass
        
        return "unknown"

    def send_alert(self, subject, message):
        """Send email alert"""
        now = datetime.now()
        last_alert = self.state["last_alerts"].get(subject, 0)
        
        # Rate limiting
        if now.timestamp() - last_alert < self.config["alerts"]["min_interval"]:
            return
        
        print(f"🚨 ALERT: {subject}")
        print(message)
        
        # Update alert timestamp
        self.state["last_alerts"][subject] = now.timestamp()
        self.save_state()

    def monitor_cycle(self):
        """Single monitoring cycle"""
        now = datetime.now()
        status_report = {
            "timestamp": now.isoformat(),
            "devices": {},
            "issues": [],
            "actions": []
        }

        for device_name, config in self.config["devices"].items():
            device_status = {
                "name": config["name"],
                "ip": config["ip"],
                "ping": False,
                "services": {}
            }

            # Basic connectivity
            device_status["ping"] = self.ping_device(config["ip"])
            
            if device_status["ping"]:
                # Check each service
                for service_name, service_config in config["services"].items():
                    port = service_config["port"]
                    
                    if service_name == "ollama":
                        # Special health check for Ollama
                        healthy = self.check_ollama_health(config["ip"], port)
                        device_status["services"][service_name] = {
                            "port_open": self.check_port(config["ip"], port),
                            "healthy": healthy
                        }
                        
                        # Auto-fix if port open but not healthy
                        if self.check_port(config["ip"], port) and not healthy:
                            print(f"🔧 Auto-fixing Ollama on {device_name}")
                            if self.auto_fix_ollama(device_name, config["ip"]):
                                status_report["actions"].append(f"Auto-restarted Ollama on {device_name}")
                                device_status["services"][service_name]["healthy"] = True
                            else:
                                status_report["issues"].append(f"Failed to auto-fix Ollama on {device_name}")
                    else:
                        # Standard port check
                        device_status["services"][service_name] = {
                            "port_open": self.check_port(config["ip"], port)
                        }
            else:
                # Device offline - try to find it
                status_report["issues"].append(f"{config['name']} offline at {config['ip']}")

            status_report["devices"][device_name] = device_status

        # Network scan if devices are missing
        offline_devices = [d for d, s in status_report["devices"].items() if not s["ping"]]
        if offline_devices:
            print("🔍 Scanning network for moved devices...")
            found = self.network_scan()
            if found:
                status_report["actions"].append(f"Found devices at new IPs: {found}")

        # Generate alerts for persistent issues
        critical_issues = [
            issue for issue in status_report["issues"] 
            if "offline" in issue.lower()
        ]
        
        if critical_issues:
            self.send_alert(
                "Compute Empire Alert", 
                f"Critical issues detected:\n" + "\n".join(critical_issues)
            )

        return status_report

    def run_forever(self, interval=60):
        """Run monitoring loop forever"""
        print("🦀 Empire Heartbeat Monitor Starting...")
        print(f"Monitoring {len(self.config['devices'])} devices every {interval}s")
        
        while True:
            try:
                report = self.monitor_cycle()
                
                # Log status
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                online_count = sum(1 for d in report["devices"].values() if d["ping"])
                total_count = len(report["devices"])
                
                print(f"[{timestamp}] Empire Status: {online_count}/{total_count} devices online")
                
                if report["issues"]:
                    print(f"⚠️  Issues: {len(report['issues'])}")
                    for issue in report["issues"]:
                        print(f"   - {issue}")
                
                if report["actions"]:
                    print(f"🔧 Actions: {len(report['actions'])}")
                    for action in report["actions"]:
                        print(f"   - {action}")

                self.save_state()
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitor stopped by user")
                break
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                time.sleep(30)  # Wait before retrying

if __name__ == "__main__":
    monitor = EmpireMonitor()
    monitor.run_forever()