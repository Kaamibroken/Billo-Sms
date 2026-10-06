#!/usr/bin/env python3
import billo
from database import init_db, seed_owner, connect
init_db()
seed_owner()
print("Billo SMS — Python-only")
print("Starting on 0.0.0.0:" + str(billo.PORT))
billo.ThreadingHTTPServer(("0.0.0.0", billo.PORT), billo.H).serve_forever()
