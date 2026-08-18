from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Tuple
import base64
import copy
import difflib
import email
import hashlib
import hmac
import imaplib
import io
import importlib
import json
import logging
import os
import re
import secrets
import shutil
import struct
import subprocess
import sys
import threading
import time
import unicodedata
import urllib.error
import urllib.request
import py_compile
import uuid as uuidlib
from datetime import datetime
from email.header import decode_header
from html import escape, unescape
from urllib.parse import parse_qs, quote, urlencode, urlparse

def _install_missing_dependencies() -> None:
 missing = []
 for module_name, package_name in (('telebot', 'pyTelegramBotAPI'), ('cryptography', 'cryptography')):
  try:
   importlib.import_module(module_name)
  except ImportError:
   missing.append(package_name)
 if not missing:
  return
 commands = ([sys.executable, '-m', 'pip', 'install', '--disable-pip-version-check', '--no-input', *missing], [sys.executable, '-m', 'pip', 'install', '--disable-pip-version-check', '--no-input', '--user', *missing])
 last_error = None
 for command in commands:
  try:
   subprocess.check_call(command, timeout=300)
   importlib.invalidate_caches()
   for module_name, package_name in (('telebot', 'pyTelegramBotAPI'), ('cryptography', 'cryptography')):
    importlib.import_module(module_name)
   return
  except Exception as error:
   last_error = error
 raise RuntimeError('Не удалось автоматически установить зависимости: ' + ', '.join(missing)) from last_error

_install_missing_dependencies()

from telebot.apihelper import ApiTelegramException
from telebot.types import InlineKeyboardButton as B
from telebot.types import InlineKeyboardMarkup as K
from telebot.types import Message
try:
 import tg_bot.CBT as CBT
except Exception:

 class CBT:
  EDIT_PLUGIN = 'PLUGIN_EDIT'
  PLUGIN_SETTINGS = 'PLUGIN_SETTINGS'
  PLUGINS_LIST = '44'
  BACK = None
try:
 from cryptography.fernet import Fernet, InvalidToken
except Exception:
 Fernet = None

 class InvalidToken(Exception):
  pass
if TYPE_CHECKING:
 from cardinal import Cardinal
NAME = 'AutoOffline'
VERSION = '1.1.1'
DESCRIPTION = 'Выдача Steam Guard (SDA/IMAP), TOTP и Denuvo-активаций через FunPay автоматически и безопасно.'
CREDITS = '@tinechelovec'
UUID = '6f7d9d18-3c69-48bb-92f1-3e91e4f1b1c8'
SETTINGS_PAGE = True
logger = logging.getLogger('AutoOffline')
logger.setLevel(logging.INFO)
PREFIX = '[AutoOffline]'

class _AutoOfflineTimestampFilter(logging.Filter):
 autooffline_timestamp = True

 def filter(self, record: logging.LogRecord) -> bool:
  if getattr(record, '_autooffline_timestamped', False):
   return True
  level = {'DEBUG': 'D', 'INFO': 'I', 'WARNING': 'W', 'ERROR': 'E', 'CRITICAL': 'C'}.get(record.levelname, 'I')
  record.msg = f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}]> {level}: {record.msg}"
  record._autooffline_timestamped = True
  return True
if not any((getattr(item, 'autooffline_timestamp', False) for item in logger.filters)):
 logger.addFilter(_AutoOfflineTimestampFilter())
ANSI_RESET = '\x1b[0m'
ANSI_DIM = '\x1b[2m'
ANSI_COLORS = {'red': '\x1b[91m', 'green': '\x1b[92m', 'yellow': '\x1b[93m', 'blue': '\x1b[94m', 'magenta': '\x1b[95m', 'cyan': '\x1b[96m', 'white': '\x1b[97m'}
PLUGIN_FOLDER = 'storage/plugins/AutoOffline'
DB_FILE = os.path.join(PLUGIN_FOLDER, 'database.json')
DB_BACKUP_FILE = DB_FILE + '.bak'
LOCAL_KEY_FILE = os.path.join(PLUGIN_FOLDER, '.local.key')
LOCAL_KEY_BACKUP_FILE = LOCAL_KEY_FILE + '.bak'
NOTIFY_LOG_FILE = os.path.join(PLUGIN_FOLDER, 'runtime.log')
TEXT_LOG_FILE = os.path.join(PLUGIN_FOLDER, 'log.txt')
os.makedirs(PLUGIN_FOLDER, exist_ok=True)
try:
 if not os.path.exists(TEXT_LOG_FILE):
  open(TEXT_LOG_FILE, 'a', encoding='utf-8').close()
except Exception:
 pass
DB_FORMAT = 'AutoOffline-encrypted-db'
DB_VERSION = 1
PBKDF2_ITERATIONS = 600000
MAX_BACKUP_SIZE = 10 * 1024 * 1024
MAX_LOGS = 3000
MAX_ORDERS = 5000
ORDER_ACTIVE_DAYS = 365
CREATOR_URL = 'https://t.me/tinechelovec'
GROUP_URL = 'https://t.me/dev_thc_chat'
CHANNEL_URL = 'https://t.me/by_thc'
INSTRUCTION_URL = os.getenv('AUTOOFFLINE_INSTRUCTION_URL', 'https://teletype.in/@tinechelovec/AutoOffline').strip()
PLUGIN_UPDATE_URL = os.getenv('AUTOOFFLINE_PLUGIN_UPDATE_URL', '').strip()
DEFAULT_SERVER_URL = (os.getenv('AUTOOFFLINE_SERVER_URL') or 'https://dev-thc-autooffline.vercel.app').strip().rstrip('/')
SMAKMAIL_API_BASE = 'https://api.smakmail.com/api/v1'
CBT_EDIT_PLUGIN = getattr(CBT, 'EDIT_PLUGIN', 'PLUGIN_EDIT')
CBT_PLUGIN_SETTINGS = getattr(CBT, 'PLUGIN_SETTINGS', 'PLUGIN_SETTINGS')
CBT_PLUGINS_LIST_OPEN = f"{getattr(CBT, 'PLUGINS_LIST', '44')}:0"
CBT_BACK = getattr(CBT, 'BACK', None) or f'{UUID}:back'
CB_HOME = f'{UUID}:h'
CB_SETTINGS = f'{UUID}:s'
CB_INFO = f'{UUID}:i'
CB_ACCOUNTS = f'{UUID}:a'
CB_ACCOUNT_ADD = f'{UUID}:aa'
CB_ACCOUNT_OPEN = f'{UUID}:ao'
CB_ACCOUNT_TOGGLE = f'{UUID}:at'
CB_ACCOUNT_LIMITS = f'{UUID}:al'
CB_ACCOUNT_LIMIT_COUNT = f'{UUID}:alc'
CB_ACCOUNT_LIMIT_RESET = f'{UUID}:alr'
CB_ACCOUNT_LIMIT_MODE = f'{UUID}:alm'
CB_ACCOUNT_LIMIT_TIME = f'{UUID}:alt'
CB_ACCOUNT_TEMPLATE = f'{UUID}:am'
CB_ACCOUNT_SECRET = f'{UUID}:as'
CB_ACCOUNT_DENUVO = f'{UUID}:av'
CB_ACCOUNT_NAME = f'{UUID}:an'
CB_ACCOUNT_DENUVO_GAME = f'{UUID}:dg'
CB_ACCOUNT_DENUVO_LIMIT = f'{UUID}:dl'
CB_ACCOUNT_QUEUE = f'{UUID}:ag'
CB_ACCOUNT_QUEUE_CHOICE = f'{UUID}:aq'
CB_ACCOUNT_DENUVO_CHOICE = f'{UUID}:dv'
CB_ACCOUNT_DELETE = f'{UUID}:ad'
CB_ACCOUNT_DELETE_YES = f'{UUID}:ady'
CB_LOTS = f'{UUID}:l'
CB_LOT_ADD = f'{UUID}:la'
CB_LOT_OPEN = f'{UUID}:lo'
CB_LOT_TOGGLE = f'{UUID}:lt'
CB_LOT_FUNPAY_TOGGLE = f'{UUID}:lf'
CB_LOT_ACCOUNTS = f'{UUID}:lac'
CB_LOT_ACCOUNT_PAGE = f'{UUID}:lg'
CB_LOT_ACCOUNT_PICK = f'{UUID}:lp'
CB_LOT_DELETE = f'{UUID}:lx'
CB_LOT_DELETE_YES = f'{UUID}:lxy'
CB_NOTIFICATIONS = f'{UUID}:n'
CB_NOTIFY_TOGGLE = f'{UUID}:nt'
CB_ANALYTICS = f'{UUID}:y'
CB_MAINTENANCE = f'{UUID}:m'
CB_LOGS = f'{UUID}:ml'
CB_BACKUP = f'{UUID}:mb'
CB_IMPORT = f'{UUID}:mi'
CB_DB_CHECK = f'{UUID}:mc'
CB_RESET_USAGE = f'{UUID}:mr'
CB_RESET_USAGE_YES = f'{UUID}:mry'
CB_SECURITY = f'{UUID}:q'
CB_UNLOCK = f'{UUID}:qu'
CB_SET_MASTER = f'{UUID}:qm'
CB_USE_LOCAL_KEY = f'{UUID}:ql'
CB_STATE = f'{UUID}:st'
CB_STATE_PLUGIN = f'{UUID}:sp'
CB_STATE_LOTS = f'{UUID}:sl'
CB_STATE_LOTS_FUNPAY = f'{UUID}:sf'
CB_STATE_ACCOUNTS = f'{UUID}:sa'
CB_UPDATE = f'{UUID}:u'
CB_UPDATE_LOCAL = f'{UUID}:ul'
CB_UPDATE_ONLINE = f'{UUID}:uo'
CB_UPDATE_YES = f'{UUID}:uy'
CB_UPDATE_NO = f'{UUID}:un'
CB_DELETE_PLUGIN = f'{UUID}:dp'
CB_DELETE_PLUGIN_YES = f'{UUID}:dpy'
CB_DELETE_PLUGIN_NO = f'{UUID}:dpn'
CB_DENUVO_CENTER = f'{UUID}:dc'
CB_DENUVO_REFRESH = f'{UUID}:dcr'
CB_DENUVO_SYNC = f'{UUID}:dcs'
CB_DENUVO_RETRY = f'{UUID}:dct'
CB_DENUVO_CLEAR = f'{UUID}:dcc'
CB_PLUGIN_TOGGLE = f'{UUID}:p'
CB_CANCEL = f'{UUID}:c'
CB_TYPE = f'{UUID}:t'
CB_SMAKMAIL_KEY = f'{UUID}:sk'
_fsm: Dict[int, Dict[str, Any]] = {}
_DB_CACHE: Optional[dict] = None
_DB_KEY: Optional[bytes] = None
_DB_MODE: Optional[str] = None
_DB_LOCK = threading.RLock()
_FSM_LOCK = threading.RLock()
_CARDINAL: Optional['Cardinal'] = None
_RECENT_EVENT_KEYS: Dict[str, float] = {}
_EVENT_LOCK = threading.RLock()
_DENUVO_QUEUE_EVENT = threading.Event()
_DENUVO_STOP_EVENT = threading.Event()
_DENUVO_WORKER: Optional[threading.Thread] = None
_STEAM_QUEUE_EVENT = threading.Event()
_STEAM_QUEUE_STOP_EVENT = threading.Event()
_STEAM_QUEUE_WORKER: Optional[threading.Thread] = None
_AUTO_REGISTER_LOCK = threading.RLock()
_AUTO_REGISTER_WORKER: Optional[threading.Thread] = None
_INVIS_RE = re.compile('[\u200b-\u200f\u202a-\u202e\u2060-\u206f\ufeff\xad]')
SENSITIVE_KEYS = {'secret', 'shared_secret', 'totp_secret', 'password', 'mail_password', 'smakmail_api_key', 'license_key', 'server_token', 'cookie', 'golden_key', 'recovery_code'}
ACCOUNT_TYPES = {'steam_sda': 'Steam Guard (SDA)', 'steam_email': 'Steam Guard (Email)', 'totp': 'Google Authenticator / TOTP', 'rockstar_email': 'Rockstar-код из почты', 'denuvo': 'Denuvo / слот'}
ACCOUNT_CREATION_TYPES = ('steam_sda', 'steam_email', 'totp')
LOT_CREATION_TYPES = ('steam_sda', 'steam_email', 'totp')
ACCOUNT_TYPE_ALIASES = {'steam_sda': 'steam_sda', 'steam': 'steam_sda', 'sda': 'steam_sda', 'steam_guard': 'steam_sda', 'steamguard': 'steam_sda', 'steam_email': 'steam_email', 'steam_mail': 'steam_email', 'steam_imap': 'steam_email', 'email_steam': 'steam_email', 'totp': 'totp', 'otp': 'totp', '2fa': 'totp', 'google_totp': 'totp', 'google_authenticator': 'totp', 'ubisoft_totp': 'totp', 'ubisoft_2fa': 'totp'}
STEAM_QUEUE_INTERVAL_SECONDS = 15
TOTP_QUEUE_INTERVAL_SECONDS = 30
STEAM_QUEUE_ACTIVE_STATES = {'queued', 'processing', 'retry'}
LOT_ACCOUNT_PAGE_SIZE = 10
NOTIFICATION_LABELS = {'command_request': 'Запросы команд', 'code_issued': 'Успешные выдачи', 'request_denied': 'Ошибки выдачи', 'new_order': 'Новые заказы', 'order_status': 'Статусы заказов', 'lot_status': 'Состояние лотов', 'denuvo': 'Denuvo', 'maintenance': 'Обслуживание'}
LOG_EVENT_META = {'START': ('🚀', 'ЗАПУСК', 'cyan'), 'ORDER': ('🛒', 'ЗАКАЗ', 'cyan'), 'ORDER_REPAIRED': ('🔗', 'ЗАКАЗ', 'green'), 'ORDER_UNRESOLVED': ('⚠️', 'ЗАКАЗ', 'yellow'), 'ORDER_MATCH_FAILED': ('⚠️', 'ЗАКАЗ', 'yellow'), 'ISSUED': ('✅', 'ВЫДАЧА', 'green'), 'DENIED': ('⛔', 'ОТКАЗ', 'yellow'), 'DENUVO': ('🎮', 'DENUVO', 'magenta'), 'LOT': ('🛒', 'ЛОТ', 'cyan'), 'REFUND': ('↩️', 'ВОЗВРАТ', 'yellow'), 'REFUND_IGNORED': ('↩️', 'ВОЗВРАТ', 'yellow'), 'SERVER': ('🌐', 'СЕРВЕР', 'cyan'), 'SETTINGS': ('⚙️', 'НАСТРОЙКИ', 'cyan'), 'MAINTENANCE': ('🛠', 'СЕРВИС', 'cyan'), 'WARNING': ('⚠️', 'ВНИМАНИЕ', 'yellow'), 'WARN': ('⚠️', 'ВНИМАНИЕ', 'yellow'), 'ERROR': ('❌', 'ОШИБКА', 'red'), 'FAILED': ('❌', 'ОШИБКА', 'red'), 'CRITICAL': ('🆘', 'КРИТИЧНО', 'red')}
LOG_DETAIL_LABELS = {'order_id': 'заказ', 'lot_id': 'лот', 'funpay_lot_id': 'LOT ID', 'account_id': 'аккаунт', 'account_type': 'тип', 'buyer': 'покупатель', 'chat_id': 'чат', 'quantity': 'количество', 'left': 'осталось', 'total': 'лимит', 'enabled': 'включён', 'synced': 'FunPay', 'reason': 'причина', 'code': 'код', 'error': 'ошибка', 'status': 'статус', 'attempts': 'попытки', 'active_slots': 'занято слотов', 'slot_limit': 'лимит слотов'}

def _now() -> int:
 return int(time.time())

def _uid(prefix: str) -> str:
 return prefix + uuidlib.uuid4().hex[:9]

def _normalize_command(value: str) -> str:
 value = unicodedata.normalize('NFKC', str(value or ''))
 value = value.replace('\xa0', ' ')
 value = _INVIS_RE.sub('', value)
 return ''.join((ch for ch in value if not ch.isspace())).strip().casefold()

def _canonical_account_type(value: Any) -> str:
 raw = unicodedata.normalize('NFKC', str(value or '')).strip().casefold()
 raw = re.sub('[^a-z0-9_]+', '_', raw).strip('_')
 return ACCOUNT_TYPE_ALIASES.get(raw, raw)

def _normalize_lot_reference(value: Any) -> str:
 text = unicodedata.normalize('NFKC', str(value or '')).strip()
 if not text:
  return ''
 match = re.search('\\d+', text)
 if match:
  try:
   return str(int(match.group(0)))
  except Exception:
   pass
 return re.sub('\\s+', '', text).casefold()

def _normalize_identity(value: Any) -> str:
 text = unicodedata.normalize('NFKC', str(value or '')).strip().lstrip('@').casefold()
 return re.sub('\\s+', '', text)

def _normalize_title(value: Any) -> str:
 text = unescape(re.sub('<[^>]+>', ' ', str(value or '')))
 text = unicodedata.normalize('NFKC', text).casefold()
 return re.sub('[^0-9a-zа-яё]+', ' ', text, flags=re.I).strip()

def _first_word(value: str) -> str:
 text = unicodedata.normalize('NFKC', str(value or ''))
 text = _INVIS_RE.sub('', text).strip()
 return _normalize_command(text.split()[0]) if text else ''

def _fmt_dt(ts: Any) -> str:
 try:
  return datetime.fromtimestamp(int(ts)).strftime('%d.%m.%Y %H:%M:%S')
 except Exception:
  return '—'

def _fmt_duration(seconds: int) -> str:
 seconds = max(0, int(seconds or 0))
 days, seconds = divmod(seconds, 86400)
 hours, seconds = divmod(seconds, 3600)
 minutes, seconds = divmod(seconds, 60)
 parts = []
 if days:
  parts.append(f'{days}д')
 if hours:
  parts.append(f'{hours}ч')
 if minutes:
  parts.append(f'{minutes}м')
 if not parts:
  parts.append(f'{seconds}с')
 return ' '.join(parts[:2])

def _safe_int(value: Any, default: int=0, minimum: Optional[int]=None, maximum: Optional[int]=None) -> int:
 try:
  result = int(value)
 except Exception:
  result = int(default)
 if minimum is not None:
  result = max(minimum, result)
 if maximum is not None:
  result = min(maximum, result)
 return result

def _mask(value: str) -> str:
 value = str(value or '').strip()
 if not value:
  return '—'
 if len(value) <= 10:
  return '********'
 return value[:4] + '…' + value[-4:]

def _json_copy(data: Any) -> Any:
 return json.loads(json.dumps(data, ensure_ascii=False))

def _atomic_write(path: str, payload: bytes) -> None:
 os.makedirs(os.path.dirname(path), exist_ok=True)
 tmp = path + '.tmp'
 with open(tmp, 'wb') as f:
  f.write(payload)
  f.flush()
  os.fsync(f.fileno())
 os.replace(tmp, path)
 try:
  os.chmod(path, 384)
 except Exception:
  pass

def _safe_edit(bot, chat_id: int, message_id: int, text: str, kb: Optional[K]=None) -> bool:
 try:
  bot.edit_message_text(text, chat_id, message_id, parse_mode='HTML', reply_markup=kb, disable_web_page_preview=True)
  return True
 except TypeError:
  try:
   bot.edit_message_text(text, chat_id, message_id, parse_mode='HTML', reply_markup=kb)
   return True
  except Exception:
   return False
 except ApiTelegramException as e:
  low = str(e).lower()
  if 'message is not modified' in low:
   return True
  logger.debug('%s edit failed: %s', PREFIX, e)
 except Exception as e:
  logger.debug('%s edit failed: %s', PREFIX, e)
 return False

def _safe_send_tg(bot, chat_id: int, text: str, kb: Optional[K]=None):
 try:
  return bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=kb, disable_web_page_preview=True)
 except TypeError:
  return bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=kb)
 except Exception as e:
  logger.debug('%s telegram send failed: %s', PREFIX, e)
  return None

def _answer(bot, call, text: str='', alert: bool=False) -> None:
 try:
  bot.answer_callback_query(call.id, text, show_alert=alert)
 except Exception:
  pass

def _delete_message(bot, chat_id: int, message_id: Optional[int]) -> None:
 if not message_id:
  return
 try:
  bot.delete_message(chat_id, int(message_id))
 except Exception:
  pass

def _cancel_kb(back: str=CB_SETTINGS) -> K:
 kb = K()
 kb.row(B('❌ Отменить', callback_data=CB_CANCEL))
 kb.row(B('◀️ Назад', callback_data=back))
 return kb

def _render(template: str, mapping: Dict[str, Any]) -> str:

 class SafeDict(dict):

  def __missing__(self, key):
   return ''
 try:
  return str(template or '').format_map(SafeDict({k: str(v) for k, v in mapping.items()}))
 except Exception:
  return str(template or '')

def _redact(data: Any) -> Any:
 if isinstance(data, dict):
  return {k: '***' if str(k).casefold() in SENSITIVE_KEYS else _redact(v) for k, v in data.items()}
 if isinstance(data, list):
  return [_redact(x) for x in data]
 return data

def _default_db() -> dict:
 return {'schema': DB_VERSION, 'global': {'plugin_enabled': True, 'admin_chat_ids': [], 'instruction_acknowledged': [], 'smakmail_api_key': os.getenv('AUTOOFFLINE_SMAKMAIL_API_KEY', '').strip(), 'notifications': {key: True for key in NOTIFICATION_LABELS}, 'server': {'url': DEFAULT_SERVER_URL, 'plugin_update_url': PLUGIN_UPDATE_URL, 'token': os.getenv('AUTOOFFLINE_SERVER_TOKEN', '').strip(), 'license_key': os.getenv('AUTOOFFLINE_LICENSE_KEY', '').strip(), 'license_type': 'manual' if os.getenv('AUTOOFFLINE_LICENSE_KEY', '').strip() else 'auto', 'cardinal_id_hash': '', 'owner_id': os.getenv('AUTOOFFLINE_OWNER_ID', '').strip(), 'seller_hash': os.getenv('AUTOOFFLINE_SELLER_HASH', '').strip().lower(), 'timeout': 15, 'fallback_local': False, 'install_id': '', 'machine_seed': '', 'installation_secret': '', 'installation_id': '', 'registered_build_hash': '', 'registered_owner_id': '', 'protocol_version': 1, 'data_binding_mode': 'off', 'clock_offset': 0, 'last_register_at': 0, 'last_verify_at': 0, 'last_verify_code': 'NOT_CONFIGURED', 'last_status_sync': 0, 'active_reservations': 0, 'queue_max_attempts': 9, 'queue_retry_base': 5, 'queue_max_wait': 1800, 'denuvo_hold_seconds': _safe_int(os.getenv('AUTOOFFLINE_DENUVO_HOLD_SECONDS'), 21600, 300, 604800), 'status_sync_interval': 300}, 'templates': {'steam_sda': '🔐 Код Steam Guard\n\n【 {code} 】\n\n📋 Скопируйте код и вставьте его в Steam.\n📊 Осталось запросов: {left}/{total}', 'steam_email': '📧 Код Steam Guard из почты\n\n【 {code} 】\n\n📋 Код подходит только для входа в Steam.\n📊 Осталось запросов: {left}/{total}', 'totp': '🔐 Код подтверждения\n\n【 {code} 】\n\n📊 Осталось запросов: {left}/{total}', 'rockstar_email': '🔐 Код Rockstar\n\n【 {code} 】\n\n📊 Осталось запросов: {left}/{total}', 'denuvo': '✅ Denuvo-доступ выдан\n\nАккаунт: {account}\nАктивации: {slot_info}', 'denuvo_queued': '🕒 Denuvo-запрос принят. Позиция в очереди: <b>{position}</b>. Повторять команду не нужно.', 'denuvo_duplicate': '🕒 Этот Denuvo-запрос уже обрабатывается. Позиция: <b>{position}</b>.', 'steam_queued': '🕒 Запрос Steam Guard поставлен в очередь. Позиция: <b>{position}</b>. Следующий код будет выдан не раньше чем через 15 секунд.', 'steam_duplicate': '🕒 Ваш запрос Steam Guard уже находится в очереди. Позиция: <b>{position}</b>.', 'totp_queued': '🕒 Запрос TOTP поставлен в очередь. Позиция: <b>{position}</b>. Новый код будет выдан в следующем 30-секундном окне.', 'totp_duplicate': '🕒 Такой TOTP-запрос уже находится в очереди. Позиция: <b>{position}</b>.', 'denied_no_order': '❌ Не найден подходящий оплаченный заказ для этого лота.', 'denied_limit': '❌ Лимит по заказу исчерпан.', 'denied_cooldown': '⏳ Повторный запрос будет доступен через {wait}.', 'unavailable': '❌ Автоматическая выдача временно недоступна. Напишите продавцу.'}}, 'accounts': [], 'lots': [], 'orders': [], 'usage': {}, 'denuvo_queue': [], 'steam_queue': [], 'logs': [], 'stats': {'orders': 0, 'issued': 0, 'denied': 0, 'server_requests': 0, 'server_errors': 0, 'queue_enqueued': 0, 'queue_enqueued_messages': 0, 'queue_completed': 0, 'queue_failed': 0, 'steam_queue_enqueued': 0, 'steam_queue_completed': 0, 'steam_queue_failed': 0}}

def _ensure_db_shape(db: dict) -> dict:
 base = _default_db()
 if not isinstance(db, dict):
  db = {}
 db.setdefault('schema', DB_VERSION)
 for key in ('accounts', 'lots', 'orders', 'denuvo_queue', 'steam_queue', 'logs'):
  if not isinstance(db.get(key), list):
   db[key] = []
 if not isinstance(db.get('usage'), dict):
  db['usage'] = {}
 if not isinstance(db.get('stats'), dict):
  db['stats'] = {}
 for key, value in base['stats'].items():
  db['stats'].setdefault(key, value)
 if not isinstance(db.get('global'), dict):
  db['global'] = {}
 g = db['global']
 for key, value in base['global'].items():
  if key not in g:
   g[key] = copy.deepcopy(value)
 if not isinstance(g.get('notifications'), dict):
  g['notifications'] = {}
 for key in NOTIFICATION_LABELS:
  g['notifications'].setdefault(key, True)
 if not isinstance(g.get('templates'), dict):
  g['templates'] = {}
 for key, value in base['global']['templates'].items():
  g['templates'].setdefault(key, value)
 old_steam_templates = {'✅ Steam Guard: <code>{code}</code>\n📊 Осталось: {left}/{total}', '✅ Steam Guard: <code>{code}</code>', '🔐 <b>Код Steam Guard</b>\n\n<code>{code}</code>\n\n📋 Нажмите на код, чтобы скопировать.\n📊 Осталось запросов: <b>{left}/{total}</b>'}
 if str(g['templates'].get('steam_sda') or '') in old_steam_templates:
  g['templates']['steam_sda'] = base['global']['templates']['steam_sda']
 g['notifications'].pop('security', None)
 if not isinstance(g.get('server'), dict):
  g['server'] = {}
 for key, value in base['global']['server'].items():
  g['server'].setdefault(key, value)
 if not str(g['server'].get('url') or '').strip():
  g['server']['url'] = DEFAULT_SERVER_URL
 for account in db['accounts']:
  if isinstance(account, dict):
   account.setdefault('id', _uid('a'))
   account['type'] = _canonical_account_type(account.get('type'))
   account.setdefault('enabled', True)
   account.setdefault('issued', 0)
   account.setdefault('limit_total', None)
   account.setdefault('limit_mode', 'count')
   if str(account.get('limit_mode') or 'count') not in {'count', 'time'}:
    account['limit_mode'] = 'count'
   account.setdefault('limit_time_seconds', 0)
   account.setdefault('cooldown_seconds', 0)
   account.setdefault('limit_reset_seconds', _safe_int(account.get('cooldown_seconds'), 0, 0, 31536000))
   account.setdefault('template', '')
   account.setdefault('data', {})
   account.setdefault('denuvo', {'enabled': False, 'slot_limit': 5, 'reserve': 0, 'active_slots': 0, 'weight': 100, 'failure_rate': 0.0, 'cooldown_until': 0, 'hold_seconds': 0})
   denuvo = account.get('denuvo') if isinstance(account.get('denuvo'), dict) else {}
   denuvo.setdefault('enabled', False)
   denuvo.setdefault('slot_limit', 5)
   if bool(denuvo.get('enabled')) and _safe_int(denuvo.get('slot_limit'), 1) == 1 and (not denuvo.get('slot_limit_custom')):
    denuvo['slot_limit'] = 5
   denuvo.setdefault('reserve', 0)
   denuvo.setdefault('active_slots', 0)
   denuvo.setdefault('weight', 100)
   denuvo.setdefault('failure_rate', 0.0)
   denuvo.setdefault('cooldown_until', 0)
   denuvo.setdefault('hold_seconds', 0)
   account['denuvo'] = denuvo
   queue_cfg = account.get('queue') if isinstance(account.get('queue'), dict) else {}
   account_type = str(account.get('type') or '')
   queue_cfg.setdefault('enabled', account_type in {'steam_sda', 'totp'})
   queue_cfg.setdefault('interval_seconds', TOTP_QUEUE_INTERVAL_SECONDS if account_type == 'totp' else STEAM_QUEUE_INTERVAL_SECONDS)
   queue_cfg.setdefault('last_issue_at', 0)
   account['queue'] = queue_cfg
 for lot in db['lots']:
  if isinstance(lot, dict):
   lot.setdefault('id', _uid('l'))
   lot['account_type'] = _canonical_account_type(lot.get('account_type'))
   lot.setdefault('enabled', True)
   lot.setdefault('funpay_active', None)
   lot.setdefault('funpay_sync', {})
   raw_ids = lot.get('account_ids') if isinstance(lot.get('account_ids'), list) else []
   compatible = [str(account.get('id')) for account in db['accounts'] if isinstance(account, dict) and _canonical_account_type(account.get('type')) == lot['account_type']]
   selected = next((str(account_id) for account_id in raw_ids if str(account_id) in compatible), '')
   if not selected and compatible:
    selected = compatible[0]
   lot['account_ids'] = [selected] if selected else []
   if str(lot.get('auto_disabled_reason') or '') == 'denuvo_capacity':
    lot['enabled'] = True
    lot['funpay_active'] = False
    lot['auto_funpay_disabled_reason'] = 'denuvo_capacity'
    if lot.get('auto_disabled_at'):
     lot['auto_funpay_disabled_at'] = lot.get('auto_disabled_at')
    lot.pop('auto_disabled_reason', None)
    lot.pop('auto_disabled_at', None)
 for job in db.get('denuvo_queue', []):
  if isinstance(job, dict):
   job.setdefault('status', 'queued')
   job.setdefault('attempts', 0)
   job.setdefault('next_attempt_at', _now())
   job.setdefault('created_at', _now())
   job.setdefault('updated_at', _now())
 for job in db.get('steam_queue', []):
  if isinstance(job, dict):
   job.setdefault('status', 'queued')
   job.setdefault('attempts', 0)
   job.setdefault('next_attempt_at', _now())
   job.setdefault('created_at', _now())
   job.setdefault('updated_at', _now())
 db['denuvo_queue'] = db['denuvo_queue'][-1000:]
 db['steam_queue'] = db['steam_queue'][-1000:]
 db['logs'] = db['logs'][-MAX_LOGS:]
 db['orders'] = db['orders'][-MAX_ORDERS:]
 return db

def _require_crypto() -> None:
 if Fernet is None:
  raise RuntimeError('Не установлен пакет cryptography. Выполните: pip install cryptography')

def _read_local_key_file(path: str) -> Optional[bytes]:
 if not os.path.isfile(path):
  return None
 try:
  raw = open(path, 'rb').read().strip()
  decoded = base64.urlsafe_b64decode(raw)
  if len(decoded) != 32:
   return None
  return base64.urlsafe_b64encode(decoded)
 except Exception:
  return None

def _write_local_key(key: bytes) -> bytes:
 encoded = base64.urlsafe_b64encode(base64.urlsafe_b64decode(key))
 _atomic_write(LOCAL_KEY_FILE, encoded)
 _atomic_write(LOCAL_KEY_BACKUP_FILE, encoded)
 return encoded

def _quarantine_local_key() -> None:
 if not os.path.isfile(LOCAL_KEY_FILE):
  return
 stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
 target = f'{LOCAL_KEY_FILE}.corrupt.{stamp}.{uuidlib.uuid4().hex[:6]}'
 try:
  shutil.copy2(LOCAL_KEY_FILE, target)
 except Exception:
  pass

def _local_key() -> bytes:
 _require_crypto()
 key = _read_local_key_file(LOCAL_KEY_FILE)
 if key is not None:
  if _read_local_key_file(LOCAL_KEY_BACKUP_FILE) != key:
   try:
    _atomic_write(LOCAL_KEY_BACKUP_FILE, key)
   except Exception:
    pass
  return key
 backup_key = _read_local_key_file(LOCAL_KEY_BACKUP_FILE)
 if backup_key is not None:
  _quarantine_local_key()
  _atomic_write(LOCAL_KEY_FILE, backup_key)
  return backup_key
 _quarantine_local_key()
 raw_key = secrets.token_bytes(32)
 return _write_local_key(base64.urlsafe_b64encode(raw_key))

def _password_key(password: str, salt: bytes, iterations: int=PBKDF2_ITERATIONS) -> bytes:
 _require_crypto()
 if len(str(password or '')) < 8:
  raise ValueError('Master-password должен содержать минимум 8 символов.')
 raw = hashlib.pbkdf2_hmac('sha256', str(password).encode('utf-8'), salt, int(iterations), dklen=32)
 return base64.urlsafe_b64encode(raw)

def _load_envelope_file(path: str) -> Optional[dict]:
 if not os.path.isfile(path):
  return None
 try:
  with open(path, 'r', encoding='utf-8') as f:
   payload = json.load(f)
 except Exception as e:
  raise RuntimeError(f'Не удалось прочитать encrypted JSON: {e}') from e
 if not isinstance(payload, dict) or payload.get('format') != DB_FORMAT:
  raise RuntimeError('Файл базы не является encrypted JSON AutoOffline.')
 required = {'format', 'version', 'cipher', 'kdf', 'ciphertext'}
 missing = required - set(payload)
 if missing:
  raise RuntimeError('В базе отсутствуют поля: ' + ', '.join(sorted(missing)))
 return payload

def _read_envelope() -> Optional[dict]:
 return _load_envelope_file(DB_FILE)

def _quarantine_database() -> Optional[str]:
 if not os.path.isfile(DB_FILE):
  return None
 stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
 target = f'{DB_FILE}.corrupt.{stamp}.{uuidlib.uuid4().hex[:6]}'
 try:
  shutil.copy2(DB_FILE, target)
  try:
   os.chmod(target, 384)
  except Exception:
   pass
  return target
 except Exception:
  return None

def _restore_database_backup(require_local_decrypt: bool=False) -> bool:
 if not os.path.isfile(DB_BACKUP_FILE):
  return False
 try:
  envelope = _load_envelope_file(DB_BACKUP_FILE)
  if envelope is None:
   return False
  mode = str((envelope.get('kdf') or {}).get('mode') or '')
  if require_local_decrypt or mode == 'local':
   if mode != 'local':
    return False
   _decrypt_envelope(envelope, _local_key())
  raw = open(DB_BACKUP_FILE, 'rb').read()
  _atomic_write(DB_FILE, raw)
  return True
 except Exception as e:
  logger.error('%s Не удалось восстановить резервную копию базы: %s', PREFIX, e)
  return False

def _replace_with_fresh_database() -> None:
 global _DB_CACHE, _DB_KEY, _DB_MODE
 _quarantine_database()
 try:
  if os.path.isfile(DB_FILE):
   os.remove(DB_FILE)
 except Exception:
  pass
 key = _local_key()
 db = _default_db()
 envelope = _encrypt_db(db, key, 'local')
 _atomic_write(DB_FILE, json.dumps(envelope, ensure_ascii=False, indent=2).encode('utf-8'))
 _DB_CACHE, _DB_KEY, _DB_MODE = (db, key, 'local')

def _repair_database_file() -> str:
 global _DB_CACHE, _DB_KEY, _DB_MODE
 _quarantine_database()
 if _restore_database_backup():
  _DB_CACHE = None
  _DB_KEY = None
  envelope = _read_envelope()
  _DB_MODE = str((envelope.get('kdf') or {}).get('mode') or 'unknown') if envelope else None
  return 'backup'
 _replace_with_fresh_database()
 return 'fresh'

def _encrypt_db(db: dict, key: bytes, mode: str, *, salt: Optional[bytes]=None, iterations: int=PBKDF2_ITERATIONS) -> dict:
 _require_crypto()
 plaintext = json.dumps(_ensure_db_shape(db), ensure_ascii=False, separators=(',', ':')).encode('utf-8')
 token = Fernet(key).encrypt(plaintext).decode('ascii')
 kdf = {'mode': mode}
 if mode == 'pbkdf2':
  if salt is None:
   raise ValueError('salt is required')
  kdf.update({'name': 'PBKDF2-HMAC-SHA256', 'salt': base64.b64encode(salt).decode('ascii'), 'iterations': int(iterations)})
 return {'format': DB_FORMAT, 'version': DB_VERSION, 'cipher': 'Fernet(AES128-CBC+HMAC-SHA256)', 'kdf': kdf, 'updated_at': _now(), 'ciphertext': token}

def _decrypt_envelope(envelope: dict, key: bytes) -> dict:
 _require_crypto()
 token = str(envelope.get('ciphertext') or '').encode('ascii')
 try:
  plain = Fernet(key).decrypt(token)
 except InvalidToken as e:
  raise ValueError('Неверный master-password или повреждённая база.') from e
 try:
  return _ensure_db_shape(json.loads(plain.decode('utf-8')))
 except Exception as e:
  raise RuntimeError('Расшифрованные данные повреждены.') from e

def _write_envelope(envelope: dict) -> None:
 raw = json.dumps(envelope, ensure_ascii=False, indent=2).encode('utf-8')
 if os.path.isfile(DB_FILE):
  try:
   current = _load_envelope_file(DB_FILE)
   if current is not None and _DB_KEY is not None:
    _decrypt_envelope(current, _DB_KEY)
   shutil.copy2(DB_FILE, DB_BACKUP_FILE)
   try:
    os.chmod(DB_BACKUP_FILE, 384)
   except Exception:
    pass
  except Exception:
   _quarantine_database()
 _atomic_write(DB_FILE, raw)

def _initialise_database() -> None:
 global _DB_CACHE, _DB_KEY, _DB_MODE
 with _DB_LOCK:
  if os.path.isfile(DB_FILE):
   return
  key = _local_key()
  db = _default_db()
  _write_envelope(_encrypt_db(db, key, 'local'))
  _DB_CACHE, _DB_KEY, _DB_MODE = (db, key, 'local')

def _auto_unlock_local() -> bool:
 global _DB_CACHE, _DB_KEY, _DB_MODE
 with _DB_LOCK:
  try:
   envelope = _read_envelope()
  except Exception as e:
   logger.error('%s Повреждение файла базы обнаружено: %s', PREFIX, e)
   source = _repair_database_file()
   logger.warning('%s База автоматически восстановлена: %s', PREFIX, 'резервная копия' if source == 'backup' else 'создана новая база')
   envelope = _read_envelope()
  if envelope is None:
   _initialise_database()
   return True
  mode = str((envelope.get('kdf') or {}).get('mode') or '')
  _DB_MODE = mode
  if mode != 'local':
   _DB_CACHE = None
   _DB_KEY = None
   return False
  key = _local_key()
  try:
   _DB_CACHE = _decrypt_envelope(envelope, key)
  except Exception as e:
   logger.error('%s Повреждение зашифрованной базы обнаружено: %s', PREFIX, e)
   _quarantine_database()
   if _restore_database_backup(require_local_decrypt=True):
    envelope = _read_envelope()
    _DB_CACHE = _decrypt_envelope(envelope, key)
    logger.warning('%s База автоматически восстановлена из резервной копии.', PREFIX)
   else:
    _replace_with_fresh_database()
    logger.warning('%s База автоматически пересоздана после повреждения.', PREFIX)
    return True
  _DB_KEY = key
  _DB_MODE = 'local'
  _ensure_db_shape(_DB_CACHE)
  _db_save()
  return True

def _ensure_database_available() -> bool:
 try:
  _initialise_database()
  if _auto_unlock_local():
   return not _db_locked()
 except Exception as e:
  logger.error('%s Автовосстановление базы при запуске не удалось: %s', PREFIX, e)
 try:
  envelope = _read_envelope()
  mode = str((envelope.get('kdf') or {}).get('mode') or '') if envelope else ''
  if mode and mode != 'local':
   return False
  _replace_with_fresh_database()
  return not _db_locked()
 except Exception as e:
  logger.error('%s Не удалось автоматически пересоздать хранилище: %s', PREFIX, e)
  return False

def _unlock_password(password: str) -> bool:
 global _DB_CACHE, _DB_KEY, _DB_MODE
 with _DB_LOCK:
  envelope = _read_envelope()
  if envelope is None:
   raise RuntimeError('База не найдена.')
  kdf = envelope.get('kdf') or {}
  if kdf.get('mode') != 'pbkdf2':
   raise ValueError('База использует локальный ключ и уже разблокируется автоматически.')
  salt = base64.b64decode(str(kdf.get('salt') or ''))
  iterations = _safe_int(kdf.get('iterations'), PBKDF2_ITERATIONS, 100000, 2000000)
  key = _password_key(password, salt, iterations)
  _DB_CACHE = _decrypt_envelope(envelope, key)
  _DB_KEY = key
  _DB_MODE = 'pbkdf2'
  return True

def _db_locked() -> bool:
 return _DB_CACHE is None or _DB_KEY is None

def _db_get() -> dict:
 with _DB_LOCK:
  if _DB_CACHE is None:
   raise RuntimeError('База AutoOffline заблокирована.')
  return _DB_CACHE

def _db_save() -> None:
 with _DB_LOCK:
  if _DB_CACHE is None or _DB_KEY is None:
   raise RuntimeError('Нельзя сохранить заблокированную базу.')
  envelope = _read_envelope()
  kdf = (envelope or {}).get('kdf') or {'mode': _DB_MODE or 'local'}
  mode = str(kdf.get('mode') or _DB_MODE or 'local')
  salt = None
  iterations = PBKDF2_ITERATIONS
  if mode == 'pbkdf2':
   salt = base64.b64decode(str(kdf.get('salt') or ''))
   iterations = _safe_int(kdf.get('iterations'), PBKDF2_ITERATIONS, 100000, 2000000)
  _write_envelope(_encrypt_db(_DB_CACHE, _DB_KEY, mode, salt=salt, iterations=iterations))

def _set_master_password(password: str) -> None:
 global _DB_KEY, _DB_MODE
 with _DB_LOCK:
  db = _db_get()
  salt = secrets.token_bytes(16)
  key = _password_key(password, salt)
  _write_envelope(_encrypt_db(db, key, 'pbkdf2', salt=salt, iterations=PBKDF2_ITERATIONS))
  _DB_KEY = key
  _DB_MODE = 'pbkdf2'

def _switch_to_local_key() -> None:
 global _DB_KEY, _DB_MODE
 with _DB_LOCK:
  db = _db_get()
  key = _local_key()
  _write_envelope(_encrypt_db(db, key, 'local'))
  _DB_KEY = key
  _DB_MODE = 'local'

def _database_status() -> Tuple[str, str]:
 try:
  if not os.path.isfile(DB_FILE) or _db_locked():
   _ensure_database_available()
  envelope = _read_envelope()
  if envelope is None:
   return ('не создана', 'unknown')
  mode = str((envelope.get('kdf') or {}).get('mode') or 'unknown')
  return ('разблокирована' if not _db_locked() else 'заблокирована', mode)
 except Exception:
  return ('ошибка', 'unknown')

def _find_account(account_id: str) -> Optional[dict]:
 if _db_locked():
  return None
 for account in _db_get().get('accounts', []):
  if str(account.get('id')) == str(account_id):
   return account
 return None

def _find_lot(lot_id: str) -> Optional[dict]:
 if _db_locked():
  return None
 for lot in _db_get().get('lots', []):
  if str(lot.get('id')) == str(lot_id):
   return lot
 return None

def _lot_by_funpay_id(funpay_lot_id: Any) -> Optional[dict]:
 target = _normalize_lot_reference(funpay_lot_id)
 if not target or _db_locked():
  return None
 for lot in _db_get().get('lots', []):
  if _normalize_lot_reference(lot.get('funpay_lot_id')) == target:
   return lot
 return None

def _order_buyer_matches(order: dict, chat_id: Any, buyer_id: str, buyer_nick: str) -> bool:
 order_chat = _normalize_identity(order.get('chat_id'))
 order_buyer = _normalize_identity(order.get('buyer_id'))
 order_nick = _normalize_identity(order.get('buyer_nick'))
 chat = _normalize_identity(chat_id)
 buyer = _normalize_identity(buyer_id)
 nick = _normalize_identity(buyer_nick)
 return bool(order_chat and chat and (order_chat == chat) or (order_buyer and buyer and (order_buyer == buyer)) or (order_nick and nick and (order_nick == nick)))

def _order_lot_reference_matches(order: dict, lot: dict) -> bool:
 if str(order.get('lot_id') or '') == str(lot.get('id') or ''):
  return True
 order_funpay_id = _normalize_lot_reference(order.get('funpay_lot_id'))
 lot_funpay_id = _normalize_lot_reference(lot.get('funpay_lot_id'))
 return bool(order_funpay_id and lot_funpay_id and (order_funpay_id == lot_funpay_id))

def _repair_order_lot_link(order: dict, lot: dict, reason: str) -> bool:
 changed = False
 expected_lot_id = str(lot.get('id') or '')
 expected_funpay_id = _normalize_lot_reference(lot.get('funpay_lot_id'))
 if str(order.get('lot_id') or '') != expected_lot_id:
  order['lot_id'] = expected_lot_id
  changed = True
 if expected_funpay_id and _normalize_lot_reference(order.get('funpay_lot_id')) != expected_funpay_id:
  order['funpay_lot_id'] = expected_funpay_id
  changed = True
 if order.pop('unresolved', None) is not None:
  changed = True
 if changed:
  order['updated_at'] = _now()
  _log('ORDER_REPAIRED', 'Связь заказа с лотом восстановлена', order_id=order.get('order_id'), lot_id=lot.get('id'), funpay_lot_id=lot.get('funpay_lot_id'), account_type=_canonical_account_type(lot.get('account_type')), reason=reason)
 return changed

def _repair_orders_for_lot(lot: dict) -> int:
 if _db_locked():
  return 0
 repaired = 0
 lot_title = _normalize_title(lot.get('title'))
 lot_funpay_id = _normalize_lot_reference(lot.get('funpay_lot_id'))
 for order in _db_get().get('orders', []):
  if str(order.get('status') or '') not in {'paid', 'active'}:
   continue
  order_funpay_id = _normalize_lot_reference(order.get('funpay_lot_id'))
  order_title = _normalize_title(order.get('title'))
  same_id = bool(lot_funpay_id and order_funpay_id and (lot_funpay_id == order_funpay_id))
  title_match = bool(lot_title and order_title and (lot_title in order_title or order_title in lot_title))
  stale_link = bool(order.get('lot_id') and _find_lot(str(order.get('lot_id'))) is None)
  if same_id or ((not order.get('lot_id') or stale_link) and title_match):
   if _repair_order_lot_link(order, lot, 'lot_created_or_migrated'):
    repaired += 1
 if repaired:
  _db_save()
 return repaired

def _log_meta(event_type: str) -> Tuple[str, str, str]:
 event_name = str(event_type or 'INFO').upper()
 return LOG_EVENT_META.get(event_name, ('ℹ️', event_name, 'cyan'))

def _format_log_details(details: dict) -> List[str]:
 safe = _redact(details or {})
 compact: List[str] = []
 for key, value in safe.items():
  if value in (None, '', [], {}):
   continue
  if isinstance(value, bool):
   rendered = 'да' if value else 'нет'
  elif isinstance(value, (dict, list)):
   rendered = json.dumps(value, ensure_ascii=False, separators=(',', ':'))
  else:
   rendered = str(value)
  label = LOG_DETAIL_LABELS.get(str(key), str(key).replace('_', ' '))
  compact.append(f'{label}: {rendered[:180]}')
 return compact[:12]

def _terminal_log_line(event_type: str, message: str, details: dict, *, colored: bool=False) -> str:
 icon, label, color_name = _log_meta(event_type)
 suffix_parts = _format_log_details(details)
 message_text = str(message or '').strip()
 title = f'{icon} [{label}]'
 if not colored:
  suffix = '  ·  ' + '  ·  '.join(suffix_parts) if suffix_parts else ''
  return f'{title} {message_text}{suffix}'
 color = ANSI_COLORS.get(color_name, ANSI_COLORS['cyan'])
 head = f'{color}{title} {message_text}{ANSI_RESET}'
 if not suffix_parts:
  return head
 details_text = '  ·  '.join(suffix_parts)
 return f'{head}  {ANSI_DIM}·  {details_text}{ANSI_RESET}'

def _append_text_log(event_type: str, message: str, details: dict) -> None:
 try:
  line = _terminal_log_line(event_type, message, details, colored=False)
  stamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
  os.makedirs(PLUGIN_FOLDER, exist_ok=True)
  with open(TEXT_LOG_FILE, 'a', encoding='utf-8') as log_file:
   log_file.write(f'[{stamp}] {line}\n')
 except Exception as e:
  logger.debug('%s text log write failed: %s', PREFIX, e)

def _is_colored_license_event(event_name: str, message: str) -> bool:
 event_name = str(event_name or '').upper()
 message_l = str(message or '').casefold()
 if event_name in {'SERVER', 'START'}:
  return True
 license_words = ('лиценз', 'license', 'регистрац', 'installation', 'build_hash', 'сервер', 'api')
 return any((word in message_l for word in license_words))

def _log(event_type: str, message: str, **details: Any) -> None:
 event_name = str(event_type or 'INFO').upper()
 _append_text_log(event_name, message, details)
 line = _terminal_log_line(event_name, message, details, colored=True)
 if event_name in {'ERROR', 'FAILED', 'CRITICAL'}:
  logger.error('%s %s', PREFIX, line)
 elif event_name in {'DENIED', 'REFUND', 'REFUND_IGNORED', 'WARNING', 'WARN', 'ORDER_UNRESOLVED', 'ORDER_MATCH_FAILED'}:
  logger.warning('%s %s', PREFIX, line)
 else:
  logger.info('%s %s', PREFIX, line)
 if _db_locked() or not _is_colored_license_event(event_name, message):
  return
 entry = {'ts': _now(), 'type': event_name, 'message': str(message or '')[:1200], 'details': _redact(details)}
 with _DB_LOCK:
  db = _db_get()
  db.setdefault('logs', []).append(entry)
  db['logs'] = db['logs'][-MAX_LOGS:]
  try:
   _db_save()
  except Exception as e:
   logger.error('%s Не удалось сохранить цветной лог: %s', PREFIX, e)

def _stats_inc(key: str, amount: int=1) -> None:
 if _db_locked():
  return
 db = _db_get()
 db.setdefault('stats', {})[key] = _safe_int(db['stats'].get(key), 0) + int(amount)

def _register_admin(chat_id: int) -> None:
 if _db_locked():
  return
 db = _db_get()
 ids = db['global'].setdefault('admin_chat_ids', [])
 sid = str(chat_id)
 if sid not in [str(x) for x in ids]:
  ids.append(sid)
  _db_save()

def _notify(kind: str, text: str) -> None:
 if _db_locked() or _CARDINAL is None:
  return
 db = _db_get()
 if not bool(db['global'].get('notifications', {}).get(kind, True)):
  return
 bot = _CARDINAL.telegram.bot
 for chat_id in db['global'].get('admin_chat_ids', []):
  try:
   bot.send_message(int(chat_id), text, parse_mode='HTML', disable_web_page_preview=True)
  except Exception:
   continue

def _notification_state(kind: str) -> bool:
 if _db_locked():
  return False
 return bool(_db_get()['global'].get('notifications', {}).get(kind, True))

def generate_steam_guard_code(shared_secret: str) -> Optional[str]:
 try:
  key = base64.b64decode(str(shared_secret or '').strip())
  timestamp = int(time.time()) // 30
  digest = hmac.new(key, timestamp.to_bytes(8, 'big'), hashlib.sha1).digest()
  offset = digest[-1] & 15
  value = int.from_bytes(digest[offset:offset + 4], 'big') & 2147483647
  alphabet = '23456789BCDFGHJKMNPQRTVWXY'
  code = ''
  for _ in range(5):
   code += alphabet[value % len(alphabet)]
   value //= len(alphabet)
  return code
 except Exception as e:
  logger.warning('%s Steam Guard generation failed: %s', PREFIX, e)
  return None

def _validate_steam_shared_secret(value: str) -> str:
 text = str(value or '').strip()
 low = text.casefold()
 if low.startswith('otpauth://') or 'secret=' in low:
  raise ValueError('Для Steam нужен только shared_secret из SDA или файл .maFile. Ссылки TOTP сюда добавлять нельзя.')
 if not generate_steam_guard_code(text):
  raise ValueError('Невалидный Steam shared_secret. Отправьте shared_secret из SDA или файл .maFile.')
 return text

def _extract_totp_secret(value: str) -> str:
 value = str(value or '').strip()
 if value.casefold().startswith('otpauth://'):
  try:
   return str((parse_qs(urlparse(value).query).get('secret') or [''])[0]).strip()
  except Exception:
   return ''
 return value.replace(' ', '')

def generate_totp_code(secret_value: str, digits: int=6, period: int=30) -> Optional[str]:
 try:
  secret_value = _extract_totp_secret(secret_value).upper()
  if not secret_value:
   return None
  secret_value += '=' * (-len(secret_value) % 8)
  key = base64.b32decode(secret_value, casefold=True)
  counter = int(time.time()) // int(period)
  digest = hmac.new(key, struct.pack('>Q', counter), hashlib.sha1).digest()
  offset = digest[-1] & 15
  value = (struct.unpack('>I', digest[offset:offset + 4])[0] & 2147483647) % 10 ** int(digits)
  return str(value).zfill(int(digits))
 except Exception as e:
  logger.warning('%s TOTP generation failed: %s', PREFIX, e)
  return None

def _decode_header(value: str) -> str:
 out = []
 for part, enc in decode_header(str(value or '')):
  if isinstance(part, bytes):
   out.append(part.decode(enc or 'utf-8', errors='replace'))
  else:
   out.append(str(part))
 return ''.join(out)

def _email_text(msg) -> str:
 parts = []
 if msg.is_multipart():
  for item in msg.walk():
   ctype = item.get_content_type()
   if ctype not in {'text/plain', 'text/html'}:
    continue
   payload = item.get_payload(decode=True)
   if payload:
    parts.append(payload.decode(item.get_content_charset() or 'utf-8', errors='replace'))
 else:
  payload = msg.get_payload(decode=True)
  if payload:
   parts.append(payload.decode(msg.get_content_charset() or 'utf-8', errors='replace'))
 return '\n'.join(parts)

def fetch_rockstar_code(account: dict) -> Tuple[Optional[str], str]:
 data = account.get('data') or {}
 host = str(data.get('imap_host') or '').strip()
 port = _safe_int(data.get('imap_port'), 993, 1, 65535)
 username = str(data.get('email') or '').strip()
 password = str(data.get('mail_password') or '')
 folder = str(data.get('folder') or 'INBOX')
 sender_filter = str(data.get('sender_filter') or 'rockstargames').casefold()
 subject_filter = str(data.get('subject_filter') or '').casefold()
 code_regex = str(data.get('code_regex') or '\\b([A-Z0-9]{6,8})\\b')
 max_age_minutes = _safe_int(data.get('max_age_minutes'), 20, 1, 1440)
 if not host or not username or (not password):
  return (None, 'IMAP не настроен')
 client = None
 try:
  client = imaplib.IMAP4_SSL(host, port, timeout=15)
  client.login(username, password)
  client.select(folder, readonly=True)
  status, ids = client.search(None, 'ALL')
  if status != 'OK':
   return (None, 'почта не вернула список писем')
  for msg_id in reversed(ids[0].split()[-30:]):
   status, rows = client.fetch(msg_id, '(RFC822 INTERNALDATE)')
   if status != 'OK' or not rows:
    continue
   raw = next((row[1] for row in rows if isinstance(row, tuple) and len(row) > 1), None)
   if not raw:
    continue
   msg = email.message_from_bytes(raw)
   sender = _decode_header(msg.get('From', '')).casefold()
   subject = _decode_header(msg.get('Subject', ''))
   if sender_filter and sender_filter not in sender:
    continue
   if subject_filter and subject_filter not in subject.casefold():
    continue
   date_tuple = email.utils.parsedate_tz(msg.get('Date', ''))
   if date_tuple:
    ts = email.utils.mktime_tz(date_tuple)
    if _now() - int(ts) > max_age_minutes * 60:
     continue
   body = _email_text(msg)
   match = re.search(code_regex, subject + '\n' + body, re.I)
   if match:
    code = match.group(1) if match.groups() else match.group(0)
    return (str(code).strip(), 'ok')
  return (None, 'свежее письмо с кодом не найдено')
 except Exception as e:
  return (None, str(e))
 finally:
  if client is not None:
   try:
    client.logout()
   except Exception:
    pass

def _imap_servers_for_email(email_address: str) -> List[str]:
 domain = (str(email_address or '').split('@')[-1] if '@' in str(email_address or '') else '').lower().strip()
 if not domain:
  raise ValueError('Некорректный email.')
 if domain.endswith('mail.ru') or domain in {'bk.ru', 'inbox.ru', 'list.ru', 'internet.ru'}:
  return ['imap.mail.ru']
 if 'gmail' in domain:
  return ['imap.gmail.com']
 if 'yandex' in domain or domain in {'ya.ru'}:
  return ['imap.yandex.ru']
 if 'firstmail' in domain:
  return ['imap.firstmail.ru']
 if 'notletters' in domain:
  return ['imap.notletters.com']
 raise ValueError('Неизвестный IMAP-провайдер.')
def _check_imap_credentials(email_address: str, password: str) -> Tuple[bool, str, str]:
 try:
  servers = _imap_servers_for_email(email_address)
 except Exception as e:
  return (False, '', str(e))
 last_error = ''
 for host in servers:
  client = None
  try:
   client = imaplib.IMAP4_SSL(host, 993, timeout=15)
   client.login(email_address, password)
   return (True, host, '')
  except Exception as e:
   last_error = str(e)
  finally:
   if client is not None:
    try:
     client.logout()
    except Exception:
     pass
 return (False, '', last_error or 'Не удалось войти по IMAP.')

def _smakmail_request(path: str, mailbox_password: str, params: Optional[dict]=None) -> Any:
 token = str((_db_get().get('global') or {}).get('smakmail_api_key') or '').strip() if not _db_locked() else ''
 if not token:
  raise RuntimeError('SmakMail API key не задан в настройках.')
 url = SMAKMAIL_API_BASE + path
 if params:
  url += '?' + urlencode(params)
 req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}', 'X-Mailbox-Password': str(mailbox_password), 'Accept': 'application/json'})
 try:
  with urllib.request.urlopen(req, timeout=20) as response:
   raw = response.read()
 except urllib.error.HTTPError as e:
  if e.code == 404:
   return None
  if e.code in {401, 403}:
   raise RuntimeError('SmakMail не принял API key или пароль ящика.') from e
  raise
 if not raw:
  return None
 return json.loads(raw.decode('utf-8'))

def _smakmail_list_messages(email_addr: str, password: str, limit: int=20) -> List[dict]:
 data = _smakmail_request('/mailbox/messages', password, {'email': email_addr, 'limit': int(limit)})
 if isinstance(data, list):
  return [x for x in data if isinstance(x, dict)]
 if isinstance(data, dict):
  for key in ('messages', 'items', 'data', 'results'):
   value = data.get(key)
   if isinstance(value, list):
    return [x for x in value if isinstance(x, dict)]
 return []

def _smakmail_message_id(item: dict) -> str:
 for key in ('msg_id', 'message_id', 'id', 'mail_id'):
  if item.get(key) not in (None, ''):
   return str(item.get(key))
 return ''

def _smakmail_text(item: dict) -> str:
 raw = ' '.join((str(item.get(k) or '') for k in ('subject', 'snippet', 'snippet_600', 'text', 'body', 'html')))
 raw = re.sub(r'(?is)<(script|style).*?>.*?</\1>', ' ', raw)
 raw = re.sub(r'(?s)<[^>]+>', ' ', raw)
 return unicodedata.normalize('NFKC', unescape(raw)).replace('\xa0', ' ')

def _smakmail_codes(item: dict) -> List[str]:
 values = []
 extract = item.get('extract') or {}
 if isinstance(extract, dict):
  raw = extract.get('codes') or extract.get('code') or []
  if not isinstance(raw, (list, tuple, set)):
   raw = [raw]
  values.extend(raw)
 for key in ('code', 'latest_code', 'otp'):
  if item.get(key):
   values.append(item.get(key))
 out = []
 for value in values:
  if isinstance(value, dict):
   value = next((value.get(k) for k in ('value', 'code', 'otp', 'token', 'text') if value.get(k)), '')
  code = str(value or '').upper().strip(' .,|:<>[](){}')
  if re.fullmatch(r'[A-Z0-9]{5,8}', code) and code not in out and code not in {'STEAM', 'HTTPS'}:
   out.append(code)
 visible = _smakmail_text(item)
 for pattern in (r'(?:steam\s*guard\s*(?:code)?|access\s*code|login\s*code|sign\s*in\s*code|security\s*code|code)\D{0,80}\b([A-Z0-9]{5,7})\b', r'(?:код\s*steam\s*guard|код\s*для\s*входа|код\s*доступа|код)\D{0,80}\b([A-Z0-9]{5,7})\b'):
  for value in re.findall(pattern, visible, re.I):
   code = str(value).upper().strip()
   if code not in out and code not in {'STEAM', 'HTTPS'}:
    out.append(code)
 return out

def _is_smakmail_steam_login(item: dict) -> bool:
 subject = str(item.get('subject') or '')
 sender = ' '.join((str(item.get(k) or '') for k in ('from_addr', 'from', 'sender')))
 return bool(_steam_login_mail_allowed(subject, sender, _smakmail_text(item)) and _smakmail_codes(item))

def _check_smakmail_credentials(email_addr: str, password: str) -> Tuple[bool, str]:
 try:
  _smakmail_list_messages(email_addr, password, 1)
  return True, ''
 except Exception as e:
  return False, str(e)

def fetch_smakmail_steam_code(account: dict) -> Tuple[Optional[str], str]:
 data = account.setdefault('data', {})
 email_addr = str(data.get('email') or '').strip().lower()
 password = str(data.get('mail_password') or '')
 last_uid = str(data.get('last_uid') or '').strip()
 if not email_addr or not password:
  return None, 'SmakMail не настроен'
 try:
  items = []
  for item in _smakmail_list_messages(email_addr, password, 20):
   msg_id = _smakmail_message_id(item)
   merged = dict(item)
   if msg_id:
    try:
     full = _smakmail_request('/messages/' + quote(msg_id, safe=''), password)
     if isinstance(full, dict):
      merged.update(full)
    except Exception:
     pass
   items.append(merged)
  seen = set()
  for item in items:
   msg_id = _smakmail_message_id(item)
   key = msg_id or hashlib.sha256(_smakmail_text(item).encode('utf-8')).hexdigest()[:24]
   if key in seen or last_uid and key == last_uid:
    continue
   seen.add(key)
   if not _is_smakmail_steam_login(item):
    continue
   codes = _smakmail_codes(item)
   if codes:
    data['pending_uid'] = key
    return codes[0], 'ok'
  return None, 'Новый Steam Guard-код для входа в SmakMail не найден'
 except Exception as e:
  return None, str(e)

def _mail_visible_text(msg) -> str:
 raw = _email_text(msg)
 raw = re.sub('(?is)<(script|style).*?>.*?</\\\\1>', ' ', raw)
 raw = re.sub('(?s)<[^>]+>', ' ', raw)
 return unicodedata.normalize('NFKC', unescape(raw)).replace('\xa0', ' ')
_STEAM_LOGIN_POS_RE = re.compile(r'(пытает(?:есь|ся)\s+войти|попытк\w*\s+входа|код\s+(?:steam\s+guard\s+)?для\s+входа|для\s+входа|вход\w*\s+(?:в|на)\s+аккаунт|авторизац\w*|нов(?:ое|ый|ого|ом)\s+(?:устройств\w*|браузер\w*|компьютер\w*)|вход\w*\s+с\s+нов\w+\s+(?:устройств\w*|браузер\w*|компьютер\w*)|attempt\s+to\s+log\s*in|trying\s+to\s+log\s*in|sign[ -]?in|log[ -]?in|login|access\s+from\s+(?:a\s+)?new\s+(?:device|browser|computer)|new\s+(?:device|browser|computer))', re.I)
_STEAM_BLOCK_RE = re.compile(r'(trade\s+confirmation|confirm\s+your\s+(?:trade|market)|steam\s+guard\s+confirmation|community\s+market|market\s+(?:listing|transaction|confirmation)|trade\s+(?:offer|request)|подтвержден\w*\s+(?:обмен|продаж|покупк)|торгов\w*\s+площадк|обмен\w*|маркет|запрос\w*\s+на\s+(?:смен|измен)\w*\s+(?:почт|email|парол|телефон)|смен\w*\s+(?:почт|email|парол|телефон)|измен\w*\s+(?:почт|email|парол|телефон)|сброс\w*\s+парол|восстановлен\w*\s+аккаунт|подтвержден\w*\s+(?:почт|email|телефон)|password\s+reset|reset\s+your\s+password|requested\s+to\s+change\s+your\s+(?:password|email)|email\s+(?:address\s+)?change|change\s+of\s+(?:email|password|phone)|account\s+recovery|recovery\s+code|email\s+verification|verify\s+your\s+email|phone\s+(?:number\s+)?change|steam\s+guard\s+(?:disabled|removed|enabled|added)|(?:remove|disable|enable|add)\s+steam\s+guard|authenticator\s+(?:removed|added|disabled|enabled))', re.I)

def _steam_login_mail_allowed(subject: str, sender: str, body: str) -> bool:
 blob = f'{subject}\n{sender}\n{body}'
 low = blob.casefold()
 sender_l = str(sender or '').casefold()
 if 'steampowered.com' not in sender_l and 'steamcommunity.com' not in sender_l:
  return False
 if 'steam guard' not in low and 'steamguard' not in low and 'стим гард' not in low:
  return False
 if _STEAM_BLOCK_RE.search(blob):
  return False
 return bool(_STEAM_LOGIN_POS_RE.search(blob))

def _is_steam_login_guard_email(msg) -> bool:
 subject = _decode_header(msg.get('Subject', ''))
 frm_raw = _decode_header(msg.get('From', ''))
 frm_addr = str(email.utils.parseaddr(frm_raw)[1] or '').lower().strip()
 return _steam_login_mail_allowed(subject, frm_addr or frm_raw, _mail_visible_text(msg))

def _extract_steam_email_code(msg) -> Optional[str]:
 subject = _decode_header(msg.get('Subject', ''))
 body = _mail_visible_text(msg)
 combined = unicodedata.normalize('NFKC', subject + '\n' + body)
 patterns = ['(?:\\bкод\\b|\\bcode\\b)[^A-Z0-9]{0,40}([A-Z0-9]{5,7})', 'steam\\s*guard[^A-Z0-9]{0,200}([A-Z0-9]{5,7})']
 for pattern in patterns:
  match = re.search(pattern, combined, re.I | re.S)
  if match:
   return str(match.group(1)).upper().strip()
 for line in combined.splitlines():
  token = ''.join((ch for ch in line.strip() if not ch.isspace()))
  if re.fullmatch('[A-Z0-9]{5,7}', token, re.I):
   return token.upper()
 return None

def fetch_steam_email_code(account: dict) -> Tuple[Optional[str], str]:
 data = account.setdefault('data', {})
 if str(data.get('provider') or 'imap').casefold() == 'smakmail':
  return fetch_smakmail_steam_code(account)
 username = str(data.get('email') or '').strip()
 password = str(data.get('mail_password') or '')
 host = str(data.get('imap_host') or '').strip()
 last_uid = str(data.get('last_uid') or '').strip()
 max_age_minutes = _safe_int(data.get('max_age_minutes'), 20, 1, 1440)
 if not username or not password:
  return (None, 'IMAP не настроен')
 hosts = [host] if host else _imap_servers_for_email(username)
 last_error = ''
 for current_host in hosts:
  client = None
  try:
   client = imaplib.IMAP4_SSL(current_host, 993, timeout=15)
   client.login(username, password)
   status, _ = client.select('INBOX', readonly=True)
   if status != 'OK':
    last_error = 'Не удалось открыть INBOX'
    continue
   status, rows = client.uid('search', None, '(OR FROM "noreply@steampowered.com" FROM "support@steampowered.com")')
   if status != 'OK' or not rows or (not rows[0]):
    return (None, 'Письма Steam не найдены')
   uids = rows[0].split()
   for uid in reversed(uids[-60:]):
    uid_s = uid.decode(errors='ignore') if isinstance(uid, bytes) else str(uid)
    if last_uid and uid_s == last_uid:
     break
    status, fetched = client.uid('fetch', uid, '(RFC822)')
    if status != 'OK' or not fetched:
     continue
    raw = next((row[1] for row in fetched if isinstance(row, tuple) and len(row) > 1), None)
    if not raw:
     continue
    msg = email.message_from_bytes(raw)
    if not _is_steam_login_guard_email(msg):
     continue
    date_tuple = email.utils.parsedate_tz(msg.get('Date', ''))
    if date_tuple:
     mail_ts = int(email.utils.mktime_tz(date_tuple))
     if _now() - mail_ts > max_age_minutes * 60:
      continue
    code = _extract_steam_email_code(msg)
    if not code:
     continue
    data['imap_host'] = current_host
    data['pending_uid'] = uid_s
    return (code, 'ok')
   return (None, 'Новое письмо Steam Guard для входа не найдено')
  except Exception as e:
   last_error = str(e)
  finally:
   if client is not None:
    try:
     client.logout()
    except Exception:
     pass
 return (None, last_error or 'Ошибка IMAP')

def _get_account_code(account: dict) -> Tuple[Optional[str], str]:
 account_type = _canonical_account_type(account.get('type'))
 if account_type == 'steam_sda':
  code = generate_steam_guard_code(str(account.get('secret') or ''))
  return (code, 'ok' if code else 'ошибка shared_secret')
 if account_type == 'steam_email':
  return fetch_steam_email_code(account)
 if account_type == 'totp':
  code = generate_totp_code(str(account.get('secret') or ''))
  return (code, 'ok' if code else 'ошибка TOTP secret')
 if account_type == 'rockstar_email':
  return fetch_rockstar_code(account)
 if account_type == 'denuvo':
  return ('', 'allocation_only')
 return (None, 'неподдерживаемый тип аккаунта')

def _field(obj: Any, name: str, default: Any=None) -> Any:
 if obj is None:
  return default
 if isinstance(obj, dict):
  return obj.get(name, default)
 try:
  return getattr(obj, name, default)
 except Exception:
  return default

def _objects(root: Any, depth: int=0) -> Iterable[Any]:
 if root is None or depth > 2:
  return []
 found = [root]
 for key in ('order', 'lot', 'offer', 'node', 'buyer', 'user', 'message', 'data', 'fields'):
  child = _field(root, key)
  if child is not None and child is not root:
   found.extend(_objects(child, depth + 1))
 return found

def _event_chat_id(event: Any) -> Optional[Any]:
 return _field(_field(event, 'message'), 'chat_id') or _field(event, 'chat_id') or _field(_field(event, 'order'), 'chat_id')

def _extract_buyer(event: Any) -> Tuple[str, str]:
 candidates = list(_objects(event))
 buyer_id = ''
 buyer_nick = ''
 for root in (event, _field(event, 'order')):
  buyer = _field(root, 'buyer')
  if buyer is None:
   continue
  direct_id = _field(buyer, 'id') or _field(buyer, 'user_id')
  if direct_id not in (None, ''):
   buyer_id = str(direct_id)
  for key in ('username', 'name', 'nickname', 'nick'):
   value = _field(buyer, key)
   if isinstance(value, str) and value.strip():
    buyer_nick = value.strip().lstrip('@')
    break
  if buyer_id or buyer_nick:
   break
 for obj in candidates:
  if buyer_id:
   break
  for key in ('buyer_id', 'user_id', 'sender_id', 'from_id'):
   value = _field(obj, key)
   if value not in (None, ''):
    buyer_id = str(_field(value, 'id', value))
    break
  if buyer_id:
   break
 for obj in candidates:
  if buyer_nick:
   break
  for key in ('buyer_username', 'buyer_name', 'username', 'nickname', 'nick', 'author', 'name'):
   value = _field(obj, key)
   if isinstance(value, str) and value.strip() and (value.casefold() != 'funpay'):
    buyer_nick = value.strip().lstrip('@')
    break
  if buyer_nick:
   break
 chat_id = _event_chat_id(event)
 if not buyer_id:
  buyer_id = str(chat_id or buyer_nick or 'unknown')
 if not buyer_nick:
  buyer_nick = buyer_id
 return (buyer_id, buyer_nick)

def _extract_order_info(event: Any) -> dict:
 order = _field(event, 'order') or event
 objects = list(_objects(order)) + list(_objects(event))
 info = {'order_id': '', 'chat_id': str(_event_chat_id(event) or _field(order, 'chat_id') or ''), 'buyer_id': '', 'buyer_nick': '', 'funpay_lot_id': '', 'quantity': 1, 'title': '', 'status': 'paid'}
 buyer_id, buyer_nick = _extract_buyer(event)
 info['buyer_id'], info['buyer_nick'] = (buyer_id, buyer_nick)
 title_keys = ('description', 'title', 'short_description', 'summary', 'order_title', 'lot_title', 'name')
 quantity_keys = ('amount', 'quantity', 'qty', 'count')
 for obj in objects:
  if not info['order_id']:
   for key in ('order_id', 'id'):
    value = _field(obj, key)
    if value not in (None, '') and obj is not _field(order, 'lot'):
     candidate = str(value).lstrip('#')
     if re.fullmatch('[A-Za-z0-9-]{5,}', candidate):
      info['order_id'] = candidate
      break
  if not info['title']:
   for key in title_keys:
    value = _field(obj, key)
    if isinstance(value, str) and value.strip():
     info['title'] = value.strip()
     break
  for key in quantity_keys:
   value = _field(obj, key)
   try:
    number = int(value)
   except Exception:
    continue
   if 1 <= number <= 100000:
    info['quantity'] = number
    break
  if not info['funpay_lot_id']:
   for key in ('lot_id', 'offer_id'):
    value = _field(obj, key)
    if value not in (None, ''):
     normalized = _normalize_lot_reference(value)
     if normalized.isdigit():
      info['funpay_lot_id'] = normalized
      break
  if not info['funpay_lot_id']:
   for key in ('html', 'link', 'url', 'public_link', 'private_link'):
    raw = str(_field(obj, key, '') or '')
    match = re.search('(?:offer(?:Edit)?\\\\?(?:id|offer)=|data-offer-id=[\\\\\\"\']?)(\\\\d+)', raw, re.I)
    if match:
     info['funpay_lot_id'] = match.group(1)
     break
 nested_lot = _field(order, 'lot') or _field(event, 'lot')
 if nested_lot is not None:
  value = _field(nested_lot, 'id') or _field(nested_lot, 'lot_id')
  normalized = _normalize_lot_reference(value)
  if normalized.isdigit():
   info['funpay_lot_id'] = normalized
 return info

def _event_seen(key: str, ttl: int=30) -> bool:
 now = time.time()
 with _EVENT_LOCK:
  stale = [k for k, ts in _RECENT_EVENT_KEYS.items() if now - ts > ttl]
  for item in stale:
   _RECENT_EVENT_KEYS.pop(item, None)
  if key in _RECENT_EVENT_KEYS:
   return True
  _RECENT_EVENT_KEYS[key] = now
  return False
LOT_TITLE_STOPWORDS = {'покупатель', 'оплатил', 'оплатила', 'заказ', 'новый', 'steam', 'оффлайн', 'активации', 'активация', 'игр', 'игра', 'товар', 'код', 'подтвердить', 'выполнение', 'order', 'paid', 'buyer', 'offline', 'activation', 'games'}

def _lot_profile_titles(lot: dict) -> List[str]:
 values: List[str] = []
 for value in (lot.get('title'), lot.get('funpay_title')):
  if isinstance(value, str) and value.strip():
   values.append(value.strip())
 cardinal = _CARDINAL
 lot_ref = _normalize_lot_reference(lot.get('funpay_lot_id'))
 if cardinal is not None and lot_ref:
  for profile_name in ('profile', 'curr_profile', 'tg_profile'):
   profile = getattr(cardinal, profile_name, None)
   getter = getattr(profile, 'get_lot', None)
   if not callable(getter):
    continue
   try:
    profile_lot = getter(int(lot_ref) if lot_ref.isdigit() else lot_ref)
   except Exception:
    profile_lot = None
   if profile_lot is None:
    continue
   for attr in ('description', 'title', 'short_description'):
    value = getattr(profile_lot, attr, None)
    if isinstance(value, str) and value.strip():
     values.append(value.strip())
   break
 return list(dict.fromkeys(values))

def _lot_title_score(order_title: str, configured_title: str) -> int:
 source = _normalize_title(order_title)
 candidate = _normalize_title(configured_title)
 if not source or not candidate:
  return 0
 if source == candidate:
  return 10000 + len(candidate)
 if candidate in source:
  return 8000 + len(candidate)
 if source in candidate and len(source) >= 5:
  return 7000 + len(source)
 source_tokens = {x for x in source.split() if len(x) >= 3 and x not in LOT_TITLE_STOPWORDS}
 candidate_tokens = {x for x in candidate.split() if len(x) >= 3 and x not in LOT_TITLE_STOPWORDS}
 if candidate_tokens:
  common = source_tokens & candidate_tokens
  coverage = len(common) / len(candidate_tokens)
  required = 1 if len(candidate_tokens) == 1 else 2
  if len(common) >= required and coverage >= 0.75:
   return 5000 + int(coverage * 1000) + len(candidate)
 ratio = difflib.SequenceMatcher(None, source, candidate).ratio()
 if ratio >= 0.82 and min(len(source), len(candidate)) >= 6:
  return 3000 + int(ratio * 1000)
 return 0

def _match_configured_lot(info: dict) -> Tuple[Optional[dict], str]:
 direct = _lot_by_funpay_id(info.get('funpay_lot_id'))
 if direct is not None:
  return (direct, 'funpay_lot_id')
 title = str(info.get('title') or '').strip()
 if not title or _db_locked():
  return (None, 'no_title')
 scored: List[Tuple[int, dict, str]] = []
 for lot in _db_get().get('lots', []):
  best_score = 0
  best_title = ''
  for candidate in _lot_profile_titles(lot):
   score = _lot_title_score(title, candidate)
   if score > best_score:
    best_score, best_title = (score, candidate)
  if best_score:
   scored.append((best_score, lot, best_title))
 if not scored:
  return (None, 'title_no_match')
 scored.sort(key=lambda row: row[0], reverse=True)
 top_score, top_lot, top_title = scored[0]
 if len(scored) > 1 and scored[1][0] >= top_score - 30:
  return (None, 'title_ambiguous')
 top_lot['funpay_title'] = top_title[:200]
 return (top_lot, 'title')

def _prefer_buyer_nick(current: Any, incoming: Any, buyer_id: Any) -> str:
 current_text = str(current or '').strip()
 incoming_text = str(incoming or '').strip()
 buyer_text = str(buyer_id or '').strip()
 incoming_is_fallback = not incoming_text or incoming_text == buyer_text or incoming_text.isdigit()
 if current_text and (not current_text.isdigit()) and incoming_is_fallback:
  return current_text
 return incoming_text or current_text

def _record_order(info: dict) -> Optional[dict]:
 if _db_locked():
  return None
 db = _db_get()
 info = dict(info or {})
 info['funpay_lot_id'] = _normalize_lot_reference(info.get('funpay_lot_id'))
 lot, match_reason = _match_configured_lot(info)
 order_id = str(info.get('order_id') or '').strip().lstrip('#')
 if not order_id:
  raw = '|'.join([str(info.get('chat_id') or ''), str(info.get('buyer_id') or ''), str(info.get('buyer_nick') or ''), str(info.get('funpay_lot_id') or ''), str(info.get('title') or '')])
  order_id = 'auto-' + hashlib.sha256(raw.encode('utf-8', 'ignore')).hexdigest()[:16]
 existing = next((x for x in db.get('orders', []) if str(x.get('order_id')) == order_id), None)
 created = existing is None
 was_unresolved = bool((existing or {}).get('unresolved'))
 was_lot_id = str((existing or {}).get('lot_id') or '')
 if existing is None:
  existing = {'order_id': order_id, 'chat_id': str(info.get('chat_id') or ''), 'buyer_id': str(info.get('buyer_id') or info.get('chat_id') or ''), 'buyer_nick': str(info.get('buyer_nick') or ''), 'funpay_lot_id': str(info.get('funpay_lot_id') or (lot or {}).get('funpay_lot_id') or ''), 'lot_id': str((lot or {}).get('id') or ''), 'title': str(info.get('title') or '')[:500], 'quantity': max(1, _safe_int(info.get('quantity'), 1, 1, 100000)), 'status': 'paid', 'created_at': _now(), 'updated_at': _now(), 'allocations': {}, 'issued': 0, 'unresolved': lot is None, 'new_order_notified': False}
  db.setdefault('orders', []).append(existing)
  db['orders'] = db['orders'][-MAX_ORDERS:]
  _stats_inc('orders')
 else:
  incoming_buyer_id = str(info.get('buyer_id') or '')
  incoming_chat_id = str(info.get('chat_id') or '')
  existing['chat_id'] = incoming_chat_id or str(existing.get('chat_id') or '')
  existing['buyer_id'] = incoming_buyer_id or str(existing.get('buyer_id') or '')
  existing['buyer_nick'] = _prefer_buyer_nick(existing.get('buyer_nick'), info.get('buyer_nick'), existing.get('buyer_id'))
  existing['quantity'] = max(1, _safe_int(info.get('quantity'), existing.get('quantity', 1), 1, 100000))
  existing['status'] = 'paid'
  existing['updated_at'] = _now()
  if info.get('title'):
   existing['title'] = str(info.get('title'))[:500]
  if info.get('funpay_lot_id'):
   existing['funpay_lot_id'] = str(info.get('funpay_lot_id'))
 if lot is not None:
  _repair_order_lot_link(existing, lot, f'new_order_{match_reason}')
 else:
  existing['unresolved'] = True
 became_resolved = bool(lot is not None and (was_unresolved or (was_lot_id and was_lot_id != str(lot.get('id')))))
 should_announce = not bool(existing.get('new_order_notified'))
 _db_save()
 if lot is None:
  if created:
   _log('ORDER_UNRESOLVED', 'Заказ сохранён без привязки к лоту. Привязка будет восстановлена по команде покупателя', order_id=order_id, funpay_lot_id=info.get('funpay_lot_id'), buyer=existing.get('buyer_nick') or existing.get('buyer_id'), chat_id=existing.get('chat_id'), title=existing.get('title'), reason=match_reason)
  if should_announce:
   _notify('new_order', f"⚠️ <b>Заказ получен, но лот пока не сопоставлен</b>\nПокупатель: <code>{escape(str(existing.get('buyer_nick') or existing.get('buyer_id')))}</code>\nЗаказ: <code>{escape(order_id)}</code>\nПри первой команде плагин попробует безопасно восстановить привязку автоматически.")
   existing['new_order_notified'] = True
   existing['new_order_notification_kind'] = 'unresolved'
   _db_save()
  return existing
 if created or became_resolved:
  _log('ORDER', 'Заказ сопоставлен с лотом', order_id=order_id, lot_id=lot['id'], funpay_lot_id=lot.get('funpay_lot_id'), account_type=_canonical_account_type(lot.get('account_type')), quantity=existing['quantity'], buyer=existing.get('buyer_nick') or existing.get('buyer_id'), reason=match_reason)
 if should_announce:
  _notify('new_order', f"🛒 <b>Новый заказ</b>\nЛот: <b>{escape(str(lot.get('title') or lot.get('funpay_lot_id')))}</b>\nТип: <b>{escape(ACCOUNT_TYPES.get(_canonical_account_type(lot.get('account_type')), str(lot.get('account_type'))))}</b>\nПокупатель: <code>{escape(str(existing.get('buyer_nick') or existing.get('buyer_id')))}</code>\nКоличество: <b>{existing.get('quantity')}</b>\nЗаказ: <code>{escape(order_id)}</code>")
  existing['new_order_notified'] = True
  existing['new_order_notification_kind'] = 'matched'
  _db_save()
 return existing

def _mark_order_from_system_message(event: Any, text: str) -> None:
 low = text.casefold()
 if not any((token in low for token in ('оплатил заказ', 'заказ оплачен', 'paid the order', 'order paid'))):
  return
 oid_match = re.search('(?:заказ|order)\\s*#?\\s*([A-Za-z0-9\\-]{5,})', text, re.I)
 qty_match = re.search('(\\d{1,5})\\s*(?:шт|коп|copies|items?)', text, re.I)
 info = {'order_id': oid_match.group(1) if oid_match else '', 'chat_id': str(_event_chat_id(event) or ''), 'buyer_id': '', 'buyer_nick': '', 'funpay_lot_id': '', 'quantity': int(qty_match.group(1)) if qty_match else 1, 'title': text}
 buyer_id, buyer_nick = _extract_buyer(event)
 info['buyer_id'], info['buyer_nick'] = (buyer_id, buyer_nick)
 _record_order(info)

def _mark_refund_from_system_message(event: Any, text: str) -> bool:
 low = str(text or '').casefold()
 refund_tokens = ('вернул деньги', 'возврат средств', 'заказ возвращ', 'возврат по заказу', 'refund', 'refunded', 'money was returned', 'order was refunded')
 if not any((token in low for token in refund_tokens)):
  return False
 db = _db_get()
 oid_match = re.search('(?:заказ|order)\\s*#?\\s*([A-Za-z0-9\\-]{5,})', str(text), re.I)
 order = None
 if oid_match:
  order = _find_order(oid_match.group(1))
 if order is None:
  chat_id = str(_event_chat_id(event) or '')
  buyer_id, buyer_nick = _extract_buyer(event)
  candidates = [row for row in db.get('orders', []) if str(row.get('status') or '') in {'paid', 'active'} and (str(row.get('chat_id') or '') == chat_id or str(row.get('buyer_id') or '') == str(buyer_id or '') or (buyer_nick and str(row.get('buyer_nick') or '').casefold() == str(buyer_nick).casefold()))]
  candidates.sort(key=lambda row: _safe_int(row.get('created_at'), 0), reverse=True)
  order = candidates[0] if candidates else None
 if order is None:
  _log('REFUND_IGNORED', 'Получено сообщение о возврате, но заказ не найден', text=str(text)[:500])
  return True
 with _DB_LOCK:
  order['status'] = 'refunded'
  order['refunded_at'] = _now()
  order['updated_at'] = _now()
  for job in db.get('denuvo_queue', []):
   if str(job.get('order_id')) != str(order.get('order_id')):
    continue
   if not job.get('reservation_id') and (not job.get('local_committed')) and (str(job.get('phase') or '') not in {'lifecycle', 'release'}):
    job['status'] = 'cancelled'
    job['last_error'] = 'order_refunded'
    job['updated_at'] = _now()
  for job in db.get('steam_queue', []):
   if str(job.get('order_id')) == str(order.get('order_id')) and str(job.get('status')) in STEAM_QUEUE_ACTIVE_STATES:
    job['status'] = 'cancelled'
    job['last_error'] = 'order_refunded'
    job['updated_at'] = _now()
  _db_save()
 _log('REFUND', 'Заказ отмечен как возвращён. Новые коды заблокированы, активная Denuvo-активация сохранена до конца срока', order_id=order.get('order_id'))
 _notify('order_status', f"↩️ <b>Заказ возвращён</b>\nЗаказ: <code>{escape(str(order.get('order_id')))}</code>\nПокупатель больше не сможет получать новые коды. Уже выданная Denuvo-активация останется активной до штатного окончания срока.")
 return True

def _matching_order(lot: dict, chat_id: Any, buyer_id: str, buyer_nick: str) -> Optional[dict]:
 if _db_locked():
  return None
 now = _now()
 exact: List[dict] = []
 unresolved: List[dict] = []
 changed = False
 lot_title = _normalize_title(lot.get('title'))
 for order in _db_get().get('orders', []):
  if str(order.get('status') or '') not in {'paid', 'active'}:
   continue
  if now - _safe_int(order.get('created_at'), 0) > ORDER_ACTIVE_DAYS * 86400:
   continue
  if not _order_buyer_matches(order, chat_id, buyer_id, buyer_nick):
   continue
  if _order_lot_reference_matches(order, lot):
   if str(order.get('lot_id') or '') != str(lot.get('id') or ''):
    changed = _repair_order_lot_link(order, lot, 'matching_funpay_lot_id') or changed
   exact.append(order)
   continue
  linked_lot = _find_lot(str(order.get('lot_id') or '')) if order.get('lot_id') else None
  order_title = _normalize_title(order.get('title'))
  title_match = bool(lot_title and order_title and (lot_title in order_title or order_title in lot_title))
  if not order.get('lot_id') or linked_lot is None or bool(order.get('unresolved')):
   if title_match:
    changed = _repair_order_lot_link(order, lot, 'matching_title') or changed
    exact.append(order)
   else:
    unresolved.append(order)
 if not exact and len(unresolved) == 1:
  order = unresolved[0]
  changed = _repair_order_lot_link(order, lot, 'single_unresolved_order_for_buyer') or changed
  exact.append(order)
 if changed:
  _db_save()
 exact.sort(key=lambda x: _safe_int(x.get('created_at'), 0), reverse=True)
 if exact:
  return exact[0]
 recent = [{'order_id': row.get('order_id'), 'lot_id': row.get('lot_id'), 'funpay_lot_id': row.get('funpay_lot_id'), 'buyer': row.get('buyer_nick') or row.get('buyer_id'), 'status': row.get('status')} for row in _db_get().get('orders', [])[-8:]]
 _log('ORDER_MATCH_FAILED', 'Не найден оплаченный заказ для команды', lot_id=lot.get('id'), funpay_lot_id=lot.get('funpay_lot_id'), account_type=_canonical_account_type(lot.get('account_type')), chat_id=chat_id, buyer_id=buyer_id, buyer_nick=buyer_nick, recent_orders=recent)
 return None
DENUVO_ACTIVE_QUEUE_STATES = {'queued', 'retry', 'processing', 'sending', 'lifecycle_retry'}
DENUVO_RETRYABLE_CODES = {'NETWORK_ERROR', 'TIMEOUT', 'RATE_LIMITED', 'INTERNAL_ERROR', 'NO_SAFE_FREE_ACCOUNT', 'SERVER_UNAVAILABLE', 'HTTP_429', 'HTTP_500', 'HTTP_502', 'HTTP_503', 'HTTP_504', 'TIMESTAMP_OUT_OF_RANGE', 'database_locked', 'server_url_empty', 'installation_not_registered'}
DENUVO_PERMANENT_CODES = {'LICENSE_NOT_FOUND', 'LICENSE_DISABLED', 'LICENSE_EXPIRED', 'PLUGIN_UUID_MISMATCH', 'OWNER_ID_MISMATCH', 'SELLER_HASH_MISMATCH', 'BUILD_NOT_ALLOWED', 'BUILD_HASH_MISMATCH', 'MACHINE_HASH_MISMATCH', 'INSTALLATION_DISABLED', 'INSTALLATION_DISABLED_OR_UNKNOWN', 'INSTALLATION_LIMIT_REACHED', 'DATA_FINGERPRINT_MISMATCH', 'ORDER_BUYER_MISMATCH', 'CARDINAL_ID_MISMATCH', 'CARDINAL_ID_REQUIRED', 'CARDINAL_ALREADY_LICENSED', 'AUTO_LICENSE_DISABLED'}

def _usage_key(order: dict, lot: dict, buyer_id: str) -> str:
 return '|'.join([str(order.get('order_id')), str(lot.get('id')), str(buyer_id)])

def _quota(lot: dict, order: dict) -> int:
 return 0

def _check_usage(lot: dict, order: dict, buyer_id: str) -> Tuple[bool, str, dict, int, int]:
 db = _db_get()
 key = _usage_key(order, lot, buyer_id)
 rec = db.setdefault('usage', {}).setdefault(key, {'count': 0, 'last_ts': 0, 'account_counts': {}, 'account_windows': {}})
 return (True, 'ok', rec, _safe_int(rec.get('count'), 0), 0)

def _account_limit_mode(account: dict) -> str:
 mode = str(account.get('limit_mode') or 'count').strip().casefold()
 return mode if mode in {'count', 'time'} else 'count'

def _reset_account_usage(account_id: str) -> None:
 if _db_locked():
  return
 aid = str(account_id or '')
 for rec in _db_get().setdefault('usage', {}).values():
  if not isinstance(rec, dict):
   continue
  rec.setdefault('account_counts', {}).pop(aid, None)
  rec.setdefault('account_windows', {}).pop(aid, None)

def _account_limit_window(account: dict, rec: dict) -> dict:
 account_id = str(account.get('id'))
 windows = rec.setdefault('account_windows', {})
 legacy_count = _safe_int(rec.get('account_counts', {}).get(account_id), 0)
 row = windows.setdefault(account_id, {'count': legacy_count, 'started_at': 0})
 now = _now()
 started_at = _safe_int(row.get('started_at'), 0)
 if started_at <= 0:
  row['started_at'] = now
  started_at = now
 if _account_limit_mode(account) == 'count':
  reset_seconds = _safe_int(account.get('limit_reset_seconds'), 0, 0, 31536000)
  if reset_seconds > 0 and now - started_at >= reset_seconds:
   row['count'] = 0
   row['started_at'] = now
   rec.setdefault('account_counts', {})[account_id] = 0
 return row

def _account_limit_values(account: dict, rec: dict, *, prospective: bool=False) -> Tuple[Any, Any]:
 mode = _account_limit_mode(account)
 row = _account_limit_window(account, rec)
 if mode == 'time':
  duration = _safe_int(account.get('limit_time_seconds'), 0, 0, 31536000)
  if duration <= 0:
   return ('∞', '∞')
  started_at = _safe_int(row.get('started_at'), _now())
  if _now() - started_at >= duration:
   return (0, _fmt_duration(duration))
  return ('∞', '∞')
 limit = account.get('limit_total')
 if limit in (None, '', 0, '0'):
  return ('∞', '∞')
 total = max(1, _safe_int(limit, 1, 1, 1000000))
 used = _safe_int(row.get('count'), 0) + (1 if prospective else 0)
 return (max(0, total - used), total)

def _account_limit_ok(account: dict, rec: dict) -> bool:
 if _account_limit_mode(account) == 'time':
  duration = _safe_int(account.get('limit_time_seconds'), 0, 0, 31536000)
  if duration > 0:
   row = _account_limit_window(account, rec)
   if _now() - _safe_int(row.get('started_at'), _now()) >= duration:
    return False
 else:
  left, total = _account_limit_values(account, rec)
  if total != '∞' and _safe_int(left, 0) <= 0:
   return False
 denuvo = account.get('denuvo') or {}
 if _safe_int(denuvo.get('cooldown_until'), 0) > _now():
  return False
 return True

def _lot_bound_accounts(lot: dict, *, enabled_only: bool=True) -> List[dict]:
 if _db_locked():
  return []
 selected = next((str(x) for x in lot.get('account_ids', []) if str(x)), '')
 if not selected:
  return []
 account_type = _canonical_account_type(lot.get('account_type'))
 result = []
 for account in _db_get().get('accounts', []):
  if str(account.get('id')) != selected:
   continue
  if account_type and _canonical_account_type(account.get('type')) != account_type:
   continue
  if enabled_only and (not bool(account.get('enabled', True))):
   continue
  result.append(account)
  break
 return result

def _candidate_accounts(lot: dict, order: dict, rec: dict) -> List[dict]:
 candidates = [account for account in _lot_bound_accounts(lot) if _account_limit_ok(account, rec)]
 allocation = (order.get('allocations') or {}).get(str(lot.get('id')))
 if allocation:
  existing = next((x for x in candidates if str(x.get('id')) == str(allocation.get('account_id'))), None)
  if existing is not None:
   return [existing] + [x for x in candidates if x is not existing]
 return candidates

def _stable_json(data: Any) -> str:
 return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def _sha256_bytes(payload: bytes) -> str:
 return hashlib.sha256(payload).hexdigest()

def _plugin_build_hash() -> str:
 try:
  with open(os.path.abspath(__file__), 'rb') as plugin_file:
   return _sha256_bytes(plugin_file.read())
 except Exception:
  return hashlib.sha256((UUID + ':' + VERSION).encode('utf-8')).hexdigest()

def _server_cfg() -> dict:
 server = _db_get()['global'].setdefault('server', {})
 if not str(server.get('url') or '').strip():
  server['url'] = DEFAULT_SERVER_URL
 return server

def _ensure_server_identity() -> dict:
 server = _server_cfg()
 changed = False
 if not str(server.get('install_id') or '').strip():
  server['install_id'] = str(uuidlib.uuid4())
  changed = True
 if not str(server.get('machine_seed') or '').strip():
  server['machine_seed'] = secrets.token_urlsafe(32)
  changed = True
 if changed:
  _db_save()
 return server

def _scalar_identity(value: Any) -> str:
 if isinstance(value, (str, int)) and str(value).strip():
  return str(value).strip()
 return ''

def _resolve_owner_id() -> str:
 if _db_locked():
  return ''
 explicit = _scalar_identity(_server_cfg().get('owner_id'))
 if explicit:
  return explicit
 cardinal = _CARDINAL
 if cardinal is None:
  return ''
 roots = [getattr(cardinal, 'account', None), cardinal]
 for root in roots:
  if root is None:
   continue
  for name in ('id', 'user_id', 'owner_id', 'username', 'nickname'):
   value = _scalar_identity(getattr(root, name, None))
   if value:
    return value.lstrip('@')
  nested = getattr(root, 'account', None)
  if nested is not None and nested is not root:
   for name in ('id', 'user_id', 'username'):
    value = _scalar_identity(getattr(nested, name, None))
    if value:
     return value.lstrip('@')
 return ''

def _telegram_bot_token_hash() -> str:
 cardinal = _CARDINAL
 bot = getattr(getattr(cardinal, 'telegram', None), 'bot', None) if cardinal is not None else None
 if bot is None:
  return ''
 for name in ('token', 'api_token', 'bot_token'):
  value = _scalar_identity(getattr(bot, name, None))
  if value:
   return hashlib.sha256(('AutoOffline-telegram-bot:' + value).encode('utf-8')).hexdigest()
 return ''

def _cardinal_identity_hash() -> str:
 owner_id = _resolve_owner_id()
 token_hash = _telegram_bot_token_hash()
 if not owner_id or not token_hash:
  return ''
 payload = {'plugin_uuid': UUID, 'owner_id': owner_id, 'telegram_bot_token_hash': token_hash}
 return hashlib.sha256(_stable_json(payload).encode('utf-8')).hexdigest()

def _machine_hash() -> str:
 server = _ensure_server_identity()
 seed = str(server.get('machine_seed') or '')
 return hashlib.sha256(('AutoOffline-machine:' + seed).encode('utf-8')).hexdigest()

def _data_fingerprint(owner_id: Optional[str]=None) -> str:
 server = _ensure_server_identity()
 safe_data = {'plugin_uuid': UUID, 'owner_id': owner_id if owner_id is not None else _resolve_owner_id(), 'seller_hash': str(server.get('seller_hash') or ''), 'schema_version': DB_VERSION, 'installation_id': str(server.get('install_id') or '')}
 return hashlib.sha256(_stable_json(safe_data).encode('utf-8')).hexdigest()

def _identity_body(extra: Optional[dict]=None) -> dict:
 server = _ensure_server_identity()
 owner_id = _resolve_owner_id()
 body = {'plugin_uuid': UUID, 'owner_id': owner_id, 'seller_hash': str(server.get('seller_hash') or ''), 'install_id': str(server.get('install_id') or ''), 'machine_hash': _machine_hash(), 'build_hash': _plugin_build_hash(), 'data_fingerprint': _data_fingerprint(owner_id), 'version': VERSION, 'cardinal_id_hash': _cardinal_identity_hash()}
 if extra:
  body.update(extra)
 return body

def _apply_server_config(cfg: dict) -> None:
 if _db_locked() or not isinstance(cfg, dict):
  return
 server = _server_cfg()
 if str(cfg.get('server_url') or cfg.get('url') or '').strip():
  new_url = str(cfg.get('server_url') or cfg.get('url')).strip().rstrip('/')
  if new_url != str(server.get('url') or ''):
   server['installation_secret'] = ''
   server['installation_id'] = ''
  server['url'] = new_url
 update_url = str(cfg.get('plugin_update_url') or cfg.get('update_url') or cfg.get('download_url') or '').strip()
 if update_url:
  server['plugin_update_url'] = update_url
 if str(cfg.get('license_key') or '').strip():
  server['license_key'] = str(cfg.get('license_key')).strip()
  server['installation_secret'] = ''
 if str(cfg.get('owner_id') or '').strip():
  server['owner_id'] = str(cfg.get('owner_id')).strip()
  server['installation_secret'] = ''
 if 'seller_hash' in cfg:
  server['seller_hash'] = str(cfg.get('seller_hash') or '').strip().lower()
  server['installation_secret'] = ''
 if 'fallback_local' in cfg:
  server['fallback_local'] = bool(cfg.get('fallback_local'))
 if 'timeout' in cfg:
  server['timeout'] = _safe_int(cfg.get('timeout'), 15, 2, 60)
 if 'queue_max_attempts' in cfg:
  server['queue_max_attempts'] = _safe_int(cfg.get('queue_max_attempts'), 9, 1, 20)
 if 'queue_retry_base' in cfg:
  server['queue_retry_base'] = _safe_int(cfg.get('queue_retry_base'), 5, 1, 600)
 if 'queue_max_wait' in cfg:
  server['queue_max_wait'] = _safe_int(cfg.get('queue_max_wait'), 1800, 60, 86400)
 if 'hold_seconds' in cfg or 'denuvo_hold_seconds' in cfg:
  server['denuvo_hold_seconds'] = _safe_int(cfg.get('hold_seconds', cfg.get('denuvo_hold_seconds')), 21600, 300, 604800)
 if 'status_sync_interval' in cfg:
  server['status_sync_interval'] = _safe_int(cfg.get('status_sync_interval'), 300, 30, 3600)
 _ensure_server_identity()

def _http_json(method: str, path: str, payload: Optional[dict]=None, headers: Optional[dict]=None) -> Tuple[bool, dict, str, int]:
 if _db_locked():
  return (False, {}, 'database_locked', 0)
 server = _server_cfg()
 base_url = str(server.get('url') or '').strip().rstrip('/')
 if not base_url:
  return (False, {}, 'server_url_empty', 0)
 url = base_url + '/' + path.lstrip('/')
 raw = None if payload is None else _stable_json(payload).encode('utf-8')
 request_headers = {'Accept': 'application/json', 'User-Agent': f'AutoOffline/{VERSION}'}
 if raw is not None:
  request_headers['Content-Type'] = 'application/json'
 if headers:
  request_headers.update(headers)
 req = urllib.request.Request(url, data=raw, headers=request_headers, method=method.upper())
 _stats_inc('server_requests')
 timeout = _safe_int(server.get('timeout'), 15, 2, 60)
 try:
  with urllib.request.urlopen(req, timeout=timeout) as response:
   body = response.read(512 * 1024)
   data = json.loads(body.decode('utf-8')) if body else {}
   status = int(getattr(response, 'status', 200) or 200)
   return (bool(data.get('ok', 200 <= status < 300)), data, str(data.get('code') or 'ok'), status)
 except urllib.error.HTTPError as e:
  raw_body = e.read(512 * 1024)
  try:
   data = json.loads(raw_body.decode('utf-8')) if raw_body else {}
  except Exception:
   data = {'message': raw_body.decode('utf-8', errors='replace')[:500]}
  _stats_inc('server_errors')
  code = str(data.get('code') or f'HTTP_{e.code}')
  return (False, data, code, int(e.code))
 except Exception as e:
  _stats_inc('server_errors')
  code = 'TIMEOUT' if isinstance(e, TimeoutError) else 'NETWORK_ERROR'
  return (False, {'message': str(e)}, code, 0)

def _update_server_clock(data: dict) -> None:
 if _db_locked() or not isinstance(data, dict):
  return
 server_time = _safe_int(data.get('server_time'), 0)
 if server_time:
  _server_cfg()['clock_offset'] = max(-3600, min(3600, server_time - _now()))

def _server_bootstrap_license(force: bool=False) -> Tuple[bool, dict, str]:
 if _db_locked():
  return (False, {}, 'database_locked')
 server = _ensure_server_identity()
 if not str(server.get('url') or '').strip():
  return (False, {}, 'server_url_empty')
 cardinal_id_hash = _cardinal_identity_hash()
 if not cardinal_id_hash:
  return (False, {}, 'cardinal_identity_unavailable')
 if str(server.get('license_key') or '').strip() and (not force):
  return (True, {'ok': True, 'code': 'LICENSE_ALREADY_PRESENT'}, 'ok')
 body = _identity_body()
 ok, data, code, _ = _http_json('POST', 'api/v1/plugin/bootstrap', body)
 _update_server_clock(data)
 server['last_register_at'] = _now()
 server['last_verify_code'] = code
 if ok and str(data.get('license_key') or '').strip():
  new_key = str(data.get('license_key')).strip()
  if new_key != str(server.get('license_key') or ''):
   server['installation_secret'] = ''
   server['installation_id'] = ''
  server['license_key'] = new_key
  server['license_type'] = 'auto'
  server['cardinal_id_hash'] = cardinal_id_hash
  server['last_verify_code'] = str(data.get('code') or 'AUTO_LICENSE_READY')
  _db_save()
  _log('SERVER', 'Автоматическая лицензия Cardinal получена', license_prefix=str(data.get('license_key_prefix') or ''), cardinal_id_hash=cardinal_id_hash)
  return (True, data, 'ok')
 _db_save()
 return (False, data, code)

def _server_register(force: bool=False) -> Tuple[bool, dict, str]:
 if _db_locked():
  return (False, {}, 'database_locked')
 server = _ensure_server_identity()
 if not str(server.get('url') or '').strip():
  return (False, {}, 'server_url_empty')
 if not str(server.get('license_key') or '').strip():
  boot_ok, boot_data, boot_code = _server_bootstrap_license()
  if not boot_ok:
   return (False, boot_data, boot_code)
  server = _ensure_server_identity()
 owner_id = _resolve_owner_id()
 if not owner_id:
  return (False, {}, 'owner_id_empty')
 build_hash = _plugin_build_hash()
 if not force and str(server.get('installation_secret') or '').strip() and (str(server.get('registered_build_hash') or '') == build_hash) and (str(server.get('registered_owner_id') or '') == owner_id):
  return (True, {'ok': True, 'code': 'ALREADY_REGISTERED'}, 'ok')
 body = _identity_body({'license_key': str(server.get('license_key') or '')})
 ok, data, code, _ = _http_json('POST', 'api/v1/plugin/register', body)
 if not ok and code == 'CARDINAL_ALREADY_LICENSED':
  boot_ok, boot_data, boot_code = _server_bootstrap_license(force=True)
  if boot_ok:
   server = _ensure_server_identity()
   body = _identity_body({'license_key': str(server.get('license_key') or '')})
   ok, data, code, _ = _http_json('POST', 'api/v1/plugin/register', body)
  else:
   data, code = (boot_data, boot_code)
 _update_server_clock(data)
 server['last_register_at'] = _now()
 server['last_verify_code'] = code
 if ok and str(data.get('installation_secret') or '').strip():
  server['installation_secret'] = str(data.get('installation_secret'))
  server['installation_id'] = str(data.get('installation_id') or '')
  server['registered_build_hash'] = build_hash
  server['registered_owner_id'] = owner_id
  server['protocol_version'] = _safe_int(data.get('protocol_version'), 1, 1, 100)
  server['data_binding_mode'] = str(data.get('data_binding_mode') or 'off')
  server['last_verify_at'] = _now()
  server['last_verify_code'] = 'REGISTERED'
  _db_save()
  _log('SERVER', 'Установка зарегистрирована в API', installation_id=server.get('installation_id'), build_hash=build_hash)
  return (True, data, 'ok')
 _db_save()
 return (False, data, code)

def _auto_registration_run() -> None:
 try:
  ok, data, code = _server_bootstrap_license()
  if ok:
   ok, data, code = _server_register(force=True)
  if ok:
   _server_verify()
   _DENUVO_QUEUE_EVENT.set()
  elif not _db_locked():
   _log('SERVER', 'Автоматическая регистрация не выполнена', code=code, response=data)
 except Exception as exc:
  logger.warning('%s automatic license registration failed: %s', PREFIX, exc)

def _start_auto_registration() -> None:
 global _AUTO_REGISTER_WORKER
 if _db_locked():
  return
 with _AUTO_REGISTER_LOCK:
  if _AUTO_REGISTER_WORKER is not None and _AUTO_REGISTER_WORKER.is_alive():
   return
  _AUTO_REGISTER_WORKER = threading.Thread(target=_auto_registration_run, name='AutoOfflineAutoLicense', daemon=True)
  _AUTO_REGISTER_WORKER.start()

def _decode_b64url(value: str) -> bytes:
 value = str(value or '').strip()
 value += '=' * (-len(value) % 4)
 return base64.urlsafe_b64decode(value.encode('ascii'))

def _signed_headers(body: dict) -> dict:
 server = _ensure_server_identity()
 secret = str(server.get('installation_secret') or '').strip()
 if not secret:
  raise RuntimeError('installation_not_registered')
 timestamp = str(_now() + _safe_int(server.get('clock_offset'), 0, -3600, 3600))
 nonce = secrets.token_urlsafe(18)
 body_hash = hashlib.sha256(_stable_json(body).encode('utf-8')).hexdigest()
 message = f'{timestamp}.{nonce}.{body_hash}'.encode('utf-8')
 signature = hmac.new(_decode_b64url(secret), message, hashlib.sha256).hexdigest()
 return {'X-AO-Install-ID': str(server.get('install_id') or ''), 'X-AO-Timestamp': timestamp, 'X-AO-Nonce': nonce, 'X-AO-Signature': signature}

def _server_signed_post(path: str, payload: Optional[dict]=None, retry_registration: bool=True) -> Tuple[bool, dict, str]:
 if _db_locked():
  return (False, {}, 'database_locked')
 server = _ensure_server_identity()
 if not str(server.get('installation_secret') or '').strip():
  registered, reg_data, reg_code = _server_register()
  if not registered:
   return (False, reg_data, reg_code)
 body = _identity_body(payload or {})
 try:
  headers = _signed_headers(body)
 except Exception as e:
  return (False, {}, str(e))
 ok, data, code, status = _http_json('POST', path, body, headers)
 _update_server_clock(data)
 if ok:
  server['last_verify_at'] = _now()
  server['last_verify_code'] = str(data.get('code') or 'OK')
  _db_save()
  return (True, data, 'ok')
 server['last_verify_code'] = code
 _db_save()
 registration_codes = {'INSTALLATION_DISABLED_OR_UNKNOWN', 'SIGNATURE_INVALID', 'MACHINE_HASH_MISMATCH', 'BUILD_HASH_MISMATCH', 'OWNER_ID_MISMATCH', 'SELLER_HASH_MISMATCH', 'INSTALL_ID_MISMATCH'}
 if retry_registration and code == 'TIMESTAMP_OUT_OF_RANGE':
  return _server_signed_post(path, payload, retry_registration=False)
 if retry_registration and (code in registration_codes or status in {401, 403}):
  registered, reg_data, reg_code = _server_register(force=True)
  if registered:
   return _server_signed_post(path, payload, retry_registration=False)
  return (False, reg_data, reg_code)
 return (False, data, code)

def _server_verify() -> Tuple[bool, dict, str]:
 return _server_signed_post('api/v1/plugin/verify', {})

def _buyer_hash(buyer_id: str) -> str:
 server = _ensure_server_identity() if not _db_locked() else {}
 seed = str(server.get('machine_seed') or 'AutoOffline-local').encode('utf-8')
 return hmac.new(seed, str(buyer_id).encode('utf-8'), hashlib.sha256).hexdigest()

def _denuvo_game_id(lot: dict, candidates: Optional[List[dict]]=None) -> str:
 for account in candidates or _lot_bound_accounts(lot):
  value = str((account.get('denuvo') or {}).get('game_id') or '').strip()
  if value:
   return value
 return str(lot.get('funpay_lot_id') or lot.get('id') or '').strip()

def _server_allocate(lot: dict, order: dict, buyer_id: str, candidates: List[dict]) -> Tuple[Optional[dict], str, dict]:
 payload_candidates = []
 for account in candidates:
  denuvo = account.get('denuvo') or {}
  failure_rate = max(0.0, min(1.0, float(denuvo.get('failure_rate') or denuvo.get('error_rate') or 0.0)))
  failure_rate = 0 if failure_rate < 1e-06 else 1 if failure_rate >= 0.999999 else round(failure_rate, 6)
  payload_candidates.append({'account_id': str(account.get('id')), 'account_name': str(account.get('name') or account.get('id') or ''), 'enabled': bool(account.get('enabled', True) and denuvo.get('enabled', True)), 'weight': _safe_int(denuvo.get('weight'), 100, 1, 10000), 'slot_limit': _safe_int(denuvo.get('slot_limit'), 5, 1, 10000), 'reserve': _safe_int(denuvo.get('reserve'), 0, 0, 10000), 'active_slots_local': _safe_int(denuvo.get('active_slots'), 0, 0, 10000), 'failure_rate': f'{failure_rate:.6f}', 'cooldown_until': _safe_int(denuvo.get('cooldown_until'), 0)})
 payload = {'game_id': _denuvo_game_id(lot, candidates), 'order_id': str(order.get('order_id') or ''), 'buyer_hash': _buyer_hash(buyer_id), 'candidates': payload_candidates}
 ok, data, code = _server_signed_post('api/v1/denuvo/allocate', payload)
 if not ok:
  return (None, code, data)
 chosen_id = str(data.get('account_id') or '')
 chosen = next((x for x in candidates if str(x.get('id')) == chosen_id), None)
 if chosen is None:
  return (None, 'server_returned_unknown_account', data)
 return (chosen, 'ok', data)

def _server_confirm(reservation_id: str) -> Tuple[bool, dict, str]:
 ok, data, code = _server_signed_post('api/v1/denuvo/confirm', {'reservation_id': str(reservation_id or '')})
 if ok:
  return (ok, data, code)
 if code == 'RESERVATION_NOT_CONFIRMABLE':
  status_ok, status_data, _ = _server_status()
  if status_ok:
   row = next((x for x in status_data.get('reservations', []) if str(x.get('id')) == str(reservation_id)), None)
   if row and str(row.get('status')) == 'confirmed':
    return (True, {'ok': True, 'code': 'ALREADY_CONFIRMED', 'reservation': row}, 'ok')
 return (False, data, code)

def _server_release(reservation_id: str) -> Tuple[bool, dict, str]:
 if not reservation_id:
  return (True, {'ok': True, 'code': 'NO_RESERVATION'}, 'ok')
 ok, data, code = _server_signed_post('api/v1/denuvo/release', {'reservation_id': str(reservation_id)})
 if code == 'RESERVATION_NOT_FOUND':
  return (True, data, 'ok')
 return (ok, data, code)

def _server_report(account_id: str, game_id: str, success: bool, error_code: str='') -> Tuple[bool, dict, str]:
 return _server_signed_post('api/v1/denuvo/report', {'account_id': str(account_id or ''), 'game_id': str(game_id or ''), 'success': bool(success), 'error_code': str(error_code or '')[:100]})

def _server_status() -> Tuple[bool, dict, str]:
 return _server_signed_post('api/v1/denuvo/status', {})

def _server_sync_status() -> Tuple[bool, dict, str]:
 ok, data, code = _server_status()
 if not ok:
  return (False, data, code)
 reservations = data.get('reservations') if isinstance(data.get('reservations'), list) else []
 counts: Dict[str, int] = {}
 for row in reservations:
  account_id = str(row.get('account_id') or '')
  if account_id:
   counts[account_id] = counts.get(account_id, 0) + 1
 with _DB_LOCK:
  db = _db_get()
  for account in db.get('accounts', []):
   denuvo = account.get('denuvo') or {}
   if account.get('type') == 'denuvo' or denuvo.get('enabled'):
    denuvo['active_slots'] = counts.get(str(account.get('id')), 0)
    account['denuvo'] = denuvo
  server = db['global'].setdefault('server', {})
  server['last_status_sync'] = _now()
  server['active_reservations'] = len(reservations)
  _db_save()
 _sync_denuvo_lot_capacity(_CARDINAL)
 return (True, data, 'ok')

def _choose_account(lot: dict, order: dict, buyer_id: str, rec: dict) -> Tuple[Optional[dict], str, dict]:
 candidates = _candidate_accounts(lot, order, rec)
 if not candidates:
  bound = _lot_bound_accounts(lot)
  if bound and all((not _account_limit_ok(account, rec) for account in bound)):
   return (None, 'limit', {})
  return (None, 'no_accounts', {})
 if _is_denuvo_lot(lot):
  chosen, reason, server_data = _server_allocate(lot, order, buyer_id, candidates)
  if chosen is not None:
   return (chosen, 'server', server_data)
  _notify('denuvo', f"⚠️ <b>Denuvo API не распределил аккаунт</b>\nЛот: <code>{escape(str(lot.get('funpay_lot_id')))}</code>\nПричина: <code>{escape(reason)}</code>")
  return (None, reason, server_data)

 def score(account: dict) -> Tuple[int, int, int, str]:
  denuvo = account.get('denuvo') or {}
  existing = 0 if str((order.get('allocations') or {}).get(str(lot.get('id')), {}).get('account_id')) == str(account.get('id')) else 1
  capacity = max(1, _safe_int(denuvo.get('slot_limit'), 5) - _safe_int(denuvo.get('reserve'), 0))
  load = _safe_int(denuvo.get('active_slots'), 0)
  ratio = int(load / capacity * 10000)
  return (existing, ratio, _safe_int(account.get('issued'), 0), str(account.get('id')))
 return (sorted(candidates, key=score)[0], 'local', {})

def _commit_issue(lot: dict, order: dict, account: dict, buyer_id: str, rec: dict, server_data: dict, *, activate_denuvo: bool=False) -> Tuple[Any, Any]:
 now = _now()
 with _DB_LOCK:
  rec['count'] = _safe_int(rec.get('count'), 0) + 1
  rec['last_ts'] = now
  window = _account_limit_window(account, rec)
  window['count'] = _safe_int(window.get('count'), 0) + 1
  rec.setdefault('account_counts', {})[account['id']] = window['count']
  if _canonical_account_type(account.get('type')) == 'steam_email':
   mail_data = account.setdefault('data', {})
   pending_uid = str(mail_data.pop('pending_uid', '') or '').strip()
   if pending_uid:
    mail_data['last_uid'] = pending_uid
  account['issued'] = _safe_int(account.get('issued'), 0) + 1
  order['issued'] = _safe_int(order.get('issued'), 0) + 1
  allocation = order.setdefault('allocations', {}).setdefault(str(lot.get('id')), {})
  allocation['account_id'] = account['id']
  allocation.setdefault('assigned_at', now)
  allocation['last_code_at'] = now
  if activate_denuvo:
   allocation.update({'reservation_id': str(server_data.get('reservation_id') or ''), 'allocation_mode': 'server' if server_data.get('reservation_id') else 'local', 'activation_started_at': now})
   denuvo = account.setdefault('denuvo', {})
   denuvo['active_slots'] = min(_safe_int(denuvo.get('slot_limit'), 5, 1, 10000), _safe_int(denuvo.get('active_slots'), 0) + 1)
   denuvo['recent_activations'] = _safe_int(denuvo.get('recent_activations'), 0) + 1
   if str(server_data.get('reservation_id') or ''):
    server = _server_cfg()
    server['active_reservations'] = _safe_int(server.get('active_reservations'), 0) + 1
  _stats_inc('issued')
  left, total = _account_limit_values(account, rec)
  _db_save()
 if activate_denuvo:
  _sync_denuvo_lot_capacity(_CARDINAL)
 return (left, total)

def _deny(cardinal: 'Cardinal', chat_id: Any, lot: Optional[dict], reason: str, mapping: Optional[dict]=None) -> None:
 mapping = mapping or {}
 templates = _db_get()['global'].get('templates', {}) if not _db_locked() else _default_db()['global']['templates']
 if reason == 'no_order':
  text = templates.get('denied_no_order')
 elif reason == 'limit':
  text = templates.get('denied_limit')
 elif reason.startswith('cooldown:'):
  mapping['wait'] = _fmt_duration(_safe_int(reason.split(':', 1)[1], 0))
  text = templates.get('denied_cooldown')
 else:
  text = templates.get('unavailable')
 _funpay_send(chat_id, _render(str(text), mapping))
 if not _db_locked():
  _stats_inc('denied')
  _db_save()
 _notify('request_denied', f"⛔ <b>Отказ в выдаче</b>\nЛот: <code>{escape(str((lot or {}).get('funpay_lot_id') or '—'))}</code>\nПричина: <code>{escape(reason)}</code>")

def _find_order(order_id: str) -> Optional[dict]:
 if _db_locked():
  return None
 return next((x for x in _db_get().get('orders', []) if str(x.get('order_id')) == str(order_id)), None)

def _is_denuvo_lot(lot: dict) -> bool:
 return any((bool((account.get('denuvo') or {}).get('enabled')) for account in _lot_bound_accounts(lot)))

def _queue_key(lot: dict, order: dict, buyer_id: str) -> str:
 raw = '|'.join([str(lot.get('id')), str(buyer_id)])
 return hashlib.sha256(raw.encode('utf-8')).hexdigest()

def _queue_jobs() -> List[dict]:
 return _db_get().setdefault('denuvo_queue', [])

def _queue_position(job_id: str) -> int:
 active = sorted([x for x in _queue_jobs() if str(x.get('status')) in DENUVO_ACTIVE_QUEUE_STATES], key=lambda x: (_safe_int(x.get('next_attempt_at'), 0), _safe_int(x.get('created_at'), 0), str(x.get('id'))))
 for index, job in enumerate(active, 1):
  if str(job.get('id')) == str(job_id):
   return index
 return 0

def _queue_prune(save: bool=True) -> None:
 if _db_locked():
  return
 now = _now()
 with _DB_LOCK:
  jobs = _queue_jobs()
  kept = []
  for job in jobs:
   status = str(job.get('status') or '')
   updated = _safe_int(job.get('updated_at'), _safe_int(job.get('created_at'), now))
   if status == 'done' and now - updated > 3 * 86400:
    continue
   if status in {'failed', 'manual_review', 'cancelled'} and now - updated > 14 * 86400:
    continue
   kept.append(job)
  _db_get()['denuvo_queue'] = kept[-1000:]
  if save:
   _db_save()

def _queue_enqueue(lot: dict, order: dict, chat_id: Any, buyer_id: str, buyer_nick: str) -> Tuple[dict, bool, int]:
 with _DB_LOCK:
  key = _queue_key(lot, order, buyer_id)
  for existing in _queue_jobs():
   same_buyer_lot = str(existing.get('lot_id') or '') == str(lot.get('id') or '') and str(existing.get('buyer_id') or '') == str(buyer_id or '')
   if (str(existing.get('dedupe_key')) == key or same_buyer_lot) and str(existing.get('status')) in DENUVO_ACTIVE_QUEUE_STATES:
    return (existing, False, _queue_position(str(existing.get('id'))))
  active_count = sum((1 for x in _queue_jobs() if str(x.get('status')) in DENUVO_ACTIVE_QUEUE_STATES))
  if active_count >= 500:
   raise RuntimeError('Очередь Denuvo переполнена.')
  now = _now()
  job = {'id': _uid('q'), 'dedupe_key': key, 'status': 'queued', 'phase': 'allocate', 'lot_id': str(lot.get('id')), 'order_id': str(order.get('order_id')), 'chat_id': str(chat_id or ''), 'buyer_id': str(buyer_id or ''), 'buyer_nick': str(buyer_nick or ''), 'attempts': 0, 'next_attempt_at': now, 'created_at': now, 'updated_at': now, 'account_id': '', 'reservation_id': '', 'game_id': _denuvo_game_id(lot), 'confirmed': False, 'reported': False, 'local_committed': False, 'last_error': ''}
  _queue_jobs().append(job)
  _stats_inc('queue_enqueued')
  _db_save()
  position = _queue_position(job['id'])
 _DENUVO_QUEUE_EVENT.set()
 return (job, True, position)

def _queue_recover_stale() -> None:
 if _db_locked():
  return
 changed = False
 now = _now()
 with _DB_LOCK:
  for job in _queue_jobs():
   status = str(job.get('status') or '')
   if status == 'sending':
    job['status'] = 'manual_review'
    job['last_error'] = 'Перезапуск произошёл во время отправки. Автоповтор отключён против двойной выдачи.'
    job['updated_at'] = now
    changed = True
   elif status == 'processing':
    job['status'] = 'retry'
    job['next_attempt_at'] = now
    job['last_error'] = 'Задача восстановлена после перезапуска.'
    job['updated_at'] = now
    changed = True
  if changed:
   _db_save()

def _queue_claim() -> Optional[str]:
 if _db_locked():
  return None
 now = _now()
 with _DB_LOCK:
  candidates = [x for x in _queue_jobs() if str(x.get('status')) in {'queued', 'retry', 'lifecycle_retry', 'holding'} and _safe_int(x.get('next_attempt_at'), 0) <= now]
  if not candidates:
   return None
  candidates.sort(key=lambda x: (_safe_int(x.get('next_attempt_at'), 0), _safe_int(x.get('created_at'), 0), str(x.get('id'))))
  job = candidates[0]
  job['status'] = 'processing'
  job['attempts'] = _safe_int(job.get('attempts'), 0) + 1
  job['updated_at'] = now
  _db_save()
  return str(job.get('id'))

def _queue_get(job_id: str) -> Optional[dict]:
 return next((x for x in _queue_jobs() if str(x.get('id')) == str(job_id)), None) if not _db_locked() else None

def _queue_retry_delay(attempts: int) -> int:
 server = _server_cfg()
 base = _safe_int(server.get('queue_retry_base'), 5, 1, 600)
 return min(600, base * 2 ** min(max(0, attempts - 1), 7))

def _queue_finish(job: dict, status: str, error: str='') -> None:
 with _DB_LOCK:
  job['status'] = status
  job['updated_at'] = _now()
  job['last_error'] = str(error or '')[:500]
  if status == 'done':
   _stats_inc('queue_completed')
  elif status in {'failed', 'manual_review'}:
   _stats_inc('queue_failed')
  _db_save()

def _queue_retry_or_fail(job: dict, code: str, message: str='') -> None:
 server = _server_cfg()
 attempts = _safe_int(job.get('attempts'), 0)
 max_attempts = _safe_int(server.get('queue_max_attempts'), 9, 1, 20)
 max_wait = _safe_int(server.get('queue_max_wait'), 1800, 60, 86400)
 age = _now() - _safe_int(job.get('created_at'), _now())
 permanent = code in DENUVO_PERMANENT_CODES
 retryable = code in DENUVO_RETRYABLE_CODES or code.startswith('HTTP_5') or code in {'no_accounts', 'provider_error'}
 if permanent or attempts >= max_attempts or age >= max_wait or (not retryable):
  _queue_finish(job, 'failed', f'{code}: {message}'.strip(': '))
  _notify('denuvo', f"❌ <b>Denuvo не удалось обработать</b>\nЗаказ: <code>{escape(str(job.get('order_id')))}</code>\nПричина: <code>{escape(code)}</code>\nПлагин прекратил повторные попытки для этого запроса.")
  return
 with _DB_LOCK:
  delay = _queue_retry_delay(attempts)
  job['status'] = 'retry'
  job['next_attempt_at'] = _now() + delay
  job['updated_at'] = _now()
  job['last_error'] = f'{code}: {message}'.strip(': ')[:500]
  _db_save()
 _DENUVO_QUEUE_EVENT.set()

def _funpay_plain_text(text: str) -> str:
 value = unescape(str(text or ''))
 value = re.sub('(?i)<br\\s*/?>', '\n', value)
 value = re.sub('(?is)<a\\b[^>]*>(.*?)</a>', '\\1', value)
 value = re.sub('(?i)</?(?:b|strong|code|i|em|u|s|pre)>', '', value)
 value = re.sub('(?s)<[^>]+>', '', value)
 value = value.replace('\r\n', '\n').replace('\r', '\n')
 value = re.sub('[ \\t]+\\n', '\n', value)
 value = re.sub('\\n{4,}', '\n\n\n', value)
 return value.strip()

def _funpay_send(chat_id: Any, text: str) -> Tuple[bool, str]:
 if _CARDINAL is None:
  return (False, 'cardinal_unavailable')
 try:
  target = int(chat_id) if str(chat_id or '').isdigit() else chat_id
  _CARDINAL.account.send_message(target, _funpay_plain_text(text))
  return (True, 'ok')
 except Exception as e:
  return (False, str(e))

def _delivery_mapping(lot: dict, order: dict, account: dict, buyer_nick: str, code: str, left: int, total: int, allocation_mode: str) -> dict:
 denuvo = account.get('denuvo') or {}
 return {'code': code or '', 'account': account.get('name') or account.get('id'), 'account_id': account.get('id'), 'lot': lot.get('title') or lot.get('funpay_lot_id'), 'order_id': order.get('order_id'), 'buyer': buyer_nick, 'left': left, 'total': total, 'quantity': order.get('quantity'), 'slot_info': f"{denuvo.get('active_slots', 0)}/{denuvo.get('slot_limit', 5)}", 'allocation_mode': allocation_mode}

def _steam_queue_jobs() -> List[dict]:
 return _db_get().setdefault('steam_queue', [])

def _steam_queue_key(lot: dict, order: dict, buyer_id: str) -> str:
 raw = '|'.join([str(lot.get('account_type') or 'otp'), str(lot.get('id')), str(order.get('order_id')), str(buyer_id)])
 return hashlib.sha256(raw.encode('utf-8')).hexdigest()

def _steam_queue_position(job_id: str) -> int:
 target = next((x for x in _steam_queue_jobs() if str(x.get('id')) == str(job_id)), None)
 lot_id = str((target or {}).get('lot_id') or '')
 active = sorted([x for x in _steam_queue_jobs() if str(x.get('status')) in STEAM_QUEUE_ACTIVE_STATES and (not lot_id or str(x.get('lot_id')) == lot_id)], key=lambda x: (_safe_int(x.get('next_attempt_at'), 0), _safe_int(x.get('created_at'), 0), str(x.get('id'))))
 for index, job in enumerate(active, 1):
  if str(job.get('id')) == str(job_id):
   return index
 return 0

def _steam_queue_accounts(lot: dict) -> List[dict]:
 account_type = _canonical_account_type(lot.get('account_type'))
 if _db_locked() or account_type not in {'steam_sda', 'totp'}:
  return []
 result = []
 for account in _lot_bound_accounts(lot):
  if _canonical_account_type(account.get('type')) != account_type:
   continue
  if bool((account.get('queue') or {}).get('enabled')):
   result.append(account)
 return result

def _steam_queue_wait_seconds(account: dict) -> int:
 queue_cfg = account.get('queue') or {}
 if not bool(queue_cfg.get('enabled')):
  return 0
 account_type = _canonical_account_type(account.get('type'))
 last_issue_at = _safe_int(queue_cfg.get('last_issue_at'), 0)
 now = _now()
 if account_type == 'totp':
  if last_issue_at > 0 and last_issue_at // TOTP_QUEUE_INTERVAL_SECONDS == now // TOTP_QUEUE_INTERVAL_SECONDS:
   return TOTP_QUEUE_INTERVAL_SECONDS - now % TOTP_QUEUE_INTERVAL_SECONDS
  return 0
 interval = _safe_int(queue_cfg.get('interval_seconds'), STEAM_QUEUE_INTERVAL_SECONDS, 1, 300)
 return max(0, interval - (now - last_issue_at))

def _steam_queue_enqueue(lot: dict, order: dict, chat_id: Any, buyer_id: str, buyer_nick: str, account_id: str='') -> Tuple[dict, bool, int]:
 with _DB_LOCK:
  key = _steam_queue_key(lot, order, buyer_id)
  for existing in _steam_queue_jobs():
   if str(existing.get('dedupe_key')) == key and str(existing.get('status')) in STEAM_QUEUE_ACTIVE_STATES:
    return (existing, False, _steam_queue_position(str(existing.get('id'))))
  active_count = sum((1 for x in _steam_queue_jobs() if str(x.get('status')) in STEAM_QUEUE_ACTIVE_STATES))
  if active_count >= 500:
   raise RuntimeError('Очередь кодов переполнена.')
  now = _now()
  job = {'id': _uid('sq'), 'dedupe_key': key, 'status': 'queued', 'lot_id': str(lot.get('id')), 'order_id': str(order.get('order_id')), 'account_id': str(account_id or ''), 'chat_id': str(chat_id or ''), 'buyer_id': str(buyer_id or ''), 'buyer_nick': str(buyer_nick or ''), 'attempts': 0, 'next_attempt_at': now, 'created_at': now, 'updated_at': now, 'last_error': ''}
  _steam_queue_jobs().append(job)
  _stats_inc('steam_queue_enqueued')
  _db_save()
  position = _steam_queue_position(job['id'])
 _STEAM_QUEUE_EVENT.set()
 return (job, True, position)

def _steam_queue_claim() -> Optional[str]:
 if _db_locked():
  return None
 now = _now()
 with _DB_LOCK:
  candidates = [x for x in _steam_queue_jobs() if str(x.get('status')) in {'queued', 'retry'} and _safe_int(x.get('next_attempt_at'), 0) <= now]
  if not candidates:
   return None
  candidates.sort(key=lambda x: (_safe_int(x.get('next_attempt_at'), 0), _safe_int(x.get('created_at'), 0), str(x.get('id'))))
  job = candidates[0]
  job['status'] = 'processing'
  job['attempts'] = _safe_int(job.get('attempts'), 0) + 1
  job['updated_at'] = now
  _db_save()
  return str(job.get('id'))

def _steam_queue_get(job_id: str) -> Optional[dict]:
 return next((x for x in _steam_queue_jobs() if str(x.get('id')) == str(job_id)), None) if not _db_locked() else None

def _steam_queue_finish(job: dict, status: str, error: str='') -> None:
 with _DB_LOCK:
  job['status'] = status
  job['updated_at'] = _now()
  job['last_error'] = str(error or '')[:500]
  if status == 'done':
   _stats_inc('steam_queue_completed')
  elif status == 'failed':
   _stats_inc('steam_queue_failed')
  _db_save()

def _steam_queue_requeue(job: dict, wait_seconds: int, error: str='') -> None:
 with _DB_LOCK:
  job['status'] = 'queued'
  job['next_attempt_at'] = _now() + max(1, _safe_int(wait_seconds, 1, 1, 86400))
  job['updated_at'] = _now()
  job['last_error'] = str(error or '')[:500]
  _db_save()
 _STEAM_QUEUE_EVENT.set()

def _steam_queue_recover_stale() -> None:
 if _db_locked():
  return
 changed = False
 with _DB_LOCK:
  for job in _steam_queue_jobs():
   if str(job.get('status')) == 'processing':
    job['status'] = 'retry'
    job['next_attempt_at'] = _now()
    job['updated_at'] = _now()
    job['last_error'] = 'Задача восстановлена после перезапуска.'
    changed = True
  if changed:
   _db_save()

def _process_steam_queue_job(job_id: str) -> None:
 job = _steam_queue_get(job_id)
 if job is None:
  return
 lot = _find_lot(str(job.get('lot_id') or ''))
 order = _find_order(str(job.get('order_id') or ''))
 if lot is None or order is None or (not bool(lot.get('enabled', True))):
  _steam_queue_finish(job, 'failed', 'lot_or_order_unavailable')
  return
 if str(order.get('status') or '') not in {'paid', 'active'}:
  _steam_queue_finish(job, 'cancelled', 'order_not_active')
  return
 buyer_id = str(job.get('buyer_id') or '')
 buyer_nick = str(job.get('buyer_nick') or buyer_id)
 _, _, rec, _, _ = _check_usage(lot, order, buyer_id)
 account_type = _canonical_account_type(lot.get('account_type'))
 pinned_account_id = str(job.get('account_id') or '')
 candidates = [account for account in _candidate_accounts(lot, order, rec) if _canonical_account_type(account.get('type')) == account_type and bool((account.get('queue') or {}).get('enabled')) and (not pinned_account_id or str(account.get('id')) == pinned_account_id)]
 if not candidates:
  if pinned_account_id:
   pinned = _find_account(pinned_account_id)
   bound = [pinned] if pinned is not None else []
  else:
   bound = _lot_bound_accounts(lot)
  reason = 'limit' if bound and all((not _account_limit_ok(x, rec) for x in bound)) else 'no_accounts'
  _steam_queue_finish(job, 'failed', reason)
  if _CARDINAL is not None:
   _deny(_CARDINAL, job.get('chat_id'), lot, reason)
  return
 candidates.sort(key=lambda x: (_steam_queue_wait_seconds(x), _safe_int(x.get('issued'), 0), str(x.get('id'))))
 account = candidates[0]
 wait_seconds = _steam_queue_wait_seconds(account)
 if wait_seconds > 0:
  reason = 'Ожидание следующего 30-секундного TOTP-окна.' if account_type == 'totp' else 'Ожидание 15-секундного интервала Steam Guard.'
  _steam_queue_requeue(job, wait_seconds, reason)
  return
 code, provider_status = _get_account_code(account)
 if provider_status != 'ok' or not code:
  if _safe_int(job.get('attempts'), 0) < 3:
   _steam_queue_requeue(job, 3, provider_status)
  else:
   _steam_queue_finish(job, 'failed', provider_status)
  return
 prospective_left, total = _account_limit_values(account, rec, prospective=True)
 mapping = _delivery_mapping(lot, order, account, buyer_nick, code, prospective_left, total, 'otp_queue')
 templates = _db_get()['global'].get('templates', {})
 template = str(account.get('template') or templates.get(account_type) or '{code}')
 sent, send_error = _funpay_send(job.get('chat_id'), _render(template, mapping))
 if not sent:
  if _safe_int(job.get('attempts'), 0) < 3:
   _steam_queue_requeue(job, 5, send_error)
  else:
   _steam_queue_finish(job, 'failed', send_error)
  return
 account.setdefault('queue', {})['last_issue_at'] = _now()
 left, total = _commit_issue(lot, order, account, buyer_id, rec, {})
 _steam_queue_finish(job, 'done')
 label = 'TOTP' if account_type == 'totp' else 'Steam Guard'
 _log('ISSUED', f'{label}-код выдан через очередь', order_id=order.get('order_id'), lot_id=lot.get('id'), account_id=account.get('id'), buyer=buyer_nick, code=code, left=left, total=total)
 _notify('code_issued', f"✅ <b>{label} выдан через очередь</b>\nАккаунт: <b>{escape(str(account.get('name')))}</b>\nПокупатель: <code>{escape(buyer_nick)}</code>\nОсталось: <b>{left}/{total}</b>")

def _steam_queue_worker_loop() -> None:
 while not _STEAM_QUEUE_STOP_EVENT.is_set():
  try:
   job_id = _steam_queue_claim()
   if job_id:
    _process_steam_queue_job(job_id)
    continue
  except Exception as e:
   logger.exception('%s Steam queue worker failed: %s', PREFIX, e)
  _STEAM_QUEUE_EVENT.wait(timeout=1.0)
  _STEAM_QUEUE_EVENT.clear()

def _start_steam_queue_worker() -> None:
 global _STEAM_QUEUE_WORKER
 if _STEAM_QUEUE_WORKER is not None and _STEAM_QUEUE_WORKER.is_alive():
  return
 _STEAM_QUEUE_STOP_EVENT.clear()
 _steam_queue_recover_stale()
 _STEAM_QUEUE_WORKER = threading.Thread(target=_steam_queue_worker_loop, name='AutoOfflineSteamQueue', daemon=True)
 _STEAM_QUEUE_WORKER.start()
 _STEAM_QUEUE_EVENT.set()

def _enqueue_steam_request(cardinal: 'Cardinal', chat_id: Any, lot: dict, order: dict, buyer_id: str, buyer_nick: str, account_id: str='') -> bool:
 account_type = _canonical_account_type(lot.get('account_type'))
 label = 'TOTP' if account_type == 'totp' else 'Steam Guard'
 try:
  job, created, position = _steam_queue_enqueue(lot, order, chat_id, buyer_id, buyer_nick, account_id=account_id)
 except Exception as e:
  _deny(cardinal, chat_id, lot, 'queue_error')
  _log('ERROR', f'Не удалось добавить {label} в очередь', error=str(e), order_id=order.get('order_id'))
  return True
 if account_id:
  account = _find_account(account_id)
  waits = [_steam_queue_wait_seconds(account)] if account is not None else []
 else:
  waits = [_steam_queue_wait_seconds(x) for x in _steam_queue_accounts(lot)]
 should_notify = not created or position > 1 or (waits and min(waits) > 0)
 if should_notify:
  templates = _db_get()['global'].get('templates', {})
  prefix = 'totp' if account_type == 'totp' else 'steam'
  key = f"{prefix}_{('queued' if created else 'duplicate')}"
  queue_text = str(templates.get(key) or f'🕒 {label}-запрос поставлен в очередь. Позиция: {{position}}.')
  _funpay_send(chat_id, _render(queue_text, {'position': position or 1, 'queue_id': job.get('id')}))
 return True

def _denuvo_hold_seconds(lot: Optional[dict], account: Optional[dict]) -> int:
 account_cfg = (account or {}).get('denuvo') or {}
 value = account_cfg.get('hold_seconds') or _server_cfg().get('denuvo_hold_seconds') or 21600
 return _safe_int(value, 21600, 300, 604800)

def _queue_schedule_release(job: dict, lot: Optional[dict], account: Optional[dict]) -> None:
 hold_seconds = _denuvo_hold_seconds(lot, account)
 with _DB_LOCK:
  job['status'] = 'holding'
  job['phase'] = 'release'
  job['hold_seconds'] = hold_seconds
  job['release_at'] = _now() + hold_seconds
  job['next_attempt_at'] = job['release_at']
  job['updated_at'] = _now()
  job['last_error'] = ''
  _db_save()

def _queue_release(job: dict) -> bool:
 reservation_id = str(job.get('reservation_id') or '')
 account = _find_account(str(job.get('account_id') or ''))
 if not reservation_id:
  _queue_finish(job, 'done')
  return True
 ok, _, code = _server_release(reservation_id)
 if ok:
  if account is not None:
   with _DB_LOCK:
    denuvo = account.setdefault('denuvo', {})
    denuvo['active_slots'] = max(0, _safe_int(denuvo.get('active_slots'), 0) - 1)
    server = _server_cfg()
    server['active_reservations'] = max(0, _safe_int(server.get('active_reservations'), 0) - 1)
    _db_save()
  _queue_finish(job, 'done')
  _sync_denuvo_lot_capacity(_CARDINAL)
  _log('DENUVO', 'Резервация автоматически освобождена', reservation_id=reservation_id, order_id=job.get('order_id'), account_id=job.get('account_id'))
  return True
 attempts = _safe_int(job.get('attempts'), 0)
 max_attempts = _safe_int(_server_cfg().get('queue_max_attempts'), 9, 1, 20) + 6
 if attempts >= max_attempts:
  _queue_finish(job, 'manual_review', 'release:' + code)
  _notify('denuvo', f'⚠️ <b>Не удалось автоматически освободить Denuvo-слот</b>\nРезервация: <code>{escape(reservation_id)}</code>\nПричина: <code>{escape(code)}</code>')
  return False
 with _DB_LOCK:
  job['status'] = 'holding'
  job['phase'] = 'release'
  job['next_attempt_at'] = _now() + _queue_retry_delay(attempts)
  job['updated_at'] = _now()
  job['last_error'] = 'release:' + code
  _db_save()
 return False

def _queue_lifecycle(job: dict, account: Optional[dict]=None) -> bool:
 reservation_id = str(job.get('reservation_id') or '')
 if not reservation_id:
  _queue_finish(job, 'done')
  return True
 account = account or _find_account(str(job.get('account_id') or ''))
 game_id = str(job.get('game_id') or '')
 errors = []
 if not bool(job.get('confirmed')):
  ok, _, code = _server_confirm(reservation_id)
  if ok:
   job['confirmed'] = True
  else:
   errors.append('confirm:' + code)
 if account is not None and (not bool(job.get('reported'))):
  ok, _, code = _server_report(str(account.get('id')), game_id, True)
  if ok:
   job['reported'] = True
  else:
   errors.append('report:' + code)
 if not errors:
  lot = _find_lot(str(job.get('lot_id') or ''))
  _queue_schedule_release(job, lot, account)
  return True
 with _DB_LOCK:
  attempts = _safe_int(job.get('attempts'), 0)
  max_attempts = _safe_int(_server_cfg().get('queue_max_attempts'), 9, 1, 20) + 3
  if attempts >= max_attempts:
   job['status'] = 'manual_review'
   job['last_error'] = ' | '.join(errors)[:500]
   job['updated_at'] = _now()
   _db_save()
   _notify('denuvo', f"⚠️ <b>Denuvo выдан, но lifecycle требует проверки</b>\nЗаказ: <code>{escape(str(job.get('order_id')))}</code>\n{escape(' | '.join(errors))}")
   return False
  job['status'] = 'lifecycle_retry'
  job['next_attempt_at'] = _now() + _queue_retry_delay(attempts)
  job['last_error'] = ' | '.join(errors)[:500]
  job['updated_at'] = _now()
  _db_save()
 return False

def _find_reusable_denuvo_job(lot: dict, order: dict, buyer_id: str) -> Optional[dict]:
 candidates = []
 for job in _queue_jobs():
  if str(job.get('lot_id') or '') != str(lot.get('id') or ''):
   continue
  if str(job.get('buyer_id') or '') != str(buyer_id or ''):
   continue
  if not bool(job.get('local_committed')):
   continue
  status = str(job.get('status') or '')
  phase = str(job.get('phase') or '')
  if status not in {'holding', 'lifecycle_retry', 'processing', 'sending'}:
   continue
  if phase == 'release' and _safe_int(job.get('release_at'), 0) <= _now():
   continue
  if status == 'processing' and phase == 'release':
   continue
  if not str(job.get('account_id') or ''):
   continue
  candidates.append(job)
 candidates.sort(key=lambda row: _safe_int(row.get('delivered_at'), _safe_int(row.get('updated_at'), 0)), reverse=True)
 return candidates[0] if candidates else None

def _reuse_denuvo_activation(cardinal: 'Cardinal', chat_id: Any, lot: dict, order: dict, buyer_id: str, buyer_nick: str, job: dict) -> bool:
 account = _find_account(str(job.get('account_id') or ''))
 if account is None or not bool(account.get('enabled', True)):
  _deny(cardinal, chat_id, lot, 'no_accounts')
  _log('ERROR', 'Активная Denuvo-активация ссылается на недоступный аккаунт', order_id=order.get('order_id'), account_id=job.get('account_id'))
  return True
 with _DB_LOCK:
  allocation = order.setdefault('allocations', {}).setdefault(str(lot.get('id')), {})
  allocation.update({'account_id': str(account.get('id')), 'reservation_id': str(job.get('reservation_id') or ''), 'allocation_mode': 'reuse'})
  _db_save()
 account_type = _canonical_account_type(account.get('type') or lot.get('account_type'))
 if account_type in {'steam_sda', 'totp'} and bool((account.get('queue') or {}).get('enabled')):
  _log('DENUVO', 'Активация уже существует. Код направлен в обычную очередь', order_id=order.get('order_id'), lot_id=lot.get('id'), account_id=account.get('id'), buyer=buyer_nick)
  return _enqueue_steam_request(cardinal, chat_id, lot, order, buyer_id, buyer_nick, account_id=str(account.get('id')))
 _, _, rec, _, _ = _check_usage(lot, order, buyer_id)
 if not _account_limit_ok(account, rec):
  _deny(cardinal, chat_id, lot, 'limit')
  return True
 code, provider_status = _get_account_code(account)
 if provider_status != 'ok' or not code:
  _deny(cardinal, chat_id, lot, 'provider_error')
  _log('ERROR', 'Не удалось получить код для существующей Denuvo-активации', order_id=order.get('order_id'), account_id=account.get('id'), status=provider_status)
  return True
 prospective_left, total = _account_limit_values(account, rec, prospective=True)
 mapping = _delivery_mapping(lot, order, account, buyer_nick, code, prospective_left, total, 'reuse')
 templates = _db_get()['global'].get('templates', {})
 template = str(account.get('template') or templates.get(account_type) or '{code}')
 sent, send_error = _funpay_send(chat_id, _render(template, mapping))
 if not sent:
  _log('ERROR', 'Не удалось отправить повторный код покупателю', error=send_error, order_id=order.get('order_id'), account_id=account.get('id'))
  return True
 account.setdefault('queue', {})['last_issue_at'] = _now()
 left, total = _commit_issue(lot, order, account, buyer_id, rec, {})
 denuvo = account.get('denuvo') or {}
 _log('DENUVO', 'Код выдан без создания нового Denuvo-слота', order_id=order.get('order_id'), lot_id=lot.get('id'), account_id=account.get('id'), buyer=buyer_nick, code=code, left=left, total=total, active_slots=_safe_int(denuvo.get('active_slots'), 0), slot_limit=_safe_int(denuvo.get('slot_limit'), 5))
 _notify('code_issued', f"🔐 <b>Steam Guard выдан по активной Denuvo-активации</b>\nПокупатель: <code>{escape(buyer_nick)}</code>\nЛот: <b>{escape(str(lot.get('title') or lot.get('funpay_lot_id')))}</b>\nАккаунт: <b>{escape(str(account.get('name')))}</b>\nОсталось кодов: <b>{left}/{total}</b>\nDenuvo-слоты: <b>{_safe_int(denuvo.get('active_slots'), 0)}/{_safe_int(denuvo.get('slot_limit'), 5)}</b>")
 return True

def _process_denuvo_job(job_id: str) -> None:
 job = _queue_get(job_id)
 if job is None:
  return
 if str(job.get('phase')) == 'release':
  _queue_release(job)
  return
 if str(job.get('phase')) == 'lifecycle' or bool(job.get('local_committed')):
  _queue_lifecycle(job)
  return
 lot = _find_lot(str(job.get('lot_id') or ''))
 order = _find_order(str(job.get('order_id') or ''))
 if lot is None or order is None:
  _queue_finish(job, 'failed', 'lot_or_order_missing')
  return
 if not bool(lot.get('enabled', True)):
  _queue_finish(job, 'failed', 'lot_disabled')
  return
 if str(order.get('status') or '') not in {'paid', 'active'}:
  _queue_finish(job, 'cancelled', 'order_not_active')
  return
 buyer_id = str(job.get('buyer_id') or '')
 buyer_nick = str(job.get('buyer_nick') or buyer_id)
 ok, reason, rec, used, total = _check_usage(lot, order, buyer_id)
 if not ok:
  if reason.startswith('cooldown:'):
   with _DB_LOCK:
    job['status'] = 'retry'
    job['next_attempt_at'] = _now() + max(1, _safe_int(reason.split(':', 1)[1], 1))
    job['updated_at'] = _now()
    job['last_error'] = reason
    _db_save()
   return
  _queue_finish(job, 'failed', reason)
  return
 queued_candidates = [account for account in _candidate_accounts(lot, order, rec) if _canonical_account_type(account.get('type')) in {'steam_sda', 'totp'} and bool((account.get('queue') or {}).get('enabled'))]
 if queued_candidates:
  queue_wait = min((_steam_queue_wait_seconds(account) for account in queued_candidates))
  if queue_wait > 0:
   with _DB_LOCK:
    job['status'] = 'retry'
    job['next_attempt_at'] = _now() + queue_wait
    job['updated_at'] = _now()
    job['last_error'] = 'Ожидание очереди кодов.'
    _db_save()
   _DENUVO_QUEUE_EVENT.set()
   return
 account, allocation_mode, server_data = _choose_account(lot, order, buyer_id, rec)
 if account is None:
  if allocation_mode == 'limit':
   _queue_finish(job, 'failed', 'limit')
   if _CARDINAL is not None:
    _deny(_CARDINAL, job.get('chat_id'), lot, 'limit')
   return
  _queue_retry_or_fail(job, allocation_mode, str(server_data.get('message') or ''))
  return
 reservation_id = str(server_data.get('reservation_id') or '')
 game_id = _denuvo_game_id(lot, [account])
 with _DB_LOCK:
  job['account_id'] = str(account.get('id'))
  job['reservation_id'] = reservation_id
  job['game_id'] = game_id
  job['allocation_mode'] = allocation_mode
  job['updated_at'] = _now()
  _db_save()
 code, provider_status = _get_account_code(account)
 if provider_status not in {'ok', 'allocation_only'}:
  if reservation_id:
   _server_release(reservation_id)
   _server_report(str(account.get('id')), game_id, False, provider_status)
  _queue_retry_or_fail(job, 'provider_error', provider_status)
  return
 prospective_left, total = _account_limit_values(account, rec, prospective=True)
 mapping = _delivery_mapping(lot, order, account, buyer_nick, code or '', prospective_left, total, allocation_mode)
 templates = _db_get()['global'].get('templates', {})
 account_type = _canonical_account_type(account.get('type') or lot.get('account_type'))
 template = str(account.get('template') or templates.get(account_type) or '{code}')
 delivery_text = _render(template, mapping)
 with _DB_LOCK:
  job['status'] = 'sending'
  job['updated_at'] = _now()
  _db_save()
 sent, send_error = _funpay_send(job.get('chat_id'), delivery_text)
 if not sent:
  if reservation_id:
   _server_release(reservation_id)
  with _DB_LOCK:
   job['reservation_id'] = ''
   job['account_id'] = ''
  _queue_retry_or_fail(job, 'NETWORK_ERROR', 'FunPay send: ' + send_error)
  return
 if _canonical_account_type(account.get('type')) in {'steam_sda', 'totp'}:
  account.setdefault('queue', {})['last_issue_at'] = _now()
 left, total = _commit_issue(lot, order, account, buyer_id, rec, server_data, activate_denuvo=True)
 with _DB_LOCK:
  job['status'] = 'lifecycle_retry' if reservation_id else 'done'
  job['phase'] = 'lifecycle'
  job['local_committed'] = True
  job['delivered_at'] = _now()
  job['updated_at'] = _now()
  job['next_attempt_at'] = _now()
  job['last_error'] = ''
  _db_save()
 _log('DENUVO', 'Создана новая Denuvo-активация для покупателя', order_id=order.get('order_id'), lot_id=lot.get('id'), account_id=account.get('id'), buyer=buyer_nick, allocation=allocation_mode, reservation_id=reservation_id)
 _notify('code_issued', f"✅ <b>Denuvo-активация выдана</b>\nПокупатель: <code>{escape(buyer_nick)}</code>\nЛот: <b>{escape(str(lot.get('title') or lot.get('funpay_lot_id')))}</b>\nАккаунт: <b>{escape(str(account.get('name')))}</b>\nЗанято уникальными покупателями: <b>{_safe_int((account.get('denuvo') or {}).get('active_slots'), 0)}/{_safe_int((account.get('denuvo') or {}).get('slot_limit'), 5)}</b>")
 if reservation_id:
  _queue_lifecycle(job, account)
 else:
  _queue_finish(job, 'done')

def _deduplicate_active_denuvo_jobs() -> int:
 if _db_locked():
  return 0
 groups: Dict[Tuple[str, str], List[dict]] = {}
 for job in _queue_jobs():
  if not bool(job.get('local_committed')):
   continue
  if str(job.get('status') or '') not in {'holding', 'lifecycle_retry', 'processing', 'sending'}:
   continue
  lot_id = str(job.get('lot_id') or '')
  buyer_id = str(job.get('buyer_id') or '')
  if not lot_id or not buyer_id:
   continue
  groups.setdefault((lot_id, buyer_id), []).append(job)
 released = 0
 for (lot_id, buyer_id), rows in groups.items():
  if len(rows) <= 1:
   continue
  rows.sort(key=lambda row: _safe_int(row.get('delivered_at'), _safe_int(row.get('created_at'), 0)))
  keep = rows[0]
  for duplicate in rows[1:]:
   reservation_id = str(duplicate.get('reservation_id') or '')
   ok, _, code = _server_release(reservation_id) if reservation_id else (True, {}, 'ok')
   if not ok:
    _log('WARNING', 'Не удалось освободить повторную Denuvo-активацию', lot_id=lot_id, buyer_id=buyer_id, reservation_id=reservation_id, error=code)
    continue
   account = _find_account(str(duplicate.get('account_id') or ''))
   with _DB_LOCK:
    if account is not None:
     denuvo = account.setdefault('denuvo', {})
     denuvo['active_slots'] = max(0, _safe_int(denuvo.get('active_slots'), 0) - 1)
    duplicate['status'] = 'cancelled'
    duplicate['phase'] = 'release'
    duplicate['updated_at'] = _now()
    duplicate['last_error'] = 'duplicate_activation_released'
    server = _server_cfg()
    server['active_reservations'] = max(0, _safe_int(server.get('active_reservations'), 0) - 1)
    _db_save()
   released += 1
   _log('DENUVO', 'Повторная Denuvo-активация автоматически освобождена', lot_id=lot_id, buyer_id=buyer_id, kept_reservation_id=keep.get('reservation_id'), released_reservation_id=reservation_id)
 if released:
  _sync_denuvo_lot_capacity(_CARDINAL)
 return released

def _denuvo_worker_loop() -> None:
 last_maintenance = 0
 while not _DENUVO_STOP_EVENT.is_set():
  try:
   if not _db_locked():
    now = _now()
    server = _server_cfg()
    interval = _safe_int(server.get('status_sync_interval'), 300, 30, 3600)
    if now - last_maintenance >= interval:
     last_maintenance = now
     if str(server.get('url') or '').strip() and str(server.get('license_key') or '').strip():
      _server_verify()
      _server_sync_status()
      _deduplicate_active_denuvo_jobs()
     _queue_prune()
    for _ in range(20):
     job_id = _queue_claim()
     if not job_id:
      break
     _process_denuvo_job(job_id)
  except Exception as e:
   logger.exception('%s Denuvo worker failed: %s', PREFIX, e)
  _DENUVO_QUEUE_EVENT.wait(2.0)
  _DENUVO_QUEUE_EVENT.clear()

def _start_denuvo_worker() -> None:
 global _DENUVO_WORKER
 if _DENUVO_WORKER is not None and _DENUVO_WORKER.is_alive():
  return
 _DENUVO_STOP_EVENT.clear()
 _queue_recover_stale()
 _DENUVO_WORKER = threading.Thread(target=_denuvo_worker_loop, name='AutoOffline-DenuvoQueue', daemon=True)
 _DENUVO_WORKER.start()
 _DENUVO_QUEUE_EVENT.set()

def _stop_workers(*_args: Any, **_kwargs: Any) -> None:
 _DENUVO_STOP_EVENT.set()
 _DENUVO_QUEUE_EVENT.set()
 _STEAM_QUEUE_STOP_EVENT.set()
 _STEAM_QUEUE_EVENT.set()

def _enqueue_denuvo_request(cardinal: 'Cardinal', chat_id: Any, lot: dict, order: dict, buyer_id: str, buyer_nick: str) -> bool:
 try:
  job, created, position = _queue_enqueue(lot, order, chat_id, buyer_id, buyer_nick)
 except Exception as e:
  _deny(cardinal, chat_id, lot, 'queue_error')
  _log('ERROR', 'Не удалось добавить Denuvo в очередь', error=str(e), order_id=order.get('order_id'))
  return True
 if created:
  _log('DENUVO', 'Запрос принят в очередь', order_id=order.get('order_id'), lot_id=lot.get('id'), buyer=buyer_nick, position=position or 1)
 else:
  _log('DENUVO', 'Повторный запрос уже находится в очереди', order_id=order.get('order_id'), lot_id=lot.get('id'), buyer=buyer_nick, position=position or 1)
 _db_save()
 return True

def _process_code_request(cardinal: 'Cardinal', event: Any, lot: dict) -> bool:
 chat_id = _event_chat_id(event)
 buyer_id, buyer_nick = _extract_buyer(event)
 _notify('command_request', f"💬 <b>Запрос команды</b>\nПокупатель: <code>{escape(buyer_nick)}</code>\nЛот: <b>{escape(str(lot.get('title') or lot.get('funpay_lot_id')))}</b>\nКоманда: <code>{escape(str(lot.get('command')))}</code>")
 if not bool(lot.get('enabled', True)):
  _deny(cardinal, chat_id, lot, 'lot_disabled')
  return True
 order = _matching_order(lot, chat_id, buyer_id, buyer_nick)
 if order is None:
  _deny(cardinal, chat_id, lot, 'no_order')
  _log('DENIED', 'Нет подходящего заказа', lot_id=lot.get('id'), buyer=buyer_nick, chat_id=chat_id)
  return True
 ok, reason, rec, used, total = _check_usage(lot, order, buyer_id)
 if not ok:
  _deny(cardinal, chat_id, lot, reason, {'left': max(0, total - used), 'total': total})
  _log('DENIED', 'Лимит или cooldown', reason=reason, order_id=order.get('order_id'), buyer=buyer_nick)
  return True
 if _is_denuvo_lot(lot):
  reusable_job = _find_reusable_denuvo_job(lot, order, buyer_id)
  if reusable_job is not None:
   return _reuse_denuvo_activation(cardinal, chat_id, lot, order, buyer_id, buyer_nick, reusable_job)
  return _enqueue_denuvo_request(cardinal, chat_id, lot, order, buyer_id, buyer_nick)
 if _canonical_account_type(lot.get('account_type')) in {'steam_sda', 'totp'} and _steam_queue_accounts(lot):
  return _enqueue_steam_request(cardinal, chat_id, lot, order, buyer_id, buyer_nick)
 account, allocation_mode, server_data = _choose_account(lot, order, buyer_id, rec)
 if account is None:
  _deny(cardinal, chat_id, lot, allocation_mode)
  _log('ERROR', 'Не найден доступный аккаунт', reason=allocation_mode, lot_id=lot.get('id'), order_id=order.get('order_id'))
  return True
 code, provider_status = _get_account_code(account)
 if provider_status not in {'ok', 'allocation_only'}:
  _deny(cardinal, chat_id, lot, 'provider_error')
  _log('ERROR', 'Провайдер кода вернул ошибку', account_id=account.get('id'), status=provider_status)
  _notify('request_denied', f"⚠️ <b>Ошибка получения кода</b>\nАккаунт: <b>{escape(str(account.get('name')))}</b>\nПричина: <code>{escape(provider_status)}</code>")
  return True
 prospective_left, total = _account_limit_values(account, rec, prospective=True)
 mapping = _delivery_mapping(lot, order, account, buyer_nick, code or '', prospective_left, total, allocation_mode)
 account_type = _canonical_account_type(account.get('type') or lot.get('account_type'))
 templates = _db_get()['global'].get('templates', {})
 template = str(account.get('template') or templates.get(account_type) or '{code}')
 sent, send_error = _funpay_send(chat_id, _render(template, mapping))
 if not sent:
  _log('ERROR', 'Не удалось отправить код покупателю', error=send_error, order_id=order.get('order_id'))
  return True
 left, total = _commit_issue(lot, order, account, buyer_id, rec, server_data)
 _log('ISSUED', 'Код/аккаунт выдан', order_id=order.get('order_id'), lot_id=lot.get('id'), account_id=account.get('id'), buyer=buyer_nick, code=code or '', left=left, total=total, allocation=allocation_mode)
 _notify('code_issued', f"✅ <b>Код успешно выдан</b>\nПокупатель: <code>{escape(buyer_nick)}</code>\nЛот: <b>{escape(str(lot.get('title') or lot.get('funpay_lot_id')))}</b>\nАккаунт: <b>{escape(str(account.get('name')))}</b>\nОсталось запросов: <b>{left}/{total}</b>")
 return True

def _locked_text() -> str:
 status, mode = _database_status()
 return f'🔐 <b>Хранилище AutoOffline недоступно</b>\n\nСостояние: <b>{escape(status)}</b>\nРежим: <code>{escape(mode)}</code>\n\nБаза в этой версии открывается локальным ключом автоматически. Если сейчас она недоступна, значит повреждён файл базы или ключ. Проверьте хранилище либо восстановите бэкап.'

def _home_text() -> str:
 return f'🧩 <b>{NAME}</b>\n📦 Версия: <code>{VERSION}</code>\n👤 Автор: <a href="{CREATOR_URL}">{escape(CREDITS)}</a>\n\nВыберите раздел:'

def _home_kb() -> K:
 kb = K()
 kb.row(B('⚙️ Настройки', callback_data=CB_SETTINGS), B('ℹ️ Информация', callback_data=CB_INFO))
 kb.row(B('♻️ Обновить', callback_data=CB_UPDATE), B('🗑 Удалить', callback_data=CB_DELETE_PLUGIN))
 kb.row(B('🔙 К списку плагинов', callback_data=CBT_PLUGINS_LIST_OPEN))
 return kb

def _settings_text() -> str:
 if _db_locked():
  _ensure_database_available()
 if _db_locked():
  return _locked_text()
 db = _db_get()
 enabled_accounts = sum((1 for x in db.get('accounts', []) if x.get('enabled', True)))
 enabled_lots = sum((1 for x in db.get('lots', []) if x.get('enabled', True)))
 smak = 'настроен' if str((db.get('global') or {}).get('smakmail_api_key') or '').strip() else 'не настроен'
 return f"<b>⚙️ Панель настроек AutoOffline</b>\n\n• Аккаунты: <b>{enabled_accounts}/{len(db.get('accounts', []))}</b>\n• Лоты: <b>{enabled_lots}/{len(db.get('lots', []))}</b>\n• Заказы в базе: <b>{len(db.get('orders', []))}</b>\n• SmakMail API: <b>{smak}</b>\n\nВыберите категорию:"

def _settings_kb() -> K:
 kb = K()
 if _db_locked():
  kb.row(B('◀️ Назад', callback_data=CB_HOME))
  return kb
 db = _db_get()
 kb.row(B('🧩 Состояние', callback_data=CB_STATE))
 kb.row(B(f"🎮 Аккаунты · {len(db.get('accounts', []))}", callback_data=CB_ACCOUNTS))
 kb.row(B(f"🛒 Настройка лотов · {len(db.get('lots', []))}", callback_data=CB_LOTS))
 kb.row(B('🎮 Denuvo', callback_data=CB_DENUVO_CENTER))
 kb.row(B('📮 SmakMail API', callback_data=CB_SMAKMAIL_KEY))
 kb.row(B('🔔 Уведомления', callback_data=CB_NOTIFICATIONS))
 kb.row(B('📊 Аналитика', callback_data=CB_ANALYTICS))
 kb.row(B('🛠 Обслуживание', callback_data=CB_MAINTENANCE))
 kb.row(B('◀️ Назад', callback_data=CB_HOME))
 return kb

def _info_text() -> str:
 return '<b>Ссылки:</b>\n• <b>Чат</b> — помощь, вопросы и обсуждение работы плагина.\n• <b>Канал</b> — новости, версии и объявления.\n• <b>Инструкция</b> — установка и настройка AutoOffline.\n• <b>Разработчик</b> — личный контакт создателя плагина.'

def _info_kb() -> K:
 kb = K()
 kb.row(B('💬 Чат', url=GROUP_URL), B('📢 Канал', url=CHANNEL_URL))
 kb.row(B('📖 Инструкция', url=INSTRUCTION_URL))
 kb.row(B('👤 Разработчик', url=CREATOR_URL))
 kb.row(B('◀️ Назад', callback_data=CB_HOME))
 return kb

def _accounts_text() -> str:
 if _db_locked():
  return _locked_text()
 accounts = _db_get().get('accounts', [])
 lines = ['<b>🎮 Аккаунты</b>', '']
 if not accounts:
  lines.append('Аккаунтов пока нет. Добавьте первый, иначе плагину придётся выдавать философские советы вместо кодов.')
 for index, account in enumerate(accounts, 1):
  state = '🟢' if account.get('enabled', True) else '🔴'
  lines.append(f"{index}. {state} <b>{escape(str(account.get('name')))}</b> — {escape(ACCOUNT_TYPES.get(str(account.get('type')), str(account.get('type'))))} — <code>{escape(str(account.get('id')))}</code>")
 return '\n'.join(lines)

def _accounts_kb() -> K:
 kb = K()
 if not _db_locked():
  for account in _db_get().get('accounts', [])[:30]:
   kb.row(B(f"{('🟢' if account.get('enabled', True) else '🔴')} {str(account.get('name'))[:28]}", callback_data=f"{CB_ACCOUNT_OPEN}:{account['id']}"))
  kb.row(B('➕ Добавить аккаунт', callback_data=CB_ACCOUNT_ADD))
 kb.row(B('◀️ Назад', callback_data=CB_SETTINGS))
 return kb

def _account_text(account: dict) -> str:
 mode = _account_limit_mode(account)
 queue_cfg = account.get('queue') or {}
 denuvo = account.get('denuvo') or {}
 account_type = _canonical_account_type(account.get('type'))
 extra = ''
 if account_type in {'steam_sda', 'totp'}:
  interval = TOTP_QUEUE_INTERVAL_SECONDS if account_type == 'totp' else STEAM_QUEUE_INTERVAL_SECONDS
  queue_name = 'TOTP' if account_type == 'totp' else 'Steam Guard'
  queue_text = f'ВКЛ · {interval} секунд' if queue_cfg.get('enabled') else 'ВЫКЛ'
  extra += f'\n• Очередь {queue_name}: <b>{queue_text}</b>'
 if account_type == 'steam_email':
  mail_data = account.get('data') or {}
  mail_addr = str(mail_data.get('email') or '—')
  provider = str(mail_data.get('provider') or 'imap').casefold()
  detail = 'SmakMail API' if provider == 'smakmail' else str(mail_data.get('imap_host') or 'авто')
  extra += f"\n• Почта: <code>{escape(mail_addr)}</code>\n• Провайдер: <code>{escape(('SmakMail' if provider == 'smakmail' else 'IMAP'))}</code>\n• Подключение: <code>{escape(detail)}</code>"
 if account_type == 'steam_sda':
  game = str(denuvo.get('game_id') or '—')
  extra += f"\n• Denuvo: <b>{('ВКЛ' if denuvo.get('enabled') else 'ВЫКЛ')}</b> · игра <b>{escape(game)}</b>"
 if denuvo.get('enabled') or account_type == 'denuvo':
  extra += f"\n• Denuvo-слоты: <b>{denuvo.get('active_slots', 0)}/{denuvo.get('slot_limit', 5)}</b>"
 if mode == 'time':
  duration = _safe_int(account.get('limit_time_seconds'), 0)
  limit_line = f'по времени · {_fmt_duration(duration)}' if duration > 0 else 'по времени · без ограничения'
  reset_line = 'не используется'
 else:
  limit = '∞' if account.get('limit_total') in (None, '', 0) else str(account.get('limit_total'))
  reset_seconds = _safe_int(account.get('limit_reset_seconds'), 0)
  limit_line = f'по количеству · {limit}'
  if account.get('limit_total') in (None, '', 0):
   reset_line = '—'
  elif reset_seconds > 0:
   reset_line = _fmt_duration(reset_seconds)
  else:
   reset_line = 'не сбрасывается'
 credential_label = 'Почта: настроена' if account_type == 'steam_email' else f"Secret: <code>{escape(_mask(str(account.get('secret') or '')))}</code>"
 return f"<b>🎮 {escape(str(account.get('name')))}</b>\n\n• ID: <code>{escape(str(account.get('id')))}</code>\n• Тип: <b>{escape(ACCOUNT_TYPES.get(account_type, account_type))}</b>\n• Состояние: <b>{('ВКЛ' if account.get('enabled', True) else 'ВЫКЛ')}</b>\n• {credential_label}\n• Лимит кодов: <b>{escape(limit_line)}</b>\n• Сброс лимита: <b>{escape(reset_line)}</b>\n• Выдано: <b>{_safe_int(account.get('issued'), 0)}</b>\n• Свой текст выдачи: <b>{('да' if str(account.get('template') or '').strip() else 'нет')}</b>{extra}"

def _account_kb(account: dict) -> K:
 aid = account['id']
 account_type = _canonical_account_type(account.get('type'))
 kb = K()
 kb.row(B(f"{('🔴 Выключить выдачу' if account.get('enabled', True) else '🟢 Включить выдачу')}", callback_data=f'{CB_ACCOUNT_TOGGLE}:{aid}'))
 kb.row(B('✏️ Изменить название', callback_data=f'{CB_ACCOUNT_NAME}:{aid}'))
 kb.row(B('📧 Заменить почту' if account_type == 'steam_email' else '🔐 Заменить secret', callback_data=f'{CB_ACCOUNT_SECRET}:{aid}'))
 kb.row(B('📛 Лимиты кодов', callback_data=f'{CB_ACCOUNT_LIMITS}:{aid}'))
 if account_type in {'steam_sda', 'totp'}:
  queue_enabled = bool((account.get('queue') or {}).get('enabled'))
  kb.row(B(f"⏳ Очередь · {('ВКЛ' if queue_enabled else 'ВЫКЛ')}", callback_data=f'{CB_ACCOUNT_QUEUE}:{aid}'))
 if account_type == 'steam_sda':
  kb.row(B('🎮 Настройки Denuvo', callback_data=f'{CB_ACCOUNT_DENUVO}:{aid}'))
 kb.row(B('💬 Текст выдачи', callback_data=f'{CB_ACCOUNT_TEMPLATE}:{aid}'))
 kb.row(B('🗑 Удалить', callback_data=f'{CB_ACCOUNT_DELETE}:{aid}'))
 kb.row(B('◀️ К аккаунтам', callback_data=CB_ACCOUNTS))
 return kb

def _lot_funpay_active(lot: dict) -> Optional[bool]:
 value = lot.get('funpay_active')
 return value if isinstance(value, bool) else None

def _lot_funpay_state_text(lot: dict) -> str:
 value = _lot_funpay_active(lot)
 if value is True:
  return 'ВКЛ'
 if value is False:
  return 'ВЫКЛ'
 return 'НЕ ПРОВЕРЕНО'

def _lot_state_icons(lot: dict) -> str:
 plugin_on = bool(lot.get('enabled', True))
 funpay_on = _lot_funpay_active(lot)
 if plugin_on and funpay_on is True:
  return '🟢'
 if not plugin_on and funpay_on is False:
  return '🔴'
 return '🟡'

def _lots_text() -> str:
 if _db_locked():
  return _locked_text()
 db = _db_get()
 lots = db.get('lots', [])
 accounts = db.get('accounts', [])
 lines = ['<b>🛒 Настройка лотов</b>', '']
 if not accounts:
  lines.append('Сначала создайте хотя бы один аккаунт. Лот только связывает LOT ID, команду и аккаунт.')
 elif not lots:
  lines.append('Лоты ещё не добавлены. Лимиты, очередь, сообщение и Denuvo настраиваются в карточке аккаунта и наследуются лотом.')
 for index, lot in enumerate(lots, 1):
  denuvo = ' · Denuvo' if _is_denuvo_lot(lot) else ''
  lines.append(f"{index}. {_lot_state_icons(lot)} <b>{escape(str(lot.get('title') or lot.get('funpay_lot_id')))}</b> · LOT <code>{escape(str(lot.get('funpay_lot_id')))}</code> · <code>{escape(str(lot.get('command')))}</code>{denuvo}")
 return '\n'.join(lines)

def _lots_kb() -> K:
 kb = K()
 if not _db_locked():
  db = _db_get()
  for lot in db.get('lots', [])[:30]:
   kb.row(B(f"{_lot_state_icons(lot)} {str(lot.get('title') or lot.get('funpay_lot_id'))[:24]}", callback_data=f"{CB_LOT_OPEN}:{lot['id']}"))
  if db.get('accounts'):
   kb.row(B('➕ Добавить лот', callback_data=CB_LOT_ADD))
  else:
   kb.row(B('➕ Сначала создать аккаунт', callback_data=CB_ACCOUNT_ADD))
 kb.row(B('◀️ Назад', callback_data=CB_SETTINGS))
 return kb

def _lot_text(lot: dict) -> str:
 bound = _lot_bound_accounts(lot, enabled_only=False)
 sync_info = lot.get('funpay_sync') if isinstance(lot.get('funpay_sync'), dict) else {}
 if not sync_info:
  sync_text = 'не проверялось'
 elif bool(sync_info.get('ok')):
  sync_text = str(sync_info.get('reason') or 'успешно')[:90]
 else:
  sync_text = 'ошибка: ' + str(sync_info.get('reason') or 'неизвестно')[:90]
 inherited = []
 for account in bound:
  account_type = str(account.get('type') or '')
  limit = '∞' if account.get('limit_total') in (None, '', 0) else str(account.get('limit_total'))
  queue = ''
  if account_type in {'steam_sda', 'totp'}:
   queue = f" · очередь {('ВКЛ' if (account.get('queue') or {}).get('enabled') else 'ВЫКЛ')}"
  inherited.append(f"• <b>{escape(str(account.get('name')))}</b> · лимит {escape(limit)}{queue}")
 inherited_text = '\n'.join(inherited) if inherited else '• подходящий аккаунт не привязан'
 return f"<b>🛒 {escape(str(lot.get('title') or lot.get('funpay_lot_id')))}</b>\n\n• LOT ID: <code>{escape(str(lot.get('funpay_lot_id')))}</code>\n• Внутренний ID: <code>{escape(str(lot.get('id')))}</code>\n• Тип: <b>{escape(ACCOUNT_TYPES.get(str(lot.get('account_type')), str(lot.get('account_type'))))}</b>\n• Команда: <code>{escape(str(lot.get('command')))}</code>\n• В плагине: <b>{('ВКЛ' if lot.get('enabled', True) else 'ВЫКЛ')}</b>\n• На FunPay: <b>{_lot_funpay_state_text(lot)}</b>\n• Последняя проверка FunPay: <b>{escape(sync_text)}</b>\n• Привязанный аккаунт: <b>{('1' if bound else '0')}</b>\n• Denuvo: <b>{('ВКЛ через аккаунт' if _is_denuvo_lot(lot) else 'ВЫКЛ')}</b>\n\n<b>Настройки аккаунта:</b>\n{inherited_text}"

def _lot_kb(lot: dict) -> K:
 lid = lot['id']
 plugin_on = bool(lot.get('enabled', True))
 funpay_on = _lot_funpay_active(lot)
 kb = K()
 kb.row(B('🔴 Выключить в плагине' if plugin_on else '🟢 Включить в плагине', callback_data=f'{CB_LOT_TOGGLE}:{lid}'))
 if funpay_on is True:
  funpay_label = '🔴 Выключить на FunPay'
 elif funpay_on is False:
  funpay_label = '🟢 Включить на FunPay'
 else:
  funpay_label = '🌐 Проверить и переключить FunPay'
 kb.row(B(funpay_label, callback_data=f'{CB_LOT_FUNPAY_TOGGLE}:{lid}'))
 kb.row(B('🎮 Привязка аккаунта', callback_data=f'{CB_LOT_ACCOUNTS}:{lid}'))
 kb.row(B('🗑 Удалить', callback_data=f'{CB_LOT_DELETE}:{lid}'))
 kb.row(B('◀️ К лотам', callback_data=CB_LOTS))
 return kb

def _denuvo_center_text() -> str:
 if _db_locked():
  return _locked_text()
 db = _db_get()
 server = db['global'].get('server', {})
 jobs = db.get('denuvo_queue', [])
 counts: Dict[str, int] = {}
 for job in jobs:
  status = str(job.get('status') or 'unknown')
  counts[status] = counts.get(status, 0) + 1
 queue_count = sum((counts.get(state, 0) for state in DENUVO_ACTIVE_QUEUE_STATES))
 completed = counts.get('done', 0)
 errors = counts.get('failed', 0) + counts.get('manual_review', 0)
 active_reservations = _safe_int(server.get('active_reservations'), 0)
 configured = bool(str(server.get('url') or '').strip() and str(server.get('license_key') or '').strip())
 registered = bool(str(server.get('installation_secret') or '').strip())
 last_code = str(server.get('last_verify_code') or 'NOT_CONFIGURED').upper()
 bad_codes = {'NOT_CONFIGURED', 'NETWORK_ERROR', 'TIMEOUT', 'SERVER_UNAVAILABLE', 'INSTALLATION_DISABLED_OR_UNKNOWN', 'LICENSE_DISABLED', 'LICENSE_EXPIRED', 'BUILD_NOT_ALLOWED', 'BUILD_HASH_MISMATCH', 'MACHINE_HASH_MISMATCH'}
 api_working = configured and registered and (last_code not in bad_codes) and (not last_code.startswith('HTTP_'))
 return f"<b>🎮 Denuvo</b>\n\n• API: <b>{('работает' if api_working else 'не работает')}</b>\n\n• В очереди: <b>{queue_count}</b>\n• Активные резервации API: <b>{active_reservations}</b>\n• Завершено: <b>{completed}</b>\n• Ошибки / требуют проверки: <b>{errors}</b>"

def _denuvo_center_kb() -> K:
 kb = K()
 kb.row(B('🔄 Обновить статус', callback_data=CB_DENUVO_REFRESH))
 kb.row(B('🔄 Синхронизировать слоты', callback_data=CB_DENUVO_SYNC))
 kb.row(B('♻️ Повторить ошибки', callback_data=CB_DENUVO_RETRY))
 kb.row(B('🧹 Очистить завершённые', callback_data=CB_DENUVO_CLEAR))
 kb.row(B('◀️ Назад', callback_data=CB_SETTINGS))
 return kb

def _denuvo_refresh_action(cardinal: 'Cardinal', call) -> None:
 bot = cardinal.telegram.bot
 ok, data, code = _server_verify()
 if ok:
  sync_ok, sync_data, sync_code = _server_sync_status()
  if not sync_ok:
   ok, data, code = (sync_ok, sync_data, sync_code)
 _safe_edit(bot, call.message.chat.id, call.message.id, _denuvo_center_text(), _denuvo_center_kb())
 _answer(bot, call, 'Статус и активации обновлены.' if ok else 'Ошибка API: ' + str(code), not ok)
 _DENUVO_QUEUE_EVENT.set()

def _denuvo_sync_action(cardinal: 'Cardinal', call) -> None:
 ok, data, code = _server_sync_status()
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, _denuvo_center_text(), _denuvo_center_kb())
 _answer(cardinal.telegram.bot, call, f"Резерваций: {len(data.get('reservations', []))}" if ok else 'Ошибка: ' + str(code), not ok)

def _denuvo_retry_action(cardinal: 'Cardinal', call) -> None:
 changed = 0
 with _DB_LOCK:
  for job in _queue_jobs():
   if str(job.get('status')) in {'failed', 'manual_review'} and (not bool(job.get('local_committed'))):
    job['status'] = 'retry'
    job['attempts'] = 0
    job['next_attempt_at'] = _now()
    job['updated_at'] = _now()
    changed += 1
  if changed:
   _db_save()
 _DENUVO_QUEUE_EVENT.set()
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, _denuvo_center_text(), _denuvo_center_kb())
 _answer(cardinal.telegram.bot, call, f'Повторно поставлено: {changed}')

def _denuvo_clear_action(cardinal: 'Cardinal', call) -> None:
 with _DB_LOCK:
  before = len(_queue_jobs())
  _db_get()['denuvo_queue'] = [x for x in _queue_jobs() if str(x.get('status')) not in {'done', 'cancelled'}]
  removed = before - len(_db_get()['denuvo_queue'])
  _db_save()
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, _denuvo_center_text(), _denuvo_center_kb())
 _answer(cardinal.telegram.bot, call, f'Удалено завершённых: {removed}')

def _notifications_text() -> str:
 if _db_locked():
  return _locked_text()
 lines = ['<b>🔔 Уведомления</b>', '', 'Нажмите кнопку, чтобы включить или выключить тип уведомлений.', '']
 for key, label in NOTIFICATION_LABELS.items():
  state = '🟢' if _notification_state(key) else '🔴'
  lines.append(f'{state} <b>{escape(label)}</b>')
 return '\n'.join(lines)

def _notifications_kb() -> K:
 kb = K()
 if not _db_locked():
  for key, label in NOTIFICATION_LABELS.items():
   kb.row(B(f"{('✅' if _notification_state(key) else '❌')} {label}", callback_data=f'{CB_NOTIFY_TOGGLE}:{key}'))
 kb.row(B('◀️ Назад', callback_data=CB_SETTINGS))
 return kb

def _analytics_text() -> str:
 if _db_locked():
  return _locked_text()
 db = _db_get()
 stats = db.get('stats', {})
 by_type: Dict[str, int] = {}
 for account in db.get('accounts', []):
  canonical_type = _canonical_account_type(account.get('type'))
  by_type[canonical_type] = by_type.get(canonical_type, 0) + _safe_int(account.get('issued'), 0)
 lines = ['<b>📊 Аналитика</b>', '', f"• Заказов: <b>{stats.get('orders', 0)}</b>", f"• Успешных выдач: <b>{stats.get('issued', 0)}</b>", f"• Отказов: <b>{stats.get('denied', 0)}</b>", f"• Запросов к серверу: <b>{stats.get('server_requests', 0)}</b>", f"• Ошибок сервера: <b>{stats.get('server_errors', 0)}</b>", f"• Denuvo поставлено в очередь: <b>{stats.get('queue_enqueued', 0)}</b>", f"• Denuvo завершено: <b>{stats.get('queue_completed', 0)}</b>", f"• Denuvo ошибок: <b>{stats.get('queue_failed', 0)}</b>", '', '<b>Выдачи по типам:</b>']
 if not by_type:
  lines.append('—')
 for key, value in sorted(by_type.items()):
  lines.append(f'• {escape(ACCOUNT_TYPES.get(key, key))}: <b>{value}</b>')
 return '\n'.join(lines)

def _analytics_kb() -> K:
 kb = K()
 kb.row(B('◀️ Назад', callback_data=CB_SETTINGS))
 return kb

def _maintenance_text() -> str:
 status, mode = _database_status()
 size = os.path.getsize(DB_FILE) if os.path.isfile(DB_FILE) else 0
 return f'<b>🛠 Обслуживание</b>\n\n• База: <b>{escape(status)}</b>\n• Режим: <code>{escape(mode)}</code>\n• Размер encrypted JSON: <b>{size} байт</b>'

def _maintenance_kb() -> K:
 kb = K()
 kb.row(B('📄 log.txt + 🎨 лицензии', callback_data=CB_LOGS))
 kb.row(B('📤 Скачать бэкап', callback_data=CB_BACKUP))
 kb.row(B('📥 Импортировать бэкап', callback_data=CB_IMPORT))
 kb.row(B('🩺 Проверить базу', callback_data=CB_DB_CHECK))
 kb.row(B('♻️ Сбросить usage', callback_data=CB_RESET_USAGE))
 kb.row(B('◀️ Назад', callback_data=CB_SETTINGS if not _db_locked() else CB_HOME))
 return kb

def _security_text() -> str:
 status, mode = _database_status()
 return f'<b>🗃 Хранение данных</b>\n\n• Состояние базы: <b>{escape(status)}</b>\n• Режим: <code>{escape(mode)}</code>\n• Шифрование: <code>Fernet + локальный ключ</code>\n• Размер encrypted JSON: <b>{(os.path.getsize(DB_FILE) if os.path.isfile(DB_FILE) else 0)} байт</b>\n\n<b>Как хранится база</b>\n• все данные плагина лежат локально в encrypted JSON.\n• локальный ключ хранится отдельным файлом.\n• чувствительные поля не уходят на Denuvo-сервер.\n• для переноса используйте бэкап/импорт из обслуживания.\n\nMaster-password в этой версии убран, чтобы не плодить лишние сценарии блокировки и потери доступа.'

def _security_kb() -> K:
 kb = K()
 kb.row(B('◀️ Назад', callback_data=CB_SETTINGS if not _db_locked() else CB_HOME))
 return kb

def _state_text() -> str:
 if _db_locked():
  return _locked_text()
 db = _db_get()
 accounts = db.get('accounts', [])
 lots = db.get('lots', [])
 enabled_accounts = sum((1 for x in accounts if x.get('enabled', True)))
 plugin_lots = sum((1 for x in lots if x.get('enabled', True)))
 funpay_lots = sum((1 for x in lots if _lot_funpay_active(x) is True))
 funpay_known = sum((1 for x in lots if _lot_funpay_active(x) is not None))
 return f"<b>🧩 Состояние</b>\n\n• Плагин: <b>{('ВКЛ' if db['global'].get('plugin_enabled', True) else 'ВЫКЛ')}</b>\n• Аккаунты в плагине: <b>{enabled_accounts}/{len(accounts)}</b>\n• Лоты в плагине: <b>{plugin_lots}/{len(lots)}</b>\n• Лоты на FunPay: <b>{funpay_lots}/{len(lots)}</b>{(' · проверено ' + str(funpay_known) if funpay_known < len(lots) else '')}\n\nСостояния лотов в плагине и на FunPay переключаются отдельно."

def _state_kb() -> K:
 kb = K()
 if not _db_locked():
  db = _db_get()
  accounts = db.get('accounts', [])
  lots = db.get('lots', [])
  enabled_accounts = sum((1 for x in accounts if x.get('enabled', True)))
  plugin_lots = sum((1 for x in lots if x.get('enabled', True)))
  funpay_lots = sum((1 for x in lots if _lot_funpay_active(x) is True))
  kb.row(B(f"🧩 Плагин · {('ВКЛ' if db['global'].get('plugin_enabled', True) else 'ВЫКЛ')}", callback_data=CB_STATE_PLUGIN))
  kb.row(B(f'🎮 Все аккаунты · {enabled_accounts}/{len(accounts)}', callback_data=CB_STATE_ACCOUNTS))
  kb.row(B(f'🛒 Лоты в плагине · {plugin_lots}/{len(lots)}', callback_data=CB_STATE_LOTS))
  kb.row(B(f'🌐 Лоты на FunPay · {funpay_lots}/{len(lots)}', callback_data=CB_STATE_LOTS_FUNPAY))
 kb.row(B('◀️ Назад', callback_data=CB_SETTINGS))
 return kb

def _update_text() -> str:
 return f'⬆️ <b>Обновление {NAME}</b>\n\nТекущая версия: <code>{escape(VERSION)}</code>\n\n• <b>Обновить локально</b> — отправить новый файл плагина <code>.py</code>.\n• <b>Обновить онлайн</b> — скачать и проверить новую версию по настроенной ссылке.\n\nПеред заменой создаётся резервная копия текущего файла. Аккаунты, лоты, заказы и настройки не удаляются.'

def _update_kb() -> K:
 kb = K()
 kb.row(B('📥 Обновить локально', callback_data=CB_UPDATE_LOCAL))
 kb.row(B('🌐 Обновить онлайн', callback_data=CB_UPDATE_ONLINE))
 kb.row(B('◀️ Назад', callback_data=CB_HOME))
 return kb

def _delete_plugin_text() -> str:
 return f'<b>🗑 Удаление плагина</b>\n\nВы точно хотите удалить <b>{escape(NAME)}</b>?\n\nСначала будет вызван штатный менеджер плагинов Cardinal. Если он недоступен, AutoOffline удалит только текущий .py-файл. База, log.txt и бэкапы останутся в storage/plugins/AutoOffline.'

def _delete_plugin_kb() -> K:
 kb = K()
 kb.row(B('🗑 Да, удалить', callback_data=CB_DELETE_PLUGIN_YES), B('❌ Отмена', callback_data=CB_DELETE_PLUGIN_NO))
 return kb

def _open_panel(cardinal: 'Cardinal', target: Any, text: str, kb: K) -> None:
 _start_auto_registration()
 bot = cardinal.telegram.bot
 if hasattr(target, 'message') and getattr(target, 'message', None) is not None:
  _register_admin(target.message.chat.id)
  _answer(bot, target)
  if not _safe_edit(bot, target.message.chat.id, target.message.id, text, kb):
   _safe_send_tg(bot, target.message.chat.id, text, kb)
 else:
  _register_admin(target.chat.id)
  _safe_send_tg(bot, target.chat.id, text, kb)

def _fsm_start(chat_id: int, mode: str, step: str, panel_msg_id: int, **data: Any) -> None:
 with _FSM_LOCK:
  _fsm[chat_id] = {'mode': mode, 'step': step, 'panel_msg_id': panel_msg_id, 'data': data, 'sensitive_messages': []}

def _fsm_prompt(bot, chat_id: int, text: str, back: str=CB_SETTINGS) -> None:
 msg = _safe_send_tg(bot, chat_id, text, _cancel_kb(back))
 if msg is not None and chat_id in _fsm:
  _fsm[chat_id].setdefault('prompt_messages', []).append(getattr(msg, 'message_id', None))

def _fsm_cleanup(bot, chat_id: int, state: Optional[dict]=None) -> None:
 state = state or _fsm.get(chat_id) or {}
 for mid in state.get('sensitive_messages', []) + state.get('prompt_messages', []):
  _delete_message(bot, chat_id, mid)

def _parse_mafile_bytes(raw: bytes) -> Tuple[str, str]:
 try:
  payload = json.loads(raw.decode('utf-8-sig'))
 except Exception as e:
  raise ValueError('Некорректный .maFile JSON.') from e
 secret = str(payload.get('shared_secret') or '').strip()
 name = str(payload.get('account_name') or payload.get('accountName') or payload.get('SteamID') or 'Steam account').strip()
 if not secret or not generate_steam_guard_code(secret):
  raise ValueError('В .maFile не найден валидный shared_secret.')
 return (secret, name)

def _download_document(bot, message: Message, max_size: int=MAX_BACKUP_SIZE) -> Tuple[str, bytes]:
 document = getattr(message, 'document', None)
 if document is None:
  raise ValueError('Документ не найден.')
 size = _safe_int(getattr(document, 'file_size', 0), 0)
 if size > max_size:
  raise ValueError('Файл слишком большой.')
 info = bot.get_file(document.file_id)
 raw = bot.download_file(info.file_path)
 if len(raw) > max_size:
  raise ValueError('Файл слишком большой.')
 return (str(getattr(document, 'file_name', None) or 'file'), bytes(raw))

def _start_add_account(cardinal: 'Cardinal', call) -> None:
 bot = cardinal.telegram.bot
 if _db_locked():
  _answer(bot, call, 'Сначала разблокируйте базу.', True)
  return
 chat_id = call.message.chat.id
 _fsm_start(chat_id, 'add_account', 'type', call.message.id)
 kb = K()
 for key in ACCOUNT_CREATION_TYPES:
  kb.row(B(ACCOUNT_TYPES[key], callback_data=f'{CB_TYPE}:acc:{key}'))
 kb.row(B('❌ Отменить', callback_data=CB_CANCEL))
 _safe_edit(bot, chat_id, call.message.id, '➕ <b>Добавление аккаунта</b>\n\nШаг 1: выберите тип аккаунта.', kb)
 _answer(bot, call)

def _start_add_lot(cardinal: 'Cardinal', call) -> None:
 bot = cardinal.telegram.bot
 if _db_locked():
  _answer(bot, call, 'База недоступна.', True)
  return
 if not _db_get().get('accounts'):
  kb = K()
  kb.row(B('➕ Создать аккаунт', callback_data=CB_ACCOUNT_ADD))
  kb.row(B('◀️ К лотам', callback_data=CB_LOTS))
  _answer(bot, call, 'Сначала создайте аккаунт.', True)
  _safe_edit(bot, call.message.chat.id, call.message.id, '⚠️ <b>Сначала нужен аккаунт</b>\n\nЛот наследует лимиты, очередь, сообщение и Denuvo из аккаунта.', kb)
  return
 chat_id = call.message.chat.id
 _fsm_start(chat_id, 'add_lot', 'funpay_lot_id', call.message.id)
 _safe_edit(bot, chat_id, call.message.id, '➕ <b>Добавление лота</b>\n\nШаг 1: отправьте числовой LOT ID FunPay.\n\nСообщение будет удалено автоматически.', _cancel_kb(CB_LOTS))
 _answer(bot, call)

def _finish_add_lot(bot, chat_id: int, state: dict, account_ids: List[str]) -> None:
 data = state.setdefault('data', {})
 selected = next((str(x) for x in account_ids if str(x)), '')
 lot = {'id': _uid('l'), 'funpay_lot_id': str(data.get('funpay_lot_id') or ''), 'title': str(data.get('title') or data.get('funpay_lot_id') or 'Лот')[:150], 'account_type': _canonical_account_type(data.get('account_type')), 'command': str(data.get('command') or ''), 'enabled': True, 'funpay_active': None, 'funpay_sync': {}, 'account_ids': [selected] if selected else []}
 if not selected:
  raise ValueError('Нужно привязать один аккаунт.')
 _db_get().setdefault('lots', []).append(lot)
 _db_save()
 repaired_orders = _repair_orders_for_lot(lot)
 _fsm_cleanup(bot, chat_id, state)
 _fsm.pop(chat_id, None)
 _safe_edit(bot, chat_id, _safe_int(state.get('panel_msg_id'), 0), _lot_text(lot), _lot_kb(lot))
 _log('SETTINGS', 'Лот добавлен', lot_id=lot['id'], funpay_lot_id=lot['funpay_lot_id'], account_type=lot['account_type'], account_id=selected, repaired_orders=repaired_orders)

def _compatible_lot_accounts(account_type: Any) -> List[dict]:
 target = _canonical_account_type(account_type)
 return [account for account in _db_get().get('accounts', []) if _canonical_account_type(account.get('type')) == target]

def _lot_account_picker_kb(mode: str, account_type: Any, page: int=0, lot: Optional[dict]=None) -> K:
 accounts = _compatible_lot_accounts(account_type)
 total_pages = max(1, (len(accounts) + LOT_ACCOUNT_PAGE_SIZE - 1) // LOT_ACCOUNT_PAGE_SIZE)
 page = max(0, min(_safe_int(page, 0), total_pages - 1))
 start = page * LOT_ACCOUNT_PAGE_SIZE
 selected = next((str(x) for x in (lot or {}).get('account_ids', []) if str(x)), '')
 kb = K()
 for account in accounts[start:start + LOT_ACCOUNT_PAGE_SIZE]:
  aid = str(account.get('id'))
  marker = '✅ ' if aid == selected else ''
  label = marker + str(account.get('name') or aid)[:45]
  callback = f'{CB_LOT_ACCOUNT_PICK}:a:{aid}' if mode == 'add' else f"{CB_LOT_ACCOUNT_PICK}:e:{lot['id']}:{aid}"
  kb.row(B(label, callback_data=callback))
 nav = []
 if page > 0:
  callback = f'{CB_LOT_ACCOUNT_PAGE}:a:{page - 1}' if mode == 'add' else f"{CB_LOT_ACCOUNT_PAGE}:e:{lot['id']}:{page - 1}"
  nav.append(B('◀️', callback_data=callback))
 if page + 1 < total_pages:
  callback = f'{CB_LOT_ACCOUNT_PAGE}:a:{page + 1}' if mode == 'add' else f"{CB_LOT_ACCOUNT_PAGE}:e:{lot['id']}:{page + 1}"
  nav.append(B('▶️', callback_data=callback))
 if nav:
  kb.row(*nav)
 if mode == 'add':
  kb.row(B('❌ Отменить', callback_data=CB_CANCEL))
 else:
  kb.row(B('◀️ К лоту', callback_data=f"{CB_LOT_OPEN}:{lot['id']}"))
 return kb

def _show_lot_account_picker(cardinal: 'Cardinal', call, mode: str, page: int=0, lot: Optional[dict]=None) -> None:
 bot = cardinal.telegram.bot
 chat_id = call.message.chat.id
 if mode == 'add':
  state = _fsm.get(chat_id)
  if not state or state.get('mode') != 'add_lot':
   _answer(bot, call, 'Добавление лота уже завершено.', True)
   return
  account_type = state.setdefault('data', {}).get('account_type')
  state['step'] = 'accounts'
 else:
  if lot is None:
   _answer(bot, call, 'Лот не найден.', True)
   return
  account_type = lot.get('account_type')
 accounts = _compatible_lot_accounts(account_type)
 if not accounts:
  _answer(bot, call, 'Нет аккаунтов выбранного типа.', True)
  return
 total_pages = max(1, (len(accounts) + LOT_ACCOUNT_PAGE_SIZE - 1) // LOT_ACCOUNT_PAGE_SIZE)
 page = max(0, min(_safe_int(page, 0), total_pages - 1))
 text = f'🎮 <b>Привязка аккаунта</b>\n\nТип: <b>{escape(ACCOUNT_TYPES.get(_canonical_account_type(account_type), str(account_type)))}</b>\nАккаунтов: <b>{len(accounts)}</b>\nСтраница: <b>{page + 1}/{total_pages}</b>\n\nВыберите один аккаунт.'
 _safe_edit(bot, chat_id, call.message.id, text, _lot_account_picker_kb(mode, account_type, page, lot))
 _answer(bot, call)

def _handle_type_choice(cardinal: 'Cardinal', call) -> None:
 bot = cardinal.telegram.bot
 parts = str(call.data).split(':')
 if len(parts) < 4:
  return
 target, account_type = (parts[-2], _canonical_account_type(parts[-1]))
 chat_id = call.message.chat.id
 state = _fsm.get(chat_id)
 if target == 'acc' and state and (state.get('mode') == 'add_account'):
  if account_type not in ACCOUNT_CREATION_TYPES:
   _answer(bot, call, 'Этот тип аккаунта не поддерживается.', True)
   return
  state['data']['type'] = account_type
  if account_type == 'steam_email':
   state['step'] = 'mail_email'
   prompt = '📧 Отправьте email почтового ящика Steam. Mail.ru, Gmail, Yandex, FirstMail и NotLetters работают через IMAP, остальные адреса — через SmakMail API.'
  else:
   state['step'] = 'secret'
   if account_type == 'steam_sda':
    prompt = '🔐 Отправьте файл <code>.maFile</code> — название и shared_secret будут взяты автоматически, или отправьте <code>shared_secret</code> текстом.'
   else:
    prompt = '🔐 Отправьте Base32 secret или целую ссылку <code>otpauth://...</code>. Плагин сам извлечёт параметр <code>secret</code> и проверит код.'
  _safe_edit(bot, chat_id, call.message.id, f'➕ <b>Добавление аккаунта</b>\n\nТип: <b>{escape(ACCOUNT_TYPES.get(account_type, account_type))}</b>\n\n{prompt}\n\nСообщение будет удалено сразу после получения.', _cancel_kb(CB_ACCOUNTS))
  _answer(bot, call)
  return
 if target == 'lot' and state and (state.get('mode') == 'add_lot'):
  compatible = _compatible_lot_accounts(account_type)
  if not compatible:
   _answer(bot, call, 'Нет аккаунта выбранного типа.', True)
   return
  state['data']['account_type'] = account_type
  state['data'].pop('selected_account_id', None)
  _show_lot_account_picker(cardinal, call, 'add', 0)

def _start_edit_text(cardinal: 'Cardinal', call, mode: str, entity_id: str, prompt: str, back: str) -> None:
 bot = cardinal.telegram.bot
 chat_id = call.message.chat.id
 _fsm_start(chat_id, mode, 'value', call.message.id, entity_id=entity_id)
 _safe_edit(bot, chat_id, call.message.id, prompt, _cancel_kb(back))
 _answer(bot, call)

def _parse_duration_input(value: str) -> int:
 text = unicodedata.normalize('NFKC', str(value or '')).strip().casefold().replace(' ', '')
 match = re.fullmatch('(\\d{1,9})(с|сек|секунд|s|м|мин|минут|m|ч|час|часов|h|д|дн|дней|d)?', text)
 if not match:
  raise ValueError('Укажите время, например: 30с, 10м, 2ч или 1д.')
 amount = int(match.group(1))
 if amount <= 0:
  raise ValueError('Время должно быть больше нуля.')
 suffix = match.group(2) or 'с'
 multiplier = 1
 if suffix in {'м', 'мин', 'минут', 'm'}:
  multiplier = 60
 elif suffix in {'ч', 'час', 'часов', 'h'}:
  multiplier = 3600
 elif suffix in {'д', 'дн', 'дней', 'd'}:
  multiplier = 86400
 return min(31536000, amount * multiplier)

def _account_flow_edit(bot, chat_id: int, state: dict, text: str, kb: Optional[K]=None) -> None:
 _safe_edit(bot, chat_id, _safe_int(state.get('panel_msg_id'), 0), text, kb or _cancel_kb(CB_ACCOUNTS))

def _account_queue_choice_kb() -> K:
 kb = K()
 kb.row(B('✅ Да, включить', callback_data=f'{CB_ACCOUNT_QUEUE_CHOICE}:y'), B('❌ Нет', callback_data=f'{CB_ACCOUNT_QUEUE_CHOICE}:n'))
 kb.row(B('◀️ Отменить', callback_data=CB_CANCEL))
 return kb

def _prompt_account_queue_choice(bot, chat_id: int, state: dict) -> None:
 account_type = str(state.get('data', {}).get('type') or '')
 if account_type not in {'steam_sda', 'totp'}:
  state.setdefault('data', {})['queue_enabled'] = False
  _prompt_account_limit_mode(bot, chat_id, state)
  return
 state['step'] = 'queue_choice'
 if account_type == 'totp':
  title = 'Очередь TOTP'
  description = 'Один TOTP-код действует 30 секунд. Первый покупатель получит текущий код, а одновременные запросы выстроятся по порядку и получат коды в следующих временных окнах. Так один и тот же код не уйдёт двум людям.'
 else:
  title = 'Очередь Steam Guard'
  description = 'Если два или больше покупателей отправят команду почти одновременно, первый запрос обработается сразу, а остальные выстроятся по порядку. Между выдачами одного Steam-аккаунта будет минимум 15 секунд.'
 _account_flow_edit(bot, chat_id, state, f'⏳ <b>{title}</b>\n\nВключить очередь для этого аккаунта?\n\n{description}', _account_queue_choice_kb())

def _account_denuvo_choice_kb(target: str='add', account_id: str='') -> K:
 suffix = f':{target}:{account_id}' if account_id else f':{target}'
 kb = K()
 kb.row(B('✅ Да', callback_data=f'{CB_ACCOUNT_DENUVO_CHOICE}{suffix}:y'), B('❌ Нет', callback_data=f'{CB_ACCOUNT_DENUVO_CHOICE}{suffix}:n'))
 kb.row(B('◀️ Отменить', callback_data=CB_CANCEL if target == 'add' else f'{CB_ACCOUNT_OPEN}:{account_id}'))
 return kb

def _account_limit_mode_choice_kb(target: str='add', account_id: str='') -> K:
 prefix = f'{CB_ACCOUNT_LIMIT_MODE}:{target}'
 if account_id:
  prefix += f':{account_id}'
 kb = K()
 kb.row(B('1️⃣ По количеству кодов', callback_data=f'{prefix}:count'))
 kb.row(B('2️⃣ По времени (безлимит кодов)', callback_data=f'{prefix}:time'))
 kb.row(B('◀️ Отменить', callback_data=CB_CANCEL if target == 'add' else f'{CB_ACCOUNT_LIMITS}:{account_id}'))
 return kb

def _prompt_account_limit_mode(bot, chat_id: int, state: dict) -> None:
 state['step'] = 'limit_mode'
 _account_flow_edit(bot, chat_id, state, '📛 <b>Тип лимита кодов</b>\n\n1️⃣ <b>По количеству</b> — старый режим: покупатель получает заданное число кодов, при желании можно настроить сброс счётчика.\n\n2️⃣ <b>По времени</b> — в течение указанного времени покупатель может запрашивать коды без ограничения по количеству. После окончания времени доступ закрывается, второй лимит/сброс не предлагается.', _account_limit_mode_choice_kb('add'))

def _prompt_account_limit_count(bot, chat_id: int, state: dict) -> None:
 state['step'] = 'limit_count'
 _account_flow_edit(bot, chat_id, state, '🔢 <b>Лимит по количеству</b>\n\nСколько кодов сможет получить один покупатель по своему заказу?\n\nОтправьте число от <code>1</code> и выше. Для безлимита отправьте <code>-</code>.\nЕсли укажете число, следующим шагом можно задать время сброса счётчика.')

def _prompt_account_limit_time(bot, chat_id: int, state: dict) -> None:
 state['step'] = 'limit_time'
 _account_flow_edit(bot, chat_id, state, '⏱ <b>Лимит по времени</b>\n\nСколько времени после первого запроса покупатель сможет получать коды без ограничения по количеству?\n\nПримеры: <code>30м</code>, <code>2ч</code>, <code>1д</code>. После окончания этого времени доступ к кодам закрывается.')

def _handle_account_limit_mode_choice(cardinal: 'Cardinal', call) -> None:
 bot = cardinal.telegram.bot
 parts = str(call.data).split(':')
 choice = parts[-1] if parts else ''
 if choice not in {'count', 'time'}:
  _answer(bot, call, 'Неизвестный режим лимита.', True)
  return
 is_add = len(parts) >= 2 and parts[-2] == 'add'
 chat_id = call.message.chat.id
 if is_add:
  state = _fsm.get(chat_id)
  if not state or state.get('mode') != 'add_account' or state.get('step') != 'limit_mode':
   _answer(bot, call, 'Этот шаг уже завершён.', True)
   return
  state.setdefault('data', {})['limit_mode'] = choice
  _answer(bot, call, 'Выбран лимит по количеству.' if choice == 'count' else 'Выбран лимит по времени.')
  if choice == 'count':
   _prompt_account_limit_count(bot, chat_id, state)
  else:
   _prompt_account_limit_time(bot, chat_id, state)
  return
 if len(parts) < 3:
  _answer(bot, call, 'Аккаунт не указан.', True)
  return
 account_id = parts[-2]
 account = _find_account(account_id)
 if account is None:
  _answer(bot, call, 'Аккаунт не найден.', True)
  return
 account['limit_mode'] = choice
 account['limit_total'] = None
 account['limit_reset_seconds'] = 0
 account['limit_time_seconds'] = 0
 _reset_account_usage(account_id)
 _db_save()
 _answer(bot, call, 'Режим лимита изменён.')
 if choice == 'count':
  _fsm_start(chat_id, 'edit_account_limit_count', 'value', call.message.id, entity_id=account_id)
  _safe_edit(bot, chat_id, call.message.id, '🔢 <b>Количество кодов</b>\n\nОтправьте число от <code>1</code> и выше или <code>-</code> для безлимита.', _cancel_kb(CB_ACCOUNTS))
 else:
  _fsm_start(chat_id, 'edit_account_limit_time', 'value', call.message.id, entity_id=account_id)
  _safe_edit(bot, chat_id, call.message.id, '⏱ <b>Время доступа</b>\n\nОтправьте срок, например <code>30м</code>, <code>2ч</code> или <code>1д</code>. В это время покупатель может получать коды без ограничения.', _cancel_kb(CB_ACCOUNTS))

def _prompt_account_denuvo_choice(bot, chat_id: int, state: dict) -> None:
 if str(state.get('data', {}).get('type') or '') != 'steam_sda':
  _finish_add_account(bot, chat_id, state)
  return
 state['step'] = 'denuvo_choice'
 _account_flow_edit(bot, chat_id, state, '🎮 <b>Использовать Denuvo для этого Steam-аккаунта?</b>\n\nЕсли включить, плагин будет учитывать этот аккаунт как Denuvo-слот и отправлять название игры в API при распределении.', _account_denuvo_choice_kb('add'))

def _finish_add_account(bot, chat_id: int, state: dict) -> None:
 data = state.setdefault('data', {})
 account_type = str(data.get('type') or 'steam_sda')
 queue_enabled = bool(data.get('queue_enabled')) if account_type in {'steam_sda', 'totp'} else False
 denuvo_enabled = bool(data.get('denuvo_enabled')) if account_type == 'steam_sda' else False
 denuvo_cfg = {'enabled': denuvo_enabled, 'slot_limit': 5, 'slot_limit_custom': False, 'reserve': 0, 'active_slots': 0, 'weight': 100, 'failure_rate': 0.0, 'cooldown_until': 0, 'hold_seconds': 0}
 if denuvo_enabled:
  denuvo_cfg['game_id'] = str(data.get('denuvo_game') or '').strip()[:200]
 default_name = 'TOTP account' if account_type == 'totp' else 'Steam Email' if account_type == 'steam_email' else 'Steam account'
 account = {'id': _uid('a'), 'name': str(data.get('name') or default_name)[:100], 'type': account_type, 'secret': str(data.get('secret') or ''), 'data': data.get('account_data', {}) if isinstance(data.get('account_data'), dict) else {}, 'enabled': True, 'limit_mode': str(data.get('limit_mode') or 'count'), 'limit_total': data.get('limit_total'), 'limit_reset_seconds': _safe_int(data.get('limit_reset_seconds'), 0, 0, 31536000), 'limit_time_seconds': _safe_int(data.get('limit_time_seconds'), 0, 0, 31536000), 'cooldown_seconds': 0, 'template': '', 'issued': 0, 'queue': {'enabled': queue_enabled, 'interval_seconds': TOTP_QUEUE_INTERVAL_SECONDS if account_type == 'totp' else STEAM_QUEUE_INTERVAL_SECONDS, 'last_issue_at': 0}, 'denuvo': denuvo_cfg}
 _db_get().setdefault('accounts', []).append(account)
 _db_save()
 _fsm_cleanup(bot, chat_id, state)
 _fsm.pop(chat_id, None)
 _safe_edit(bot, chat_id, _safe_int(state.get('panel_msg_id'), 0), _account_text(account), _account_kb(account))
 _log('SETTINGS', 'Аккаунт добавлен', account_id=account['id'], account_type=account['type'], queue_enabled=queue_enabled, denuvo_enabled=denuvo_enabled)

def _handle_account_queue_choice(cardinal: 'Cardinal', call) -> None:
 bot = cardinal.telegram.bot
 chat_id = call.message.chat.id
 state = _fsm.get(chat_id)
 if not state or state.get('mode') != 'add_account' or state.get('step') != 'queue_choice':
  _answer(bot, call, 'Этот шаг уже завершён.', True)
  return
 enabled = str(call.data).rsplit(':', 1)[-1] == 'y'
 state.setdefault('data', {})['queue_enabled'] = enabled
 _answer(bot, call, 'Очередь включена.' if enabled else 'Очередь отключена.')
 _prompt_account_limit_mode(bot, chat_id, state)

def _handle_account_denuvo_choice(cardinal: 'Cardinal', call) -> None:
 bot = cardinal.telegram.bot
 chat_id = call.message.chat.id
 tail = str(call.data)[len(CB_ACCOUNT_DENUVO_CHOICE):].lstrip(':').split(':')
 target = tail[0] if tail else 'add'
 choice = tail[-1] if tail else 'n'
 if target == 'add':
  state = _fsm.get(chat_id)
  if not state or state.get('mode') != 'add_account' or state.get('step') != 'denuvo_choice':
   _answer(bot, call, 'Этот шаг уже завершён.', True)
   return
  enabled = choice == 'y'
  state.setdefault('data', {})['denuvo_enabled'] = enabled
  _answer(bot, call, 'Denuvo включён.' if enabled else 'Denuvo не используется.')
  if enabled:
   state['step'] = 'denuvo_game'
   _account_flow_edit(bot, chat_id, state, '🎮 <b>Название игры</b>\n\nОтправьте любое название, например <code>F1 25</code>. Оно сохранится в аккаунте и будет передаваться в API.')
  else:
   _finish_add_account(bot, chat_id, state)
  return
 if target in {'edit', 'e'} and len(tail) >= 3:
  account_id = tail[1]
  account = _find_account(account_id)
  if account is None:
   _answer(bot, call, 'Аккаунт не найден.', True)
   return
  if choice == 'n':
   account.setdefault('denuvo', {})['enabled'] = False
   _db_save()
   _sync_denuvo_lot_capacity(_CARDINAL)
   _answer(bot, call, 'Denuvo отключён.')
   _safe_edit(bot, chat_id, call.message.id, _account_text(account), _account_kb(account))
   return
  denuvo = account.setdefault('denuvo', {})
  denuvo['enabled'] = True
  denuvo.setdefault('slot_limit_custom', False)
  if _safe_int(denuvo.get('slot_limit'), 1) == 1 and (not denuvo.get('slot_limit_custom')):
   denuvo['slot_limit'] = 5
  else:
   denuvo.setdefault('slot_limit', 5)
  _db_save()
  if str(denuvo.get('game_id') or '').strip():
   _answer(bot, call, 'Denuvo включён.')
   _safe_edit(bot, chat_id, call.message.id, _account_text(account), _account_kb(account))
   _sync_denuvo_lot_capacity(_CARDINAL)
   return
  _fsm_start(chat_id, 'edit_account_denuvo_game', 'value', call.message.id, entity_id=account_id)
  _answer(bot, call, 'Denuvo включён. Отправьте название игры.')
  _safe_edit(bot, chat_id, call.message.id, '🎮 <b>Название Denuvo-игры</b>\n\nОтправьте любое название, например <code>F1 25</code>.', _cancel_kb(CB_ACCOUNTS))

def _toggle_account_queue(cardinal: 'Cardinal', call) -> None:
 account = _find_account(str(call.data).split(':')[-1])
 if account is None:
  _answer(cardinal.telegram.bot, call, 'Аккаунт не найден.', True)
  return
 account_type = _canonical_account_type(account.get('type'))
 if account_type not in {'steam_sda', 'totp'}:
  _answer(cardinal.telegram.bot, call, 'Очередь доступна для Steam Guard и TOTP.', True)
  return
 queue_cfg = account.setdefault('queue', {})
 queue_cfg['enabled'] = not bool(queue_cfg.get('enabled'))
 queue_cfg['interval_seconds'] = TOTP_QUEUE_INTERVAL_SECONDS if account_type == 'totp' else STEAM_QUEUE_INTERVAL_SECONDS
 queue_cfg.setdefault('last_issue_at', 0)
 _db_save()
 _answer(cardinal.telegram.bot, call, 'Очередь включена.' if queue_cfg['enabled'] else 'Очередь отключена.')
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, _account_text(account), _account_kb(account))

def _start_edit_account_denuvo(cardinal: 'Cardinal', call) -> None:
 account_id = str(call.data).split(':')[-1]
 account = _find_account(account_id)
 if account is None:
  _answer(cardinal.telegram.bot, call, 'Аккаунт не найден.', True)
  return
 if _canonical_account_type(account.get('type')) != 'steam_sda':
  _answer(cardinal.telegram.bot, call, 'Denuvo доступен только для Steam-аккаунта.', True)
  return
 denuvo = account.setdefault('denuvo', {})
 game = str(denuvo.get('game_id') or 'не указана')
 limit = _safe_int(denuvo.get('slot_limit'), 5, 1, 10000)
 active = _safe_int(denuvo.get('active_slots'), 0, 0, 10000)
 text = f"🎮 <b>Настройки Denuvo</b>\n\n• Состояние: <b>{('ВКЛ' if denuvo.get('enabled') else 'ВЫКЛ')}</b>\n• Игра: <b>{escape(game)}</b>\n• Активации: <b>{active}/{limit}</b>\n\nКогда заняты все активации, связанные лоты автоматически выключаются. После освобождения активации они включаются обратно."
 kb = K()
 kb.row(B(f"{('🔴 Отключить Denuvo' if denuvo.get('enabled') else '🟢 Включить Denuvo')}", callback_data=f"{CB_ACCOUNT_DENUVO_CHOICE}:edit:{account_id}:{('n' if denuvo.get('enabled') else 'y')}"))
 kb.row(B('✏️ Изменить игру', callback_data=f'{CB_ACCOUNT_DENUVO_GAME}:{account_id}'))
 kb.row(B('🔢 Лимит активаций', callback_data=f'{CB_ACCOUNT_DENUVO_LIMIT}:{account_id}'))
 kb.row(B('◀️ К аккаунту', callback_data=f'{CB_ACCOUNT_OPEN}:{account_id}'))
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, text, kb)
 _answer(cardinal.telegram.bot, call)

def _start_edit_account_secret(cardinal: 'Cardinal', call) -> None:
 account_id = str(call.data).split(':')[-1]
 account = _find_account(account_id)
 if account is None:
  _answer(cardinal.telegram.bot, call, 'Аккаунт не найден.', True)
  return
 account_type = _canonical_account_type(account.get('type'))
 if account_type == 'steam_email':
  _start_edit_text(cardinal, call, 'edit_account_mail', account_id, '📧 <b>Замена почты Steam</b>\n\nОтправьте одной строкой <code>email:пароль</code>. Известные провайдеры подключаются через IMAP, остальные через SmakMail API. Выдаются только Steam Guard-коды для входа.\n\nСообщение удалится автоматически.', CB_ACCOUNTS)
  return
 if account_type == 'steam_sda':
  prompt = '🔐 <b>Замена Steam shared_secret</b>\n\nОтправьте shared_secret из Steam Desktop Authenticator или файл <code>.maFile</code>. Ссылки <code>otpauth://</code> и TOTP-secret не принимаются.\n\nСообщение удалится автоматически.'
 elif account_type == 'totp':
  prompt = '🔐 <b>Замена TOTP secret</b>\n\nОтправьте Base32 secret или полную ссылку <code>otpauth://...</code>.\n\nСообщение удалится автоматически.'
 else:
  prompt = '🔐 Отправьте новые данные аккаунта. Сообщение удалится автоматически.'
 _start_edit_text(cardinal, call, 'edit_account_secret', account_id, prompt, CB_ACCOUNTS)

def _account_limit_reset_label(account: dict) -> str:
 if _account_limit_mode(account) == 'time':
  return 'не используется'
 if account.get('limit_total') in (None, '', 0, '0'):
  return 'не используется'
 reset_seconds = _safe_int(account.get('limit_reset_seconds'), 0)
 return _fmt_duration(reset_seconds) if reset_seconds > 0 else 'не сбрасывается'

def _account_limits_text(account: dict) -> str:
 mode = _account_limit_mode(account)
 if mode == 'time':
  duration = _safe_int(account.get('limit_time_seconds'), 0)
  details = f"• Режим: <b>по времени</b>\n• Время доступа: <b>{escape(_fmt_duration(duration) if duration > 0 else 'не задано')}</b>\n• Количество кодов: <b>без ограничений в течение срока</b>"
 else:
  limit = '∞' if account.get('limit_total') in (None, '', 0, '0') else str(account.get('limit_total'))
  details = f'• Режим: <b>по количеству</b>\n• Количество кодов: <b>{escape(limit)}</b>\n• Сброс счётчика: <b>{escape(_account_limit_reset_label(account))}</b>'
 return f"📛 <b>Лимиты кодов</b>\n\nАккаунт: <b>{escape(str(account.get('name') or '—'))}</b>\n\n{details}\n\nРежимы взаимоисключающие: при лимите по времени второй лимит/сброс не используется. Denuvo-активация считается отдельно."

def _account_limits_kb(account: dict) -> K:
 aid = str(account.get('id') or '')
 mode = _account_limit_mode(account)
 kb = K()
 kb.row(B(f"🔀 Режим · {('время' if mode == 'time' else 'количество')}", callback_data=f'{CB_ACCOUNT_LIMIT_MODE}:menu:{aid}'))
 if mode == 'time':
  duration = _safe_int(account.get('limit_time_seconds'), 0)
  kb.row(B(f"⏱ Время · {(_fmt_duration(duration) if duration > 0 else 'не задано')}", callback_data=f'{CB_ACCOUNT_LIMIT_TIME}:{aid}'))
 else:
  limit = '∞' if account.get('limit_total') in (None, '', 0, '0') else str(account.get('limit_total'))
  kb.row(B(f'🔢 Количество кодов · {limit}', callback_data=f'{CB_ACCOUNT_LIMIT_COUNT}:{aid}'))
  kb.row(B(f'♻️ Сброс лимита · {_account_limit_reset_label(account)}', callback_data=f'{CB_ACCOUNT_LIMIT_RESET}:{aid}'))
 kb.row(B('◀️ К аккаунту', callback_data=f'{CB_ACCOUNT_OPEN}:{aid}'))
 return kb

def _start_edit_account_limits(cardinal: 'Cardinal', call) -> None:
 account_id = str(call.data).split(':')[-1]
 account = _find_account(account_id)
 if account is None:
  _answer(cardinal.telegram.bot, call, 'Аккаунт не найден.', True)
  return
 if str(call.data).startswith(CB_ACCOUNT_LIMIT_MODE + ':menu:'):
  _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, '🔀 <b>Выберите режим лимита</b>\n\n1 — количество кодов.\n2 — ограниченное время с безлимитными запросами кодов.', _account_limit_mode_choice_kb('edit', account_id))
 else:
  _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, _account_limits_text(account), _account_limits_kb(account))
 _answer(cardinal.telegram.bot, call)

def _start_edit_account_limit_count(cardinal: 'Cardinal', call) -> None:
 account_id = str(call.data).split(':')[-1]
 account = _find_account(account_id)
 if account is None:
  _answer(cardinal.telegram.bot, call, 'Аккаунт не найден.', True)
  return
 account['limit_mode'] = 'count'
 _fsm_start(call.message.chat.id, 'edit_account_limit_count', 'value', call.message.id, entity_id=account_id)
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, '🔢 <b>Количество кодов</b>\n\nСколько Steam Guard/TOTP/Email-кодов сможет получить покупатель?\n\nОтправьте число от <code>1</code> и выше или <code>-</code> для безлимита.', _cancel_kb(CB_ACCOUNTS))
 _answer(cardinal.telegram.bot, call)

def _start_edit_account_limit_reset(cardinal: 'Cardinal', call) -> None:
 account_id = str(call.data).split(':')[-1]
 account = _find_account(account_id)
 if account is None:
  _answer(cardinal.telegram.bot, call, 'Аккаунт не найден.', True)
  return
 if _account_limit_mode(account) != 'count':
  _answer(cardinal.telegram.bot, call, 'В режиме лимита по времени сброс не используется.', True)
  return
 if account.get('limit_total') in (None, '', 0, '0'):
  _answer(cardinal.telegram.bot, call, 'Сначала задайте количество кодов.', True)
  return
 _fsm_start(call.message.chat.id, 'edit_account_limit_reset', 'value', call.message.id, entity_id=account_id)
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, '♻️ <b>Сброс лимита</b>\n\nЧерез какое время счётчик количества должен начинаться заново?\nПримеры: <code>30с</code>, <code>10м</code>, <code>2ч</code>, <code>1д</code>.\nДля лимита без сброса отправьте <code>-</code>.', _cancel_kb(CB_ACCOUNTS))
 _answer(cardinal.telegram.bot, call)

def _start_edit_account_limit_time(cardinal: 'Cardinal', call) -> None:
 account_id = str(call.data).split(':')[-1]
 account = _find_account(account_id)
 if account is None:
  _answer(cardinal.telegram.bot, call, 'Аккаунт не найден.', True)
  return
 account['limit_mode'] = 'time'
 _fsm_start(call.message.chat.id, 'edit_account_limit_time', 'value', call.message.id, entity_id=account_id)
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, '⏱ <b>Время доступа</b>\n\nУкажите срок, например <code>30м</code>, <code>2ч</code> или <code>1д</code>. В течение срока количество запросов не ограничено, после окончания доступ закрывается.', _cancel_kb(CB_ACCOUNTS))
 _answer(cardinal.telegram.bot, call)

def _handle_fsm(message: Message, cardinal: 'Cardinal') -> None:
 chat_id = message.chat.id
 state = _fsm.get(chat_id)
 if not state:
  return
 bot = cardinal.telegram.bot
 text = str(getattr(message, 'text', None) or '').strip()
 document = getattr(message, 'document', None)
 mode, step = (state.get('mode'), state.get('step'))
 if mode in {'add_account', 'add_lot', 'edit_account_limit_count', 'edit_account_limit_reset', 'edit_account_limit_time', 'edit_account_mail', 'edit_account_name', 'edit_account_template', 'edit_account_secret', 'edit_account_denuvo_game', 'edit_account_denuvo_limit', 'smakmail_key'}:
  _delete_message(bot, chat_id, getattr(message, 'message_id', None))
 if text.casefold() in {'/cancel', 'cancel'}:
  _fsm_cleanup(bot, chat_id, state)
  _fsm.pop(chat_id, None)
  _safe_send_tg(bot, chat_id, '❌ Операция отменена.')
  return
 data = state.setdefault('data', {})
 panel_msg_id = _safe_int(state.get('panel_msg_id'), 0)
 try:
  if mode == 'unlock' and step == 'password':
   state.setdefault('sensitive_messages', []).append(message.message_id)
   _unlock_password(text)
   _fsm_cleanup(bot, chat_id, state)
   _fsm.pop(chat_id, None)
   _register_admin(chat_id)
   _safe_edit(bot, chat_id, panel_msg_id, _security_text(), _security_kb())
   return
  if mode == 'set_master' and step == 'password':
   state.setdefault('sensitive_messages', []).append(message.message_id)
   if len(text) < 8:
    raise ValueError('Пароль должен содержать минимум 8 символов.')
   data['password'] = text
   state['step'] = 'confirm'
   _fsm_prompt(bot, chat_id, '🔑 Повторите новый master-password.', CB_SECURITY)
   return
  if mode == 'set_master' and step == 'confirm':
   state.setdefault('sensitive_messages', []).append(message.message_id)
   if text != data.get('password'):
    raise ValueError('Пароли не совпадают.')
   _set_master_password(text)
   _fsm_cleanup(bot, chat_id, state)
   _fsm.pop(chat_id, None)
   _safe_edit(bot, chat_id, panel_msg_id, _security_text(), _security_kb())
   return
  if mode == 'import' and step == 'document':
   filename, raw = _download_document(bot, message)
   payload = json.loads(raw.decode('utf-8-sig'))
   if not isinstance(payload, dict) or payload.get('format') != DB_FORMAT:
    raise ValueError('Это не encrypted backup AutoOffline.')
   old = open(DB_FILE, 'rb').read() if os.path.isfile(DB_FILE) else b''
   try:
    _atomic_write(DB_FILE, json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8'))
    global _DB_CACHE, _DB_KEY, _DB_MODE
    _DB_CACHE = _DB_KEY = None
    _DB_MODE = str((payload.get('kdf') or {}).get('mode') or 'unknown')
    if _DB_MODE == 'local':
     _auto_unlock_local()
   except Exception:
    if old:
     _atomic_write(DB_FILE, old)
    raise
   _fsm_cleanup(bot, chat_id, state)
   _fsm.pop(chat_id, None)
   _safe_edit(bot, chat_id, panel_msg_id, _maintenance_text(), _maintenance_kb())
   if _db_locked():
    _safe_send_tg(bot, chat_id, '📥 Бэкап импортирован. Теперь разблокируйте его master-password.')
   return
  if mode == 'smakmail_key':
   state.setdefault('sensitive_messages', []).append(message.message_id)
   _db_get().setdefault('global', {})['smakmail_api_key'] = '' if text == '-' else text.strip()
   _db_save()
   _fsm_cleanup(bot, chat_id, state)
   _fsm.pop(chat_id, None)
   _safe_edit(bot, chat_id, panel_msg_id, _settings_text(), _settings_kb())
   return
  if mode == 'add_account':
   if step == 'mail_email':
    email_addr = text.strip().lower()
    if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email_addr):
     raise ValueError('Отправьте корректный email.')
    try:
     _imap_servers_for_email(email_addr)
     provider = 'imap'
    except ValueError:
     provider = 'smakmail'
     if not str((_db_get().get('global') or {}).get('smakmail_api_key') or '').strip():
      raise ValueError('IMAP-провайдер не поддерживается. Для этого адреса нужен SmakMail API key в настройках.')
    data['mail_provider'] = provider
    data['mail_email'] = email_addr
    state['step'] = 'mail_password'
    label = 'пароль ящика SmakMail' if provider == 'smakmail' else 'пароль IMAP или пароль приложения'
    _account_flow_edit(bot, chat_id, state, f'🔑 <b>Пароль почты</b>\n\nОтправьте {label}. Доступ будет проверен сразу.')
    return
   if step == 'mail_password':
    if not text:
     raise ValueError('Пароль не может быть пустым.')
    email_addr = str(data.get('mail_email') or '')
    provider = str(data.get('mail_provider') or 'imap')
    if provider == 'smakmail':
     ok, err = _check_smakmail_credentials(email_addr, text)
     if not ok:
      raise ValueError('Не удалось войти через SmakMail: ' + err)
     account_data = {'provider': 'smakmail', 'email': email_addr, 'mail_password': text, 'max_age_minutes': 20}
    else:
     ok, host, err = _check_imap_credentials(email_addr, text)
     if not ok:
      raise ValueError('Не удалось войти по IMAP: ' + err)
     account_data = {'provider': 'imap', 'email': email_addr, 'mail_password': text, 'imap_host': host, 'imap_port': 993, 'folder': 'INBOX', 'max_age_minutes': 20}
    data['secret'] = ''
    data['account_data'] = account_data
    data['source'] = provider
    state['step'] = 'name'
    _account_flow_edit(bot, chat_id, state, '🏷 <b>Название аккаунта</b>\n\nОтправьте понятное название, например <code>Steam Mail Main</code>.')
    return
   if step == 'secret':
    account_type = str(data.get('type') or '')
    if account_type not in ACCOUNT_CREATION_TYPES:
     raise ValueError('Этот тип аккаунта больше не поддерживается.')
    inferred_name = ''
    if document is not None:
     filename, raw = _download_document(bot, message, 2 * 1024 * 1024)
     if account_type != 'steam_sda':
      raise ValueError('Для TOTP нужен Base32 secret или ссылка otpauth://, а не файл.')
     secret, inferred_name = _parse_mafile_bytes(raw)
     data['secret'] = secret
     data['name'] = inferred_name[:100]
     data['source'] = 'mafile'
    else:
     if account_type == 'steam_sda':
      data['secret'] = _validate_steam_shared_secret(text)
     else:
      extracted = _extract_totp_secret(text)
      if not generate_totp_code(extracted):
       raise ValueError('Невалидный TOTP secret. Нужен Base32 или ссылка otpauth:// с параметром secret.')
      data['secret'] = extracted
     data['source'] = 'manual'
    data['account_data'] = {}
    if inferred_name:
     _prompt_account_queue_choice(bot, chat_id, state)
    else:
     state['step'] = 'name'
     example = 'Ubisoft Main' if account_type == 'totp' else 'Steam Main'
     _account_flow_edit(bot, chat_id, state, f'🏷 <b>Название аккаунта</b>\n\nОтправьте понятное название, например <code>{example}</code>.')
    return
   if step == 'name':
    if not text:
     raise ValueError('Название пустое.')
    data['name'] = text[:100]
    _prompt_account_queue_choice(bot, chat_id, state)
    return
   if step == 'limit_mode':
    raise ValueError('Выберите тип лимита кнопкой ниже.')
   if step == 'limit_count':
    data['limit_mode'] = 'count'
    data['limit_time_seconds'] = 0
    if text in {'-', '∞'}:
     data['limit_total'] = None
     data['limit_reset_seconds'] = 0
     _prompt_account_denuvo_choice(bot, chat_id, state)
     return
    limit = _safe_int(text, 0)
    if limit <= 0:
     raise ValueError("Отправьте число от 1 и выше или '-' для безлимита.")
    data['limit_total'] = limit
    state['step'] = 'limit_reset'
    _account_flow_edit(bot, chat_id, state, f'♻️ <b>Сброс лимита</b>\n\nЛимит: <b>{limit} кодов</b>. Через какое время он должен начинаться заново?\n\nПримеры: <code>30с</code>, <code>10м</code>, <code>2ч</code>, <code>1д</code>.\nДля лимита без сброса отправьте <code>-</code>.')
    return
   if step == 'limit_reset':
    data['limit_reset_seconds'] = 0 if text in {'-', '0', '∞'} else _parse_duration_input(text)
    _prompt_account_denuvo_choice(bot, chat_id, state)
    return
   if step == 'limit_time':
    data['limit_mode'] = 'time'
    data['limit_total'] = None
    data['limit_reset_seconds'] = 0
    data['limit_time_seconds'] = _parse_duration_input(text)
    _prompt_account_denuvo_choice(bot, chat_id, state)
    return
   if step == 'denuvo_game':
    if not text:
     raise ValueError('Название игры не может быть пустым.')
    data['denuvo_enabled'] = True
    data['denuvo_game'] = text[:200]
    _finish_add_account(bot, chat_id, state)
    return
  if mode == 'add_lot':
   if step == 'funpay_lot_id':
    lot_num = _safe_int(text, 0)
    if lot_num <= 0:
     raise ValueError('LOT ID должен быть положительным числом.')
    if _lot_by_funpay_id(lot_num):
     raise ValueError('Этот LOT ID уже добавлен.')
    data['funpay_lot_id'] = str(lot_num)
    state['step'] = 'title'
    _safe_edit(bot, chat_id, panel_msg_id, '🏷 <b>Название лота</b>\n\nОтправьте название игры или товара.', _cancel_kb(CB_LOTS))
    return
   if step == 'title':
    if not text:
     raise ValueError('Название лота не может быть пустым.')
    data['title'] = text[:150]
    state['step'] = 'type'
    kb = K()
    available_types = {_canonical_account_type(x.get('type')) for x in _db_get().get('accounts', []) if _canonical_account_type(x.get('type')) in LOT_CREATION_TYPES}
    for key in LOT_CREATION_TYPES:
     if key in available_types:
      count = sum((1 for x in _db_get().get('accounts', []) if _canonical_account_type(x.get('type')) == key))
      kb.row(B(f'{ACCOUNT_TYPES[key]} · {count}', callback_data=f'{CB_TYPE}:lot:{key}'))
    kb.row(B('❌ Отменить', callback_data=CB_CANCEL))
    _safe_edit(bot, chat_id, panel_msg_id, '➕ <b>Добавление лота</b>\n\nВыберите тип аккаунта. Все лимиты, очередь, сообщение и Denuvo будут унаследованы из него.', kb)
    return
   if step == 'command':
    cmd = _first_word(text)
    if not cmd or cmd.startswith('/'):
     raise ValueError('Нужна команда вроде !code_game.')
    if any((_normalize_command(x.get('command')) == cmd for x in _db_get().get('lots', []))):
     raise ValueError('Такая команда уже используется другим лотом.')
    selected = str(data.get('selected_account_id') or '')
    valid = next((x for x in _compatible_lot_accounts(data.get('account_type')) if str(x.get('id')) == selected), None)
    if valid is None:
     raise ValueError('Сначала выберите аккаунт кнопкой.')
    data['command'] = cmd
    _finish_add_lot(bot, chat_id, state, [selected])
    return
  if mode == 'edit_account_limit_count':
   account = _find_account(str(data.get('entity_id') or ''))
   if account is None:
    raise ValueError('Аккаунт не найден.')
   if text in {'-', '∞'}:
    account['limit_total'] = None
    account['limit_reset_seconds'] = 0
    account['cooldown_seconds'] = 0
   else:
    limit = _safe_int(text, 0)
    if limit <= 0:
     raise ValueError("Отправьте число от 1 и выше или '-' для безлимита.")
    account['limit_total'] = limit
    account.setdefault('limit_reset_seconds', 0)
    account['cooldown_seconds'] = 0
   account['limit_mode'] = 'count'
   account['limit_time_seconds'] = 0
   _reset_account_usage(account.get('id'))
   _db_save()
   _fsm_cleanup(bot, chat_id, state)
   _fsm.pop(chat_id, None)
   _safe_edit(bot, chat_id, panel_msg_id, _account_limits_text(account), _account_limits_kb(account))
   return
  if mode == 'edit_account_limit_reset':
   account = _find_account(str(data.get('entity_id') or ''))
   if account is None:
    raise ValueError('Аккаунт не найден.')
   if account.get('limit_total') in (None, '', 0, '0'):
    raise ValueError('Сначала задайте количество кодов.')
   account['limit_reset_seconds'] = 0 if text in {'-', '0', '∞'} else _parse_duration_input(text)
   account['cooldown_seconds'] = 0
   _reset_account_usage(account.get('id'))
   _db_save()
   _fsm_cleanup(bot, chat_id, state)
   _fsm.pop(chat_id, None)
   _safe_edit(bot, chat_id, panel_msg_id, _account_limits_text(account), _account_limits_kb(account))
   return
  if mode == 'edit_account_limit_time':
   account = _find_account(str(data.get('entity_id') or ''))
   if account is None:
    raise ValueError('Аккаунт не найден.')
   account['limit_mode'] = 'time'
   account['limit_total'] = None
   account['limit_reset_seconds'] = 0
   account['limit_time_seconds'] = _parse_duration_input(text)
   account['cooldown_seconds'] = 0
   _reset_account_usage(account.get('id'))
   _db_save()
   _fsm_cleanup(bot, chat_id, state)
   _fsm.pop(chat_id, None)
   _safe_edit(bot, chat_id, panel_msg_id, _account_limits_text(account), _account_limits_kb(account))
   return
  if mode in {'edit_account_name', 'edit_account_template', 'edit_account_secret', 'edit_account_mail', 'edit_account_denuvo_game', 'edit_account_denuvo_limit', 'plugin_update_local'}:
   entity_id = str(data.get('entity_id') or '')
   if mode.startswith('edit_account'):
    account = _find_account(entity_id)
    if account is None:
     raise ValueError('Аккаунт не найден.')
    if mode == 'edit_account_name':
     if not text:
      raise ValueError('Название не может быть пустым.')
     account['name'] = text[:100]
    elif mode == 'edit_account_template':
     account['template'] = '' if text == '-' else text
    elif mode == 'edit_account_denuvo_game':
     if not text:
      raise ValueError('Название игры не может быть пустым.')
     denuvo = account.setdefault('denuvo', {})
     denuvo['enabled'] = True
     denuvo['game_id'] = text[:200]
     denuvo.setdefault('slot_limit_custom', False)
     if _safe_int(denuvo.get('slot_limit'), 1) == 1 and (not denuvo.get('slot_limit_custom')):
      denuvo['slot_limit'] = 5
     else:
      denuvo.setdefault('slot_limit', 5)
     denuvo.setdefault('reserve', 0)
     denuvo.setdefault('active_slots', 0)
     denuvo.setdefault('weight', 100)
     denuvo.setdefault('failure_rate', 0.0)
     denuvo.setdefault('cooldown_until', 0)
     denuvo.setdefault('hold_seconds', 0)
    elif mode == 'edit_account_denuvo_limit':
     limit = _safe_int(text, 0)
     if limit <= 0:
      raise ValueError('Отправьте количество активаций от 1 и выше.')
     denuvo = account.setdefault('denuvo', {})
     denuvo['slot_limit'] = min(limit, 10000)
     denuvo['slot_limit_custom'] = True
    elif mode == 'edit_account_mail':
     state.setdefault('sensitive_messages', []).append(message.message_id)
     if ':' not in text:
      raise ValueError('Формат: email:пароль')
     email_addr, password = text.split(':', 1)
     email_addr = email_addr.strip().lower()
     password = password.strip()
     if not email_addr or not password or not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email_addr):
      raise ValueError('Формат: email:пароль')
     try:
      _imap_servers_for_email(email_addr)
      provider = 'imap'
     except ValueError:
      provider = 'smakmail'
     if provider == 'smakmail':
      if not str((_db_get().get('global') or {}).get('smakmail_api_key') or '').strip():
       raise ValueError('Для этого адреса нужен SmakMail API key в настройках.')
      ok, err = _check_smakmail_credentials(email_addr, password)
      if not ok:
       raise ValueError('Не удалось войти через SmakMail: ' + err)
      account['data'] = {'provider': 'smakmail', 'email': email_addr, 'mail_password': password, 'max_age_minutes': 20}
     else:
      ok, host, err = _check_imap_credentials(email_addr, password)
      if not ok:
       raise ValueError('Не удалось войти по IMAP: ' + err)
      account['data'] = {'provider': 'imap', 'email': email_addr, 'mail_password': password, 'imap_host': host, 'imap_port': 993, 'folder': 'INBOX', 'max_age_minutes': 20}
     account['secret'] = ''
    else:
     state.setdefault('sensitive_messages', []).append(message.message_id)
     if account.get('type') == 'steam_sda':
      if document is not None:
       _, raw = _download_document(bot, message, 2 * 1024 * 1024)
       secret, inferred_name = _parse_mafile_bytes(raw)
       account['secret'] = secret
       if inferred_name:
        account['name'] = inferred_name[:100]
      else:
       account['secret'] = _validate_steam_shared_secret(text)
     elif account.get('type') == 'totp':
      if not generate_totp_code(text):
       raise ValueError('Невалидный TOTP secret.')
      account['secret'] = _extract_totp_secret(text)
     elif account.get('type') == 'rockstar_email':
      cfg = json.loads(text)
      if not isinstance(cfg, dict):
       raise ValueError('Нужен JSON-объект.')
      account['data'] = cfg
    _db_save()
    _fsm_cleanup(bot, chat_id, state)
    _fsm.pop(chat_id, None)
    _safe_edit(bot, chat_id, panel_msg_id, _account_text(account), _account_kb(account))
    if _canonical_account_type(account.get('type')) == 'steam_sda':
     _sync_denuvo_lot_capacity(_CARDINAL)
    return
   if mode.startswith('edit_lot'):
    lot = _find_lot(entity_id)
    if lot is None:
     raise ValueError('Лот не найден.')
   if mode == 'plugin_update_local':
    filename, raw = _download_document(bot, message, 5 * 1024 * 1024)
    if not str(filename).casefold().endswith('.py'):
     raise ValueError('Нужен файл с расширением .py.')
    result = _install_plugin_payload(raw, f'локального файла {filename}')
    _fsm_cleanup(bot, chat_id, state)
    _fsm.pop(chat_id, None)
    if result.get('ok') and result.get('changed'):
     result_text = f"✅ <b>Локальное обновление установлено.</b>\n\nФайл: <code>{escape(str(filename))}</code>\nВерсия: <code>{escape(str(result.get('current_version')))}</code> → <code>{escape(str(result.get('remote_version')))}</code>\nРезервная копия: <code>{escape(os.path.basename(str(result.get('backup_file') or '')))}</code>\nАккаунты, лоты, заказы и настройки сохранены.\n\n🔁 Выполните <code>/restart</code>."
    elif result.get('ok'):
     result_text = '✅ <b>Этот файл уже установлен.</b>\n\nОсновной файл и данные не изменены.'
    else:
     result_text = f"❌ <b>Локальное обновление не установлено.</b>\n\nОшибка: <code>{escape(str(result.get('error') or 'неизвестная ошибка'))}</code>\n\nТекущий файл и данные не изменены."
    _safe_edit(bot, chat_id, panel_msg_id, result_text, _update_kb())
    return
 except Exception as e:
  _safe_send_tg(bot, chat_id, f'❌ {escape(str(e))}')
  logger.debug('%s FSM error: %s', PREFIX, e)

def _cancel_fsm(cardinal: 'Cardinal', call) -> None:
 bot = cardinal.telegram.bot
 chat_id = call.message.chat.id
 state = _fsm.pop(chat_id, None) or {}
 _fsm_cleanup(bot, chat_id, state)
 _answer(bot, call, 'Отменено.')
 _safe_edit(bot, chat_id, call.message.id, _settings_text(), _settings_kb())

def _toggle_plugin(cardinal: 'Cardinal', call) -> None:
 if _db_locked():
  return
 db = _db_get()
 db['global']['plugin_enabled'] = not bool(db['global'].get('plugin_enabled', True))
 _db_save()
 _answer(cardinal.telegram.bot, call, 'Состояние изменено.')
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, _settings_text(), _settings_kb())

def _toggle_all_accounts(cardinal: 'Cardinal', call) -> None:
 if _db_locked():
  return
 accounts = _db_get().get('accounts', [])
 if not accounts:
  _answer(cardinal.telegram.bot, call, 'Аккаунтов пока нет.', True)
  return
 turn_on = not all((bool(x.get('enabled', True)) for x in accounts))
 for account in accounts:
  account['enabled'] = turn_on
 _db_save()
 _answer(cardinal.telegram.bot, call, 'Состояние аккаунтов изменено.')
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, _state_text(), _state_kb())

def _toggle_all_lots(cardinal: 'Cardinal', call) -> None:
 if _db_locked():
  return
 lots = _db_get().get('lots', [])
 if not lots:
  _answer(cardinal.telegram.bot, call, 'Лотов пока нет.', True)
  return
 turn_on = not all((bool(x.get('enabled', True)) for x in lots))
 for lot in lots:
  lot['enabled'] = turn_on
  if not turn_on:
   lot.pop('auto_funpay_disabled_reason', None)
   lot.pop('auto_funpay_disabled_at', None)
 _db_save()
 _log('LOT', 'Локальное состояние всех лотов изменено', enabled=turn_on, count=len(lots))
 _answer(cardinal.telegram.bot, call, 'Все лоты включены в плагине.' if turn_on else 'Все лоты выключены в плагине.')
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, _state_text(), _state_kb())

def _toggle_all_funpay_lots(cardinal: 'Cardinal', call) -> None:
 if _db_locked():
  return
 lots = _db_get().get('lots', [])
 if not lots:
  _answer(cardinal.telegram.bot, call, 'Лотов пока нет.', True)
  return
 turn_on = not all((_lot_funpay_active(x) is True for x in lots))
 synced_count = 0
 failed_count = 0
 for lot in lots:
  synced, reason = _set_funpay_lot_enabled(cardinal, lot.get('funpay_lot_id'), turn_on)
  lot['funpay_sync'] = {'ok': synced, 'reason': reason, 'active': turn_on if synced else _lot_funpay_active(lot), 'ts': _now()}
  if synced:
   lot['funpay_active'] = turn_on
   lot.pop('auto_funpay_disabled_reason', None)
   lot.pop('auto_funpay_disabled_at', None)
   synced_count += 1
   _log('LOT', 'Состояние лота на FunPay изменено', lot_id=lot.get('id'), funpay_lot_id=lot.get('funpay_lot_id'), enabled=turn_on, synced=True)
  else:
   failed_count += 1
   _log('ERROR', 'FunPay не изменил состояние лота', lot_id=lot.get('id'), funpay_lot_id=lot.get('funpay_lot_id'), enabled=turn_on, error=reason)
 _db_save()
 action = 'включено' if turn_on else 'выключено'
 answer = f'На FunPay {action}: {synced_count}.'
 if failed_count:
  answer += f' Ошибок: {failed_count}.'
 _answer(cardinal.telegram.bot, call, answer, bool(failed_count))
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, _state_text(), _state_kb())

def _plugin_self_path() -> str:
 return os.path.abspath(__file__)

def _plugin_version_key(value: Any) -> Tuple[int, int, int, int]:
 nums = [int(x) for x in re.findall('\\d+', str(value or ''))[:4]]
 nums.extend([0] * (4 - len(nums)))
 return tuple(nums[:4])

def _plugin_version_from_source(source: str) -> Optional[str]:
 match = re.search('(?m)^\\s*VERSION\\s*=\\s*["\\\']([^"\\\']+)["\\\']', source or '')
 return match.group(1).strip() if match else None

def _cleanup_plugin_bytecode(plugin_file: str) -> None:
 try:
  cache = os.path.join(os.path.dirname(plugin_file), '__pycache__')
  if not os.path.isdir(cache):
   return
  base = os.path.splitext(os.path.basename(plugin_file))[0]
  for filename in os.listdir(cache):
   if filename.startswith(base + '.') and filename.endswith('.pyc'):
    try:
     os.remove(os.path.join(cache, filename))
    except Exception:
     pass
 except Exception:
  pass

def _validate_plugin_update_payload(payload: bytes) -> Tuple[str, str, str]:
 if not isinstance(payload, (bytes, bytearray)):
  raise RuntimeError('файл обновления не прочитан')
 payload = bytes(payload)
 if len(payload) < 10000:
  raise RuntimeError(f'файл обновления слишком маленький ({len(payload)} байт)')
 if len(payload) > 5 * 1024 * 1024:
  raise RuntimeError('файл обновления слишком большой (>5 МБ)')
 try:
  source = payload.decode('utf-8-sig')
 except UnicodeDecodeError as error:
  raise RuntimeError(f'файл обновления не UTF-8: {error}') from error
 head = source[:700].casefold()
 if '<html' in head or '<!doctype' in head:
  raise RuntimeError('вместо Python-файла получена HTML-страница')
 missing = [value for value in (UUID, 'def init_cardinal', 'BIND_TO_PRE_INIT', 'BIND_TO_NEW_MESSAGE') if value not in source]
 if missing:
  raise RuntimeError('файл не похож на AutoOffline: отсутствует ' + ', '.join(missing))
 remote_version = _plugin_version_from_source(source)
 if not remote_version:
  raise RuntimeError('в файле обновления не найдена VERSION')
 compile(source, _plugin_self_path(), 'exec')
 return (source, remote_version, hashlib.sha256(payload).hexdigest())

def _pending_update_file() -> str:
 return _plugin_self_path() + '.update.pending'

def _install_plugin_payload(payload: bytes, origin: str='файла') -> dict:
 plugin_file = _plugin_self_path()
 backup_file = plugin_file + '.pre-update.bak'
 tmp_file = plugin_file + '.update.tmp'
 result = {'ok': False, 'changed': False, 'current_version': VERSION, 'remote_version': None, 'backup_file': backup_file, 'error': None}
 try:
  _, remote_version, remote_hash = _validate_plugin_update_payload(payload)
  result['remote_version'] = remote_version
  with open(plugin_file, 'rb') as file:
   current_hash = hashlib.sha256(file.read()).hexdigest()
  if current_hash == remote_hash:
   result.update(ok=True, changed=False)
   return result
  with open(tmp_file, 'wb') as file:
   file.write(payload)
   file.flush()
   os.fsync(file.fileno())
  try:
   os.chmod(tmp_file, os.stat(plugin_file).st_mode)
  except Exception:
   pass
  shutil.copy2(plugin_file, backup_file)
  os.replace(tmp_file, plugin_file)
  _cleanup_plugin_bytecode(plugin_file)
  result.update(ok=True, changed=True)
  logger.warning('%s plugin updated from %s: %s -> %s', PREFIX, origin, VERSION, remote_version)
 except Exception as error:
  result['error'] = str(error)
  logger.exception('%s plugin update failed: %s', PREFIX, error)
  try:
   if os.path.exists(tmp_file):
    os.remove(tmp_file)
  except Exception:
   pass
 return result

def _plugin_update_candidate_urls() -> List[str]:
 urls = []
 def add(value: Any) -> None:
  value = str(value or '').strip()
  if value and value.casefold().startswith('https://') and value not in urls:
   urls.append(value)
 add(PLUGIN_UPDATE_URL)
 base_url = DEFAULT_SERVER_URL
 if not _db_locked():
  try:
   server = _server_cfg()
   add(server.get('plugin_update_url'))
   base_url = str(server.get('url') or DEFAULT_SERVER_URL).strip().rstrip('/')
  except Exception:
   base_url = DEFAULT_SERVER_URL
 base_url = str(base_url or '').strip().rstrip('/')
 if base_url.casefold().startswith('https://'):
  query = urlencode({'uuid': UUID, 'name': NAME, 'version': VERSION})
  for path in (f'/api/v1/plugin/update?{query}', f'/api/v1/plugin/latest?{query}', f'/api/v1/plugin/download?{query}', f'/api/plugin/update?{query}', f'/plugins/{quote(NAME)}.py', f'/{quote(NAME)}.py'):
   add(base_url + path)
 return urls

def _plugin_update_json_info(payload: bytes) -> Tuple[Optional[bytes], Optional[str], Optional[str], Optional[bool]]:
 raw = bytes(payload or b'').lstrip()
 if not raw.startswith((b'{', b'[')):
  return (None, None, None, None)
 try:
  data = json.loads(raw.decode('utf-8-sig'))
 except Exception:
  return (None, None, None, None)
 if not isinstance(data, dict):
  return (None, None, None, None)
 nested = data.get('data')
 if isinstance(nested, dict):
  merged = dict(data)
  merged.update(nested)
  data = merged
 remote_version = str(data.get('latest_version') or data.get('remote_version') or data.get('version') or '').strip() or None
 update_available = data.get('update_available')
 if update_available is None and 'has_update' in data:
  update_available = data.get('has_update')
 if update_available is not None:
  update_available = bool(update_available)
 for key in ('source', 'plugin_source', 'content', 'python'):
  value = data.get(key)
  if isinstance(value, str) and value.strip():
   return (value.encode('utf-8'), remote_version, None, update_available)
 for key in ('content_base64', 'payload_base64', 'source_base64'):
  value = data.get(key)
  if isinstance(value, str) and value.strip():
   try:
    return (base64.b64decode(value), remote_version, None, update_available)
   except Exception:
    pass
 download_url = ''
 for key in ('plugin_update_url', 'download_url', 'file_url', 'raw_url', 'update_url'):
  value = str(data.get(key) or '').strip()
  if value:
   download_url = value
   break
 if not download_url:
  value = str(data.get('url') or '').strip()
  if value.casefold().startswith('https://') and (value.casefold().endswith('.py') or 'download' in value.casefold() or 'update' in value.casefold()):
   download_url = value
 return (None, remote_version, download_url or None, update_available)

def _fetch_plugin_update_candidate(url: str) -> Tuple[Optional[bytes], Optional[str], Optional[bool]]:
 request = urllib.request.Request(url, headers={'Accept': 'text/plain, application/octet-stream, application/json, */*', 'User-Agent': f'{NAME}/{VERSION} self-updater', 'Cache-Control': 'no-cache'})
 with urllib.request.urlopen(request, timeout=45) as response:
  payload = response.read(5 * 1024 * 1024 + 1)
 embedded, remote_version, redirect_url, update_available = _plugin_update_json_info(payload)
 if embedded is not None:
  return (embedded, remote_version, update_available)
 if redirect_url:
  if not redirect_url.casefold().startswith('https://'):
   raise RuntimeError('сервер обновлений вернул небезопасную ссылку')
  request = urllib.request.Request(redirect_url, headers={'Accept': 'text/plain, application/octet-stream, */*', 'User-Agent': f'{NAME}/{VERSION} self-updater', 'Cache-Control': 'no-cache'})
  with urllib.request.urlopen(request, timeout=45) as response:
   return (response.read(5 * 1024 * 1024 + 1), remote_version, update_available)
 if payload.lstrip().startswith((b'{', b'[')):
  return (None, remote_version, update_available)
 return (payload, remote_version, update_available)

def _download_online_plugin_update() -> dict:
 pending_file = _pending_update_file()
 result = {'ok': False, 'changed': False, 'current_version': VERSION, 'remote_version': None, 'pending_file': pending_file, 'error': None}
 errors = []
 try:
  candidates = _plugin_update_candidate_urls()
  if not _db_locked():
   try:
    ok, data, code = _server_signed_post('api/v1/plugin/update', {'current_version': VERSION})
    if ok and isinstance(data, dict):
     embedded, announced_version, redirect_url, update_available = _plugin_update_json_info(_stable_json(data).encode('utf-8'))
     if redirect_url and redirect_url.casefold().startswith('https://') and redirect_url not in candidates:
      candidates.insert(0, redirect_url)
     if embedded is not None:
      _, remote_version, _ = _validate_plugin_update_payload(embedded)
      result['remote_version'] = remote_version
      if _plugin_version_key(remote_version) <= _plugin_version_key(VERSION):
       result.update(ok=True, changed=False)
       return result
      with open(pending_file, 'wb') as file:
       file.write(embedded)
       file.flush()
       os.fsync(file.fileno())
      result.update(ok=True, changed=True)
      return result
     if announced_version and (_plugin_version_key(announced_version) <= _plugin_version_key(VERSION) or update_available is False):
      result.update(ok=True, changed=False, remote_version=announced_version)
      return result
    elif code not in {'HTTP_404', 'HTTP_405', 'NOT_FOUND', 'METHOD_NOT_ALLOWED'}:
     errors.append('api/v1/plugin/update: ' + str(code))
   except Exception as error:
    errors.append('api/v1/plugin/update: ' + str(error))
  if not candidates:
   raise RuntimeError('не удалось определить адрес сервера обновлений')
  for update_url in candidates:
   try:
    payload, announced_version, update_available = _fetch_plugin_update_candidate(update_url)
    if payload is None:
     if announced_version and (_plugin_version_key(announced_version) <= _plugin_version_key(VERSION) or update_available is False):
      try:
       if os.path.exists(pending_file):
        os.remove(pending_file)
      except Exception:
       pass
      result.update(ok=True, changed=False, remote_version=announced_version)
      return result
     errors.append(f'{urlparse(update_url).path or "/"}: сервер не вернул файл')
     continue
    _, remote_version, _ = _validate_plugin_update_payload(payload)
    result['remote_version'] = remote_version
    if _plugin_version_key(remote_version) <= _plugin_version_key(VERSION):
     try:
      if os.path.exists(pending_file):
       os.remove(pending_file)
     except Exception:
      pass
     result.update(ok=True, changed=False)
     return result
    with open(pending_file, 'wb') as file:
     file.write(payload)
     file.flush()
     os.fsync(file.fileno())
    result.update(ok=True, changed=True)
    if not PLUGIN_UPDATE_URL and not _db_locked():
     try:
      server = _server_cfg()
      if update_url.casefold().endswith('.py'):
       server['plugin_update_url'] = update_url
       _db_save()
     except Exception:
      pass
    return result
   except Exception as error:
    errors.append(f'{urlparse(update_url).path or "/"}: {error}')
  compact = '; '.join(errors[-4:])
  raise RuntimeError('сервер AutoOffline не отдал корректный файл обновления' + (f': {compact}' if compact else ''))
 except Exception as error:
  result['error'] = str(error)
  logger.exception('%s online update check failed: %s', PREFIX, error)
  try:
   if os.path.exists(pending_file):
    os.remove(pending_file)
  except Exception:
   pass
 return result

def _install_pending_plugin_update() -> dict:
 pending_file = _pending_update_file()
 if not os.path.isfile(pending_file):
  return {'ok': False, 'changed': False, 'current_version': VERSION, 'remote_version': None, 'backup_file': '', 'error': 'файл обновления не найден. Сначала нажмите «Обновить онлайн»'}
 with open(pending_file, 'rb') as file:
  payload = file.read()
 result = _install_plugin_payload(payload, 'online-обновления')
 try:
  os.remove(pending_file)
 except Exception:
  pass
 return result

def _plugin_update_online(cardinal: 'Cardinal', call) -> None:
 bot = cardinal.telegram.bot
 chat_id = call.message.chat.id
 _answer(bot, call, 'Проверяю обновление…')
 _safe_edit(bot, chat_id, call.message.id, '⏬ <b>Проверяю новую версию…</b>\n\nСкачиваю файл и проверяю его. Установка начнётся только после подтверждения.', K())
 result = _download_online_plugin_update()
 if result.get('ok') and result.get('changed'):
  kb = K()
  kb.row(B('✅ Обновить', callback_data=CB_UPDATE_YES), B('❌ Отмена', callback_data=CB_UPDATE_NO))
  kb.row(B('◀️ Назад', callback_data=CB_UPDATE))
  text = f"🆕 <b>Найдена новая версия плагина.</b>\n\nТекущая версия: <code>{escape(str(result.get('current_version')))}</code>\nНовая версия: <code>{escape(str(result.get('remote_version')))}</code>\n\nФайл скачан во временный буфер и прошёл проверку. Установить обновление сейчас?"
 elif result.get('ok'):
  kb = _update_kb()
  text = f"✅ <b>Обновление не требуется.</b>\n\nУстановлена версия: <code>{escape(str(result.get('current_version')))}</code>\nВерсия по ссылке: <code>{escape(str(result.get('remote_version') or 'не определена'))}</code>\n\nФайл плагина и данные не изменены."
 else:
  kb = _update_kb()
  text = f"❌ <b>Не удалось проверить обновление.</b>\n\nОшибка: <code>{escape(str(result.get('error') or 'неизвестная ошибка'))}</code>\n\nТекущий файл и данные не изменены."
 _safe_edit(bot, chat_id, call.message.id, text, kb)

def _plugin_update_online_yes(cardinal: 'Cardinal', call) -> None:
 bot = cardinal.telegram.bot
 chat_id = call.message.chat.id
 _answer(bot, call, 'Устанавливаю обновление…')
 _safe_edit(bot, chat_id, call.message.id, '⏬ <b>Устанавливаю обновление…</b>\n\nСоздаю резервную копию и заменяю файл плагина.', K())
 result = _install_pending_plugin_update()
 if result.get('ok') and result.get('changed'):
  text = f"✅ <b>Плагин обновлён.</b>\n\nВерсия: <code>{escape(str(result.get('current_version')))}</code> → <code>{escape(str(result.get('remote_version')))}</code>\nРезервная копия: <code>{escape(os.path.basename(str(result.get('backup_file') or '')))}</code>\nАккаунты, лоты, заказы и настройки сохранены.\n\n🔁 Выполните <code>/restart</code>."
 elif result.get('ok'):
  text = '✅ <b>Этот файл уже установлен.</b>\n\nОсновной файл и данные не изменены.'
 else:
  text = f"❌ <b>Обновление не установлено.</b>\n\nОшибка: <code>{escape(str(result.get('error') or 'неизвестная ошибка'))}</code>\n\nТекущий файл и данные не изменены."
 _safe_edit(bot, chat_id, call.message.id, text, _update_kb())

def _plugin_update_online_no(cardinal: 'Cardinal', call) -> None:
 try:
  pending_file = _pending_update_file()
  if os.path.exists(pending_file):
   os.remove(pending_file)
 except Exception:
  pass
 _answer(cardinal.telegram.bot, call, 'Обновление отменено.')
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, '❌ <b>Обновление отменено.</b>\n\nФайл плагина и данные не изменены.', _update_kb())

def _delete_plugin_confirm(cardinal: 'Cardinal', call) -> None:
 _answer(cardinal.telegram.bot, call)
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, _delete_plugin_text(), _delete_plugin_kb())

def _delete_plugin(cardinal: 'Cardinal', call) -> None:
 bot = cardinal.telegram.bot
 _answer(bot, call)
 ok = False
 err = None
 candidates = [(cardinal, 'delete_plugin'), (cardinal, 'remove_plugin'), (cardinal, 'uninstall_plugin'), (cardinal, 'unload_plugin'), (getattr(cardinal, 'plugins', None), 'delete_plugin'), (getattr(cardinal, 'plugins', None), 'remove_plugin'), (getattr(cardinal, 'plugin_manager', None), 'delete_plugin'), (getattr(cardinal, 'plugin_manager', None), 'remove_plugin'), (getattr(cardinal, 'plugin_manager', None), 'unload_plugin')]
 for obj, method in candidates:
  try:
   if obj is None:
    continue
   fn = getattr(obj, method, None)
   if callable(fn):
    fn(UUID)
    ok = True
    break
  except Exception as e:
   err = e
 if not ok:
  try:
   path = _plugin_self_path()
   if os.path.isfile(path):
    os.remove(path)
    _cleanup_plugin_bytecode(path)
    ok = True
  except Exception as e:
   err = e
 if ok:
  try:
   _safe_edit(bot, call.message.chat.id, call.message.id, '✅ <b>Плагин удалён.</b>\n\nДанные AutoOffline сохранены. Если пункт ещё виден в меню — перезапустите Cardinal.', K())
  except Exception:
   pass
  return
 _safe_edit(bot, call.message.chat.id, call.message.id, '❌ <b>Не удалось удалить плагин автоматически.</b>\n\nУдалите его через Cardinal → Плагины.\n\nОшибка: <code>' + escape(str(err) if err else '—') + '</code>', _home_kb())

def _open_account(cardinal: 'Cardinal', call) -> None:
 account = _find_account(str(call.data).split(':')[-1])
 if account is None:
  _answer(cardinal.telegram.bot, call, 'Аккаунт не найден.', True)
  return
 _open_panel(cardinal, call, _account_text(account), _account_kb(account))

def _toggle_account(cardinal: 'Cardinal', call) -> None:
 account = _find_account(str(call.data).split(':')[-1])
 if account is None:
  return
 account['enabled'] = not bool(account.get('enabled', True))
 _db_save()
 _log('SETTINGS', 'Состояние аккаунта изменено', account_id=account['id'], enabled=account['enabled'])
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, _account_text(account), _account_kb(account))
 _answer(cardinal.telegram.bot, call)

def _delete_account_confirm(cardinal: 'Cardinal', call) -> None:
 account = _find_account(str(call.data).split(':')[-1])
 if account is None:
  return
 kb = K()
 kb.row(B('✅ Да, удалить', callback_data=f"{CB_ACCOUNT_DELETE_YES}:{account['id']}"))
 kb.row(B('◀️ Нет', callback_data=f"{CB_ACCOUNT_OPEN}:{account['id']}"))
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, f"🗑 Удалить аккаунт <b>{escape(str(account.get('name')))}</b>?\n\nПривязки к этому ID будут очищены. Лоты без оставшихся аккаунтов автоматически отключатся.", kb)
 _answer(cardinal.telegram.bot, call)

def _delete_account(cardinal: 'Cardinal', call) -> None:
 aid = str(call.data).split(':')[-1]
 db = _db_get()
 db['accounts'] = [x for x in db.get('accounts', []) if str(x.get('id')) != aid]
 disabled_lots = []
 for lot in db.get('lots', []):
  previous = [str(x) for x in lot.get('account_ids', [])]
  lot['account_ids'] = [x for x in lot.get('account_ids', []) if str(x) != aid]
  if aid in previous and (not lot['account_ids']):
   lot['enabled'] = False
   disabled_lots.append(str(lot.get('title') or lot.get('funpay_lot_id') or lot.get('id')))
   try:
    synced, reason = _set_funpay_lot_enabled(cardinal, lot.get('funpay_lot_id'), False)
    lot['funpay_sync'] = {'ok': synced, 'reason': reason, 'active': False if synced else _lot_funpay_active(lot), 'ts': _now()}
    if synced:
     lot['funpay_active'] = False
   except Exception as e:
    lot['funpay_sync'] = {'ok': False, 'reason': str(e), 'active': _lot_funpay_active(lot), 'ts': _now()}
 _db_save()
 _log('SETTINGS', 'Аккаунт удалён', account_id=aid, disabled_lots=', '.join(disabled_lots))
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, _accounts_text(), _accounts_kb())
 notice = 'Удалено.'
 if disabled_lots:
  notice += f' Отключено лотов: {len(disabled_lots)}.'
 _answer(cardinal.telegram.bot, call, notice)

def _open_lot(cardinal: 'Cardinal', call) -> None:
 lot = _find_lot(str(call.data).split(':')[-1])
 if lot is None:
  _answer(cardinal.telegram.bot, call, 'Лот не найден.', True)
  return
 active, reason = _get_funpay_lot_enabled(cardinal, lot.get('funpay_lot_id'))
 lot['funpay_sync'] = {'ok': active is not None, 'reason': reason, 'active': active, 'ts': _now()}
 if active is not None:
  lot['funpay_active'] = active
 _db_save()
 _open_panel(cardinal, call, _lot_text(lot), _lot_kb(lot))

def _get_funpay_lot_enabled(cardinal: 'Cardinal', funpay_lot_id: Any) -> Tuple[Optional[bool], str]:
 account = getattr(cardinal, 'account', None)
 if account is None:
  return (None, 'FunPay account недоступен')
 lot_reference = _normalize_lot_reference(funpay_lot_id)
 if not lot_reference or not lot_reference.isdigit():
  return (None, 'некорректный LOT ID')
 try:
  fields = account.get_lot_fields(int(lot_reference))
  if fields is None:
   return (None, 'get_lot_fields вернул пустой результат')
  return (bool(getattr(fields, 'active', False)), 'ok')
 except Exception as e:
  return (None, str(e) or e.__class__.__name__)

def _set_funpay_lot_enabled(cardinal: 'Cardinal', funpay_lot_id: Any, enabled: bool) -> Tuple[bool, str]:
 account = getattr(cardinal, 'account', None)
 if account is None:
  return (False, 'FunPay account недоступен')
 lot_reference = _normalize_lot_reference(funpay_lot_id)
 if not lot_reference or not lot_reference.isdigit():
  return (False, 'некорректный LOT ID')
 lot_id = int(lot_reference)
 desired = bool(enabled)
 last_error = 'неизвестная ошибка'
 for attempt in range(1, 4):
  try:
   fields = account.get_lot_fields(lot_id)
   if fields is None:
    raise RuntimeError('get_lot_fields вернул пустой результат')
   if bool(getattr(fields, 'active', False)) == desired:
    return (True, 'уже в нужном состоянии')
   fields.active = desired
   result = account.save_lot(fields)
   if isinstance(result, dict) and (result.get('success') is False or result.get('ok') is False):
    raise RuntimeError(str(result.get('error') or result.get('errors') or 'FunPay отклонил сохранение'))
   verified, verify_reason = _get_funpay_lot_enabled(cardinal, lot_id)
   if verified is desired:
    return (True, 'ok')
   if verified is None:
    return (True, f'сохранено, проверка недоступна: {verify_reason}')
   last_error = 'FunPay не подтвердил новое состояние'
  except Exception as e:
   last_error = str(e) or e.__class__.__name__
  if attempt < 3:
   time.sleep(1.0)
 return (False, last_error)

def _denuvo_account_has_capacity(account: dict) -> bool:
 if not bool(account.get('enabled', True)):
  return False
 denuvo = account.get('denuvo') or {}
 if not bool(denuvo.get('enabled')):
  return False
 if _safe_int(denuvo.get('cooldown_until'), 0) > _now():
  return False
 limit = max(1, _safe_int(denuvo.get('slot_limit'), 5, 1, 10000) - _safe_int(denuvo.get('reserve'), 0, 0, 9999))
 return _safe_int(denuvo.get('active_slots'), 0, 0, 10000) < limit

def _sync_denuvo_lot_capacity(cardinal: Optional['Cardinal']=None) -> None:
 if _db_locked():
  return
 cardinal = cardinal or _CARDINAL
 if cardinal is None:
  return
 changed = False
 for lot in _db_get().get('lots', []):
  bound = _lot_bound_accounts(lot)
  if not bound or not any((bool((account.get('denuvo') or {}).get('enabled')) for account in bound)):
   continue
  has_capacity = any((_denuvo_account_has_capacity(account) for account in bound))
  auto_reason = str(lot.get('auto_funpay_disabled_reason') or '')
  plugin_enabled = bool(lot.get('enabled', True))
  current_funpay = _lot_funpay_active(lot)
  if not has_capacity and plugin_enabled and (current_funpay is not False):
   synced, reason = _set_funpay_lot_enabled(cardinal, lot.get('funpay_lot_id'), False)
   lot['funpay_sync'] = {'ok': synced, 'reason': reason, 'active': False if synced else current_funpay, 'ts': _now()}
   changed = True
   if synced:
    lot['funpay_active'] = False
    lot['auto_funpay_disabled_reason'] = 'denuvo_capacity'
    lot['auto_funpay_disabled_at'] = _now()
    _log('LOT', 'Лот автоматически выключен на FunPay', lot_id=lot.get('id'), funpay_lot_id=lot.get('funpay_lot_id'), reason='все Denuvo-активации заняты', synced=True)
    _notify('lot_status', f"🔴 <b>Лот автоматически выключен на FunPay</b>\nЛот: <b>{escape(str(lot.get('title') or lot.get('funpay_lot_id')))}</b>\nПричина: все Denuvo-активации заняты.")
   else:
    _log('ERROR', 'Не удалось автоматически выключить лот на FunPay', lot_id=lot.get('id'), funpay_lot_id=lot.get('funpay_lot_id'), error=reason)
  elif has_capacity and auto_reason == 'denuvo_capacity' and plugin_enabled:
   synced, reason = _set_funpay_lot_enabled(cardinal, lot.get('funpay_lot_id'), True)
   lot['funpay_sync'] = {'ok': synced, 'reason': reason, 'active': True if synced else current_funpay, 'ts': _now()}
   changed = True
   if synced:
    lot['funpay_active'] = True
    lot.pop('auto_funpay_disabled_reason', None)
    lot.pop('auto_funpay_disabled_at', None)
    _log('LOT', 'Лот автоматически включён на FunPay', lot_id=lot.get('id'), funpay_lot_id=lot.get('funpay_lot_id'), reason='освободилась Denuvo-активация', synced=True)
    _notify('lot_status', f"🟢 <b>Лот автоматически включён на FunPay</b>\nЛот: <b>{escape(str(lot.get('title') or lot.get('funpay_lot_id')))}</b>\nПричина: освободилась Denuvo-активация.")
   else:
    _log('ERROR', 'Не удалось автоматически включить лот на FunPay', lot_id=lot.get('id'), funpay_lot_id=lot.get('funpay_lot_id'), error=reason)
 if changed:
  _db_save()

def _toggle_lot(cardinal: 'Cardinal', call) -> None:
 lot = _find_lot(str(call.data).split(':')[-1])
 if lot is None:
  _answer(cardinal.telegram.bot, call, 'Лот не найден.', True)
  return
 target_state = not bool(lot.get('enabled', True))
 lot['enabled'] = target_state
 if not target_state:
  lot.pop('auto_funpay_disabled_reason', None)
  lot.pop('auto_funpay_disabled_at', None)
 _db_save()
 reason = 'включён в плагине' if target_state else 'выключен в плагине'
 _log('LOT', reason, lot_id=lot.get('id'), funpay_lot_id=lot.get('funpay_lot_id'), enabled=target_state)
 _notify('lot_status', f"{('🟢' if target_state else '🔴')} <b>Лот {escape(str(lot.get('title') or lot.get('funpay_lot_id')))}</b> {escape(reason)}.")
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, _lot_text(lot), _lot_kb(lot))
 _answer(cardinal.telegram.bot, call, 'Лот включён в плагине.' if target_state else 'Лот выключен в плагине.')

def _toggle_funpay_lot(cardinal: 'Cardinal', call) -> None:
 lot = _find_lot(str(call.data).split(':')[-1])
 if lot is None:
  _answer(cardinal.telegram.bot, call, 'Лот не найден.', True)
  return
 current = _lot_funpay_active(lot)
 if current is None:
  current, check_reason = _get_funpay_lot_enabled(cardinal, lot.get('funpay_lot_id'))
  lot['funpay_sync'] = {'ok': current is not None, 'reason': check_reason, 'active': current, 'ts': _now()}
  if current is None:
   _db_save()
   _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, _lot_text(lot), _lot_kb(lot))
   _answer(cardinal.telegram.bot, call, 'Не удалось проверить лот: ' + str(check_reason)[:130], True)
   return
  lot['funpay_active'] = current
 target_state = not bool(current)
 synced, sync_reason = _set_funpay_lot_enabled(cardinal, lot.get('funpay_lot_id'), target_state)
 lot['funpay_sync'] = {'ok': synced, 'reason': sync_reason, 'active': target_state if synced else current, 'ts': _now()}
 if not synced:
  _db_save()
  _log('ERROR', 'FunPay не изменил состояние лота', lot_id=lot.get('id'), funpay_lot_id=lot.get('funpay_lot_id'), enabled=target_state, error=sync_reason)
  _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, _lot_text(lot), _lot_kb(lot))
  _answer(cardinal.telegram.bot, call, 'Не удалось переключить FunPay: ' + str(sync_reason)[:130], True)
  return
 lot['funpay_active'] = target_state
 lot.pop('auto_funpay_disabled_reason', None)
 lot.pop('auto_funpay_disabled_at', None)
 _db_save()
 reason = 'включён на FunPay' if target_state else 'выключен на FunPay'
 _log('LOT', reason, lot_id=lot.get('id'), funpay_lot_id=lot.get('funpay_lot_id'), enabled=target_state, synced=True)
 _notify('lot_status', f"{('🟢' if target_state else '🔴')} <b>Лот {escape(str(lot.get('title') or lot.get('funpay_lot_id')))}</b> {escape(reason)}.")
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, _lot_text(lot), _lot_kb(lot))
 _answer(cardinal.telegram.bot, call, 'Лот включён на FunPay.' if target_state else 'Лот выключен на FunPay.')

def _open_lot_account_picker(cardinal: 'Cardinal', call) -> None:
 lot = _find_lot(str(call.data).split(':')[-1])
 _show_lot_account_picker(cardinal, call, 'edit', 0, lot)

def _lot_account_page(cardinal: 'Cardinal', call) -> None:
 parts = str(call.data).split(':')
 if len(parts) < 4:
  return
 mode = parts[2]
 if mode == 'a':
  _show_lot_account_picker(cardinal, call, 'add', _safe_int(parts[3], 0))
  return
 if mode == 'e' and len(parts) >= 5:
  lot = _find_lot(parts[3])
  _show_lot_account_picker(cardinal, call, 'edit', _safe_int(parts[4], 0), lot)

def _lot_account_pick(cardinal: 'Cardinal', call) -> None:
 bot = cardinal.telegram.bot
 parts = str(call.data).split(':')
 if len(parts) < 4:
  return
 mode = parts[2]
 if mode == 'a':
  state = _fsm.get(call.message.chat.id)
  if not state or state.get('mode') != 'add_lot':
   _answer(bot, call, 'Добавление лота уже завершено.', True)
   return
  account = _find_account(parts[3])
  account_type = _canonical_account_type(state.setdefault('data', {}).get('account_type'))
  if account is None or _canonical_account_type(account.get('type')) != account_type:
   _answer(bot, call, 'Аккаунт не найден или несовместим.', True)
   return
  state['data']['selected_account_id'] = str(account.get('id'))
  state['step'] = 'command'
  _safe_edit(bot, call.message.chat.id, call.message.id, f"➕ <b>Добавление лота</b>\n\nАккаунт: <b>{escape(str(account.get('name') or account.get('id')))}</b>\nТип: <b>{escape(ACCOUNT_TYPES.get(account_type, account_type))}</b>\n\nОтправьте команду покупателя, например <code>!code_game</code>.", _cancel_kb(CB_LOTS))
  _answer(bot, call, 'Аккаунт выбран.')
  return
 if mode == 'e' and len(parts) >= 5:
  lot = _find_lot(parts[3])
  account = _find_account(parts[4])
  if lot is None or account is None:
   _answer(bot, call, 'Лот или аккаунт не найден.', True)
   return
  if _canonical_account_type(account.get('type')) != _canonical_account_type(lot.get('account_type')):
   _answer(bot, call, 'Аккаунт несовместим с типом лота.', True)
   return
  lot['account_ids'] = [str(account.get('id'))]
  _db_save()
  _log('SETTINGS', 'Аккаунт лота изменён', lot_id=lot.get('id'), funpay_lot_id=lot.get('funpay_lot_id'), account_id=account.get('id'))
  _safe_edit(bot, call.message.chat.id, call.message.id, _lot_text(lot), _lot_kb(lot))
  _answer(bot, call, 'Аккаунт привязан.')

def _delete_lot_confirm(cardinal: 'Cardinal', call) -> None:
 lot = _find_lot(str(call.data).split(':')[-1])
 if lot is None:
  return
 kb = K()
 kb.row(B('✅ Да, удалить', callback_data=f"{CB_LOT_DELETE_YES}:{lot['id']}"))
 kb.row(B('◀️ Нет', callback_data=f"{CB_LOT_OPEN}:{lot['id']}"))
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, f"🗑 Удалить лот <b>{escape(str(lot.get('title')))}</b>?\n\nЗаказы и история выдач останутся в базе.", kb)
 _answer(cardinal.telegram.bot, call)

def _delete_lot(cardinal: 'Cardinal', call) -> None:
 lid = str(call.data).split(':')[-1]
 db = _db_get()
 db['lots'] = [x for x in db.get('lots', []) if str(x.get('id')) != lid]
 _db_save()
 _log('SETTINGS', 'Лот удалён', lot_id=lid)
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, _lots_text(), _lots_kb())
 _answer(cardinal.telegram.bot, call, 'Удалено.')

def _toggle_notification(cardinal: 'Cardinal', call) -> None:
 kind = str(call.data).split(':')[-1]
 if kind not in NOTIFICATION_LABELS or _db_locked():
  return
 notif = _db_get()['global'].setdefault('notifications', {})
 notif[kind] = not bool(notif.get(kind, True))
 _db_save()
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, _notifications_text(), _notifications_kb())
 _answer(cardinal.telegram.bot, call)

def _log_html_class(event_type: str) -> str:
 event_name = str(event_type or 'INFO').upper()
 if event_name in {'ERROR', 'FAILED', 'CRITICAL'}:
  return 'danger'
 if event_name in {'DENIED', 'REFUND', 'REFUND_IGNORED', 'WARNING', 'WARN', 'ORDER_UNRESOLVED', 'ORDER_MATCH_FAILED'}:
  return 'warning'
 if event_name in {'ISSUED', 'ORDER_REPAIRED'}:
  return 'success'
 return 'info'

def _logs_html(entries: List[dict]) -> bytes:
 cards = []
 for item in entries:
  event_type = str(item.get('type') or 'INFO').upper()
  icon, label, _ = _log_meta(event_type)
  detail_items = []
  for detail in _format_log_details(item.get('details') or {}):
   if ': ' in detail:
    key, value = detail.split(': ', 1)
    detail_items.append(f'<span><b>{escape(key)}</b>: <code>{escape(value)}</code></span>')
   else:
    detail_items.append(f'<span>{escape(detail)}</span>')
  details_html = ''.join(detail_items) or '<span class=muted>без дополнительных данных</span>'
  cards.append(f"""<article class="log {_log_html_class(event_type)}"><div class="head"><span class="badge">{icon} {escape(label)}</span><time>{escape(_fmt_dt(item.get('ts')))}</time></div><div class="message">{escape(str(item.get('message') or ''))}</div><div class="details">{details_html}</div></article>""")
 body = ''.join(cards) or '<div class="empty">Лог пока пуст.</div>'
 document = f'<!doctype html>\n<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n<title>AutoOffline — лицензионные логи</title><style>\n:root{{--bg:#0b1020}}:root{{--card:#141b2d}}:root{{--text:#eef2ff}}:root{{--muted:#94a3b8}}:root{{--line:#27324a}}:root{{--info:#38bdf8}}:root{{--success:#4ade80}}:root{{--warning:#facc15}}:root{{--danger:#fb7185}}\n*{{box-sizing:border-box}}\nbody{{margin:0}}body{{background:var(--bg)}}body{{color:var(--text)}}body{{font:14px/1.45 Inter,Segoe UI,Arial,sans-serif}}\nmain{{max-width:1100px}}main{{margin:auto}}main{{padding:28px 18px}}\nh1{{margin:0 0 4px}}h1{{font-size:26px}}\n.sub{{color:var(--muted)}}.sub{{margin-bottom:22px}}\n.log{{background:var(--card)}}.log{{border:1px solid var(--line)}}.log{{border-left:5px solid var(--info)}}.log{{border-radius:12px}}.log{{padding:14px 16px}}.log{{margin:10px 0}}.log{{box-shadow:0 8px 22px #0004}}\n.log.success{{border-left-color:var(--success)}}.log.warning{{border-left-color:var(--warning)}}.log.danger{{border-left-color:var(--danger)}}\n.head{{display:flex}}.head{{justify-content:space-between}}.head{{gap:12px}}.head{{align-items:center}}\n.badge{{font-weight:800}}.badge{{letter-spacing:.03em}}\ntime{{color:var(--muted)}}time{{white-space:nowrap}}\n.message{{font-size:16px}}.message{{font-weight:650}}.message{{margin:8px 0 10px}}\n.details{{display:flex}}.details{{flex-wrap:wrap}}.details{{gap:7px}}\n.details span{{background:#0d1425}}.details span{{border:1px solid var(--line)}}.details span{{border-radius:8px}}.details span{{padding:5px 8px}}.details span{{color:#cbd5e1}}\ncode{{color:#e2e8f0}}.muted,.empty{{color:var(--muted)}}\n</style></head><body><main><h1>AutoOffline — цветные логи лицензии / API</h1><div class="sub">Сформировано: {escape(_fmt_dt(_now()))} · секреты скрыты</div>{body}</main></body></html>'
 return document.encode('utf-8')

def _send_logs(cardinal: 'Cardinal', call) -> None:
 bot = cardinal.telegram.bot
 sent_any = False
 try:
  if os.path.isfile(TEXT_LOG_FILE):
   raw = open(TEXT_LOG_FILE, 'rb').read()
  else:
   raw = b''
  bot.send_document(call.message.chat.id, ('log.txt', raw), caption='📄 Рабочий log.txt: выдачи кодов, заказы, лимиты, настройки и ошибки плагина.')
  sent_any = True
 except Exception as e:
  logger.warning('%s text log send failed: %s', PREFIX, e)
 if not _db_locked():
  try:
   entries = [item for item in _db_get().get('logs', []) if _is_colored_license_event(str(item.get('type') or ''), str(item.get('message') or ''))]
   payload = _logs_html(entries)
   filename = f"AutoOffline-license-logs-{time.strftime('%Y%m%d-%H%M%S')}.html"
   bot.send_document(call.message.chat.id, (filename, payload), caption='🎨 Цветные логи: лицензия, регистрация и сервер AutoOffline. Секреты скрыты.')
   sent_any = True
  except Exception as e:
   logger.warning('%s colored log send failed: %s', PREFIX, e)
 _answer(bot, call, 'Логи отправлены.' if sent_any else 'Не удалось отправить логи.', not sent_any)

def _send_backup(cardinal: 'Cardinal', call) -> None:
 bot = cardinal.telegram.bot
 if not os.path.isfile(DB_FILE):
  _answer(bot, call, 'База не найдена.', True)
  return
 raw = open(DB_FILE, 'rb').read()
 filename = f"AutoOffline-backup-{time.strftime('%Y%m%d-%H%M%S')}.json"
 bot.send_document(call.message.chat.id, (filename, raw), caption='📀 Зашифрованный бэкап AutoOffline.')
 _answer(bot, call, 'Бэкап отправлен.')
 _notify('maintenance', '📤 <b>Скачан зашифрованный бэкап AutoOffline.</b>')

def _check_database(cardinal: 'Cardinal', call) -> None:
 bot = cardinal.telegram.bot
 repaired = ''
 try:
  try:
   envelope = _read_envelope()
  except Exception:
   source = _repair_database_file()
   repaired = ' Восстановление: резервная копия.' if source == 'backup' else ' Восстановление: создана новая база.'
   envelope = _read_envelope()
  if envelope is None:
   _initialise_database()
   envelope = _read_envelope()
   repaired = ' База была отсутствующей и создана заново.'
  if str((envelope.get('kdf') or {}).get('mode') or '') == 'local' and _db_locked():
   _auto_unlock_local()
  details = 'Envelope корректен.' + repaired
  if not _db_locked():
   db = _ensure_db_shape(_db_get())
   _db_save()
   details += f" Расшифровка успешна: аккаунтов {len(db['accounts'])}, лотов {len(db['lots'])}, заказов {len(db['orders'])}."
  _answer(bot, call, details, True)
 except Exception as e:
  _answer(bot, call, 'Ошибка: ' + str(e), True)

def _reset_usage_confirm(cardinal: 'Cardinal', call) -> None:
 kb = K()
 kb.row(B('✅ Сбросить', callback_data=CB_RESET_USAGE_YES))
 kb.row(B('◀️ Нет', callback_data=CB_MAINTENANCE))
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, '♻️ <b>Сбросить usage?</b>\n\nЛимиты покупателей начнут считаться заново. Заказы и логи не удалятся.', kb)
 _answer(cardinal.telegram.bot, call)

def _reset_usage(cardinal: 'Cardinal', call) -> None:
 if not _db_locked():
  _db_get()['usage'] = {}
  _db_save()
  _log('MAINTENANCE', 'Usage сброшен')
 _safe_edit(cardinal.telegram.bot, call.message.chat.id, call.message.id, _maintenance_text(), _maintenance_kb())
 _answer(cardinal.telegram.bot, call, 'Usage сброшен.')

def _server_test(cardinal: 'Cardinal', call) -> None:
 ok, data, code, _ = _http_json('GET', 'api/v1/health')
 _answer(cardinal.telegram.bot, call, 'Соединение установлено.' if ok else 'Ошибка: ' + str(code), not ok)
 if ok:
  _log('SERVER', 'Проверка сервера успешна', response=data)

def _denuvo_check(cardinal: 'Cardinal', call) -> None:
 ok, data, code = _server_sync_status()
 if ok:
  _answer(cardinal.telegram.bot, call, f"Активных резерваций: {len(data.get('reservations', []))}", True)
  _log('DENUVO', 'Статус Denuvo синхронизирован', reservations=len(data.get('reservations', [])))
 else:
  _answer(cardinal.telegram.bot, call, 'Ошибка Denuvo: ' + str(code), True)
  _notify('denuvo', f'⚠️ <b>Ошибка проверки Denuvo</b>\n<code>{escape(str(code))}</code>')

def new_order_handler(cardinal: 'Cardinal', event: Any) -> None:
 try:
  if _db_locked() or not _db_get()['global'].get('plugin_enabled', True):
   return
  info = _extract_order_info(event)
  order_id = str(info.get('order_id') or '').strip()
  key = f'order:{order_id}' if order_id else f"order:{info.get('chat_id')}:{info.get('title')}"
  if _event_seen(key):
   return
  _record_order(info)
 except Exception as e:
  logger.exception('%s new_order_handler failed: %s', PREFIX, e)
  _log('ERROR', 'Ошибка обработки нового заказа', error=str(e))

def new_message_handler(cardinal: 'Cardinal', event: Any) -> None:
 try:
  raw_text = str(_field(_field(event, 'message'), 'text', '') or '').strip()
  if not raw_text:
   return
  if _db_locked():
   return
  db = _db_get()
  if not bool(db['global'].get('plugin_enabled', True)):
   return
  author = str(_field(_field(event, 'message'), 'author', '') or '').casefold()
  if author == 'funpay':
   if _mark_refund_from_system_message(event, raw_text):
    return
   _mark_order_from_system_message(event, raw_text)
   return
  command = _first_word(raw_text)
  if not command:
   return
  matches = [x for x in db.get('lots', []) if _normalize_command(x.get('command')) == command]
  if not matches:
   return
  return _process_code_request(cardinal, event, matches[0])
 except Exception as e:
  logger.exception('%s new_message_handler failed: %s', PREFIX, e)
  _log('ERROR', 'Ошибка обработки команды', error=str(e))

def init_cardinal(cardinal: 'Cardinal') -> None:
 global _CARDINAL
 _CARDINAL = cardinal
 try:
  _ensure_database_available()
  if not _db_locked():
   _ensure_server_identity()
   repaired_orders = 0
   for configured_lot in _db_get().get('lots', []):
    repaired_orders += _repair_orders_for_lot(configured_lot)
   _queue_recover_stale()
   _steam_queue_recover_stale()
   if repaired_orders:
    _log('ORDER_REPAIRED', 'При запуске восстановлены связи заказов с лотами', count=repaired_orders)
 except Exception as e:
  logger.exception('%s database init failed: %s', PREFIX, e)
 tg = cardinal.telegram
 bot = tg.bot
 try:
  cardinal.add_telegram_commands(UUID, [('autooffline', 'Открыть панель AutoOffline', True), ('ao', 'Открыть панель AutoOffline', True)])
 except Exception:
  pass
 tg.msg_handler(lambda m: _open_panel(cardinal, m, _home_text(), _home_kb()), commands=['autooffline', 'ao'])
 tg.msg_handler(lambda m: _handle_fsm(m, cardinal), func=lambda m: m.chat.id in _fsm, content_types=['text', 'document'])
 tg.msg_handler(lambda m: (_fsm_cleanup(bot, m.chat.id, _fsm.pop(m.chat.id, None) or {}), _safe_send_tg(bot, m.chat.id, '❌ Операция отменена.')), commands=['cancel'])
 tg.cbq_handler(lambda c: _open_panel(cardinal, c, _home_text(), _home_kb()), func=lambda c: c.data.startswith(f'{CBT_EDIT_PLUGIN}:{UUID}') or c.data.startswith(f'{CBT_PLUGIN_SETTINGS}:{UUID}') or c.data in {CB_HOME, CBT_BACK})
 tg.cbq_handler(lambda c: _open_panel(cardinal, c, _settings_text(), _settings_kb()), func=lambda c: c.data == CB_SETTINGS)
 tg.cbq_handler(lambda c: _open_panel(cardinal, c, _info_text(), _info_kb()), func=lambda c: c.data == CB_INFO)
 tg.cbq_handler(lambda c: (_fsm_start(c.message.chat.id, 'smakmail_key', 'value', c.message.id), _safe_edit(bot, c.message.chat.id, c.message.id, '📮 <b>SmakMail API key</b>\n\nОтправьте API key SmakMail. Для удаления ключа отправьте <code>-</code>.', _cancel_kb(CB_SETTINGS)), _answer(bot, c, 'Отправьте API key')), func=lambda c: c.data == CB_SMAKMAIL_KEY)
 tg.cbq_handler(lambda c: _open_panel(cardinal, c, _denuvo_center_text(), _denuvo_center_kb()), func=lambda c: c.data == CB_DENUVO_CENTER)
 tg.cbq_handler(lambda c: _denuvo_refresh_action(cardinal, c), func=lambda c: c.data == CB_DENUVO_REFRESH)
 tg.cbq_handler(lambda c: _denuvo_sync_action(cardinal, c), func=lambda c: c.data == CB_DENUVO_SYNC)
 tg.cbq_handler(lambda c: _denuvo_retry_action(cardinal, c), func=lambda c: c.data == CB_DENUVO_RETRY)
 tg.cbq_handler(lambda c: _denuvo_clear_action(cardinal, c), func=lambda c: c.data == CB_DENUVO_CLEAR)
 tg.cbq_handler(lambda c: _open_panel(cardinal, c, _state_text(), _state_kb()), func=lambda c: c.data == CB_STATE)
 tg.cbq_handler(lambda c: _open_panel(cardinal, c, _update_text(), _update_kb()), func=lambda c: c.data == CB_UPDATE)
 tg.cbq_handler(lambda c: (_fsm_start(c.message.chat.id, 'plugin_update_local', 'document', c.message.id), _safe_edit(bot, c.message.chat.id, c.message.id, '📥 <b>Локальное обновление</b>\n\nОтправьте новый файл AutoOffline с расширением <code>.py</code>.\n\nФайл будет проверен перед установкой. Текущий плагин сохранится в резервной копии, а данные останутся на месте.', _cancel_kb(CB_UPDATE)), _answer(bot, c, 'Пришлите файл плагина .py')), func=lambda c: c.data == CB_UPDATE_LOCAL)
 tg.cbq_handler(lambda c: _plugin_update_online(cardinal, c), func=lambda c: c.data == CB_UPDATE_ONLINE)
 tg.cbq_handler(lambda c: _plugin_update_online_yes(cardinal, c), func=lambda c: c.data == CB_UPDATE_YES)
 tg.cbq_handler(lambda c: _plugin_update_online_no(cardinal, c), func=lambda c: c.data == CB_UPDATE_NO)
 tg.cbq_handler(lambda c: _delete_plugin_confirm(cardinal, c), func=lambda c: c.data == CB_DELETE_PLUGIN)
 tg.cbq_handler(lambda c: _delete_plugin(cardinal, c), func=lambda c: c.data == CB_DELETE_PLUGIN_YES)
 tg.cbq_handler(lambda c: _open_panel(cardinal, c, _home_text(), _home_kb()), func=lambda c: c.data == CB_DELETE_PLUGIN_NO)
 tg.cbq_handler(lambda c: _open_panel(cardinal, c, _accounts_text(), _accounts_kb()), func=lambda c: c.data == CB_ACCOUNTS)
 tg.cbq_handler(lambda c: _start_add_account(cardinal, c), func=lambda c: c.data == CB_ACCOUNT_ADD)
 tg.cbq_handler(lambda c: _open_account(cardinal, c), func=lambda c: c.data.startswith(CB_ACCOUNT_OPEN + ':'))
 tg.cbq_handler(lambda c: _toggle_account(cardinal, c), func=lambda c: c.data.startswith(CB_ACCOUNT_TOGGLE + ':'))
 tg.cbq_handler(lambda c: _start_edit_account_limits(cardinal, c), func=lambda c: c.data.startswith(CB_ACCOUNT_LIMITS + ':') or c.data.startswith(CB_ACCOUNT_LIMIT_MODE + ':menu:'))
 tg.cbq_handler(lambda c: _handle_account_limit_mode_choice(cardinal, c), func=lambda c: c.data.startswith(CB_ACCOUNT_LIMIT_MODE + ':add:') or c.data.startswith(CB_ACCOUNT_LIMIT_MODE + ':edit:'))
 tg.cbq_handler(lambda c: _start_edit_account_limit_count(cardinal, c), func=lambda c: c.data.startswith(CB_ACCOUNT_LIMIT_COUNT + ':'))
 tg.cbq_handler(lambda c: _start_edit_account_limit_time(cardinal, c), func=lambda c: c.data.startswith(CB_ACCOUNT_LIMIT_TIME + ':'))
 tg.cbq_handler(lambda c: _start_edit_account_limit_reset(cardinal, c), func=lambda c: c.data.startswith(CB_ACCOUNT_LIMIT_RESET + ':'))
 tg.cbq_handler(lambda c: _start_edit_account_denuvo(cardinal, c), func=lambda c: c.data.startswith(CB_ACCOUNT_DENUVO + ':'))
 tg.cbq_handler(lambda c: _toggle_account_queue(cardinal, c), func=lambda c: c.data.startswith(CB_ACCOUNT_QUEUE + ':'))
 tg.cbq_handler(lambda c: _start_edit_text(cardinal, c, 'edit_account_name', c.data.split(':')[-1], '✏️ <b>Название аккаунта</b>\n\nОтправьте новое понятное название.', CB_ACCOUNTS), func=lambda c: c.data.startswith(CB_ACCOUNT_NAME + ':'))
 tg.cbq_handler(lambda c: _start_edit_text(cardinal, c, 'edit_account_template', c.data.split(':')[-1], '💬 Отправьте шаблон. Плейсхолдеры: <code>{code} {account} {lot} {order_id} {buyer} {left} {total} {quantity} {slot_info}</code>. Для общего шаблона: <code>-</code>.', CB_ACCOUNTS), func=lambda c: c.data.startswith(CB_ACCOUNT_TEMPLATE + ':'))
 tg.cbq_handler(lambda c: _start_edit_account_secret(cardinal, c), func=lambda c: c.data.startswith(CB_ACCOUNT_SECRET + ':'))
 tg.cbq_handler(lambda c: _start_edit_text(cardinal, c, 'edit_account_denuvo_game', c.data.split(':')[-1], '🎮 <b>Название Denuvo-игры</b>\n\nОтправьте любое название, например <code>F1 25</code>.', CB_ACCOUNTS), func=lambda c: c.data.startswith(CB_ACCOUNT_DENUVO_GAME + ':'))
 tg.cbq_handler(lambda c: _start_edit_text(cardinal, c, 'edit_account_denuvo_limit', c.data.split(':')[-1], '🔢 <b>Лимит Denuvo-активаций</b>\n\nСколько одновременных активаций разрешено для этого аккаунта? Например: <code>5</code>.', CB_ACCOUNTS), func=lambda c: c.data.startswith(CB_ACCOUNT_DENUVO_LIMIT + ':'))
 tg.cbq_handler(lambda c: _delete_account_confirm(cardinal, c), func=lambda c: c.data.startswith(CB_ACCOUNT_DELETE + ':'))
 tg.cbq_handler(lambda c: _delete_account(cardinal, c), func=lambda c: c.data.startswith(CB_ACCOUNT_DELETE_YES + ':'))
 tg.cbq_handler(lambda c: _open_panel(cardinal, c, _lots_text(), _lots_kb()), func=lambda c: c.data == CB_LOTS)
 tg.cbq_handler(lambda c: _start_add_lot(cardinal, c), func=lambda c: c.data == CB_LOT_ADD)
 tg.cbq_handler(lambda c: _open_lot(cardinal, c), func=lambda c: c.data.startswith(CB_LOT_OPEN + ':'))
 tg.cbq_handler(lambda c: _toggle_lot(cardinal, c), func=lambda c: c.data.startswith(CB_LOT_TOGGLE + ':'))
 tg.cbq_handler(lambda c: _toggle_funpay_lot(cardinal, c), func=lambda c: c.data.startswith(CB_LOT_FUNPAY_TOGGLE + ':'))
 tg.cbq_handler(lambda c: _open_lot_account_picker(cardinal, c), func=lambda c: c.data.startswith(CB_LOT_ACCOUNTS + ':'))
 tg.cbq_handler(lambda c: _lot_account_page(cardinal, c), func=lambda c: c.data.startswith(CB_LOT_ACCOUNT_PAGE + ':'))
 tg.cbq_handler(lambda c: _lot_account_pick(cardinal, c), func=lambda c: c.data.startswith(CB_LOT_ACCOUNT_PICK + ':'))
 tg.cbq_handler(lambda c: _delete_lot_confirm(cardinal, c), func=lambda c: c.data.startswith(CB_LOT_DELETE + ':'))
 tg.cbq_handler(lambda c: _delete_lot(cardinal, c), func=lambda c: c.data.startswith(CB_LOT_DELETE_YES + ':'))
 tg.cbq_handler(lambda c: _open_panel(cardinal, c, _notifications_text(), _notifications_kb()), func=lambda c: c.data == CB_NOTIFICATIONS)
 tg.cbq_handler(lambda c: _toggle_notification(cardinal, c), func=lambda c: c.data.startswith(CB_NOTIFY_TOGGLE + ':'))
 tg.cbq_handler(lambda c: _open_panel(cardinal, c, _analytics_text(), _analytics_kb()), func=lambda c: c.data == CB_ANALYTICS)
 tg.cbq_handler(lambda c: _open_panel(cardinal, c, _maintenance_text(), _maintenance_kb()), func=lambda c: c.data == CB_MAINTENANCE)
 tg.cbq_handler(lambda c: _toggle_plugin(cardinal, c), func=lambda c: c.data == CB_STATE_PLUGIN)
 tg.cbq_handler(lambda c: _toggle_all_accounts(cardinal, c), func=lambda c: c.data == CB_STATE_ACCOUNTS)
 tg.cbq_handler(lambda c: _toggle_all_lots(cardinal, c), func=lambda c: c.data == CB_STATE_LOTS)
 tg.cbq_handler(lambda c: _toggle_all_funpay_lots(cardinal, c), func=lambda c: c.data == CB_STATE_LOTS_FUNPAY)
 tg.cbq_handler(lambda c: _send_logs(cardinal, c), func=lambda c: c.data == CB_LOGS)
 tg.cbq_handler(lambda c: _send_backup(cardinal, c), func=lambda c: c.data == CB_BACKUP)
 tg.cbq_handler(lambda c: (_fsm_start(c.message.chat.id, 'import', 'document', c.message.id), _safe_edit(bot, c.message.chat.id, c.message.id, '📥 <b>Импорт бэкапа</b>\n\nОтправьте encrypted JSON AutoOffline.', _cancel_kb(CB_MAINTENANCE)), _answer(bot, c)), func=lambda c: c.data == CB_IMPORT)
 tg.cbq_handler(lambda c: _check_database(cardinal, c), func=lambda c: c.data == CB_DB_CHECK)
 tg.cbq_handler(lambda c: _reset_usage_confirm(cardinal, c), func=lambda c: c.data == CB_RESET_USAGE)
 tg.cbq_handler(lambda c: _reset_usage(cardinal, c), func=lambda c: c.data == CB_RESET_USAGE_YES)
 tg.cbq_handler(lambda c: _open_panel(cardinal, c, _security_text(), _security_kb()), func=lambda c: c.data == CB_SECURITY)
 tg.cbq_handler(lambda c: _handle_type_choice(cardinal, c), func=lambda c: c.data.startswith(CB_TYPE + ':'))
 tg.cbq_handler(lambda c: _handle_account_queue_choice(cardinal, c), func=lambda c: c.data.startswith(CB_ACCOUNT_QUEUE_CHOICE + ':'))
 tg.cbq_handler(lambda c: _handle_account_denuvo_choice(cardinal, c), func=lambda c: c.data.startswith(CB_ACCOUNT_DENUVO_CHOICE + ':'))
 tg.cbq_handler(lambda c: _cancel_fsm(cardinal, c), func=lambda c: c.data == CB_CANCEL)
 _start_denuvo_worker()
 _start_steam_queue_worker()
 _start_auto_registration()
 _log('START', 'Плагин запущен', version=VERSION, database='заблокирована' if _db_locked() else 'готова', denuvo_worker=bool(_DENUVO_WORKER is not None and _DENUVO_WORKER.is_alive()), code_queue_worker=bool(_STEAM_QUEUE_WORKER is not None and _STEAM_QUEUE_WORKER.is_alive()), build_hash=_plugin_build_hash())
BIND_TO_PRE_INIT = [init_cardinal]
BIND_TO_NEW_MESSAGE = [new_message_handler]
try:
 BIND_TO_NEW_ORDER = [new_order_handler]
except Exception:
 pass
BIND_TO_DELETE = [_stop_workers]