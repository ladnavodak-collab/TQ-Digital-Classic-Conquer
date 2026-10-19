#include "packet_framing.h"
namespace tq {
PacketFramer::Status PacketFramer::append(const std::uint8_t* bytes, std::size_t count) {
    if (invalid_ || (count && !bytes)) return Status::Invalid;
    if (count > kMaxFrame || pending_.size() > kMaxFrame - count) {
        invalid_ = true;
        return Status::Invalid;
    }
    if (count) pending_.insert(pending_.end(), bytes, bytes + count);
    if (pending_.size() < 2) return Status::NeedMore;
    const std::size_t length = std::size_t(pending_[0]) | (std::size_t(pending_[1]) << 8);
    if (length < 2 || length > kMaxFrame) {
        invalid_ = true;
        return Status::Invalid;
    }
    return pending_.size() >= length ? Status::Ready : Status::NeedMore;
}
bool PacketFramer::pop(std::vector<std::uint8_t>& packet) {
    if (invalid_ || pending_.size() < 2) return false;
    const std::size_t length = std::size_t(pending_[0]) | (std::size_t(pending_[1]) << 8);
    if (length < 2 || length > kMaxFrame || pending_.size() < length) return false;
    packet.assign(pending_.begin(), pending_.begin() + length);
    pending_.erase(pending_.begin(), pending_.begin() + length);
    return true;
}
void PacketFramer::reset() { pending_.clear(); invalid_ = false; }
}
