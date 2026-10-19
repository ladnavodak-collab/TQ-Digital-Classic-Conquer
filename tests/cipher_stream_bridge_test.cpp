#include "cipher_stream_bridge.hpp"
#include <cassert>
#include <cstdint>
#include <vector>
using tq::CipherStreamBridge;
using Result=tq::StreamReassembler::Result;
struct ToyCipher : CipherStreamBridge::Cipher {
    std::size_t position = 0;
    std::size_t calls = 0;
    void decrypt(std::uint8_t* bytes, std::size_t n) override {
        ++calls;
        for (std::size_t i = 0; i < n; ++i)
            bytes[i] ^= static_cast<std::uint8_t>((position++ * 31 + 17) & 255);
    }
};
std::vector<std::uint8_t> encode(std::vector<std::uint8_t> plain) {
    ToyCipher encryptor;
    encryptor.decrypt(plain.data(), plain.size());
    return plain;
}
int main() {
    const std::vector<std::uint8_t> plain{
        6,0,42,0,9,8, 4,0,43,0, 7,0,44,0,1,2,3
    };
    const auto encrypted=encode(plain);
    ToyCipher cipher;
    CipherStreamBridge bridge(cipher);
    std::vector<std::uint8_t> out;
    assert(bridge.receive(encrypted.data(),1)==Result::NeedMore);
    assert(bridge.receive(encrypted.data()+1,2)==Result::NeedMore);
    assert(!bridge.pop(out));
    assert(bridge.receive(encrypted.data()+3,3)==Result::Ready);
    assert(bridge.pop(out));
    assert((out==std::vector<std::uint8_t>{6,0,42,0,9,8}));
    assert(bridge.receive(encrypted.data()+6,encrypted.size()-6)==Result::Ready);
    assert(bridge.pop(out));
    assert((out==std::vector<std::uint8_t>{4,0,43,0}));
    assert(bridge.pop(out));
    assert((out==std::vector<std::uint8_t>{7,0,44,0,1,2,3}));
    assert(!bridge.pop(out) && bridge.buffered()==0);
    assert(cipher.position==plain.size());
    assert(cipher.calls==4);
    assert(bridge.resetIfDrained());
    // A key-epoch reset cannot silently discard buffered partial messages.
    ToyCipher next;
    CipherStreamBridge partial(next);
    const std::vector<std::uint8_t> p{6,0,42,0,9,8};
    const auto encryptedPartial=encode(p);
    assert(partial.receive(encryptedPartial.data(),2)==Result::NeedMore);
    assert(!partial.resetIfDrained());
    assert(partial.receive(encryptedPartial.data()+2,4)==Result::Ready);
    assert(partial.pop(out));
    assert(partial.resetIfDrained());
    // If limits reject a burst, the cipher state must not advance.
    ToyCipher capped;
    CipherStreamBridge guarded(capped);
    std::vector<std::uint8_t> excessive(tq::StreamReassembler::kMaxBufferedBytes+1,0);
    assert(guarded.receive(excessive.data(),excessive.size())==Result::Invalid);
    assert(capped.position==0 && capped.calls==0 && guarded.failed());
    assert(guarded.receive(nullptr,0)==Result::Invalid);
    // Bad plaintext headers are rejected after exactly one decryption.
    ToyCipher invalidCipher;
    CipherStreamBridge malformed(invalidCipher);
    const auto invalidEncrypted=encode({0,0,0,0});
    assert(malformed.receive(invalidEncrypted.data(),invalidEncrypted.size())==Result::Invalid);
    assert(invalidCipher.position==4);
    return 0;
}
