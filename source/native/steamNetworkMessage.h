///
// Copyright (c) 2026, Digital Descent, LLC. All rights reserved.
//

#pragma once

#include "steamConstants_bindings.h"
#include "steamPython_bindings.h"

#include "datagram.h"
#include "datagramIterator.h"

////////////////////////////////////////////////////////////////////
//       Class : SteamNetworkMessage
// Description : Represents a Valve GameSockets message.
////////////////////////////////////////////////////////////////////
class EXPORT_CLASS SteamNetworkMessage {
PUBLISHED:
  SteamNetworkMessage()
    : _connection(INVALID_STEAM_NETWORK_CONNECTION_HANDLE) {}
  virtual ~SteamNetworkMessage() = default;

  void set_datagram(const Datagram &dg);
  void set_datagram(Datagram &&dg);
  Datagram get_datagram() const;
  DatagramIterator get_datagram_iterator() const;

  void set_connection(SteamNetworkConnectionHandle connection);
  SteamNetworkConnectionHandle get_connection() const;

  MAKE_PROPERTY(dg, get_datagram, set_datagram);
  MAKE_PROPERTY(dgi, get_datagram_iterator);
  MAKE_PROPERTY(connection, get_connection, set_connection);

private:
  Datagram _dg;
  DatagramIterator _dgi;
  SteamNetworkConnectionHandle _connection;
};

