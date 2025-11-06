# This scripts installs ghidra into the users /home/azul/.local/bin
# This makes it available to run and avoids some of the complexity with finding the binary at runtime.

set -e
# Remove previous install
rm -f ghidra_11.4.2_PUBLIC_20250826.zip
rm -rf /usr/bin/ghidra

# Download latest version of Ghidra (last updated October 2025)
wget https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_11.4.2_build/ghidra_11.4.2_PUBLIC_20250826.zip
# Extract zip files and move it into /home/azul/.local/bin
unzip -o ghidra_11.4.2_PUBLIC_20250826.zip
rm -f ghidra_11.4.2_PUBLIC_20250826.zip
mv ghidra_11.4.2_PUBLIC /usr/bin/ghidra
echo "ghidra installed"