INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_CHIRP chirp)

FIND_PATH(
    CHIRP_INCLUDE_DIRS
    NAMES chirp/api.h
    HINTS $ENV{CHIRP_DIR}/include
        ${PC_CHIRP_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    CHIRP_LIBRARIES
    NAMES gnuradio-chirp
    HINTS $ENV{CHIRP_DIR}/lib
        ${PC_CHIRP_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(CHIRP DEFAULT_MSG CHIRP_LIBRARIES CHIRP_INCLUDE_DIRS)
MARK_AS_ADVANCED(CHIRP_LIBRARIES CHIRP_INCLUDE_DIRS)

