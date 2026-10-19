#include "daily_claim_store.hpp"
#include <cassert>
#include <filesystem>
#include <iostream>
int main() {
    auto path = std::filesystem::temp_directory_path() / "tq_daily_claim_store_test.sqlite";
    std::filesystem::remove(path);
    {
        tq::DailyClaimStore db(path.string());
        assert(db.try_claim({42,"hunt","2026-10-19"}));
        assert(!db.try_claim({42,"hunt","2026-10-19"}));
        assert(db.try_claim({42,"hunt","2026-10-20"}));
        assert(!db.try_claim({0,"hunt","2026-10-19"}));
    }
    {
        tq::DailyClaimStore db(path.string());
        assert(!db.try_claim({42,"hunt","2026-10-19"}));
        assert(db.try_claim({43,"hunt","2026-10-19"}));
    }
    std::filesystem::remove(path);
    std::cout << "Persistent daily claim tests passed\n";
}
