///
// Copyright (c) 2026, Digital Descent, LLC. All rights reserved.
//

#pragma once

#include "steamConstants_bindings.h"
#include "steamPython_bindings.h"
#include "referenceCount.h"

////////////////////////////////////////////////////////////////////
//       Class : SteamNetworkEvent
// Description : Represents a single callback event for a connnection state change.
////////////////////////////////////////////////////////////////////
class EXPORT_CLASS SteamNetworkEvent : public ReferenceCount {
public:
    SteamNetworkEvent(SteamNetworkConnectionHandle connection, int old_state, int state)
        : _connection(connection), _old_state(old_state), _state(state) {}

PUBLISHED:
  SteamNetworkConnectionHandle get_connection() const;
  int get_old_state() const;
  int get_state() const;
  
  MAKE_PROPERTY(connection, get_connection);
  MAKE_PROPERTY(old_state, get_old_state);
  MAKE_PROPERTY(state, get_state);

private:
  SteamNetworkConnectionHandle _connection;
  int _old_state;
  int _state;
};