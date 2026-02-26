/**
 * Copyright (c) 2026 Digital Descent LLC. All rights reserved.
 */

#include "config_module.h"

#include "steamApps.h"
#include "steamAppTicket.h"
#include "steamController.h"

#include "dconfig.h"

Configure(config_mymodule);
NotifyCategoryDef(mymodule , "");

ConfigureFn(config_mymodule) {
  init_libmymodule();
}

void
init_libmymodule() {
  static bool initialized = false;
  if (initialized) {
    return;
  }
  initialized = true;

  return;
}

