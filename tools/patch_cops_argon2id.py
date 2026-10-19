#!/usr/bin/env python3
"""Patch disposable COPS v7 checkout to verify Argon2id password hashes."""
from pathlib import Path
import sys

def replace_one(file, old, new):
    content=file.read_text(encoding="utf-8")
    count=content.count(old)
    if count != 1: raise RuntimeError(f"{file}: wanted one anchor, found {count}")
    file.write_text(content.replace(old,new),encoding="utf-8")

def patch(root):
    database=root/"src/Database/database.cpp"
    replace_one(database, '#include <QThread>', '#include <QThread>\n#include <sodium.h>')
    old='''            QString password = query.value(1).toString();
            if (password.compare(aPassword) == 0)'''
    new='''            // The account.password column must hold a libsodium
            // Argon2id PHC string, never an unhashed password.
            const QByteArray encodedHash = query.value(1).toString().toUtf8();
            const bool hashLooksValid =
                encodedHash.startsWith("$argon2id$") &&
                encodedHash.size() < crypto_pwhash_STRBYTES;
            const bool verified = hashLooksValid &&
                sodium_init() >= 0 &&
                crypto_pwhash_str_verify(encodedHash.constData(),
                                        aPassword, strlen(aPassword)) == 0;
            if (verified)'''
    replace_one(database,old,new)
    project=root/"COPS v7 Emulator.pro"
    replace_one(project,"QT -= gui","QT -= gui\n\n# Requires libsodium headers and development library.\nunix: LIBS += -lsodium")
    # A Windows application will require a properly installed libsodium SDK;
    # do not silently build an insecure fallback.
    replace_one(project,"unix: LIBS += -lsodium","unix: LIBS += -lsodium\nwin32: LIBS += -lsodium")

if __name__ == "__main__":
    if len(sys.argv)!=2: raise SystemExit("Usage: patch_cops_argon2id.py <upstream-checkout>")
    patch(Path(sys.argv[1]))
