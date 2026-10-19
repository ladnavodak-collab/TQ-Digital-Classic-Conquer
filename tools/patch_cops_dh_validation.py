#!/usr/bin/env python3
"""Add strict bounds checks before parsing an upstream COPS Diffie-Hellman response.
Only apply to a pinned, disposable upstream checkout. This is not full login compatibility.
"""
from pathlib import Path
import sys

def patch(root: Path) -> None:
    file = root / "src/Network/msgloginchallenges.cpp"
    source = file.read_text(encoding="utf-8")
    old = """    uint8_t* ptr = mBuf;

    ptr += MsgLoginChallengeS::PADDING_LEN; // Padding
    ptr += sizeof(int32_t); // Size
    ptr += *((int32_t*)(ptr)) + sizeof(int32_t); // JunkSize + Junk

    int32_t b_len = *((int32_t*)(ptr));
    ptr += sizeof(int32_t);

    char* b_key = new char[b_len + 1];"""
    new = """    // Validate all user-controlled offsets before accessing the payload.
    // The native-endian fields have already been swapped on BE platforms.
    const size_t prefix = MsgLoginChallengeS::PADDING_LEN;
    if (mLen < prefix + 3 * sizeof(int32_t))
    {
        client.disconnect();
        return;
    }
    int32_t advertisedSize = 0;
    memcpy(&advertisedSize, mBuf + prefix, sizeof(advertisedSize));
    if (advertisedSize < static_cast<int32_t>(3 * sizeof(int32_t)) ||
        static_cast<size_t>(advertisedSize) > mLen - prefix)
    {
        client.disconnect();
        return;
    }
    const size_t bound = prefix + static_cast<size_t>(advertisedSize);
    int32_t junkSize = 0;
    memcpy(&junkSize, mBuf + prefix + sizeof(int32_t), sizeof(junkSize));
    const size_t junkStart = prefix + 2 * sizeof(int32_t);
    if (junkSize < 0 || static_cast<size_t>(junkSize) > bound - junkStart ||
        bound - junkStart - static_cast<size_t>(junkSize) < sizeof(int32_t))
    {
        client.disconnect();
        return;
    }
    const size_t keyLengthOffset = junkStart + static_cast<size_t>(junkSize);
    int32_t b_len = 0;
    memcpy(&b_len, mBuf + keyLengthOffset, sizeof(b_len));
    const size_t keyStart = keyLengthOffset + sizeof(int32_t);
    // DH's hex public key must be nonempty, reasonably bounded, and fit
    // wholly in the declared message. Never allocate from unchecked length.
    if (b_len <= 0 || b_len > 512 ||
        static_cast<size_t>(b_len) > bound - keyStart)
    {
        client.disconnect();
        return;
    }
    const uint8_t* ptr = mBuf + keyStart;
    for (int32_t index = 0; index < b_len; ++index)
    {
        const uint8_t digit = ptr[index];
        if (!((digit >= '0' && digit <= '9') ||
              (digit >= 'a' && digit <= 'f') ||
              (digit >= 'A' && digit <= 'F')))
        {
            client.disconnect();
            return;
        }
    }

    char* b_key = new char[b_len + 1];"""
    if source.count(old) != 1:
        raise RuntimeError(f"Expected unique upstream source anchor in {file}, found {source.count(old)}")
    source = source.replace(old, new)
    old2 = """    uint8_t seed[256]; // would mean a 2048 bits integer...
    size_t seed_len(0);
    hex2bin(s_key.c_str(), seed, seed_len);"""
    new2 = """    // hex2bin writes into a fixed array; enforce the capacity first.
    if (s_key.empty() || s_key.size() > 512 ||
        (s_key.size() % 2) != 0)
    {
        client.disconnect();
        return;
    }
    uint8_t seed[256] = { 0 };
    size_t seed_len(0);
    hex2bin(s_key.c_str(), seed, seed_len);"""
    if source.count(old2) != 1:
        raise RuntimeError(f"Expected unique seed conversion anchor, found {source.count(old2)}")
    file.write_text(source.replace(old2, new2), encoding="utf-8")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: patch_cops_dh_validation.py <upstream-source-directory>")
    patch(Path(sys.argv[1]))
    print("Applied DH payload offset and seed bounds checks.")
