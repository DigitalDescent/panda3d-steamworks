#include "steamAppTicket.h"

// Guard everything below from interrogate's parser.
#ifndef CPPPARSER

#include <steam/steam_api.h>
#include <steam/steam_api_flat.h>
#include <steam/isteamappticket.h>
#include <cstring>

// Helper: obtains the ISteamAppTicket interface via the generic
// interface accessor on ISteamClient.
static ISteamAppTicket *get_steam_app_ticket() {
  ISteamClient *client = SteamClient();
  if (!client) return nullptr;

  HSteamUser  user = SteamAPI_GetHSteamUser();
  HSteamPipe  pipe = SteamAPI_GetHSteamPipe();
  void *iface = client->GetISteamGenericInterface(
      user, pipe, STEAMAPPTICKET_INTERFACE_VERSION);
  return static_cast<ISteamAppTicket *>(iface);
}

////////////////////////////////////////////////////////////////////
//     Function: SteamAppTicket::get_app_ownership_ticket_data
//       Access: Published, Static
//  Description: Returns the app ownership ticket as a byte vector.
//               Returns an empty vector if the interface is
//               unavailable or the call fails.
////////////////////////////////////////////////////////////////////
std::vector<unsigned char>
SteamAppTicket::get_app_ownership_ticket_data(unsigned int app_id) {
  ISteamAppTicket *ticket = get_steam_app_ticket();
  if (!ticket) return {};

  // First call to determine the required buffer size.
  unsigned char buf[4096];
  uint32 pi_app = 0, pi_steam = 0, pi_sig = 0, cb_sig = 0;
  uint32 size = ticket->GetAppOwnershipTicketData(
      app_id, buf, sizeof(buf),
      &pi_app, &pi_steam, &pi_sig, &cb_sig);

  if (size == 0) return {};

  return std::vector<unsigned char>(buf, buf + size);
}

////////////////////////////////////////////////////////////////////
//     Function: SteamAppTicket::get_app_ownership_ticket_data_with_info
//       Access: Published, Static
//  Description: Returns the ownership ticket prepended with 16 bytes
//               of little-endian uint32 offset data:
//                 bytes  0- 3 : app-id offset in ticket
//                 bytes  4- 7 : steam-id offset in ticket
//                 bytes  8-11 : signature offset in ticket
//                 bytes 12-15 : signature length
//                 bytes 16+   : raw ticket data
//               Returns an empty vector on failure.
////////////////////////////////////////////////////////////////////
std::vector<unsigned char>
SteamAppTicket::get_app_ownership_ticket_data_with_info(unsigned int app_id) {
  ISteamAppTicket *ticket = get_steam_app_ticket();
  if (!ticket) return {};

  unsigned char buf[4096];
  uint32 pi_app = 0, pi_steam = 0, pi_sig = 0, cb_sig = 0;
  uint32 size = ticket->GetAppOwnershipTicketData(
      app_id, buf, sizeof(buf),
      &pi_app, &pi_steam, &pi_sig, &cb_sig);

  if (size == 0) return {};

  // Build result: 4 x uint32 header + ticket bytes.
  std::vector<unsigned char> result(16 + size);

  auto write_u32 = [&](size_t offset, uint32 val) {
    std::memcpy(result.data() + offset, &val, 4);
  };

  write_u32(0,  pi_app);
  write_u32(4,  pi_steam);
  write_u32(8,  pi_sig);
  write_u32(12, cb_sig);
  std::memcpy(result.data() + 16, buf, size);

  return result;
}

#endif  // CPPPARSER
