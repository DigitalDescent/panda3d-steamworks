/**
 * Copyright (c) 2026 Digital Descent LLC. All rights reserved.
 */

#include "steamApps.h"

// Guard everything below from interrogate's parser - it only needs the header.
#ifndef CPPPARSER

#include <steam/steam_api.h>
#include <steam/steam_api_flat.h>

// Helper: returns the ISteamApps interface pointer, or nullptr if not initialized.
static ISteamApps *get_steam_apps() {
  return SteamAPI_SteamApps();
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::init
//       Access: Published, Static
//  Description: Initializes the Steamworks API.  Must be called
//               before any other SteamApps methods.  Returns true
//               on success.
////////////////////////////////////////////////////////////////////
bool SteamApps::init() {
  return SteamAPI_Init();
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::shutdown
//       Access: Published, Static
//  Description: Shuts down the Steamworks API.
////////////////////////////////////////////////////////////////////
void SteamApps::shutdown() {
  SteamAPI_Shutdown();
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::is_subscribed
//       Access: Published, Static
//  Description: Returns true if the active user owns the current app.
////////////////////////////////////////////////////////////////////
bool SteamApps::is_subscribed() {
  ISteamApps *apps = get_steam_apps();
  if (!apps) return false;
  return apps->BIsSubscribed();
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::is_low_violence
//       Access: Published, Static
//  Description: Returns true if the license is a low-violence version.
////////////////////////////////////////////////////////////////////
bool SteamApps::is_low_violence() {
  ISteamApps *apps = get_steam_apps();
  if (!apps) return false;
  return apps->BIsLowViolence();
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::is_cybercafe
//       Access: Published, Static
//  Description: Returns true if the app is running from a cybercafe.
////////////////////////////////////////////////////////////////////
bool SteamApps::is_cybercafe() {
  ISteamApps *apps = get_steam_apps();
  if (!apps) return false;
  return apps->BIsCybercafe();
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::is_vac_banned
//       Access: Published, Static
//  Description: Returns true if the user has a VAC ban on their account.
////////////////////////////////////////////////////////////////////
bool SteamApps::is_vac_banned() {
  ISteamApps *apps = get_steam_apps();
  if (!apps) return false;
  return apps->BIsVACBanned();
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::is_subscribed_app
//       Access: Published, Static
//  Description: Returns true if the user owns the given app_id.
////////////////////////////////////////////////////////////////////
bool SteamApps::is_subscribed_app(unsigned int app_id) {
  ISteamApps *apps = get_steam_apps();
  if (!apps) return false;
  return apps->BIsSubscribedApp(app_id);
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::is_subscribed_from_free_weekend
//       Access: Published, Static
//  Description: Returns true if the user is playing via a free weekend.
////////////////////////////////////////////////////////////////////
bool SteamApps::is_subscribed_from_free_weekend() {
  ISteamApps *apps = get_steam_apps();
  if (!apps) return false;
  return apps->BIsSubscribedFromFreeWeekend();
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::is_subscribed_from_family_sharing
//       Access: Published, Static
//  Description: Returns true if the user is playing via Family Sharing.
////////////////////////////////////////////////////////////////////
bool SteamApps::is_subscribed_from_family_sharing() {
  ISteamApps *apps = get_steam_apps();
  if (!apps) return false;
  return apps->BIsSubscribedFromFamilySharing();
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::is_app_installed
//       Access: Published, Static
//  Description: Returns true if the given app is installed (not
//               necessarily owned).
////////////////////////////////////////////////////////////////////
bool SteamApps::is_app_installed(unsigned int app_id) {
  ISteamApps *apps = get_steam_apps();
  if (!apps) return false;
  return apps->BIsAppInstalled(app_id);
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::is_dlc_installed
//       Access: Published, Static
//  Description: Returns true if the user owns and has installed the
//               given DLC.
////////////////////////////////////////////////////////////////////
bool SteamApps::is_dlc_installed(unsigned int app_id) {
  ISteamApps *apps = get_steam_apps();
  if (!apps) return false;
  return apps->BIsDlcInstalled(app_id);
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::get_dlc_count
//       Access: Published, Static
//  Description: Returns the number of DLC pieces for the running app.
////////////////////////////////////////////////////////////////////
int SteamApps::get_dlc_count() {
  ISteamApps *apps = get_steam_apps();
  if (!apps) return 0;
  return apps->GetDLCCount();
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::install_dlc
//       Access: Published, Static
//  Description: Triggers installation of the given optional DLC.
////////////////////////////////////////////////////////////////////
void SteamApps::install_dlc(unsigned int app_id) {
  ISteamApps *apps = get_steam_apps();
  if (apps) apps->InstallDLC(app_id);
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::uninstall_dlc
//       Access: Published, Static
//  Description: Triggers uninstallation of the given optional DLC.
////////////////////////////////////////////////////////////////////
void SteamApps::uninstall_dlc(unsigned int app_id) {
  ISteamApps *apps = get_steam_apps();
  if (apps) apps->UninstallDLC(app_id);
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::set_dlc_context
//       Access: Published, Static
//  Description: Sets the current DLC context (or 0 to clear).
////////////////////////////////////////////////////////////////////
bool SteamApps::set_dlc_context(unsigned int app_id) {
  ISteamApps *apps = get_steam_apps();
  if (!apps) return false;
  return apps->SetDlcContext(app_id);
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::get_earliest_purchase_unix_time
//       Access: Published, Static
//  Description: Returns the Unix timestamp of the purchase of the
//               given app.
////////////////////////////////////////////////////////////////////
unsigned int SteamApps::get_earliest_purchase_unix_time(unsigned int app_id) {
  ISteamApps *apps = get_steam_apps();
  if (!apps) return 0;
  return apps->GetEarliestPurchaseUnixTime(app_id);
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::get_app_build_id
//       Access: Published, Static
//  Description: Returns the current build ID of this app.
////////////////////////////////////////////////////////////////////
int SteamApps::get_app_build_id() {
  ISteamApps *apps = get_steam_apps();
  if (!apps) return 0;
  return apps->GetAppBuildId();
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::get_current_game_language
//       Access: Published, Static
//  Description: Returns the current language the game is set to.
////////////////////////////////////////////////////////////////////
std::string SteamApps::get_current_game_language() {
  ISteamApps *apps = get_steam_apps();
  if (!apps) return std::string();
  const char *lang = apps->GetCurrentGameLanguage();
  return lang ? std::string(lang) : std::string();
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::get_available_game_languages
//       Access: Published, Static
//  Description: Returns a comma-separated list of all available
//               languages for this game.
////////////////////////////////////////////////////////////////////
std::string SteamApps::get_available_game_languages() {
  ISteamApps *apps = get_steam_apps();
  if (!apps) return std::string();
  const char *langs = apps->GetAvailableGameLanguages();
  return langs ? std::string(langs) : std::string();
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::get_current_beta_name
//       Access: Published, Static
//  Description: Returns the name of the current beta branch, or an
//               empty string if on the default "public" branch.
////////////////////////////////////////////////////////////////////
std::string SteamApps::get_current_beta_name() {
  ISteamApps *apps = get_steam_apps();
  if (!apps) return std::string();
  char buf[256];
  if (apps->GetCurrentBetaName(buf, sizeof(buf))) {
    return std::string(buf);
  }
  return std::string();
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::get_app_install_dir
//       Access: Published, Static
//  Description: Returns the install directory for the given app.
////////////////////////////////////////////////////////////////////
std::string SteamApps::get_app_install_dir(unsigned int app_id) {
  ISteamApps *apps = get_steam_apps();
  if (!apps) return std::string();
  char buf[1024];
  uint32 len = apps->GetAppInstallDir(app_id, buf, sizeof(buf));
  if (len > 0) {
    return std::string(buf);
  }
  return std::string();
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::get_launch_query_param
//       Access: Published, Static
//  Description: Returns the value of a launch query parameter.
////////////////////////////////////////////////////////////////////
std::string SteamApps::get_launch_query_param(const std::string &key) {
  ISteamApps *apps = get_steam_apps();
  if (!apps) return std::string();
  const char *val = apps->GetLaunchQueryParam(key.c_str());
  return val ? std::string(val) : std::string();
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::mark_content_corrupt
//       Access: Published, Static
//  Description: Signals Steam that the game files may be corrupt.
////////////////////////////////////////////////////////////////////
bool SteamApps::mark_content_corrupt(bool missing_files_only) {
  ISteamApps *apps = get_steam_apps();
  if (!apps) return false;
  return apps->MarkContentCorrupt(missing_files_only);
}

////////////////////////////////////////////////////////////////////
//     Function: SteamApps::get_app_owner
//       Access: Published, Static
//  Description: Returns the SteamID (as uint64) of the original
//               owner of the app.  Compare with the current user's
//               SteamID to detect Family Sharing.
////////////////////////////////////////////////////////////////////
unsigned long long SteamApps::get_app_owner() {
  ISteamApps *apps = get_steam_apps();
  if (!apps) return 0;
  return apps->GetAppOwner().ConvertToUint64();
}

#endif  // CPPPARSER
