#!/usr/bin/env python3
import os

import cereal.messaging as messaging
from openpilot.common.params import Params
from openpilot.common.realtime import config_realtime_process
from openpilot.selfdrive.monitoring.helpers import DriverMonitoring


def dmonitoringd_thread():
  config_realtime_process([0, 1, 2, 3], 5)

  params = Params()
  pm = messaging.PubMaster(['driverMonitoringState'])
  c3x_lite = os.getenv("C3X_LITE") is not None
  poll_service = 'carState' if c3x_lite else 'driverStateV2'
  ignore = ['driverStateV2'] if c3x_lite else []
  sm = messaging.SubMaster(['driverStateV2', 'liveCalibration', 'carState', 'selfdriveState', 'modelV2', 'carControl'],
                           poll=poll_service, ignore_alive=ignore, ignore_avg_freq=ignore, ignore_valid=ignore)

  always_on = False if c3x_lite else params.get_bool("AlwaysOnDM")
  DM = DriverMonitoring(rhd_saved=params.get_bool("IsRhdDetected"), always_on=always_on)
  demo_mode=False

  # 20Hz from dmonitoringmodeld, or every fifth 100Hz carState on C3X Lite.
  while True:
    sm.update()
    if not sm.updated[poll_service] or (c3x_lite and sm.frame % 5 != 0):
      continue

    valid = sm.all_checks()
    if c3x_lite:
      if valid:
        DM.run_passive_step(sm)
    elif demo_mode and sm.valid['driverStateV2']:
      DM.run_step(sm, demo=demo_mode)
    elif valid:
      DM.run_step(sm, demo=demo_mode)

    # publish
    dat = DM.get_state_packet(valid=valid)
    pm.send('driverMonitoringState', dat)

    if c3x_lite:
      continue

    # load live always-on toggle
    if sm['driverStateV2'].frameId % 40 == 1:
      DM.always_on = params.get_bool("AlwaysOnDM")
      demo_mode = params.get_bool("IsDriverViewEnabled")

    # save rhd virtual toggle every 5 mins
    if (sm['driverStateV2'].frameId % 6000 == 0 and not demo_mode and
     DM.wheelpos.prob_offseter.filtered_stat.n > DM.settings._WHEELPOS_FILTER_MIN_COUNT and
     DM.wheel_on_right == (DM.wheelpos.prob_offseter.filtered_stat.M > DM.settings._WHEELPOS_THRESHOLD)):
      params.put_bool_nonblocking("IsRhdDetected", DM.wheel_on_right)

def main():
  dmonitoringd_thread()


if __name__ == '__main__':
  main()
