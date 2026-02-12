"""
Email delivery module for the Energy Intelligence Agent.

Sends daily digest emails with:
- Top 3 signals (full analysis)
- 10 interesting signals (one-liners)
- Thumbs up/down links for feedback
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Any
import logging
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from synthesis.llm import generate_digest_narrative, analyze_convergence
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

try:
    from config.tickers import find_tickers_in_text
    TICKERS_AVAILABLE = True
except ImportError:
    TICKERS_AVAILABLE = False
    def find_tickers_in_text(text):
        return []

try:
    from config.tickers import find_tickers_in_text
    TICKERS_AVAILABLE = True
except ImportError:
    TICKERS_AVAILABLE = False
    def find_tickers_in_text(text):
        return []

FEEDBACK_EMAIL = "oc@cloudmonkey.io"

logger = logging.getLogger(__name__)


class EmailDelivery:
    """Send digest emails via Gmail SMTP."""
    
    def __init__(
        self,
        smtp_user: str = None,
        smtp_password: str = None,
        recipient: str = None
    ):
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_user = smtp_user or os.getenv("SMTP_USER", "")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD", "")
        self.recipient = recipient or os.getenv("EMAIL_RECIPIENT", self.smtp_user)
        
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured")
    
    def send_digest(
        self, 
        top_signals: List[Dict[str, Any]], 
        interesting_signals: List[Dict[str, Any]],
        stats: Dict[str, Any] = None
    ) -> bool:
        """
        Send the daily digest email.
        
        Args:
            top_signals: Top 3 signals with full analysis
            interesting_signals: Next 10 signals (one-liners)
            stats: Optional collection statistics
        """
        if not self.smtp_user or not self.smtp_password:
            logger.error("Cannot send email: SMTP credentials not configured")
            return False
        
        subject = f"🔋 Energy Intelligence Digest - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Generate AI narrative if available
        ai_narrative = None
        convergence = None
        if LLM_AVAILABLE:
            try:
                all_signals = top_signals + interesting_signals
                digest_stats = {
                    'total': stats.get('total_signals', 0) if stats else len(all_signals),
                    'strong': len([s for s in all_signals if s.get('score', {}).get('final_score', 0) >= 7]),
                    'critical': len([s for s in all_signals if s.get('score', {}).get('final_score', 0) >= 12])
                }
                ai_narrative = generate_digest_narrative(all_signals, digest_stats)
                convergence = analyze_convergence(all_signals)
                logger.info("AI narrative generated successfully")
            except Exception as e:
                logger.warning(f"Failed to generate AI narrative: {e}")
        
        # Build HTML email
        html_content = self._build_html(top_signals, interesting_signals, stats, ai_narrative, convergence)
        text_content = self._build_text(top_signals, interesting_signals, stats)
        
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.smtp_user
        msg["To"] = self.recipient
        
        msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))
        
        # Send
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, self.recipient, msg.as_string())
            
            logger.info(f"Digest email sent to {self.recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_critical_alert(self, signal: Dict[str, Any]) -> bool:
        """Send immediate alert for critical signals (score >= 12)."""
        if not self.smtp_user or not self.smtp_password:
            return False
        
        subject = f"🚨 CRITICAL SIGNAL [{signal.get('score', {}).get('final_score', 0):.1f}] - {signal.get('domain', 'Unknown')}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #dc3545; color: white; padding: 20px; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0;">🚨 Critical Signal Detected</h1>
            </div>
            <div style="padding: 20px; border: 1px solid #ddd; border-top: none;">
                <h2 style="color: #333; margin-top: 0;">{signal.get('title', 'Unknown')}</h2>
                
                <table style="width: 100%; margin: 20px 0;">
                    <tr>
                        <td><strong>Score:</strong></td>
                        <td>{signal.get('score', {}).get('final_score', 0):.1f}</td>
                    </tr>
                    <tr>
                        <td><strong>Domain:</strong></td>
                        <td>{signal.get('domain', 'Unknown')}</td>
                    </tr>
                    <tr>
                        <td><strong>Source:</strong></td>
                        <td>{signal.get('source', 'Unknown')}</td>
                    </tr>
                </table>
                
                <p>{signal.get('abstract', '')[:500]}...</p>
                
                <a href="{signal.get('url', '#')}" style="display: inline-block; background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">View Source →</a>
            </div>
        </body>
        </html>
        """
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.smtp_user
        msg["To"] = self.recipient
        msg["X-Priority"] = "1"  # High priority
        
        msg.attach(MIMEText(html_content, "html"))
        
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, self.recipient, msg.as_string())
            
            logger.info(f"Critical alert sent for signal {signal.get('source_id')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send critical alert: {e}")
            return False
    
    def _ticker_html(self, sig: Dict) -> str:
        """Build ticker badges for a signal."""
        text = f"{sig.get('title', '')} {sig.get('abstract', '')}"
        tickers = find_tickers_in_text(text)
        if not tickers:
            return ''
        badges = ' '.join(
            f'<span style="display:inline-block;background:#e8f5e9;color:#2e7d32;padding:2px 8px;border-radius:12px;font-size:12px;font-weight:bold;margin:2px;">${t}</span>'
            for _, t in tickers[:5]
        )
        return f'<p style="margin:5px 0;">{badges}</p>'
    
    def _ticker_inline(self, sig: Dict) -> str:
        """Inline ticker tags for interesting signals table."""
        text = f"{sig.get('title', '')} {sig.get('abstract', '')}"
        tickers = find_tickers_in_text(text)
        if not tickers:
            return ''
        return ' ' + ' '.join(
            f'<span style="color:#2e7d32;font-size:11px;font-weight:bold;">${t}</span>'
            for _, t in tickers[:3]
        )
    
    def _feedback_html(self, sig: Dict, idx: int) -> str:
        """Build thumbs up/down mailto links for a signal."""
        from urllib.parse import quote
        sig_id = sig.get('source_id', f'signal_{idx}')
        subject = quote(f'Signal Feedback #{idx}')
        up_body = quote(f'{sig_id}:thumbsup')
        down_body = quote(f'{sig_id}:thumbsdown')
        return (
            f'<a href="mailto:{FEEDBACK_EMAIL}?subject={subject}&body={up_body}" '
            f'style="text-decoration:none;font-size:18px;" title="Good signal">👍</a> '
            f'<a href="mailto:{FEEDBACK_EMAIL}?subject={subject}&body={down_body}" '
            f'style="text-decoration:none;font-size:18px;" title="Not useful">👎</a>'
        )
    
    def _build_html(
        self, 
        top_signals: List[Dict], 
        interesting: List[Dict],
        stats: Dict = None,
        ai_narrative: str = None,
        convergence: str = None
    ) -> str:
        """Build HTML email content."""
        
        today = datetime.now().strftime('%A, %B %d, %Y')
        
        # AI Narrative section
        ai_section = ""
        if ai_narrative:
            # Find tickers mentioned across all signals for the narrative
            all_text = " ".join(s.get('title', '') + ' ' + s.get('abstract', '') for s in top_signals + interesting)
            narrative_tickers = find_tickers_in_text(all_text + ' ' + ai_narrative)
            ticker_badge = ""
            if narrative_tickers:
                ticker_badge = f'<p style="margin:8px 0 0 0;"><strong style="color:#007bff;">📈 Key tickers: {", ".join(f"${t}" for _, t in narrative_tickers)}</strong></p>'
            ai_section = f"""
            <div style="background: #f0f7ff; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #007bff;">
                <h3 style="margin: 0 0 10px 0; color: #007bff;">🤖 AI Analysis</h3>
                <p style="color: #333; line-height: 1.6;">{ai_narrative.replace(chr(10), '<br>')}</p>
                {ticker_badge}
            </div>
            """
        
        # Convergence section
        convergence_section = ""
        if convergence:
            convergence_section = f"""
            <div style="background: #fff3cd; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #ffc107;">
                <h4 style="margin: 0 0 10px 0; color: #856404;">📊 Convergence Signals</h4>
                <p style="color: #856404;">{convergence}</p>
            </div>
            """
        
        # Top 3 section
        top_html = ""
        for i, sig in enumerate(top_signals[:3], 1):
            score = sig.get('score', {})
            top_html += f"""
            <div style="background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #28a745;">
                <h3 style="margin: 0 0 10px 0; color: #333;">
                    #{i} [{score.get('final_score', 0):.1f}] {sig.get('title', 'Unknown')[:80]}...
                </h3>
                {self._ticker_html(sig)}
                <p style="color: #666; margin: 5px 0;">
                    <strong>Domain:</strong> {sig.get('domain', 'N/A')} | 
                    <strong>Source:</strong> {sig.get('source', 'N/A')} |
                    <strong>Category:</strong> {score.get('category', 'N/A')}
                </p>
                <p style="color: #333;">{sig.get('abstract', '')[:300]}...</p>
                <p>
                    <a href="{sig.get('url', '#')}" style="color: #007bff;">View Source →</a>
                    &nbsp;&nbsp;{self._feedback_html(sig, i)}
                </p>
                <p style="font-size: 12px; color: #999;">
                    Score breakdown: {score.get('breakdown', {})}
                </p>
            </div>
            """
        
        # Interesting signals section
        interesting_html = "<table style='width: 100%; border-collapse: collapse;'>"
        for idx, sig in enumerate(interesting[:10], len(top_signals) + 1):
            score = sig.get('score', {})
            interesting_html += f"""
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 10px; width: 50px; font-weight: bold; color: #28a745;">{score.get('final_score', 0):.1f}</td>
                <td style="padding: 10px;">{sig.get('domain', 'N/A')}</td>
                <td style="padding: 10px;">
                    <a href="{sig.get('url', '#')}" style="color: #333;">{sig.get('title', 'Unknown')[:60]}...</a>
                    {self._ticker_inline(sig)}
                </td>
                <td style="padding: 10px; white-space: nowrap;">{self._feedback_html(sig, idx)}</td>
            </tr>
            """
        interesting_html += "</table>"
        
        # Stats section
        stats_html = ""
        if stats:
            stats_html = f"""
            <div style="background: #e9ecef; padding: 15px; border-radius: 8px; margin-top: 20px;">
                <h4 style="margin: 0 0 10px 0;">📊 Collection Stats</h4>
                <p style="margin: 5px 0;">Total signals: {stats.get('total_signals', 0)}</p>
                <p style="margin: 5px 0;">By source: {stats.get('by_source', {})}</p>
                <p style="margin: 5px 0;">By domain: {stats.get('by_domain', {})}</p>
            </div>
            """
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 700px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0;">
                <h1 style="margin: 0;">🔋 Energy Intelligence Digest</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">{today}</p>
            </div>
            
            <div style="padding: 20px; border: 1px solid #ddd; border-top: none;">
                {ai_section}
                {convergence_section}
                
                <h2 style="color: #333; border-bottom: 2px solid #28a745; padding-bottom: 10px;">🎯 Top 3 Signals</h2>
                {top_html}
                
                <h2 style="color: #333; border-bottom: 2px solid #17a2b8; padding-bottom: 10px; margin-top: 40px;">📋 Interesting Signals</h2>
                {interesting_html}
                
                {stats_html}
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #999; font-size: 12px;">
                    <p>Energy Intelligence Agent v1.0</p>
                    <p>Reply to rate signals: +ID for 👍, -ID for 👎</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _build_text(
        self, 
        top_signals: List[Dict], 
        interesting: List[Dict],
        stats: Dict = None
    ) -> str:
        """Build plain text email content."""
        
        today = datetime.now().strftime('%A, %B %d, %Y')
        
        text = f"""
ENERGY INTELLIGENCE DIGEST
{today}
{'=' * 50}

TOP 3 SIGNALS
{'-' * 30}
"""
        
        for i, sig in enumerate(top_signals[:3], 1):
            score = sig.get('score', {})
            text += f"""
#{i} [{score.get('final_score', 0):.1f}] {sig.get('title', 'Unknown')[:70]}
Domain: {sig.get('domain', 'N/A')} | Source: {sig.get('source', 'N/A')}
{sig.get('abstract', '')[:200]}...
URL: {sig.get('url', 'N/A')}

"""
        
        text += f"""
INTERESTING SIGNALS
{'-' * 30}
"""
        
        for sig in interesting[:10]:
            score = sig.get('score', {})
            text += f"[{score.get('final_score', 0):.1f}] {sig.get('domain', 'N/A')}: {sig.get('title', 'Unknown')[:50]}...\n"
        
        return text


def send_test_email(recipient: str = None):
    """Send a test email to verify configuration."""
    delivery = EmailDelivery(recipient=recipient)
    
    test_signal = {
        'title': 'Test Signal - Energy Intelligence Agent',
        'abstract': 'This is a test signal to verify email delivery is working correctly.',
        'domain': 'test',
        'source': 'test',
        'url': 'https://example.com',
        'score': {
            'final_score': 10.5,
            'category': 'strong',
            'breakdown': {'test': 1}
        }
    }
    
    return delivery.send_digest([test_signal], [test_signal] * 5)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test with environment variables
    if send_test_email():
        print("Test email sent successfully!")
    else:
        print("Failed to send test email. Check credentials.")
