# Python Normal
# py
# Python nix-shell + global normal venv (~/.Virtual-Environment/normal)
{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = with pkgs; [
    python3 python3Packages.tkinter python3Packages.pytest pkg-config
    logisim-evolution
    glibc stdenv.cc.cc.lib gfortran.cc.lib
    bzip2 xz zlib openssl sqlite ncurses readline
    libffi expat gdbm mpdecimal
    libGL freetype harfbuzz libpng libjpeg libtiff libwebp
    SDL2 SDL2_image SDL2_mixer SDL2_ttf
    libx11 libxcursor libxext libxfixes
    libxi libxinerama libxrandr libxrender
    wayland libxkbcommon
    alsa-lib pulseaudio jack2
    flac libogg libvorbis libopus mpg123
    libsndfile libmodplug fluidsynth portmidi
    openblas lapack
  ];
  LD_LIBRARY_PATH = with pkgs; lib.makeLibraryPath [
    glibc stdenv.cc.cc.lib gfortran.cc.lib
    bzip2 xz zlib openssl sqlite ncurses readline
    libffi expat gdbm mpdecimal
    libGL freetype harfbuzz libpng libjpeg libtiff libwebp
    SDL2 SDL2_image SDL2_mixer SDL2_ttf
    libx11 libxcursor libxext libxfixes
    libxi libxinerama libxrandr libxrender
    wayland libxkbcommon
    alsa-lib pulseaudio jack2
    flac libogg libvorbis libopus mpg123
    libsndfile libmodplug fluidsynth portmidi
    openblas lapack
  ];
  shellHook = ''
    source $HOME/.Virtual-Environment/normal/bin/activate
    echo "[✓] Normal venv activated."
  '';
}
