#include "cipher_stream_bridge.hpp"
namespace tq {
StreamReassembler::Result CipherStreamBridge::receive(
    const std::uint8_t* encrypted, std::size_t size) {
    using Result = StreamReassembler::Result;
    if (frames_.invalid()) return Result::Invalid;
    if (size && !encrypted) return frames_.append(nullptr, size);
    // Apply limits BEFORE invoking a stateful cipher: rejected data should
    // never consume cipher state.
    if (size > StreamReassembler::kMaxBufferedBytes ||
        frames_.buffered() > StreamReassembler::kMaxBufferedBytes - size) {
        return frames_.append(encrypted, size);
    }
    if (!size) return frames_.append(nullptr, 0);
    std::vector<std::uint8_t> clear(encrypted, encrypted + size);
    cipher_.decrypt(clear.data(), clear.size());
    return frames_.append(clear.data(), clear.size());
}
bool CipherStreamBridge::resetIfDrained() noexcept {
    if (frames_.invalid() || frames_.buffered() != 0) return false;
    frames_.reset();
    return true;
}
}
