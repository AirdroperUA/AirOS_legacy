#!/usr/bin/env bash

# Exit if something goes wrong
set -e

# Mavftp uses libfuse2 to make a transparent fs for browsing
echo "Installing libfuse2 for mavftp."
apt update
apt install -y --no-install-recommends fuse libfuse2
