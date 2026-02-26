#pragma once

#include "pandabase.h"
#include <string>
#include <vector>

////////////////////////////////////////////////////////////////////
// Enums mirrored from ISteamController / ISteamInput for
// interrogate visibility.  Values match the Steamworks SDK.
////////////////////////////////////////////////////////////////////

// BEGIN_PUBLISH

////////////////////////////////////////////////////////////////////
// Enum: SteamControllerPad
////////////////////////////////////////////////////////////////////
enum SteamControllerPad {
  SCP_left  = 0,
  SCP_right = 1,
};

////////////////////////////////////////////////////////////////////
// Enum: SteamControllerLEDFlag
////////////////////////////////////////////////////////////////////
enum SteamControllerLEDFlag {
  SCLED_set_color             = 0,
  SCLED_restore_user_default  = 1,
};

////////////////////////////////////////////////////////////////////
// Enum: SteamInputType
////////////////////////////////////////////////////////////////////
enum SteamInputType {
  SIT_unknown              = 0,
  SIT_steam_controller     = 1,
  SIT_xbox_360_controller  = 2,
  SIT_xbox_one_controller  = 3,
  SIT_generic_gamepad      = 4,
  SIT_ps4_controller       = 5,
  SIT_apple_mfi_controller = 6,
  SIT_android_controller   = 7,
  SIT_switch_joycon_pair   = 8,
  SIT_switch_joycon_single = 9,
  SIT_switch_pro_controller = 10,
  SIT_mobile_touch         = 11,
  SIT_ps3_controller       = 12,
  SIT_ps5_controller       = 13,
  SIT_count                = 14,
};

////////////////////////////////////////////////////////////////////
// Enum: SteamXboxOrigin
////////////////////////////////////////////////////////////////////
enum SteamXboxOrigin {
  SXO_a                       = 0,
  SXO_b                       = 1,
  SXO_x                       = 2,
  SXO_y                       = 3,
  SXO_left_bumper             = 4,
  SXO_right_bumper            = 5,
  SXO_menu                    = 6,
  SXO_view                    = 7,
  SXO_left_trigger_pull       = 8,
  SXO_left_trigger_click      = 9,
  SXO_right_trigger_pull      = 10,
  SXO_right_trigger_click     = 11,
  SXO_left_stick_move         = 12,
  SXO_left_stick_click        = 13,
  SXO_left_stick_dpad_north   = 14,
  SXO_left_stick_dpad_south   = 15,
  SXO_left_stick_dpad_west    = 16,
  SXO_left_stick_dpad_east    = 17,
  SXO_right_stick_move        = 18,
  SXO_right_stick_click       = 19,
  SXO_right_stick_dpad_north  = 20,
  SXO_right_stick_dpad_south  = 21,
  SXO_right_stick_dpad_west   = 22,
  SXO_right_stick_dpad_east   = 23,
  SXO_dpad_north              = 24,
  SXO_dpad_south              = 25,
  SXO_dpad_west               = 26,
  SXO_dpad_east               = 27,
};

// END_PUBLISH

////////////////////////////////////////////////////////////////////
// Data structs visible to Python
////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////
//       Class : SteamControllerAnalogActionData
// Description : Holds analog action state: mode, x/y axes, and
//               whether the action is currently bound.
////////////////////////////////////////////////////////////////////
class EXPORT_CLASS SteamControllerAnalogActionData {
PUBLISHED:
  int   mode;
  float x;
  float y;
  bool  active;

public:
  SteamControllerAnalogActionData()
    : mode(0), x(0.0f), y(0.0f), active(false) {}
};

////////////////////////////////////////////////////////////////////
//       Class : SteamControllerDigitalActionData
// Description : Holds digital action state.
////////////////////////////////////////////////////////////////////
class EXPORT_CLASS SteamControllerDigitalActionData {
PUBLISHED:
  bool state;
  bool active;

public:
  SteamControllerDigitalActionData()
    : state(false), active(false) {}
};

////////////////////////////////////////////////////////////////////
//       Class : SteamControllerMotionData
// Description : Holds raw motion / IMU data from a controller.
////////////////////////////////////////////////////////////////////
class EXPORT_CLASS SteamControllerMotionData {
PUBLISHED:
  float rot_quat_x;
  float rot_quat_y;
  float rot_quat_z;
  float rot_quat_w;
  float pos_accel_x;
  float pos_accel_y;
  float pos_accel_z;
  float rot_vel_x;
  float rot_vel_y;
  float rot_vel_z;

public:
  SteamControllerMotionData()
    : rot_quat_x(0), rot_quat_y(0), rot_quat_z(0), rot_quat_w(0),
      pos_accel_x(0), pos_accel_y(0), pos_accel_z(0),
      rot_vel_x(0), rot_vel_y(0), rot_vel_z(0) {}
};

////////////////////////////////////////////////////////////////////
//       Class : SteamController
// Description : Static wrapper around the Steamworks ISteamController
//               interface.  Provides controller enumeration, action
//               sets, digital/analog actions, haptics, and glyphs.
//               NOTE: ISteamController is deprecated by Valve in
//               favour of ISteamInput but remains functional.
////////////////////////////////////////////////////////////////////
class EXPORT_CLASS SteamController {
PUBLISHED:

  // --- Constants ---
  static const int MAX_COUNT = 16;
  static const int MAX_ANALOG_ACTIONS = 24;
  static const int MAX_DIGITAL_ACTIONS = 256;
  static const int MAX_ORIGINS = 8;
  static const int MAX_ACTIVE_LAYERS = 16;

  // --- Lifecycle ---
  static bool init();
  static bool shutdown();
  static void run_frame();

  // --- Connected controllers ---
  // Returns a list of currently-connected controller handles.
  static std::vector<unsigned long long> get_connected_controllers();

  // --- Action sets ---
  static unsigned long long get_action_set_handle(const std::string &action_set_name);
  static void activate_action_set(unsigned long long controller_handle,
                                  unsigned long long action_set_handle);
  static unsigned long long get_current_action_set(unsigned long long controller_handle);

  // --- Action set layers ---
  static void activate_action_set_layer(unsigned long long controller_handle,
                                        unsigned long long action_set_layer_handle);
  static void deactivate_action_set_layer(unsigned long long controller_handle,
                                          unsigned long long action_set_layer_handle);
  static void deactivate_all_action_set_layers(unsigned long long controller_handle);
  static std::vector<unsigned long long> get_active_action_set_layers(
      unsigned long long controller_handle);

  // --- Digital actions ---
  static unsigned long long get_digital_action_handle(const std::string &action_name);
  static SteamControllerDigitalActionData get_digital_action_data(
      unsigned long long controller_handle,
      unsigned long long digital_action_handle);
  static std::vector<int> get_digital_action_origins(
      unsigned long long controller_handle,
      unsigned long long action_set_handle,
      unsigned long long digital_action_handle);

  // --- Analog actions ---
  static unsigned long long get_analog_action_handle(const std::string &action_name);
  static SteamControllerAnalogActionData get_analog_action_data(
      unsigned long long controller_handle,
      unsigned long long analog_action_handle);
  static std::vector<int> get_analog_action_origins(
      unsigned long long controller_handle,
      unsigned long long action_set_handle,
      unsigned long long analog_action_handle);

  static void stop_analog_action_momentum(unsigned long long controller_handle,
                                          unsigned long long analog_action_handle);

  // --- Motion ---
  static SteamControllerMotionData get_motion_data(unsigned long long controller_handle);

  // --- Haptics / LED ---
  static void trigger_haptic_pulse(unsigned long long controller_handle,
                                   int target_pad,
                                   unsigned short duration_micro_sec);
  static void trigger_repeated_haptic_pulse(unsigned long long controller_handle,
                                            int target_pad,
                                            unsigned short duration_micro_sec,
                                            unsigned short off_micro_sec,
                                            unsigned short repeat,
                                            unsigned int flags);
  static void trigger_vibration(unsigned long long controller_handle,
                                unsigned short left_speed,
                                unsigned short right_speed);
  static void set_led_color(unsigned long long controller_handle,
                            unsigned char r, unsigned char g, unsigned char b,
                            unsigned int flags);

  // --- Utility ---
  static bool show_binding_panel(unsigned long long controller_handle);
  static int  get_input_type_for_handle(unsigned long long controller_handle);
  static unsigned long long get_controller_for_gamepad_index(int index);
  static int  get_gamepad_index_for_controller(unsigned long long controller_handle);

  // --- Glyphs / Strings ---
  static std::string get_glyph_for_action_origin(int origin);
  static std::string get_string_for_action_origin(int origin);
  static std::string get_string_for_xbox_origin(int origin);
  static std::string get_glyph_for_xbox_origin(int origin);

  // --- Origin translation ---
  static int get_action_origin_from_xbox_origin(unsigned long long controller_handle,
                                                int xbox_origin);
  static int translate_action_origin(int destination_input_type, int source_origin);

  // --- Binding revision ---
  static bool get_controller_binding_revision(unsigned long long controller_handle,
                                              int &major, int &minor);

private:
  SteamController() = delete;
};
