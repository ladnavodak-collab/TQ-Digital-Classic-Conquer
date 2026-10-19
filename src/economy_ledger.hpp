#pragma once
#include <cstdint>
#include <memory>
#include <string>
struct sqlite3;

namespace tq {
enum class EconomyResult { applied, already_applied, insufficient_funds, not_owner, invalid, conflict, database_error };
// Development-only ledger. No authentication, game packets, or COPS adapter.
class EconomyLedger {
public:
    explicit EconomyLedger(const std::string& path);
    ~EconomyLedger();
    EconomyLedger(const EconomyLedger&) = delete;
    EconomyLedger& operator=(const EconomyLedger&) = delete;
    bool ready() const { return ready_; }
    // Provisioning only: never expose account creation or balance seeding to game clients.
    bool provision_wallet(std::int64_t id, std::int64_t starting_silver);
    bool provision_item(std::int64_t item_id, std::int64_t owner_id);
    std::int64_t balance(std::int64_t id) const;
    std::int64_t item_owner(std::int64_t item_id) const;
    EconomyResult transfer(const std::string& request_id, std::int64_t sender, std::int64_t receiver, std::int64_t silver);
    EconomyResult purchase_item(const std::string& request_id, std::int64_t buyer, std::int64_t seller,
                                std::int64_t item_id, std::int64_t silver);
private:
    sqlite3* db_ = nullptr;
    bool ready_ = false;
    EconomyResult transact(const std::string& request_id, const std::string& fingerprint,
                           std::int64_t sender, std::int64_t receiver, std::int64_t silver, std::int64_t item_id);
};
}
