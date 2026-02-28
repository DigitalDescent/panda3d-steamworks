///
// Copyright (c) 2026, Digital Descent, LLC. All rights reserved.
//

#pragma once

#include "config_module.h"
#include "steamConstants_bindings.h"
#include "steamPython_bindings.h"

#ifndef CPPPARSER
#include <steam/isteamnetworkingsockets.h>
#endif

#include "referenceCount.h"
#include "pointerTo.h"
#include "datagram.h"
#include "netAddress.h"
#include "datagramIterator.h"
#include "pdeque.h"
#include "register_type.h"
#include "steamNetworkEvent.h"
#include "typedObject.h"

class SteamNetworkConnectionInfo;
class SteamNetworkMessage;

////////////////////////////////////////////////////////////////////
//       Class : SteamNetworkManager
// Description : Responsible for managing Steam GameSockets connections 
//               and messages.
////////////////////////////////////////////////////////////////////
class EXPORT_CLASS SteamNetworkManager : public TypedObject {
#ifndef CPPPARSER
public:
    static void OnSteamNetConnectionStatusChanged(SteamNetConnectionStatusChangedCallback_t *pInfo);
#endif

PUBLISHED:
    SteamNetworkManager();
    virtual ~SteamNetworkManager() = default;
    static SteamNetworkManager *get_global_ptr();

    SteamNetworkConnectionHandle create_ip_socket(int port);
    SteamNetworkConnectionHandle create_steam_id_socket(int port);
    SteamNetworkConnectionHandle connect_by_ip_address(const NetAddress &address);
    SteamNetworkConnectionHandle connect_by_steam_id(const std::string &steam_id);
    bool get_connection_info(SteamNetworkConnectionHandle connection, SteamNetworkConnectionInfo &info);
    void close_connection(SteamNetworkConnectionHandle connection);
    void accept_connection(SteamNetworkConnectionHandle connection);

    bool receive_message_on_connection(SteamNetworkConnectionHandle connection, SteamNetworkMessage &message);
    bool receive_message_on_poll_group(SteamNetworkPollGroupHandle poll_group, SteamNetworkMessage &message);

    SteamNetworkPollGroupHandle create_poll_group();
    void set_connection_poll_group(SteamNetworkConnectionHandle connection, SteamNetworkPollGroupHandle poll_group);

    void send_datagram(SteamNetworkConnectionHandle connection, const Datagram &dg, int send_flags);
    void send_datagram(const Datagram &&dg, int send_flags);

    void run_callbacks();
    PT(SteamNetworkEvent) get_next_event();

public:
    static TypeHandle get_class_type() {
        return _type_handle;
    }
    static void init_type() {
        TypedObject::init_type();
        register_type(_type_handle, "SteamNetworkManager",
                      TypedObject::get_class_type());
    }
    virtual TypeHandle get_type() const {
        return get_class_type();
    }
    virtual TypeHandle force_init_type() {
        init_type();
        return get_class_type();
    }

private:
  static TypeHandle _type_handle;
  pdeque<PT(SteamNetworkEvent)> _events;
  static SteamNetworkManager *_global_ptr;

#ifndef CPPPARSER
  ISteamNetworkingSockets *_interface;
#endif

  SteamNetworkConnectionHandle _client_connection;
  bool _is_client;
};