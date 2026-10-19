#pragma once
#include <cstddef>
#include <cstdint>
#include <vector>
namespace tq {
// Generic little-endian length-prefixed framing experiment.
// Not a verified Conquer Online packet format.
class PacketFramer {
public:
    static constexpr std::size_t kMaxFrame = 8192;
    enum class Status { NeedMore, Ready, Invalid };
    Status append(const std::uint8_t* bytes, std::size_t count);
    bool pop(std::vector<std::uint8_t>& packet);
    void reset();
private:
    std::vector<std::uint8_t> pending_;
    bool invalid_ = false;
};
}
