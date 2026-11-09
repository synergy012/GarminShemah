# Garmin device-package authentication handoff — 2026-11-09

The published network policy is active and includes `api.gcs.garmin.com`. A fresh
request to the official SDK Manager's FR970 device endpoint reaches Garmin but returns
**HTTP 401 Unauthorized**. It has no explanatory response body. This replaces the
earlier network-policy denial. No Garmin secret binding or Garmin/Connect IQ process
variable is present; no stored secret values have been inspected or printed.

The official SDK Manager's onboarding states that the developer must sign in before
downloading devices. Use that normal sign-in flow; do not paste a password, session
cookie or copied access token into this chat. Authentication has not been completed.

## Shared-desktop limitation

Selected environment:
`ccarenv_b64_Y2NhcmVudl84ZDM4OTFkZGJmYjQ4MTkxOWU5YTU3ZDY4MzBlNDAwNQ`.

The status tool reports `remote_desktop.enabled: true`, `state: unknown`. No desktop
`js`/computer-use tool or `open_in_codex` tool is available in this chat, and the
managed X11 display has not started. The suggested Desktop tab may not be exposed
in the current onboarding interface. The separate simulator Xvfb display is running,
but it does not let the user complete a secure interactive login.

This is a tool/UI limitation, not evidence that the user lacks a Garmin account.
There is no reason to publish an unchanged environment or reapply the existing domains.

## Alternative path

If shared desktop sign-in is unavailable, the user can sign in to the **official
Garmin Connect IQ SDK Manager on their own computer**, install/download the
**Forerunner 970** and **Venu 2** device packages, and attach a ZIP of the two device
package folders here. Include their resource files and subdirectories. Do not include
SDK Manager account settings, keychain files, cookies or signing keys.

After receiving the packages, inspect their structure and provenance, preserve any
existing local device data, and install them in the SDK's supported device directory
outside the source repository. Do not commit proprietary device packages. Then retry
compilation and resolve source/API/resource issues before testing actual app behavior.
No target package, successful PRG, or application simulator screenshot exists yet.
