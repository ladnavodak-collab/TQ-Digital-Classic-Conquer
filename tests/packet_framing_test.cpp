#include "packet_framing.h"
#include <cassert>
#include <cstdint>
#include <vector>
int main() {
    tq::PacketFramer f;
    std::vector<std::uint8_t> out;
    const std::uint8_t a[]{4};
    assert(f.append(a, 1) == tq::PacketFramer::Status::NeedMore);
    const std::uint8_t b[]{0, 42, 43};
    assert(f.append(b, 3) == tq::PacketFramer::Status::Ready);
    assert(f.pop(out) && out == std::vector<std::uint8_t>({4, 0, 42, 43}));
    assert(!f.pop(out));
    const std::uint8_t two[]{2,0,2,0};
    assert(f.append(two, 4) == tq::PacketFramer::Status::Ready);
    assert(f.pop(out) && out.size() == 2);
    assert(f.pop(out) && out.size() == 2);
    const std::uint8_t bad[]{1,0};
    assert(f.append(bad, 2) == tq::PacketFramer::Status::Invalid);
    f.reset();
    assert(f.append(two, 4) == tq::PacketFramer::Status::Ready);
    assert(f.pop(out));
    const std::uint8_t huge[]{0xff,0xff};
    f.reset();
    assert(f.append(huge, 2) == tq::PacketFramer::Status::Invalid);
}
