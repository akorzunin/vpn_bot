#!/bin/bash
while true;
do eval "$(cat /home/akorz/Documents/wg_setup/pivpn_api/pipes/pivpn_pipe)" > /home/akorz/Documents/wg_setup/pivpn_api/pipes/pivpn_out 2>&1;
done
