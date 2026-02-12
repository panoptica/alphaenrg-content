#!/usr/bin/env python3
"""
OpenClaw Intelligence Email Generator
"""

import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv()

class IntelligenceEmailer:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.environ.get("EMAIL_USER", "oc@cloudmonkey.io")
        self.sender_password = os.environ.get("EMAIL_PASSWORD", "")
        
    def generate_email_content(self, findings: Dict) -> str:
        """Generate HTML email content from research findings"""
        
        date = findings.get("date", datetime.now().strftime("%Y-%m-%d"))
        opportunities = findings.get("opportunities", [])
        trends = findings.get("trends", [])
        competitive_intel = findings.get("competitive_intel", [])
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px; }}
        .section {{ background: #f8f9fa; padding: 25px; margin-bottom: 20px; border-radius: 10px; border-left: 4px solid #667eea; }}
        .opportunity {{ background: white; padding: 20px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .revenue {{ color: #28a745; font-weight: bold; }}
        .innovation {{ color: #17a2b8; font-weight: bold; }}
        .trend {{ background: #e3f2fd; padding: 15px; border-radius: 8px; border-left: 3px solid #2196f3; margin-bottom: 10px; }}
        .competitor {{ background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 3px solid #ffc107; margin-bottom: 10px; }}
        h1 {{ margin: 0; font-size: 28px; }}
        h2 {{ color: #667eea; border-bottom: 2px solid #e9ecef; padding-bottom: 10px; }}
        .footer {{ text-align: center; margin-top: 30px; color: #6c757d; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 OpenClaw Intelligence Brief</h1>
        <p style="margin: 10px 0 0 0; font-size: 18px;">Daily Market Intelligence • {date}</p>
    </div>
"""
        
        # Top Opportunities
        if opportunities:
            html_content += """
    <div class="section">
        <h2>💰 Top Revenue Opportunities</h2>
"""
            for opp in opportunities[:3]:  # Top 3
                html_content += f"""
        <div class="opportunity">
            <h3>{opp.get('title', 'Untitled Opportunity')}</h3>
            <p>{opp.get('description', 'No description available')}</p>
            <p><span class="revenue">Revenue Potential:</span> {opp.get('revenue_potential', 'TBD')}</p>
            <p><span class="innovation">Innovation Level:</span> {opp.get('innovation_level', 'TBD')}</p>
            <p><strong>Implementation:</strong> {opp.get('implementation', 'To be determined')}</p>
        </div>
"""
            html_content += """
    </div>
"""
        
        # Market Trends
        if trends:
            html_content += """
    <div class="section">
        <h2>📈 Market Trends</h2>
"""
            for trend in trends:
                html_content += f"""
        <div class="trend">
            <h4>{trend.get('trend', 'Trend')}</h4>
            <p>{trend.get('description', '')}</p>
            <p><strong>OpenClaw Angle:</strong> {trend.get('openclaw_angle', 'TBD')}</p>
        </div>
"""
            html_content += """
    </div>
"""
        
        # Competitive Intelligence
        if competitive_intel:
            html_content += """
    <div class="section">
        <h2>🎯 Competitive Intelligence</h2>
"""
            for comp in competitive_intel[:2]:  # Top 2
                html_content += f"""
        <div class="competitor">
            <h4>{comp.get('competitor', 'Competitor')}</h4>
            <p><strong>Their Strength:</strong> {comp.get('strength', 'TBD')}</p>
            <p><strong>Their Weakness:</strong> {comp.get('weakness', 'TBD')}</p>
            <p><strong>OpenClaw Advantage:</strong> {comp.get('openclaw_advantage', 'TBD')}</p>
        </div>
"""
            html_content += """
    </div>
"""
        
        # Action Items
        html_content += """
    <div class="section">
        <h2>🎯 Recommended Actions</h2>
        <div style="background: white; padding: 20px; border-radius: 8px;">
            <ul style="margin: 0; padding-left: 20px;">
                <li><strong>Immediate:</strong> Research top revenue opportunity in detail</li>
                <li><strong>This Week:</strong> Create MVP for highest-potential use case</li>
                <li><strong>This Month:</strong> Outreach to 3 potential enterprise clients</li>
                <li><strong>Strategic:</strong> Position OpenClaw against competitor weaknesses</li>
            </ul>
        </div>
    </div>
    
    <div class="footer">
        <p>Generated by OpenClaw Intelligence Agent • Daily at 8:00 AM</p>
        <p>Questions? Reply to this email or check the research data.</p>
    </div>
</body>
</html>
"""
        
        return html_content
    
    def send_email(self, findings: Dict, recipient: str = "oc@cloudmonkey.io") -> bool:
        """Send intelligence email"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🚀 OpenClaw Intelligence Brief - {findings.get('date', 'Today')}"
            msg['From'] = self.sender_email
            msg['To'] = recipient
            
            # Generate content
            html_content = self.generate_email_content(findings)
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            print(f"📧 Sending intelligence brief to {recipient}...")
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient, msg.as_string())
            
            print("✅ Intelligence brief sent successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def preview_email(self, findings: Dict) -> str:
        """Generate email preview without sending"""
        return self.generate_email_content(findings)

def main():
    # Load latest research data
    import glob
    
    data_files = glob.glob("data/research_*.json")
    if not data_files:
        print("❌ No research data found. Run research.py first.")
        return
    
    latest_file = max(data_files)
    print(f"📊 Loading research data: {latest_file}")
    
    with open(latest_file, 'r') as f:
        findings = json.load(f)
    
    emailer = IntelligenceEmailer()
    
    # Send email
    success = emailer.send_email(findings)
    
    if not success:
        print("📄 Email preview:")
        print(emailer.preview_email(findings))

if __name__ == "__main__":
    main()