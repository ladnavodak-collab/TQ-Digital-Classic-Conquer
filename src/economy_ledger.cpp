#include "economy_ledger.hpp"
#include <sqlite3.h>
#include <limits>
#include <string>
namespace tq {
namespace {
class Statement {
public:
    Statement(sqlite3* db, const char* sql) { if(sqlite3_prepare_v2(db,sql,-1,&s_,nullptr)!=SQLITE_OK) s_=nullptr; }
    ~Statement() { sqlite3_finalize(s_); }
    sqlite3_stmt* get() const { return s_; }
private: sqlite3_stmt* s_ = nullptr;
};
bool exec(sqlite3* db,const char* sql) { return sqlite3_exec(db,sql,nullptr,nullptr,nullptr)==SQLITE_OK; }
std::int64_t query_int(sqlite3* db,const char* sql,std::int64_t id) {
    Statement st(db,sql);
    if(!st.get()) return -1;
    sqlite3_bind_int64(st.get(),1,id);
    return sqlite3_step(st.get()) == SQLITE_ROW ? sqlite3_column_int64(st.get(),0) : -1;
}
std::string fingerprint(const char* type,std::int64_t a,std::int64_t b,std::int64_t item,std::int64_t amt) {
    return std::string(type)+":"+std::to_string(a)+":"+std::to_string(b)+":"+std::to_string(item)+":"+std::to_string(amt);
}
}
EconomyLedger::EconomyLedger(const std::string& path) {
    if(sqlite3_open(path.c_str(),&db_)!=SQLITE_OK) return;
    sqlite3_busy_timeout(db_,3000);
    ready_ = exec(db_,"PRAGMA foreign_keys=ON") &&
        exec(db_,"CREATE TABLE IF NOT EXISTS wallets(id INTEGER PRIMARY KEY, silver INTEGER NOT NULL CHECK(silver>=0))") &&
        exec(db_,"CREATE TABLE IF NOT EXISTS items(id INTEGER PRIMARY KEY, owner INTEGER NOT NULL REFERENCES wallets(id))") &&
        exec(db_,"CREATE TABLE IF NOT EXISTS requests(id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL)");
}
EconomyLedger::~EconomyLedger() { if(db_) sqlite3_close(db_); }
bool EconomyLedger::provision_wallet(std::int64_t id,std::int64_t silver) {
    if(!ready_ || id<=0 || silver<0) return false;
    Statement st(db_,"INSERT INTO wallets(id,silver) VALUES(?,?)");
    if(!st.get()) return false;
    sqlite3_bind_int64(st.get(),1,id); sqlite3_bind_int64(st.get(),2,silver);
    return sqlite3_step(st.get())==SQLITE_DONE;
}
bool EconomyLedger::provision_item(std::int64_t item,std::int64_t owner) {
    if(!ready_ || item<=0 || owner<=0) return false;
    Statement st(db_,"INSERT INTO items(id,owner) VALUES(?,?)");
    if(!st.get()) return false;
    sqlite3_bind_int64(st.get(),1,item); sqlite3_bind_int64(st.get(),2,owner);
    return sqlite3_step(st.get())==SQLITE_DONE;
}
std::int64_t EconomyLedger::balance(std::int64_t id) const { return ready_ ? query_int(db_,"SELECT silver FROM wallets WHERE id=?",id) : -1; }
std::int64_t EconomyLedger::item_owner(std::int64_t id) const { return ready_ ? query_int(db_,"SELECT owner FROM items WHERE id=?",id) : -1; }
EconomyResult EconomyLedger::transfer(const std::string& request,std::int64_t sender,std::int64_t receiver,std::int64_t silver) {
    return transact(request,fingerprint("transfer",sender,receiver,0,silver),sender,receiver,silver,0);
}
EconomyResult EconomyLedger::purchase_item(const std::string& request,std::int64_t buyer,std::int64_t seller,std::int64_t item,std::int64_t silver) {
    return transact(request,fingerprint("purchase",buyer,seller,item,silver),buyer,seller,silver,item);
}
EconomyResult EconomyLedger::transact(const std::string& request,const std::string& fp,std::int64_t from,std::int64_t to,std::int64_t amount,std::int64_t item) {
    if(!ready_) return EconomyResult::database_error;
    if(request.empty() || request.size()>128 || from<=0 || to<=0 || from==to || amount<=0 || item<0) return EconomyResult::invalid;
    if(!exec(db_,"BEGIN IMMEDIATE")) return EconomyResult::database_error;
    bool committed=false;
    auto finish=[&](EconomyResult r) { if(!committed) exec(db_,"ROLLBACK"); return r; };
    {
        Statement seen(db_,"SELECT fingerprint FROM requests WHERE id=?");
        if(!seen.get()) return finish(EconomyResult::database_error);
        sqlite3_bind_text(seen.get(),1,request.c_str(),-1,SQLITE_TRANSIENT);
        int res=sqlite3_step(seen.get());
        if(res==SQLITE_ROW) {
            const char* existing=reinterpret_cast<const char*>(sqlite3_column_text(seen.get(),0));
            return finish(existing && fp==existing ? EconomyResult::already_applied : EconomyResult::conflict);
        }
        if(res!=SQLITE_DONE) return finish(EconomyResult::database_error);
    }
    const auto sender_balance=balance(from), receiver_balance=balance(to);
    if(sender_balance<0 || receiver_balance<0) return finish(EconomyResult::invalid);
    if(sender_balance<amount) return finish(EconomyResult::insufficient_funds);
    if(receiver_balance>std::numeric_limits<std::int64_t>::max()-amount) return finish(EconomyResult::invalid);
    if(item>0 && item_owner(item)!=to) return finish(EconomyResult::not_owner);
    {
        Statement pay(db_,"UPDATE wallets SET silver=silver-? WHERE id=? AND silver>=?");
        if(!pay.get()) return finish(EconomyResult::database_error);
        sqlite3_bind_int64(pay.get(),1,amount); sqlite3_bind_int64(pay.get(),2,from); sqlite3_bind_int64(pay.get(),3,amount);
        if(sqlite3_step(pay.get())!=SQLITE_DONE || sqlite3_changes(db_)!=1) return finish(EconomyResult::database_error);
    }
    {
        Statement receive(db_,"UPDATE wallets SET silver=silver+? WHERE id=?");
        if(!receive.get()) return finish(EconomyResult::database_error);
        sqlite3_bind_int64(receive.get(),1,amount); sqlite3_bind_int64(receive.get(),2,to);
        if(sqlite3_step(receive.get())!=SQLITE_DONE || sqlite3_changes(db_)!=1) return finish(EconomyResult::database_error);
    }
    if(item>0) {
        Statement move(db_,"UPDATE items SET owner=? WHERE id=? AND owner=?");
        if(!move.get()) return finish(EconomyResult::database_error);
        sqlite3_bind_int64(move.get(),1,from); sqlite3_bind_int64(move.get(),2,item); sqlite3_bind_int64(move.get(),3,to);
        if(sqlite3_step(move.get())!=SQLITE_DONE || sqlite3_changes(db_)!=1) return finish(EconomyResult::database_error);
    }
    {
        Statement save(db_,"INSERT INTO requests(id,fingerprint) VALUES(?,?)");
        if(!save.get()) return finish(EconomyResult::database_error);
        sqlite3_bind_text(save.get(),1,request.c_str(),-1,SQLITE_TRANSIENT);
        sqlite3_bind_text(save.get(),2,fp.c_str(),-1,SQLITE_TRANSIENT);
        if(sqlite3_step(save.get())!=SQLITE_DONE) return finish(EconomyResult::database_error);
    }
    if(!exec(db_,"COMMIT")) return finish(EconomyResult::database_error);
    committed=true;
    return EconomyResult::applied;
}
}
