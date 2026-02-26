#include "steamController.h"

#ifndef CPPPARSER

#include <steam/steam_api.h>
#include <steam/steam_api_flat.h>

// Helper: returns the ISteamController* or nullptr.
static ISteamController *get_steam_controller() {
  return SteamController();
}

// ---- Lifecycle ----

bool SteamController::init() {
  ISteamController *sc = get_steam_controller();
  if (!sc) return false;
  return sc->Init();
}

bool SteamController::shutdown() {
  ISteamController *sc = get_steam_controller();
  if (!sc) return false;
  return sc->Shutdown();
}

void SteamController::run_frame() {
  ISteamController *sc = get_steam_controller();
  if (sc) sc->RunFrame();
}

// ---- Connected controllers ----

std::vector<unsigned long long> SteamController::get_connected_controllers() {
  ISteamController *sc = get_steam_controller();
  if (!sc) return {};
  ControllerHandle_t handles[STEAM_CONTROLLER_MAX_COUNT];
  int n = sc->GetConnectedControllers(handles);
  std::vector<unsigned long long> result;
  result.reserve(n);
  for (int i = 0; i < n; ++i) {
    result.push_back(static_cast<unsigned long long>(handles[i]));
  }
  return result;
}

// ---- Action sets ----

unsigned long long SteamController::get_action_set_handle(const std::string &action_set_name) {
  ISteamController *sc = get_steam_controller();
  if (!sc) return 0;
  return static_cast<unsigned long long>(sc->GetActionSetHandle(action_set_name.c_str()));
}

void SteamController::activate_action_set(unsigned long long controller_handle,
                                           unsigned long long action_set_handle) {
  ISteamController *sc = get_steam_controller();
  if (sc) sc->ActivateActionSet(controller_handle, action_set_handle);
}

unsigned long long SteamController::get_current_action_set(unsigned long long controller_handle) {
  ISteamController *sc = get_steam_controller();
  if (!sc) return 0;
  return static_cast<unsigned long long>(sc->GetCurrentActionSet(controller_handle));
}

// ---- Action set layers ----

void SteamController::activate_action_set_layer(unsigned long long controller_handle,
                                                 unsigned long long action_set_layer_handle) {
  ISteamController *sc = get_steam_controller();
  if (sc) sc->ActivateActionSetLayer(controller_handle, action_set_layer_handle);
}

void SteamController::deactivate_action_set_layer(unsigned long long controller_handle,
                                                    unsigned long long action_set_layer_handle) {
  ISteamController *sc = get_steam_controller();
  if (sc) sc->DeactivateActionSetLayer(controller_handle, action_set_layer_handle);
}

void SteamController::deactivate_all_action_set_layers(unsigned long long controller_handle) {
  ISteamController *sc = get_steam_controller();
  if (sc) sc->DeactivateAllActionSetLayers(controller_handle);
}

std::vector<unsigned long long> SteamController::get_active_action_set_layers(
    unsigned long long controller_handle) {
  ISteamController *sc = get_steam_controller();
  if (!sc) return {};
  ControllerActionSetHandle_t handles[STEAM_CONTROLLER_MAX_ACTIVE_LAYERS];
  int n = sc->GetActiveActionSetLayers(controller_handle, handles);
  std::vector<unsigned long long> result;
  result.reserve(n);
  for (int i = 0; i < n; ++i) {
    result.push_back(static_cast<unsigned long long>(handles[i]));
  }
  return result;
}

// ---- Digital actions ----

unsigned long long SteamController::get_digital_action_handle(const std::string &action_name) {
  ISteamController *sc = get_steam_controller();
  if (!sc) return 0;
  return static_cast<unsigned long long>(sc->GetDigitalActionHandle(action_name.c_str()));
}

SteamControllerDigitalActionData SteamController::get_digital_action_data(
    unsigned long long controller_handle,
    unsigned long long digital_action_handle) {
  SteamControllerDigitalActionData out;
  ISteamController *sc = get_steam_controller();
  if (!sc) return out;
  ControllerDigitalActionData_t d = sc->GetDigitalActionData(controller_handle, digital_action_handle);
  out.state  = d.bState;
  out.active = d.bActive;
  return out;
}

std::vector<int> SteamController::get_digital_action_origins(
    unsigned long long controller_handle,
    unsigned long long action_set_handle,
    unsigned long long digital_action_handle) {
  ISteamController *sc = get_steam_controller();
  if (!sc) return {};
  EControllerActionOrigin origins[STEAM_CONTROLLER_MAX_ORIGINS];
  int n = sc->GetDigitalActionOrigins(controller_handle, action_set_handle,
                                      digital_action_handle, origins);
  std::vector<int> result;
  result.reserve(n);
  for (int i = 0; i < n; ++i) {
    result.push_back(static_cast<int>(origins[i]));
  }
  return result;
}

// ---- Analog actions ----

unsigned long long SteamController::get_analog_action_handle(const std::string &action_name) {
  ISteamController *sc = get_steam_controller();
  if (!sc) return 0;
  return static_cast<unsigned long long>(sc->GetAnalogActionHandle(action_name.c_str()));
}

SteamControllerAnalogActionData SteamController::get_analog_action_data(
    unsigned long long controller_handle,
    unsigned long long analog_action_handle) {
  SteamControllerAnalogActionData out;
  ISteamController *sc = get_steam_controller();
  if (!sc) return out;
  ControllerAnalogActionData_t d = sc->GetAnalogActionData(controller_handle, analog_action_handle);
  out.mode   = static_cast<int>(d.eMode);
  out.x      = d.x;
  out.y      = d.y;
  out.active = d.bActive;
  return out;
}

std::vector<int> SteamController::get_analog_action_origins(
    unsigned long long controller_handle,
    unsigned long long action_set_handle,
    unsigned long long analog_action_handle) {
  ISteamController *sc = get_steam_controller();
  if (!sc) return {};
  EControllerActionOrigin origins[STEAM_CONTROLLER_MAX_ORIGINS];
  int n = sc->GetAnalogActionOrigins(controller_handle, action_set_handle,
                                     analog_action_handle, origins);
  std::vector<int> result;
  result.reserve(n);
  for (int i = 0; i < n; ++i) {
    result.push_back(static_cast<int>(origins[i]));
  }
  return result;
}

void SteamController::stop_analog_action_momentum(unsigned long long controller_handle,
                                                    unsigned long long analog_action_handle) {
  ISteamController *sc = get_steam_controller();
  if (sc) sc->StopAnalogActionMomentum(controller_handle, analog_action_handle);
}

// ---- Motion ----

SteamControllerMotionData SteamController::get_motion_data(unsigned long long controller_handle) {
  SteamControllerMotionData out;
  ISteamController *sc = get_steam_controller();
  if (!sc) return out;
  ControllerMotionData_t d = sc->GetMotionData(controller_handle);
  out.rot_quat_x = d.rotQuatX;
  out.rot_quat_y = d.rotQuatY;
  out.rot_quat_z = d.rotQuatZ;
  out.rot_quat_w = d.rotQuatW;
  out.pos_accel_x = d.posAccelX;
  out.pos_accel_y = d.posAccelY;
  out.pos_accel_z = d.posAccelZ;
  out.rot_vel_x = d.rotVelX;
  out.rot_vel_y = d.rotVelY;
  out.rot_vel_z = d.rotVelZ;
  return out;
}

// ---- Haptics / LED ----

void SteamController::trigger_haptic_pulse(unsigned long long controller_handle,
                                            int target_pad,
                                            unsigned short duration_micro_sec) {
  ISteamController *sc = get_steam_controller();
  if (sc) sc->TriggerHapticPulse(controller_handle,
                                  static_cast<ESteamControllerPad>(target_pad),
                                  duration_micro_sec);
}

void SteamController::trigger_repeated_haptic_pulse(unsigned long long controller_handle,
                                                     int target_pad,
                                                     unsigned short duration_micro_sec,
                                                     unsigned short off_micro_sec,
                                                     unsigned short repeat,
                                                     unsigned int flags) {
  ISteamController *sc = get_steam_controller();
  if (sc) sc->TriggerRepeatedHapticPulse(controller_handle,
                                          static_cast<ESteamControllerPad>(target_pad),
                                          duration_micro_sec, off_micro_sec, repeat, flags);
}

void SteamController::trigger_vibration(unsigned long long controller_handle,
                                         unsigned short left_speed,
                                         unsigned short right_speed) {
  ISteamController *sc = get_steam_controller();
  if (sc) sc->TriggerVibration(controller_handle, left_speed, right_speed);
}

void SteamController::set_led_color(unsigned long long controller_handle,
                                     unsigned char r, unsigned char g, unsigned char b,
                                     unsigned int flags) {
  ISteamController *sc = get_steam_controller();
  if (sc) sc->SetLEDColor(controller_handle, r, g, b, flags);
}

// ---- Utility ----

bool SteamController::show_binding_panel(unsigned long long controller_handle) {
  ISteamController *sc = get_steam_controller();
  if (!sc) return false;
  return sc->ShowBindingPanel(controller_handle);
}

int SteamController::get_input_type_for_handle(unsigned long long controller_handle) {
  ISteamController *sc = get_steam_controller();
  if (!sc) return 0;
  return static_cast<int>(sc->GetInputTypeForHandle(controller_handle));
}

unsigned long long SteamController::get_controller_for_gamepad_index(int index) {
  ISteamController *sc = get_steam_controller();
  if (!sc) return 0;
  return static_cast<unsigned long long>(sc->GetControllerForGamepadIndex(index));
}

int SteamController::get_gamepad_index_for_controller(unsigned long long controller_handle) {
  ISteamController *sc = get_steam_controller();
  if (!sc) return -1;
  return sc->GetGamepadIndexForController(controller_handle);
}

// ---- Glyphs / Strings ----

std::string SteamController::get_glyph_for_action_origin(int origin) {
  ISteamController *sc = get_steam_controller();
  if (!sc) return std::string();
  const char *p = sc->GetGlyphForActionOrigin(static_cast<EControllerActionOrigin>(origin));
  return p ? std::string(p) : std::string();
}

std::string SteamController::get_string_for_action_origin(int origin) {
  ISteamController *sc = get_steam_controller();
  if (!sc) return std::string();
  const char *p = sc->GetStringForActionOrigin(static_cast<EControllerActionOrigin>(origin));
  return p ? std::string(p) : std::string();
}

std::string SteamController::get_string_for_xbox_origin(int origin) {
  ISteamController *sc = get_steam_controller();
  if (!sc) return std::string();
  const char *p = sc->GetStringForXboxOrigin(static_cast<EXboxOrigin>(origin));
  return p ? std::string(p) : std::string();
}

std::string SteamController::get_glyph_for_xbox_origin(int origin) {
  ISteamController *sc = get_steam_controller();
  if (!sc) return std::string();
  const char *p = sc->GetGlyphForXboxOrigin(static_cast<EXboxOrigin>(origin));
  return p ? std::string(p) : std::string();
}

// ---- Origin translation ----

int SteamController::get_action_origin_from_xbox_origin(unsigned long long controller_handle,
                                                         int xbox_origin) {
  ISteamController *sc = get_steam_controller();
  if (!sc) return 0;
  return static_cast<int>(sc->GetActionOriginFromXboxOrigin(
      controller_handle, static_cast<EXboxOrigin>(xbox_origin)));
}

int SteamController::translate_action_origin(int destination_input_type, int source_origin) {
  ISteamController *sc = get_steam_controller();
  if (!sc) return 0;
  return static_cast<int>(sc->TranslateActionOrigin(
      static_cast<ESteamInputType>(destination_input_type),
      static_cast<EControllerActionOrigin>(source_origin)));
}

// ---- Binding revision ----

bool SteamController::get_controller_binding_revision(unsigned long long controller_handle,
                                                       int &major, int &minor) {
  ISteamController *sc = get_steam_controller();
  if (!sc) return false;
  return sc->GetControllerBindingRevision(controller_handle, &major, &minor);
}

#endif  // CPPPARSER
