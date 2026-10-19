// Test-only CLI adapter to the EXACT upstream COPS Blowfish CFB64 implementation.
// Never linked into a production server, and does not print credentials.
#include "blowfish.h"
#include <cstdint>
#include <cstdio>
#include <iostream>
#include <string>
#include <vector>

static int nibble(char c)
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

static bool decode(const char* text, std::vector<uint8_t>& out, size_t maxLen)
{
    const std::string hex(text);
    if (hex.empty() || hex.size() % 2 != 0 || hex.size()/2 > maxLen)
        return false;
    for (size_t i = 0; i < hex.size(); i += 2)
    {
        const int hi=nibble(hex[i]), lo=nibble(hex[i+1]);
        if (hi < 0 || lo < 0) return false;
        out.push_back(static_cast<uint8_t>((hi << 4) | lo));
    }
    return true;
}

int main(int argc, char** argv)
{
    if (argc != 5) return 2;
    std::vector<uint8_t> key, iv, bytes;
    if (!decode(argv[2], key, 72) || !decode(argv[3], iv, 8) ||
        !decode(argv[4], bytes, 4096) || iv.size()!=8)
        return 2;
    Blowfish cipher;
    cipher.generateKey(key.data(),key.size());
    cipher.setIVs(iv.data(),iv.data());
    const std::string operation=argv[1];
    if (operation=="encrypt")
        cipher.encrypt(bytes.data(),bytes.size());
    else if (operation=="decrypt")
        cipher.decrypt(bytes.data(),bytes.size());
    else
        return 2;
    const char digits[]="0123456789abcdef";
    for (uint8_t b:bytes)
    {
        std::cout << digits[b >> 4] << digits[b & 15];
    }
    std::cout << '\n';
    return 0;
}
