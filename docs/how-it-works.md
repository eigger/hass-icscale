# How it works

The scale only advertises over Bluetooth while it is awake, and it does **not**
put weight in the advertisement — weight is streamed over a connection. This
integration follows the scale's natural lifecycle:

- **Connect while awake**: As soon as the scale is seen advertising, Home
  Assistant connects and streams weight changes in real time.
- **Idle auto-disconnect**: If the weight does not change for the configured idle
  timeout (default 3 minutes), HA disconnects so the scale can power itself off
  and so the phone app can use Bluetooth (these scales allow only one connection
  at a time).
- **Automatic reconnect**: After an idle disconnect, HA reconnects when the scale
  genuinely wakes again (it stopped advertising and reappeared). A scale that
  keeps advertising is re-checked periodically as a fallback.
- **Automatic measurement switch**: Turn the **Automatic measurement** switch off
  to stop HA from auto-connecting entirely, freeing the scale for the phone app;
  turn it back on to resume automatic streaming. (The **Measure now** button still
  works while it is off.)
- **On-demand measurement**: Since the advertisement carries no weight, putting
  something on an already-connected scale streams instantly — but if HA has
  idle-disconnected and the scale never stopped advertising, press **Measure now**
  to force an immediate connection and reading. Turning the scale off and on (so
  it re-advertises) also triggers an automatic reconnect.
- **Interactive Commands**: The **Measure now**, **Tare**, and **Power off**
  buttons connect on demand to perform the action even if HA is currently
  disconnected.

## Configuration Options

You can adjust this under **Configure** on the integration page:
- **Idle disconnect timeout (minutes)**: How long with no weight change before HA
  releases the connection (default 3).
