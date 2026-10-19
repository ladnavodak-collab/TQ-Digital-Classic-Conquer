#pragma once
#include "classic_rules.hpp"
#include <string>
struct sqlite3;
namespace tq {
// SQLite prototype: unique constraint makes claims durable and atomic across restarts.
// Integrating rewards requires a single transaction for both claim and reward grant.
class DailyClaimStore {
public:
    explicit DailyClaimStore(const std::string& path);
    ~DailyClaimStore();
    DailyClaimStore(const DailyClaimStore&) = delete;
    DailyClaimStore& operator=(const DailyClaimStore&) = delete;
    bool try_claim(const DailyClaim& claim);
private:
    sqlite3* db_ = nullptr;
};
}
