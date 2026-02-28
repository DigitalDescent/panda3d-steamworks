///
// Copyright (c) 2026, Digital Descent, LLC. All rights reserved.
//

#include "steamNetworkMessage.h"

// Guard everything below from interrogate's parser.
#ifndef CPPPARSER
#include "steamConstants_bindings.h"
#include "steamEnums_bindings.h"

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkMessage::set_datagram
//       Access: Published
//  Description: Sets the message datagram by const reference and
//               resets the iterator to the beginning.
////////////////////////////////////////////////////////////////////
void SteamNetworkMessage::set_datagram(const Datagram &dg) {
    _dg = dg;
    _dgi = DatagramIterator(_dg);
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkMessage::set_datagram
//       Access: Published
//  Description: Sets the message datagram by move and resets the
//               iterator to the beginning.
////////////////////////////////////////////////////////////////////
void SteamNetworkMessage::set_datagram(Datagram &&dg) {
    _dg = std::move(dg);
    _dgi = DatagramIterator(_dg);
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkMessage::get_datagram
//       Access: Published
////////////////////////////////////////////////////////////////////
Datagram SteamNetworkMessage::get_datagram() const {
    return _dg;
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkMessage::get_datagram_iterator
//       Access: Published
////////////////////////////////////////////////////////////////////
DatagramIterator SteamNetworkMessage::get_datagram_iterator() const {
    return _dgi;
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkMessage::set_connection
//       Access: Published
////////////////////////////////////////////////////////////////////
void SteamNetworkMessage::set_connection(SteamNetworkConnectionHandle connection) {
    _connection = connection;
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkMessage::get_connection
//       Access: Published
////////////////////////////////////////////////////////////////////
SteamNetworkConnectionHandle SteamNetworkMessage::get_connection() const {
    return _connection;
}

#endif  // CPPPARSER