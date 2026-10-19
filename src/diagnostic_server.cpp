#include <atomic>
#include <cerrno>
#include <csignal>
#include <cstdlib>
#include <iostream>
#include <string>
#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
using Socket = SOCKET;
static void close_socket(Socket s) { closesocket(s); }
#else
#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>
using Socket = int;
static void close_socket(Socket s) { close(s); }
constexpr Socket INVALID_SOCKET = -1;
constexpr int SOCKET_ERROR = -1;
#endif

// Diagnostic-only TCP listener. It is NOT a Conquer client protocol endpoint.
// Bind to loopback to avoid exposing an unauthenticated service to a network.
int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "Usage: tq_tcp_diagnostic <port 1..65535>\n";
        return 2;
    }
    std::string arg = argv[1];
    if (arg.empty() || arg.find_first_not_of("0123456789") != std::string::npos) {
        std::cerr << "Invalid port\n";
        return 2;
    }
    unsigned long parsed = std::strtoul(arg.c_str(), nullptr, 10);
    if (parsed == 0 || parsed > 65535) {
        std::cerr << "Invalid port\n";
        return 2;
    }
#ifdef _WIN32
    WSADATA wsa{};
    if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) return 1;
#endif
    Socket listener = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (listener == INVALID_SOCKET) return 1;
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(static_cast<unsigned short>(parsed));
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    if (bind(listener, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) == SOCKET_ERROR ||
        listen(listener, 8) == SOCKET_ERROR) {
        std::cerr << "Unable to bind/listen on 127.0.0.1:" << parsed << "\n";
        close_socket(listener);
#ifdef _WIN32
        WSACleanup();
#endif
        return 1;
    }
    std::cout << "Diagnostic TCP listener on 127.0.0.1:" << parsed
              << " (not a game server)" << std::endl;
    while (true) {
        Socket client = accept(listener, nullptr, nullptr);
        if (client == INVALID_SOCKET) break;
        const char message[] = "TQ diagnostic only; no Conquer protocol implemented.\n";
        send(client, message, static_cast<int>(sizeof(message) - 1), 0);
        close_socket(client);
    }
    close_socket(listener);
#ifdef _WIN32
    WSACleanup();
#endif
    return 1;
}
