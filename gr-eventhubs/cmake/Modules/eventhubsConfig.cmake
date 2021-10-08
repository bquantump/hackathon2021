if(NOT PKG_CONFIG_FOUND)
    INCLUDE(FindPkgConfig)
endif()
PKG_CHECK_MODULES(PC_EVENTHUBS eventhubs)

FIND_PATH(
    EVENTHUBS_INCLUDE_DIRS
    NAMES eventhubs/api.h
    HINTS $ENV{EVENTHUBS_DIR}/include
        ${PC_EVENTHUBS_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    EVENTHUBS_LIBRARIES
    NAMES gnuradio-eventhubs
    HINTS $ENV{EVENTHUBS_DIR}/lib
        ${PC_EVENTHUBS_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/eventhubsTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(EVENTHUBS DEFAULT_MSG EVENTHUBS_LIBRARIES EVENTHUBS_INCLUDE_DIRS)
MARK_AS_ADVANCED(EVENTHUBS_LIBRARIES EVENTHUBS_INCLUDE_DIRS)
