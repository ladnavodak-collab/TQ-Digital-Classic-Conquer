#include "daily_claim_store.hpp"
#include <sqlite3.h>
#include <stdexcept>
namespace tq {
DailyClaimStore::DailyClaimStore(const std::string& path) {
    if (sqlite3_open(path.c_str(), &db_) != SQLITE_OK) {
        std::string message = db_ ? sqlite3_errmsg(db_) : "sqlite open failed";
        if (db_) sqlite3_close(db_);
        db_ = nullptr;
        throw std::runtime_error(message);
    }
    constexpr auto schema = "CREATE TABLE IF NOT EXISTS daily_claims ("
        "character_id INTEGER NOT NULL CHECK(character_id > 0),"
        "quest_id TEXT NOT NULL CHECK(length(quest_id) > 0),"
        "date_utc TEXT NOT NULL CHECK(length(date_utc) = 10),"
        "PRIMARY KEY(character_id,quest_id,date_utc));";
    char* error = nullptr;
    if (sqlite3_exec(db_, schema, nullptr, nullptr, &error) != SQLITE_OK) {
        std::string message = error ? error : "schema failed";
        sqlite3_free(error);
        sqlite3_close(db_);
        db_ = nullptr;
        throw std::runtime_error(message);
    }
}
DailyClaimStore::~DailyClaimStore() { if (db_) sqlite3_close(db_); }
bool DailyClaimStore::try_claim(const DailyClaim& c) {
    if (c.character_id == 0 || c.character_id > 0x7fffffffffffffffULL || c.quest_id.empty() || c.date_utc.size() != 10 ||
        c.date_utc[4] != '-' || c.date_utc[7] != '-') return false;
    sqlite3_stmt* statement = nullptr;
    constexpr auto sql = "INSERT OR IGNORE INTO daily_claims(character_id,quest_id,date_utc) VALUES(?,?,?)";
    if (sqlite3_prepare_v2(db_, sql, -1, &statement, nullptr) != SQLITE_OK) throw std::runtime_error(sqlite3_errmsg(db_));
    sqlite3_bind_int64(statement, 1, static_cast<sqlite3_int64>(c.character_id));
    sqlite3_bind_text(statement, 2, c.quest_id.c_str(), -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(statement, 3, c.date_utc.c_str(), -1, SQLITE_TRANSIENT);
    int rc = sqlite3_step(statement);
    int changes = sqlite3_changes(db_);
    sqlite3_finalize(statement);
    if (rc != SQLITE_DONE) throw std::runtime_error(sqlite3_errmsg(db_));
    return changes == 1;
}
}
