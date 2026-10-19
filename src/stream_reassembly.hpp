#pragma once
#include <cstddef>
#include <cstdint>
#include <vector>

namespace tq {
// Reassembles plaintext, little-endian [length:u16][type:u16] frames.
// This is NOT a drop-in COPS encrypted socket or key-exchange parser.
class StreamReassembler {
public:
    static constexpr std::size_t kHeaderBytes = 4;
    static constexpr std::size_t kMaxPacketBytes = 1024;
    static constexpr std::size_t kMaxBufferedBytes = 8192;
    enum class Result { NeedMore, Ready, Invalid };
    Result append(const std::uint8_t* data, std::size_t count);
    bool pop(std::vector<std::uint8_t>& frame);
    void reset();
    bool invalid() const noexcept { return invalid_; }
    std::size_t buffered() const noexcept { return pending_.size(); }
private:
    std::size_t nextLength() const noexcept;
    std::vector<std::uint8_t> pending_;
    bool invalid_ = false;
};
} // namespace tq
