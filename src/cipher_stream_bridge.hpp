#pragma once
#include "stream_reassembly.hpp"
#include <cstddef>
#include <cstdint>
#include <vector>
namespace tq {
// A connection-scoped *post-handshake* encrypted TCP stream boundary.
// The implementation calls the provided cipher once for each arriving byte.
// It must not be used for the initial COPS Diffie-Hellman negotiation, where
// cipher keys/IVs change mid-stream. No real COPS cipher is wired in here.
class CipherStreamBridge {
public:
    class Cipher {
    public:
        virtual ~Cipher() = default;
        virtual void decrypt(std::uint8_t* bytes, std::size_t count) = 0;
    };
    explicit CipherStreamBridge(Cipher& cipher) : cipher_(cipher) {}
    StreamReassembler::Result receive(const std::uint8_t* encrypted, std::size_t size);
    bool pop(std::vector<std::uint8_t>& packet) { return frames_.pop(packet); }
    bool failed() const noexcept { return frames_.invalid(); }
    std::size_t buffered() const noexcept { return frames_.buffered(); }
    // A new stream/cipher epoch is only permitted after draining everything.
    // The caller must initialize the new cipher independently.
    bool resetIfDrained() noexcept;
private:
    Cipher& cipher_;
    StreamReassembler frames_;
};
}
