#include "stream_reassembly.hpp"
#include <cassert>
#include <cstdint>
#include <vector>
#include <limits>
using tq::StreamReassembler;
using Result = StreamReassembler::Result;
int main() {
    StreamReassembler s;
    std::vector<std::uint8_t> out;
    // No data and split header/payload.
    assert(s.append(nullptr, 0) == Result::NeedMore);
    const std::uint8_t a[]{6};
    assert(s.append(a, 1) == Result::NeedMore);
    const std::uint8_t b[]{0, 12, 0, 99};
    assert(s.append(b, 4) == Result::NeedMore);
    assert(!s.pop(out));
    const std::uint8_t c[]{98};
    assert(s.append(c, 1) == Result::Ready);
    assert(s.pop(out));
    assert((out == std::vector<std::uint8_t>{6,0,12,0,99,98}));
    assert(!s.pop(out));
    // Coalesced frames and a trailing fragmented header.
    const std::uint8_t two[]{4,0,7,0,5,0,8,0,42,6};
    assert(s.append(two, sizeof(two)) == Result::Ready);
    assert(s.pop(out) && out.size() == 4);
    assert(s.pop(out) && out.size() == 5);
    assert(s.buffered() == 1);
    const std::uint8_t rest[]{0,4,0,1,2};
    assert(s.append(rest, sizeof(rest)) == Result::Ready);
    assert(s.pop(out) && out.size() == 6);
    // Reject incomplete, invalid and nonsensical headers.
    s.reset();
    const std::uint8_t bad0[]{0,0,0,0};
    assert(s.append(bad0, 4) == Result::Invalid);
    assert(s.invalid());
    const std::uint8_t good[]{4,0,2,0};
    assert(s.append(good,4) == Result::Invalid);
    s.reset();
    const std::uint8_t too_big[]{0xff,0x7f,0,0};
    assert(s.append(too_big,4) == Result::Invalid);
    // Reject a bad second frame immediately.
    s.reset();
    const std::uint8_t second_bad[]{4,0,1,0,3,0,1,0};
    assert(s.append(second_bad,sizeof(second_bad)) == Result::Invalid);
    // Reject null pointer/nonzero length and extreme count without pointer math.
    s.reset();
    assert(s.append(nullptr,1) == Result::Invalid);
    s.reset();
    assert(s.append(good,std::numeric_limits<std::size_t>::max()) == Result::Invalid);
    // Bound pending bytes, including incomplete frames and full coalesced packets.
    s.reset();
    std::vector<std::uint8_t> many;
    for (int i=0;i<2048;++i) many.insert(many.end(),{4,0,1,0});
    assert(many.size() == s.kMaxBufferedBytes);
    assert(s.append(many.data(),many.size()) == Result::Ready);
    assert(s.buffered() == s.kMaxBufferedBytes);
    assert(s.append(good,4) == Result::Invalid);
    s.reset();
    assert(s.buffered() == 0 && !s.invalid());
    assert(s.append(good,4) == Result::Ready);
    assert(s.pop(out) && out.size() == 4);
    return 0;
}
