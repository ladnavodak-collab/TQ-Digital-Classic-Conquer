Classic COPS character creation safeguards

This actual COPS v7 C++ patch prevents creating a character unless its requested initial profession is Trojan (10), Warrior (20), Archer (40) or Taoist (100). It rejects missing level-1 point allot records before executing the INSERT. Upstream had also declared the Soul output argument by value in both database.h and database.cpp, causing the newly created Taoist's Soul/Mana allocation to be lost; both are fixed by passing a reference.

Only first-character creation is covered; class promotion, rebirth paths, in-game skills and actual 5065 client login are still unverified. This is for the loopback-only development server.
