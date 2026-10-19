#include "stream_reassembly.hpp"
namespace tq {
std::size_t StreamReassembler::nextLength() const noexcept {
    if (pending_.size() < kHeaderBytes) return 0;
    return std::size_t(pending_[0]) | (std::size_t(pending_[1]) << 8);
}
StreamReassembler::Result StreamReassembler::append(const std::uint8_t* data, std::size_t count) {
    if (invalid_) return Result::Invalid;
    if (count && !data) { invalid_ = true; return Result::Invalid; }
    if (count > kMaxBufferedBytes || pending_.size() > kMaxBufferedBytes - count) {
        invalid_ = true;
        return Result::Invalid;
    }
    if (count) pending_.insert(pending_.end(), data, data + count);
    // Check every complete frame, not only the first. Otherwise malformed
    // second/third frames could be silently queued after a valid first one.
    std::size_t offset = 0;
    bool complete = false;
    while (pending_.size() - offset >= kHeaderBytes) {
        const std::size_t len = std::size_t(pending_[offset]) |
                                (std::size_t(pending_[offset + 1]) << 8);
        if (len < kHeaderBytes || len > kMaxPacketBytes) {
            invalid_ = true;
            return Result::Invalid;
        }
        if (pending_.size() - offset < len) break;
        offset += len;
        complete = true;
    }
    return complete ? Result::Ready : Result::NeedMore;
}
bool StreamReassembler::pop(std::vector<std::uint8_t>& frame) {
    if (invalid_ || pending_.size() < kHeaderBytes) return false;
    const std::size_t len = nextLength();
    if (len < kHeaderBytes || len > kMaxPacketBytes || pending_.size() < len) return false;
    frame.assign(pending_.begin(), pending_.begin() + len);
    pending_.erase(pending_.begin(), pending_.begin() + len);
    return true;
}
void StreamReassembler::reset() { pending_.clear(); invalid_ = false; }
} // namespace tq
