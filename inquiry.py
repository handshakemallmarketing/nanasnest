import os, json, re, time, base64, threading
from collections import deque
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.parse import urlencode

MAIL = "nanasnestcare@gmail.com"
KEYS = ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REFRESH_TOKEN")
ORIGINS = {"https://nanasnestcare.com", "https://nanasnest-preview-production.up.railway.app"}
lock = threading.Lock()
attempts = deque()
recipients = {}

def validate(data):
    if not isinstance(data, dict) or data.get("website"):
        raise ValueError()
    name = data.get("name", "")
    address = data.get("email", "")
    service = data.get("service", "")
    if not all(isinstance(x, str) for x in (name,address,service)):
        raise ValueError()
    if not 1 <= len(name.strip()) <= 80 or any(ord(c)<32 for c in name):
        raise ValueError()
    if len(address)>254 or not re.fullmatch(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,63}",address):
        raise ValueError()
    if service not in ("Overnight newborn care","Sleep coaching","General inquiry"):
        raise ValueError()
    return name.strip(), address.lower(), service

def reserve(address):
    now=time.monotonic()
    with lock:
        while attempts and now-attempts[0]>3600: attempts.popleft()
        for key, stamp in list(recipients.items()):
            if now-stamp>3600: del recipients[key]
        if len(attempts)>=20 or address in recipients: return False
        attempts.append(now)
        recipients[address]=now
        return True

def post(url, data, headers):
    with urlopen(Request(url,data=data,headers=headers,method="POST"),timeout=8) as response:
        return json.load(response)

def send(to, subject, body, token, reply=None):
    msg=EmailMessage()
    msg["From"]=MAIL
    msg["To"]=to
    msg["Subject"]=subject
    if reply: msg["Reply-To"]=reply
    msg.set_content(body)
    raw=base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return post("https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
                json.dumps({"raw":raw}).encode(),
                {"Authorization":"Bearer "+token,"Content-Type":"application/json"})

def deliver(name,address,service):
    token=post("https://oauth2.googleapis.com/token",urlencode({
        "client_id":os.environ[KEYS[0]],"client_secret":os.environ[KEYS[1]],
        "refresh_token":os.environ[KEYS[2]],"grant_type":"refresh_token"
    }).encode(),{"Content-Type":"application/x-www-form-urlencoded"})["access_token"]
    send(MAIL,"New website inquiry",f"Name: {name}\nEmail: {address}\nService: {service}",token,address)
    try:
        send(address,"Nana's Nest received your inquiry",
             "Thank you for contacting Nana's Nest. We will follow up personally. If you did not submit this inquiry, please disregard this message.",token)
    except Exception:
        print("Acknowledgment delivery failed",flush=True)
        return False
    return True

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def reply(self,status,message):
        body=json.dumps({"message":message}).encode()
        self.send_response(status)
        self.send_header("Content-Type","application/json")
        self.send_header("Cache-Control","no-store")
        self.send_header("Content-Length",str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def do_POST(self):
        if self.path!="/api/inquiry": return self.reply(404,"Not found")
        if self.headers.get("Origin") not in ORIGINS: return self.reply(403,"Forbidden")
        if self.headers.get("Content-Type","").split(";")[0]!="application/json": return self.reply(415,"Unsupported format")
        try:
            length=int(self.headers.get("Content-Length","0"))
            if not 0<length<=2048: raise ValueError()
            name,address,service=validate(json.loads(self.rfile.read(length)))
        except (ValueError,UnicodeError): return self.reply(400,"Please check your inquiry details.")
        if not all(os.environ.get(k) for k in KEYS) or os.environ.get("INQUIRY_ENABLED")!="true":
            return self.reply(503,"Please contact us directly by phone or email.")
        if not reserve(address): return self.reply(429,"Please wait before submitting again or call us.")
        try:
            ack=deliver(name,address,service)
        except Exception:
            print("Inquiry delivery failed",flush=True)
            return self.reply(503,"Unable to confirm delivery. Please contact us directly.")
        return self.reply(200,"Inquiry received. Thank you." if ack else "Inquiry received. A confirmation email may not arrive.")

if __name__=="__main__":
    ThreadingHTTPServer(("127.0.0.1",8090),Handler).serve_forever()
