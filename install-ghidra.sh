# This scripts installs ghidra into the users /home/azul/.local/bin
# This makes it available to run and avoids some of the complexity with finding the binary at runtime.

set -e
# Remove previous install
rm -f ghidra_12.0_PUBLIC_*.zip
rm -rf /usr/bin/ghidra

# Download latest version of Ghidra (last updated October 2025)
wget https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_12.0_build/ghidra_12.0_PUBLIC_20251205.zip
# Extract zip files and move it into /home/azul/.local/bin
unzip -o ghidra_12.0_PUBLIC_*.zip
rm -f ghidra_12.0_PUBLIC_*.zip
mv ghidra_12.0_PUBLIC /usr/bin/ghidra
echo "ghidra installed"