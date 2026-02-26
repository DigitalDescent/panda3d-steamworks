/**
 * Copyright (c) 2026 Digital Descent LLC. All rights reserved.
 */

#pragma once

#include "pandabase.h"
#include <string>

// Forward declaration - we don't include Steam headers here so interrogate
// only sees our clean wrapper class.

////////////////////////////////////////////////////////////////////
//       Class : SteamApps
// Description : Static wrapper around the Steamworks ISteamApps
//               interface, providing access to app ownership,
//               DLC, language, and installation information.
////////////////////////////////////////////////////////////////////
class EXPORT_CLASS SteamApps {
PUBLISHED:
  // Initialization - must be called before any other SteamApps methods.
  // Returns true if SteamAPI was initialized successfully.
  static bool init();
  static void shutdown();

  // Ownership queries
  static bool is_subscribed();
  static bool is_low_violence();
  static bool is_cybercafe();
  static bool is_vac_banned();
  static bool is_subscribed_app(unsigned int app_id);
  static bool is_subscribed_from_free_weekend();
  static bool is_subscribed_from_family_sharing();
  static bool is_app_installed(unsigned int app_id);

  // DLC
  static bool is_dlc_installed(unsigned int app_id);
  static int get_dlc_count();
  static void install_dlc(unsigned int app_id);
  static void uninstall_dlc(unsigned int app_id);
  static bool set_dlc_context(unsigned int app_id);

  // App info
  static unsigned int get_earliest_purchase_unix_time(unsigned int app_id);
  static int get_app_build_id();
  static std::string get_current_game_language();
  static std::string get_available_game_languages();
  static std::string get_current_beta_name();
  static std::string get_app_install_dir(unsigned int app_id);
  static std::string get_launch_query_param(const std::string &key);

  // Misc
  static bool mark_content_corrupt(bool missing_files_only);
  static unsigned long long get_app_owner();

private:
  SteamApps() = delete;
};
