with (import ./inputs.nix);
pkgs.mkShell {
  buildInputs = [
    (import ./python.nix)
    mach-nix.mach-nix
  ];
  nativeBuildIntputs = [ pkgs.libsForQt5.wrapQtAppsHook ];
  QT_QPA_PLATFORM_PLUGIN_PATH="${pkgs.libsForQt5.qt5.qtbase.bin}/lib/qt-${pkgs.libsForQt5.qt5.qtbase.version}/plugins";
  QT_XCB_GL_INTEGRATION="none";
  QT_DEBUG_PLUGINS=1;
}
