#!/usr/bin/env python3
"""
Empire Heartbeat Dashboard
Simple web interface for monitoring status
"""

import json
import time
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.serve_dashboard()
        elif self.path == '/api/status':
            self.serve_api()
        elif self.path.startswith('/static/'):
            self.serve_static()
        else:
            self.send_error(404)

    def serve_dashboard(self):
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>🦀 Empire Status</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: monospace; margin: 20px; background: #1a1a1a; color: #00ff00; }
        .header { text-align: center; margin-bottom: 30px; }
        .device { border: 1px solid #333; margin: 10px 0; padding: 15px; border-radius: 5px; }
        .online { border-color: #00ff00; background: #001100; }
        .offline { border-color: #ff0000; background: #110000; }
        .status { font-weight: bold; }
        .service { margin: 5px 0; padding-left: 20px; }
        .timestamp { color: #888; font-size: 0.9em; }
        .refresh { margin: 20px 0; text-align: center; }
        .issues { background: #330000; border: 1px solid #ff0000; padding: 10px; margin: 10px 0; }
        .actions { background: #003300; border: 1px solid #00ff00; padding: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🦀 Empire Compute Status</h1>
        <div class="timestamp" id="lastUpdate">Loading...</div>
    </div>
    
    <div id="content">Loading empire status...</div>
    
    <div class="refresh">
        <button onclick="loadStatus()" style="background: #333; color: #00ff00; border: 1px solid #666; padding: 10px 20px; font-family: monospace;">Refresh Status</button>
    </div>

    <script>
        function loadStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => updateDashboard(data))
                .catch(error => {
                    document.getElementById('content').innerHTML = '<div class="offline">❌ Error loading status: ' + error + '</div>';
                });
        }
        
        function updateDashboard(data) {
            let html = '';
            
            // Issues
            if (data.issues && data.issues.length > 0) {
                html += '<div class="issues"><h3>🚨 Issues</h3>';
                data.issues.forEach(issue => html += '<div>• ' + issue + '</div>');
                html += '</div>';
            }
            
            // Actions  
            if (data.actions && data.actions.length > 0) {
                html += '<div class="actions"><h3>🔧 Recent Actions</h3>';
                data.actions.forEach(action => html += '<div>• ' + action + '</div>');
                html += '</div>';
            }
            
            // Devices
            if (data.devices) {
                Object.entries(data.devices).forEach(([key, device]) => {
                    let cssClass = device.ping ? 'online' : 'offline';
                    let statusIcon = device.ping ? '✅' : '❌';
                    
                    html += `<div class="device ${cssClass}">`;
                    html += `<div class="status">${statusIcon} ${device.name} (${device.ip})</div>`;
                    
                    if (device.services) {
                        Object.entries(device.services).forEach(([service, status]) => {
                            let serviceIcon = status.healthy !== undefined ? 
                                (status.healthy ? '✅' : '❌') : 
                                (status.port_open ? '✅' : '❌');
                            html += `<div class="service">${serviceIcon} ${service.toUpperCase()}`;
                            if (status.healthy !== undefined) {
                                html += ` (${status.healthy ? 'healthy' : 'unhealthy'})`;
                            }
                            html += '</div>';
                        });
                    }
                    
                    html += '</div>';
                });
            }
            
            document.getElementById('content').innerHTML = html;
            document.getElementById('lastUpdate').textContent = 'Last updated: ' + new Date(data.timestamp).toLocaleString();
        }
        
        // Auto-refresh every 30 seconds
        setInterval(loadStatus, 30000);
        
        // Initial load
        loadStatus();
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_api(self):
        # Load latest status
        state_file = Path("empire-state.json")
        
        if state_file.exists():
            try:
                with open(state_file) as f:
                    data = json.load(f)
                
                # Generate mock report based on current state
                report = {
                    "timestamp": datetime.now().isoformat(),
                    "devices": data.get("devices", {}),
                    "issues": [],
                    "actions": []
                }
                
                response = json.dumps(report)
            except Exception as e:
                response = json.dumps({"error": str(e)})
        else:
            response = json.dumps({"error": "No monitoring data available"})
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response.encode())

    def log_message(self, format, *args):
        # Suppress access logs
        pass

def run_dashboard(port=8888):
    server_address = ('', port)
    httpd = HTTPServer(server_address, DashboardHandler)
    
    print(f"🦀 Empire Dashboard running on http://localhost:{port}")
    print("Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped")
        httpd.server_close()

if __name__ == "__main__":
    run_dashboard()