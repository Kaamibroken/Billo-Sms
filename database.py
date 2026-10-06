#!/usr/bin/env python3
import os, sqlite3, hashlib, hmac, secrets, tempfile
from datetime import datetime, timezone


def _choose_db_path():
    # FRESH Billo database: deliberately does not reuse the old billo.db.
    # The filename is unique to this rebuilt package and is created automatically.
    override=os.environ.get('BILLO_DB_PATH','').strip()
    if override:
        return override
    candidates=[]
    for base in (os.path.join(os.getcwd(),'data'), '/app/data', os.path.join(os.path.expanduser('~'),'.billo_sms')):
        candidates.append(os.path.join(base,'billo_sms_fresh.db'))
    candidates.append(os.path.join(tempfile.gettempdir(),'billo_sms_data','billo_sms_fresh.db'))
    for path in candidates:
        try:
            parent=os.path.dirname(path) or '.'
            os.makedirs(parent,exist_ok=True)
            probe=os.path.join(parent,'.billo_write_test')
            with open(probe,'a',encoding='utf-8'): pass
            os.remove(probe)
            return path
        except Exception:
            continue
    return os.path.join(tempfile.gettempdir(),'billo_sms_data','billo_sms_fresh.db')

DB_PATH=_choose_db_path()

def connect():
    parent=os.path.dirname(DB_PATH) or '.'
    os.makedirs(parent,exist_ok=True)
    c=sqlite3.connect(DB_PATH,timeout=30)
    c.row_factory=sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    try: c.execute('PRAGMA journal_mode=WAL')
    except Exception: pass
    return c

def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat(sep=' ')

def hash_password(password):
    salt=secrets.token_bytes(16)
    digest=hashlib.scrypt(password.encode(),salt=salt,n=16384,r=8,p=1)
    return salt.hex()+'$'+digest.hex()

def verify_password(password,stored):
    try:
        salt_hex,digest_hex=stored.split('$',1)
        digest=hashlib.scrypt(password.encode(),salt=bytes.fromhex(salt_hex),n=16384,r=8,p=1)
        return hmac.compare_digest(digest.hex(),digest_hex)
    except Exception:return False

def _cols(c,table): return {r['name'] for r in c.execute(f'PRAGMA table_info({table})').fetchall()}
def _add(c,table,col,definition):
    if col not in _cols(c,table): c.execute(f'ALTER TABLE {table} ADD COLUMN {col} {definition}')

def init_db():
    c=connect()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS users(
      id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,
      role TEXT NOT NULL CHECK(role IN ('OWNER','MANAGER','AGENT','CLIENT')),
      parent_id INTEGER REFERENCES users(id), full_name TEXT DEFAULT '', email TEXT DEFAULT '',
      whatsapp TEXT DEFAULT '', telegram TEXT DEFAULT '', profile_photo TEXT DEFAULT '', profile_photo_type TEXT DEFAULT '', theme TEXT NOT NULL DEFAULT 'Billo Original', music_enabled INTEGER NOT NULL DEFAULT 1, music_volume REAL NOT NULL DEFAULT 0.18, active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS ix_users_parent ON users(parent_id);
    CREATE INDEX IF NOT EXISTS ix_users_role ON users(role);
    CREATE TABLE IF NOT EXISTS ranges(
      id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, country TEXT NOT NULL DEFAULT 'Other', country_code TEXT DEFAULT '',
      rate REAL NOT NULL DEFAULT 0, active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL, deleted_at TEXT
    );
    CREATE TABLE IF NOT EXISTS numbers(
      id INTEGER PRIMARY KEY, range_id INTEGER NOT NULL REFERENCES ranges(id), value TEXT NOT NULL UNIQUE,
      country TEXT NOT NULL DEFAULT 'Other', country_code TEXT DEFAULT '', active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS ix_numbers_range ON numbers(range_id);
    CREATE INDEX IF NOT EXISTS ix_numbers_value ON numbers(value);
    CREATE TABLE IF NOT EXISTS allocations(
      id INTEGER PRIMARY KEY, number_id INTEGER NOT NULL REFERENCES numbers(id), target_user_id INTEGER NOT NULL REFERENCES users(id),
      parent_allocation_id INTEGER REFERENCES allocations(id), payout REAL NOT NULL, term TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'ACTIVE', allocated_at TEXT NOT NULL, unallocated_at TEXT
    );
    CREATE INDEX IF NOT EXISTS ix_alloc_active ON allocations(number_id,status);
    CREATE TABLE IF NOT EXISTS carriers(
      id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, method TEXT NOT NULL DEFAULT 'POST', status TEXT NOT NULL DEFAULT 'ACTIVE',
      field_from TEXT NOT NULL DEFAULT 'from', field_to TEXT NOT NULL DEFAULT 'to', field_message TEXT NOT NULL DEFAULT 'message',
      field_sms_id TEXT NOT NULL DEFAULT 'sms_id', created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS carrier_ips(id INTEGER PRIMARY KEY, carrier_id INTEGER NOT NULL REFERENCES carriers(id) ON DELETE CASCADE,cidr TEXT NOT NULL,UNIQUE(carrier_id,cidr));
    CREATE TABLE IF NOT EXISTS sms_cdr(
      id INTEGER PRIMARY KEY, sms_id TEXT NOT NULL UNIQUE, carrier_id INTEGER REFERENCES carriers(id), number TEXT NOT NULL, cli TEXT NOT NULL,
      message TEXT NOT NULL, range_id INTEGER REFERENCES ranges(id) ON DELETE SET NULL, range_name_snapshot TEXT DEFAULT '',
      rate_snapshot REAL NOT NULL DEFAULT 0,
      client_id INTEGER REFERENCES users(id), agent_id INTEGER REFERENCES users(id), manager_id INTEGER REFERENCES users(id), received_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS ix_sms_time ON sms_cdr(received_at); CREATE INDEX IF NOT EXISTS ix_sms_number ON sms_cdr(number);
    CREATE TABLE IF NOT EXISTS rates(id INTEGER PRIMARY KEY,name TEXT NOT NULL,country TEXT DEFAULT '',carrier_id INTEGER REFERENCES carriers(id),user_id INTEGER REFERENCES users(id),rate REAL NOT NULL DEFAULT 0,active INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS payments(id INTEGER PRIMARY KEY,manager_id INTEGER REFERENCES users(id),period_start TEXT NOT NULL,period_end TEXT NOT NULL,sms_count INTEGER NOT NULL DEFAULT 0,payout REAL NOT NULL DEFAULT 0,status TEXT NOT NULL DEFAULT 'PENDING',created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,captcha_answer INTEGER,captcha_a INTEGER,captcha_b INTEGER,created_at TEXT NOT NULL,last_seen TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,user_id INTEGER,action TEXT NOT NULL,detail TEXT DEFAULT '',created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS chat_groups(id INTEGER PRIMARY KEY,creator_id INTEGER NOT NULL REFERENCES users(id),name TEXT NOT NULL,kind TEXT NOT NULL DEFAULT 'SUPPORT',created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS chat_members(group_id INTEGER NOT NULL REFERENCES chat_groups(id) ON DELETE CASCADE,user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,label TEXT DEFAULT '',PRIMARY KEY(group_id,user_id));
    CREATE TABLE IF NOT EXISTS chat_messages(id INTEGER PRIMARY KEY,group_id INTEGER NOT NULL REFERENCES chat_groups(id) ON DELETE CASCADE,user_id INTEGER NOT NULL REFERENCES users(id),message TEXT NOT NULL,created_at TEXT NOT NULL);
    CREATE INDEX IF NOT EXISTS ix_chat_messages_time ON chat_messages(created_at);
    CREATE TABLE IF NOT EXISTS helper_requests(id INTEGER PRIMARY KEY,requester_id INTEGER NOT NULL REFERENCES users(id),target_id INTEGER NOT NULL REFERENCES users(id),status TEXT NOT NULL DEFAULT 'PENDING',created_at TEXT NOT NULL,responded_at TEXT);
    ''')
    # Migrations for older Billo databases.
    for table,col,definition in [
        ('users','theme',"TEXT NOT NULL DEFAULT 'Billo Original'"),('users','music_enabled',"INTEGER NOT NULL DEFAULT 1"),('users','music_volume',"REAL NOT NULL DEFAULT 0.18"),('users','full_name',"TEXT DEFAULT ''"),('users','email',"TEXT DEFAULT ''"),('users','profile_photo',"TEXT DEFAULT ''"),('users','profile_photo_type',"TEXT DEFAULT ''"),
        ('ranges','country_code',"TEXT DEFAULT ''"),('ranges','deleted_at',"TEXT"),
        ('numbers','country_code',"TEXT DEFAULT ''"),('sms_cdr','range_name_snapshot',"TEXT DEFAULT ''"),('sms_cdr','rate_snapshot',"REAL NOT NULL DEFAULT 0")]:
        _add(c,table,col,definition)
    c.execute("UPDATE users SET theme='New UI' WHERE theme='Vampire Mode'")
    c.commit();c.close()

def seed_owner(username=None,password=None):
    username=(username or os.environ.get('OWNER_USERNAME') or 'Billo_Asad').strip()
    password=password or os.environ.get('OWNER_PASSWORD') or 'Owner_Asad'
    c=connect()
    if not c.execute("SELECT id FROM users WHERE role='OWNER' LIMIT 1").fetchone():
        c.execute("INSERT INTO users(username,password_hash,role,full_name,created_at) VALUES(?,?,?,?,?)",(username,hash_password(password),'OWNER','Muhammad Asad',now()));c.commit()
    c.close()

def audit(c,user_id,action,detail=''):
    c.execute('INSERT INTO audit(user_id,action,detail,created_at) VALUES(?,?,?,?)',(user_id,action,detail,now()))
