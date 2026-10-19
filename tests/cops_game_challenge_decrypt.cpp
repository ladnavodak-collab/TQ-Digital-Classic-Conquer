// Decrypt actual COPS first game-port challenge using upstream Blowfish CFB64.
// Input/output are binary standard streams; no credentials, token or key printed.
#include "blowfish.h"
#include <iostream>
#include <iterator>
#include <string>
#include <vector>

int main() {
    std::string input((std::istreambuf_iterator<char>(std::cin)),
                      std::istreambuf_iterator<char>());
    if (input.empty() || input.size() > 4096)
        return 2;
    std::vector<uint8_t> data(input.begin(), input.end());
    const char key[] = "DR654dt34trg4UI6";
    const uint8_t iv[8] = {0};
    Blowfish cipher;
    cipher.generateKey(reinterpret_cast<const uint8_t*>(key), sizeof(key)-1);
    cipher.setIVs(iv,iv);
    cipher.decrypt(data.data(),data.size());
    std::cout.write(reinterpret_cast<const char*>(data.data()),data.size());
    return std::cout.good() ? 0 : 3;
}
