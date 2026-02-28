///
// Copyright (c) 2026, Digital Descent, LLC. All rights reserved.
//

#include "steamNetworkEvent.h"

// Guard everything below from interrogate's parser.
#ifndef CPPPARSER
#include "steamConstants_bindings.h"
#include "steamEnums_bindings.h"

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkEvent::get_connection
//       Access: Published
////////////////////////////////////////////////////////////////////
SteamNetworkConnectionHandle SteamNetworkEvent::get_connection() const {
    return _connection;
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkEvent::get_old_state
//       Access: Published
////////////////////////////////////////////////////////////////////
int SteamNetworkEvent::get_old_state() const {
    return _old_state;
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkEvent::get_state
//       Access: Published
////////////////////////////////////////////////////////////////////
int SteamNetworkEvent::get_state() const {
    return _state;
}

#endif  // CPPPARSER