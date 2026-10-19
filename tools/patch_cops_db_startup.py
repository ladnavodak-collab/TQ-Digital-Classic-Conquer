#!/usr/bin/env python3
"""Reject default database credentials and avoid SQL parameter logging in COPS."""
from pathlib import Path
import sys

def replace_once(path, old, new):
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError("Unexpected upstream source version: " + str(path))
    path.write_text(text.replace(old, new), encoding="utf-8")

def patch(root):
    server = root / "src/server.cpp"
    old = '    string sql_user = settings.readString("COPS_EMULATOR/SQL_USER", "root");\n    string sql_pwd = settings.readString("COPS_EMULATOR/SQL_PWD", "");'
    new = '''    string sql_user = settings.readString("COPS_EMULATOR/SQL_USER", "");
    const char* dbSecret = getenv("COPS_SQL_PASSWORD");
    string sql_pwd = dbSecret ? dbSecret : "";
    if (sql_user.empty() || sql_user == "root" || sql_pwd.empty() ||
        sql_pwd == "root" || sql_pwd == "password")
    {
        fprintf(stderr, "Refusing unsafe database configuration.\\n");
        return ERROR_INVALID_PASSWORD;
    }'''
    replace_once(server, old, new)
    database = root / "src/Database/database.cpp"
    text = database.read_text(encoding="utf-8")
    old_expr = 'qPrintable(getSqlCommand(query))'
    if old_expr not in text:
        raise RuntimeError("SQL logging anchor missing")
    database.write_text(text.replace(old_expr, 'qPrintable(query.lastQuery())'), encoding="utf-8")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Supply a disposable COPS checkout path")
    patch(Path(sys.argv[1]))
