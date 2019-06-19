# PrivApp

## Interception

### Dependencies

The PrivApp interception tool makes use of some external tools to connect to and control the Android device, and to intercept the traffic. Without them it will not work correctly. For the first part [adb](https://developer.android.com/studio/command-line/adb) and [aapt](https://developer.android.com/studio/command-line/aapt2) will be needed, and for the second one [mitmproxy](https://mitmproxy.org).

### Running

Before execution it is necessary that the `config.yaml` file is placed in the `/home/${user}/.mitmproxy/` directory. To execute simply run the `proxy.sh` script, the output will be a pickled file: `output.log`.


