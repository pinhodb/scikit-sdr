INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_GRSKSDR grsksdr)

FIND_PATH(
    GRSKSDR_INCLUDE_DIRS
    NAMES grsksdr/api.h
    HINTS $ENV{GRSKSDR_DIR}/include
        ${PC_GRSKSDR_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GRSKSDR_LIBRARIES
    NAMES gnuradio-grsksdr
    HINTS $ENV{GRSKSDR_DIR}/lib
        ${PC_GRSKSDR_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/grsksdrTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GRSKSDR DEFAULT_MSG GRSKSDR_LIBRARIES GRSKSDR_INCLUDE_DIRS)
MARK_AS_ADVANCED(GRSKSDR_LIBRARIES GRSKSDR_INCLUDE_DIRS)
