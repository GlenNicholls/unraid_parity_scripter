# Unraid Parity Scripter
Unraid user script that supports specifying Python functions to call during parity check start/stop stages

## Usage
After downloading the Parity Check Tuning, user scripts, and python plugins, this repo can be cloned to a
desireable location. The following is an example of the user script:

``` bash
#!/bin/bash

python3 /mnt/<loc>/unraid_parity_scripter/parity_scripter/main.py \
    -c /mnt/<config loc>/config.json \
    -s 300
```

Where `-c` is the config file path and `-s` is the sleep/check interval. An example `config.json` looks like
the following:

``` json
{
    "containers": [
        "jellyfin",
        "unmanic",
        "grafana"
    ]
}
```

The `containers` variable is a list of the Docker container names (as defined in the Docker tab) to start/stop
based on the state of the Parity Check status. The above containers, for example, will all be stopped in the
specified order when parity is started and killed in the same order when parity check is stopped or resumed.

My use-case is that I am only allowing parity check to occur during off-hours and I need certain containers to
be stopped so they aren't saturating IO bandwidth. I.e. when parity starts, I disable certain containers to
minimize the time to complete the parity check and then re-enable the containers when parity check is paused or
not running (e.g. outside allowed parity check hours).

## Disclaimers

* Without code modifications, this script cannot support arbitrary functions. If desireable, open an issue and I
  can work on adding a proper API for importing and adding arbitrary Python functions to call for the desired
  stage.
* For non-Python API support, open a PR. However, I will not maintain or support those APIs.
* I do not plan to support the unraid UI as this script meets my needs. This code is loosely licensed to
  allow you to repurpose it for your needs. I'm happy to help depending on the use-case, but no guarantees.
