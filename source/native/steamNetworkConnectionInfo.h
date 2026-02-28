///
// Copyright (c) 2026, Digital Descent, LLC. All rights reserved.
//

#pragma once

#include "steamConstants_bindings.h"
#include "steamPython_bindings.h"

#include "referenceCount.h"
#include "netAddress.h"

////////////////////////////////////////////////////////////////////
//       Class : SteamNetworkConnectionInfo
// Description : Represents a Valve GameSockets connection.
////////////////////////////////////////////////////////////////////
class EXPORT_CLASS SteamNetworkConnectionInfo : public ReferenceCount {
PUBLISHED:
  SteamNetworkConnectionInfo();
  virtual ~SteamNetworkConnectionInfo() = default;

  void set_listen_socket(SteamNetworkListenSocketHandle socket);
  SteamNetworkListenSocketHandle get_listen_socket() const;
    
  void set_net_address(const NetAddress &addr);
  const NetAddress &get_net_address() const;
    
  void set_state(int state);
  int get_state() const;
    
  void set_end_reason(int reason);
  int get_end_reason() const;

  MAKE_PROPERTY(listen_socket, get_listen_socket, set_listen_socket);
  MAKE_PROPERTY(net_address, get_net_address);
  MAKE_PROPERTY(state, get_state);
  MAKE_PROPERTY(end_reason, get_end_reason);

private:
  SteamNetworkListenSocketHandle _listen_socket;
  NetAddress _net_address;
  int _state;
  int _end_reason;
};