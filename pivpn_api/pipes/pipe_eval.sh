#!/bin/bash
while true;
do eval "$(cat /home/wguser/vpn_bot/pivpn_api/pipes/pivpn_pipe)" > /home/wguser/vpn_bot/pivpn_api/pipes/pivpn_out 2>&1;
done
