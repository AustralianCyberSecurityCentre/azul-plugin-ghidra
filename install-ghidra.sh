# This scripts installs ghidra into the users /home/azul/.local/bin
# This makes it available to run and avoids some of the complexity with finding the binary at runtime.

# NOTE - the wget link is easier to update manually due to the date at the end.
GHIDRA_VERSION=12.0.4

set -e
# Remove previous install
rm -f ghidra_${GHIDRA_VERSION}_PUBLIC_*.zip
rm -rf /usr/bin/ghidra

# Download latest version of Ghidra (last updated October 2025)
# refer to https://github.com/NationalSecurityAgency/ghidra/releases - for latest
wget https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_12.0.4_build/ghidra_12.0.4_PUBLIC_20260303.zip
# Extract zip files and move it into /home/azul/.local/bin
unzip -o ghidra_${GHIDRA_VERSION}_PUBLIC_*.zip
rm -f ghidra_${GHIDRA_VERSION}_PUBLIC_*.zip
mv ghidra_${GHIDRA_VERSION}_PUBLIC /usr/bin/ghidra
echo "ghidra installed"