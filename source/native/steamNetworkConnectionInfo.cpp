///
// Copyright (c) 2026, Digital Descent, LLC. All rights reserved.
//

#include "steamNetworkConnectionInfo.h"

// Guard everything below from interrogate's parser.
#ifndef CPPPARSER
#include "steamConstants_bindings.h"
#include "steamEnums_bindings.h"

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkConnectionInfo::SteamNetworkConnectionInfo
//       Access: Published
//  Description: Default constructor. Initializes the connection info
//               with invalid/default values.
////////////////////////////////////////////////////////////////////
SteamNetworkConnectionInfo::SteamNetworkConnectionInfo() {
  _listen_socket = INVALID_STEAM_NETWORK_LISTEN_SOCKET_HANDLE;
  _state = SteamNetworkingConnectionState::k_ESteamNetworkingConnectionState_None;
  _end_reason = 0;
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkConnectionInfo::set_listen_socket
//       Access: Published
////////////////////////////////////////////////////////////////////
void SteamNetworkConnectionInfo::set_listen_socket(SteamNetworkListenSocketHandle socket) {
    _listen_socket = socket;
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkConnectionInfo::get_listen_socket
//       Access: Published
////////////////////////////////////////////////////////////////////
SteamNetworkListenSocketHandle SteamNetworkConnectionInfo::get_listen_socket() const {
    return _listen_socket;
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkConnectionInfo::set_net_address
//       Access: Published
////////////////////////////////////////////////////////////////////
void SteamNetworkConnectionInfo::set_net_address(const NetAddress &addr) {
    _net_address = addr;
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkConnectionInfo::get_net_address
//       Access: Published
////////////////////////////////////////////////////////////////////
const NetAddress &SteamNetworkConnectionInfo::get_net_address() const {
    return _net_address;
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkConnectionInfo::set_state
//       Access: Published
////////////////////////////////////////////////////////////////////
void SteamNetworkConnectionInfo::set_state(int state) {
    _state = state;
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkConnectionInfo::get_state
//       Access: Published
////////////////////////////////////////////////////////////////////
int SteamNetworkConnectionInfo::get_state() const {
    return _state;
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkConnectionInfo::set_end_reason
//       Access: Published
////////////////////////////////////////////////////////////////////
void SteamNetworkConnectionInfo::set_end_reason(int reason) {
    _end_reason = reason;
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkConnectionInfo::get_end_reason
//       Access: Published
////////////////////////////////////////////////////////////////////
int SteamNetworkConnectionInfo::get_end_reason() const {
    return _end_reason;
}

#endif // CPPPARSER