# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file LICENSE.rst or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION ${CMAKE_VERSION}) # this file comes with cmake

# If CMAKE_DISABLE_SOURCE_CHANGES is set to true and the source directory is an
# existing directory in our source tree, calling file(MAKE_DIRECTORY) on it
# would cause a fatal error, even though it would be a no-op.
if(NOT EXISTS "/home/amrit/Documents/Code/engineering/projects/aero/Micropython/hardware/esp-idf/components/bootloader/subproject")
  file(MAKE_DIRECTORY "/home/amrit/Documents/Code/engineering/projects/aero/Micropython/hardware/esp-idf/components/bootloader/subproject")
endif()
file(MAKE_DIRECTORY
  "/home/amrit/Documents/Code/engineering/projects/aero/Micropython/hardware/esp/helloworld/build/bootloader"
  "/home/amrit/Documents/Code/engineering/projects/aero/Micropython/hardware/esp/helloworld/build/bootloader-prefix"
  "/home/amrit/Documents/Code/engineering/projects/aero/Micropython/hardware/esp/helloworld/build/bootloader-prefix/tmp"
  "/home/amrit/Documents/Code/engineering/projects/aero/Micropython/hardware/esp/helloworld/build/bootloader-prefix/src/bootloader-stamp"
  "/home/amrit/Documents/Code/engineering/projects/aero/Micropython/hardware/esp/helloworld/build/bootloader-prefix/src"
  "/home/amrit/Documents/Code/engineering/projects/aero/Micropython/hardware/esp/helloworld/build/bootloader-prefix/src/bootloader-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "/home/amrit/Documents/Code/engineering/projects/aero/Micropython/hardware/esp/helloworld/build/bootloader-prefix/src/bootloader-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "/home/amrit/Documents/Code/engineering/projects/aero/Micropython/hardware/esp/helloworld/build/bootloader-prefix/src/bootloader-stamp${cfgdir}") # cfgdir has leading slash
endif()
