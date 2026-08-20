# C3X Lite Variant

This variant targets C3X Lite hardware used with NotAutopilot on a pre-AP
Tesla Model S. The device has no cabin-facing driver camera. It is not the
regular comma 3X release and must not be installed on unrelated vehicles.

## Camera Configuration

- The narrow road camera remains active.
- The wide road camera remains active.
- The missing cabin-facing driver camera is not opened, monitored, recorded,
  or treated as a required camera stream.
- Cabin-camera recording, preview, and reverse-view settings are forced off
  and hidden from the UI.
- `dmonitoringmodeld` is disabled because there is no cabin image source.

## Attention Fallback

Mirrors the FrogPilot C3X Lite approach. The cabin-camera model is replaced
with passive interaction monitoring. While steering is active (`enabled` or
`latActive`), steering-wheel torque or accelerator input resets the attention
timer. Existing pre-alert, prompt, and terminal driver-unresponsive events
remain active, with a 30-second passive timeout. Park and Reverse do not nag.

This fallback is less capable than camera-based driver monitoring. The driver
must remain attentive and ready to take over at all times.

## Validation

Before driving on C3X Lite hardware, perform an ignition-on test while
stationary in Park and verify all of the following:

1. `camerad`, `selfdrived`, and `dmonitoringd` remain running.
2. Narrow and wide road-camera streams are live.
3. No cabin-camera communication or malfunction alert appears.
4. No controls mismatch, process lag, radar, or CAN communication alert
   appears.

Do not begin a driving test until the stationary checks pass.
