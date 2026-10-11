"""Atomic bounded rate counters; no submitted content or plaintext client IPs."""
from storage_modes import protect
import os
import secrets
import sqlite3
import threading
from pathlib import Path


class RateLedger:
    def __init__(self, directory, clock):
        root=Path(directory)
        self.path=root/'web_security.sqlite3'
        key=root/'.web-rate-key'
        try:
            fd=os.open(key,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        except FileExistsError:
            self.salt=key.read_bytes()
        else:
            self.salt=secrets.token_bytes(32)
            with os.fdopen(fd,'wb') as f:
                f.write(self.salt);f.flush();os.fsync(f.fileno())
        if len(self.salt)!=32:
            raise ValueError('Invalid rate key')
        self.clock=clock
        self.lock=threading.Lock()
        self.next_prune=0
        self.max_rows=50000
        with self.connect() as c:
            c.executescript('CREATE TABLE IF NOT EXISTS counters (client TEXT, category TEXT, span INTEGER, bucket INTEGER, hits INTEGER, expires INTEGER, PRIMARY KEY(client,category,span,bucket)); CREATE INDEX IF NOT EXISTS counter_expiry ON counters(expires);')
        protect(key,'key');protect(self.path)

    def connect(self):
        # close explicitly; Connection's own context manager only commits.
        from contextlib import contextmanager
        @contextmanager
        def opened():
            c=sqlite3.connect(self.path,timeout=2)
            try:
                with c:yield c
            finally:c.close()
        return opened()

    def limited(self,key,category,rules):
        now=int(self.clock())
        with self.lock,self.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            if now>=self.next_prune:
                c.execute('DELETE FROM counters WHERE expires<=?',(now,))
                self.next_prune=now+60
            entries=[]
            for span,cap in rules:
                bucket=now//span
                row=c.execute('SELECT hits FROM counters WHERE client=? AND category=? AND span=? AND bucket=?',(key,category,span,bucket)).fetchone()
                if row and row[0]>=cap:return True
                entries.append((span,bucket,row))
            new=sum(row is None for _,_,row in entries)
            if new and c.execute('SELECT count(*) FROM counters').fetchone()[0]+new>self.max_rows:
                return True
            for span,bucket,_ in entries:
                c.execute('INSERT INTO counters VALUES(?,?,?,?,1,?) ON CONFLICT(client,category,span,bucket) DO UPDATE SET hits=hits+1',(key,category,span,bucket,(bucket+1)*span))
            return False
