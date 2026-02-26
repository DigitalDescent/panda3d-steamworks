#pragma once

#include "pandabase.h"
#include <string>
#include <vector>

////////////////////////////////////////////////////////////////////
//       Class : SteamAppTicket
// Description : Static wrapper around the Steamworks ISteamAppTicket
//               interface, providing access to app ownership ticket
//               data for DRM and ownership verification.
////////////////////////////////////////////////////////////////////
class EXPORT_CLASS SteamAppTicket {
PUBLISHED:
  // Returns the raw ownership ticket for the given app as a byte
  // vector, or an empty vector on failure.  The ticket can be sent
  // to a server for ownership verification.
  static std::vector<unsigned char> get_app_ownership_ticket_data(unsigned int app_id);

  // Returns the raw ownership ticket along with offset information
  // encoded as: [app_id_offset, steam_id_offset, signature_offset,
  // signature_length, ticket_bytes...].  This lets callers locate
  // the app-id, steam-id, and signature within the ticket blob.
  // Returns an empty vector on failure.
  static std::vector<unsigned char> get_app_ownership_ticket_data_with_info(unsigned int app_id);

private:
  SteamAppTicket() = delete;
};
