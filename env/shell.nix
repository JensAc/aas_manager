with (import ./inputs.nix);
with import <nixpkgs> {};
with libsForQt5;
pkgs.mkShell {
  buildInputs = [
    (import ./python.nix)
    mach-nix.mach-nix
  ];
  QT_QPA_PLATFORM_PLUGIN_PATH="${qt5.qtbase.bin}/lib/qt-${qt5.qtbase.version}/plugins";
  QT_DEBUG_PLUGINS=1;
}
