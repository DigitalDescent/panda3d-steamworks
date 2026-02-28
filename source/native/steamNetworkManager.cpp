///
// Copyright (c) 2026, Digital Descent, LLC. All rights reserved.
//

#include "steamNetworkManager.h"

// Guard everything below from interrogate's parser.
#ifndef CPPPARSER
#include "steamConstants_bindings.h"
#include "steamEnums_bindings.h"
#include "steamNetworkConnectionInfo.h"
#include "steamNetworkMessage.h"
#include "pStatCollector.h"

#include <steam/isteamnetworkingutils.h>

TypeHandle SteamNetworkManager::_type_handle;
SteamNetworkManager *SteamNetworkManager::_global_ptr = nullptr;
static SteamNetworkManager *_cast_global_ptr = nullptr;

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkManager::SteamNetworkManager
//       Access: Published
//  Description: Default constructor.  Initialises the Steam
//               GameSockets interface and registers this as the
//               global manager when none exists yet.
////////////////////////////////////////////////////////////////////
SteamNetworkManager::SteamNetworkManager() {
    _client_connection = 0;
    _is_client = false;

    _interface = SteamNetworkingSockets();
    if (_interface == nullptr) {
        steam_cat.error() << "Failed to get SteamNetworkingSockets interface." << std::endl;
    }
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkManager::get_global_ptr
//       Access: Published, Static
//  Description: Returns the global SteamNetworkManager pointer,
//               or nullptr if none has been created.
////////////////////////////////////////////////////////////////////
SteamNetworkManager *SteamNetworkManager::get_global_ptr() {
    if (!_global_ptr) {
      _global_ptr = new SteamNetworkManager();
    }

    return _global_ptr;
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkManager::create_ip_socket
//       Access: Published
//  Description: Creates a listen socket bound to the given local
//               port.  Returns a connection handle that remote
//               peers can connect to via connect_by_ip_address.
////////////////////////////////////////////////////////////////////
SteamNetworkConnectionHandle SteamNetworkManager::create_ip_socket(int port) {
    if (_interface == nullptr) {
        steam_cat.error() << "SteamNetworkingSockets interface not initialised." << std::endl;
        return INVALID_STEAM_NETWORK_CONNECTION_HANDLE;
    }

    SteamNetworkingIPAddr local_addr;
    local_addr.Clear();
    local_addr.m_port = static_cast<uint16>(port);

    SteamNetworkingConfigValue_t opt;
    opt.SetPtr(k_ESteamNetworkingConfig_Callback_ConnectionStatusChanged, (void *)OnSteamNetConnectionStatusChanged);

    HSteamListenSocket listen_socket = _interface->CreateListenSocketIP(local_addr, 1, &opt);
    return static_cast<SteamNetworkConnectionHandle>(listen_socket);
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkManager::create_steam_id_socket
//       Access: Published
//  Description: Creates a P2P listen socket on the given virtual
//               port.  Remote peers connect via connect_by_steam_id.
////////////////////////////////////////////////////////////////////
SteamNetworkConnectionHandle SteamNetworkManager::create_steam_id_socket(int port) {
    if (_interface == nullptr) {
        steam_cat.error() << "SteamNetworkingSockets interface not initialised." << std::endl;
        return INVALID_STEAM_NETWORK_CONNECTION_HANDLE;
    }

    SteamNetworkingConfigValue_t opt;
    opt.SetPtr(k_ESteamNetworkingConfig_Callback_ConnectionStatusChanged, (void *)OnSteamNetConnectionStatusChanged);

    HSteamListenSocket listen_socket = _interface->CreateListenSocketP2P(port, 1, &opt);
    return static_cast<SteamNetworkConnectionHandle>(listen_socket);
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkManager::connect_by_ip_address
//       Access: Published
//  Description: Begins connecting to a remote host by IP address.
//               Returns the connection handle.
////////////////////////////////////////////////////////////////////
SteamNetworkConnectionHandle SteamNetworkManager::connect_by_ip_address(const NetAddress &address) {
    if (_interface == nullptr) {
        steam_cat.error() << "SteamNetworkingSockets interface not initialised." << std::endl;
        return INVALID_STEAM_NETWORK_CONNECTION_HANDLE;
    }

    SteamNetworkingIPAddr steam_addr;
    steam_addr.Clear();
    steam_addr.ParseString(address.get_ip_string().c_str());
    steam_addr.m_port = address.get_port();

    SteamNetworkingConfigValue_t opt;
    opt.SetPtr(k_ESteamNetworkingConfig_Callback_ConnectionStatusChanged, (void *)OnSteamNetConnectionStatusChanged);

    SteamNetworkConnectionHandle handle = _interface->ConnectByIPAddress(steam_addr, 1, &opt);
    if (handle == k_HSteamNetConnection_Invalid) {
        steam_cat.error() << "Failed to connect by IP address." << std::endl;
        return INVALID_STEAM_NETWORK_CONNECTION_HANDLE;
    }

    _client_connection = handle;
    _is_client = true;
    return handle;
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkManager::connect_by_steam_id
//       Access: Published
//  Description: Begins connecting to a remote peer by Steam ID
//               string.  Returns the connection handle.
////////////////////////////////////////////////////////////////////
SteamNetworkConnectionHandle SteamNetworkManager::connect_by_steam_id(const std::string &steam_id) {
    if (_interface == nullptr) {
        steam_cat.error() << "SteamNetworkingSockets interface not initialised." << std::endl;
        return INVALID_STEAM_NETWORK_CONNECTION_HANDLE;
    }

    SteamNetworkingIdentity identity;
    identity.SetSteamID64(strtoull(steam_id.c_str(), nullptr, 10));

    SteamNetworkingConfigValue_t opt;
    opt.SetPtr(k_ESteamNetworkingConfig_Callback_ConnectionStatusChanged, (void *)OnSteamNetConnectionStatusChanged);

    SteamNetworkConnectionHandle handle = _interface->ConnectP2P(identity, 0, 1, &opt);
    if (handle == k_HSteamNetConnection_Invalid) {
        steam_cat.error() << "Failed to connect by Steam ID." << std::endl;
        return INVALID_STEAM_NETWORK_CONNECTION_HANDLE;
    }

    _client_connection = handle;
    _is_client = true;
    return handle;
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkManager::get_connection_info
//       Access: Published
//  Description: Fills in a SteamNetworkConnectionInfo structure
//               with the current state of the given connection.
//               Returns true on success.
////////////////////////////////////////////////////////////////////
bool SteamNetworkManager::get_connection_info(SteamNetworkConnectionHandle connection, SteamNetworkConnectionInfo &info) {
    if (_interface == nullptr) return false;

    SteamNetConnectionInfo_t native_info;
    if (!_interface->GetConnectionInfo(connection, &native_info)) {
        return false;
    }

    info.set_listen_socket(static_cast<SteamNetworkListenSocketHandle>(native_info.m_hListenSocket));
    info.set_state(native_info.m_eState);
    info.set_end_reason(native_info.m_eEndReason);
    return true;
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkManager::close_connection
//       Access: Published
//  Description: Closes the given connection gracefully.
////////////////////////////////////////////////////////////////////
void SteamNetworkManager::close_connection(SteamNetworkConnectionHandle connection) {
    if (_interface == nullptr) return;
    _interface->CloseConnection(connection, 0, nullptr, false);
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkManager::accept_connection
//       Access: Published
//  Description: Accepts an incoming connection that has been
//               signalled via a connection status callback.
////////////////////////////////////////////////////////////////////
void SteamNetworkManager::accept_connection(SteamNetworkConnectionHandle connection) {
    if (_interface == nullptr) return;
    _interface->AcceptConnection(connection);
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkManager::receive_message_on_connection
//       Access: Published
//  Description: Receives the next pending message on the given
//               connection and populates the supplied
//               SteamNetworkMessage.  Returns true when a message
//               was received.
////////////////////////////////////////////////////////////////////
bool SteamNetworkManager::receive_message_on_connection(SteamNetworkConnectionHandle connection, SteamNetworkMessage &message) {
    if (_interface == nullptr) return false;

    SteamNetworkingMessage_t *pMsg = nullptr;
    int count = _interface->ReceiveMessagesOnConnection(connection, &pMsg, 1);
    if (count <= 0 || pMsg == nullptr) {
        return false;
    }

    Datagram dg(pMsg->m_pData, pMsg->m_cbSize);
    message.set_datagram(std::move(dg));
    message.set_connection(static_cast<SteamNetworkConnectionHandle>(pMsg->m_conn));
    pMsg->Release();
    return true;
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkManager::receive_message_on_poll_group
//       Access: Published
//  Description: Receives the next pending message on the given
//               poll group and populates the supplied
//               SteamNetworkMessage.  Returns true when a message
//               was received.
////////////////////////////////////////////////////////////////////
bool SteamNetworkManager::receive_message_on_poll_group(SteamNetworkPollGroupHandle poll_group, SteamNetworkMessage &message) {
    if (_interface == nullptr) return false;

    SteamNetworkingMessage_t *pMsg = nullptr;
    int count = _interface->ReceiveMessagesOnPollGroup(poll_group, &pMsg, 1);
    if (count <= 0 || pMsg == nullptr) {
        return false;
    }

    Datagram dg(pMsg->m_pData, pMsg->m_cbSize);
    message.set_datagram(std::move(dg));
    message.set_connection(static_cast<SteamNetworkConnectionHandle>(pMsg->m_conn));
    pMsg->Release();
    return true;
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkManager::create_poll_group
//       Access: Published
//  Description: Creates a new poll group and returns its handle.
////////////////////////////////////////////////////////////////////
SteamNetworkPollGroupHandle SteamNetworkManager::create_poll_group() {
    if (_interface == nullptr) return INVALID_STEAM_NETWORK_POLL_GROUP_HANDLE;
    return static_cast<SteamNetworkPollGroupHandle>(_interface->CreatePollGroup());
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkManager::set_connection_poll_group
//       Access: Published
//  Description: Assigns a connection to the given poll group so
//               messages can be received via
//               receive_message_on_poll_group.
////////////////////////////////////////////////////////////////////
void SteamNetworkManager::set_connection_poll_group(SteamNetworkConnectionHandle connection, SteamNetworkPollGroupHandle poll_group) {
    if (_interface == nullptr) return;
    _interface->SetConnectionPollGroup(connection, poll_group);
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkManager::send_datagram
//       Access: Published
//  Description: Sends a datagram to the specified connection with
//               the given send flags (reliable, unreliable, etc.).
////////////////////////////////////////////////////////////////////
void SteamNetworkManager::send_datagram(SteamNetworkConnectionHandle connection, const Datagram &dg, int send_flags) {
    if (_interface == nullptr) return;
    _interface->SendMessageToConnection(connection, dg.get_data(), dg.get_length(), send_flags, nullptr);
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkManager::send_datagram
//       Access: Published
//  Description: Sends a datagram to the current client connection
//               with the given send flags.  Only valid after a
//               successful connect_by_* call.
////////////////////////////////////////////////////////////////////
void SteamNetworkManager::send_datagram(const Datagram &&dg, int send_flags) {
    if (_interface == nullptr || !_is_client) return;
    _interface->SendMessageToConnection(_client_connection, dg.get_data(), dg.get_length(), send_flags, nullptr);
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkManager::run_callbacks
//       Access: Published
//  Description: Pumps the networking callbacks.  Should be called
//               once per frame.
////////////////////////////////////////////////////////////////////
void SteamNetworkManager::run_callbacks() {
    if (_interface != nullptr) {
        _interface->RunCallbacks();
    }
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkManager::get_next_event
//       Access: Published
//  Description: Returns and removes the oldest queued connection
//               state-change event, or nullptr if the queue is
//               empty.
////////////////////////////////////////////////////////////////////
PT(SteamNetworkEvent) SteamNetworkManager::get_next_event() {
    if (_events.empty()) {
        return nullptr;
    }
    PT(SteamNetworkEvent) event = _events.front();
    _events.pop_front();
    return event;
}

////////////////////////////////////////////////////////////////////
//     Function: SteamNetworkManager::OnSteamNetConnectionStatusChanged
//       Access: Public, Static
//  Description: Static callback invoked by Steam when a connection
//               changes state.  Queues a SteamNetworkEvent on the
//               global manager.
////////////////////////////////////////////////////////////////////
void SteamNetworkManager::OnSteamNetConnectionStatusChanged(SteamNetConnectionStatusChangedCallback_t *pInfo) {
    if (_global_ptr == nullptr) return;

    PT(SteamNetworkEvent) event = new SteamNetworkEvent(
        static_cast<SteamNetworkConnectionHandle>(pInfo->m_hConn),
        static_cast<int>(pInfo->m_eOldState),
        static_cast<int>(pInfo->m_info.m_eState)
    );
    _global_ptr->_events.push_back(event);
}

#endif // CPPPARSER