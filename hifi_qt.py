import hifi_utils
import hifi_android
import hashlib
import os
import platform
import re
import shutil
import tempfile
import json
import xml.etree.ElementTree as ET
import functools

# The way Qt is handled is a bit complicated, so I'm documenting it here.
#
# 1. User runs cmake
# 2. cmake calls prebuild.py, which is referenced in /CMakeLists.txt
# 3. prebuild.py calls this code.
# 4. hifi_qt.py determines how to handle cmake: do we need to download a package, and which?
# 4.a - Using system Qt
#       No download, most special paths are turned off.
#       We build in the same way a normal Qt program would.
# 4.b - Using an user-provided Qt build in a custom directory.
#       We just need to set the cmakePath to the right dir (qt5-install/lib/cmake)
# 4.c - Using a premade package.
#       We check the OS and distro and set qtUrl to the URL to download.
#       After this, it works on the same pathway as 4.b.
# 5. We write /qt.cmake, which contains paths that are passed down to SetupQt.cmake
#    The template for this file is in CMAKE_TEMPLATE just below this comment
#    and it sets the QT_CMAKE_PREFIX_PATH variable used by SetupQt.cmake.
# 6. cmake includes /qt.cmake receiving our information
#    In the case of system Qt, this step is skipped.
# 7. cmake runs SetupQt.cmake which takes care of the cmake parts of the Qt configuration.
#    In the case of system Qt, SetupQt.cmake is a no-op. It runs but exits immediately.
#
# The format for a prebuilt qt is a package containing a top-level directory named
# 'qt5-install', which contains the result of a "make install" from a build of the Qt source.

print = functools.partial(print, flush=True)

# Encapsulates the vcpkg system
class QtDownloader:
    CMAKE_TEMPLATE = """
# this file auto-generated by hifi_qt.py
get_filename_component(QT_CMAKE_PREFIX_PATH "{}" ABSOLUTE CACHE)
get_filename_component(QT_CMAKE_PREFIX_PATH_UNCACHED "{}" ABSOLUTE)

# If the cached cmake toolchain path is different from the computed one, exit
if(NOT (QT_CMAKE_PREFIX_PATH_UNCACHED STREQUAL QT_CMAKE_PREFIX_PATH))
    message(FATAL_ERROR "QT_CMAKE_PREFIX_PATH has changed, please wipe the build directory and rerun cmake")
endif()
"""
    def __init__(self, args):
        self.args = args
        self.configFilePath = os.path.join(args.build_root, 'qt.cmake')
        self.version = os.getenv('VIRCADIA_USE_QT_VERSION', '5.15.2')
        self.assets_url = hifi_utils.readEnviromentVariableFromFile(args.build_root, 'EXTERNAL_BUILD_ASSETS')

        # OS dependent information
        system = platform.system()

        qt_found = False
        system_qt = False

        # Here we handle the 3 possible cases of dealing with Qt:
        if os.getenv('VIRCADIA_USE_SYSTEM_QT', "") != "":
            # 1. Using the system provided Qt. This is only recommended for Qt 5.15.0 and above,
            # as it includes a required fix on Linux.
            #
            # This path only works on Linux as neither Windows nor OSX ship Qt.

            if system != "Linux":
                raise Exception("Using the system Qt is only supported on Linux")

            self.path = None
            self.cmakePath = None

            qt_found = True
            system_qt = True
            print("Using system Qt")

        elif os.getenv('VIRCADIA_QT_PATH', "") != "":
            # 2. Using an user-provided directory.
            # VIRCADIA_QT_PATH must point to a directory with a Qt install in it.

            self.path = os.getenv('VIRCADIA_QT_PATH')
            self.fullPath = self.path
            self.cmakePath = os.path.join(self.fullPath, 'lib', 'cmake')

            qt_found = True
            print("Using Qt from " + self.fullPath)

        else:
            # 3. Using a pre-built Qt.
            #
            # This works somewhat differently from above, notice how path and fullPath are
            # used differently in this case.
            #
            # In the case of an user-provided directory, we just use the user-supplied directory.
            #
            # For a pre-built qt, however, we have to unpack it. The archive is required to contain
            # a qt5-install directory in it.

            self.path = os.path.expanduser("~/vircadia-files/qt")
            self.fullPath = os.path.join(self.path, 'qt5-install')
            self.cmakePath = os.path.join(self.fullPath, 'lib', 'cmake')

            if (not os.path.isdir(self.path)):
                os.makedirs(self.path)

            qt_found = os.path.isdir(self.fullPath)
            print("Using a packaged Qt")


        if not system_qt:
            if qt_found:
                # Sanity check, ensure we have a good cmake directory
                qt5_dir = os.path.join(self.cmakePath, "Qt5")
                if not os.path.isdir(qt5_dir):
                    raise Exception("Failed to find Qt5 directory under " + self.cmakePath + ". There should be a " + qt5_dir)
                else:
                    print("Qt5 check passed, found " + qt5_dir)

            # I'm not sure why this is needed. It's used by hifi_singleton.
            # Perhaps it stops multiple build processes from interferring?
            lockDir, lockName = os.path.split(self.path)
            lockName += '.lock'
            if not os.path.isdir(lockDir):
                os.makedirs(lockDir)

            self.lockFile = os.path.join(lockDir, lockName)

        if qt_found:
            print("Found pre-built Qt5")
            return

        if 'Windows' == system:
            self.qtUrl = self.assets_url + '/dependencies/vcpkg/qt5-install-5.15.2-windows.tar.gz'
        elif 'Darwin' == system:
            self.qtUrl = "https://data.moto9000.moe/vircadia_packages/qt5-install-5.15.2-qtwebengine-5.15.7-macOSXSDK10.14-macos.tar.xz"
        elif 'Linux' == system:
            import distro
            cpu_architecture = platform.machine()

            if 'x86_64' == cpu_architecture:
                if distro.id() == 'ubuntu':
                    u_major = int( distro.major_version() )
                    u_minor = int( distro.minor_version() )

                    if u_major == 18:
                        self.qtUrl = self.assets_url + '/dependencies/vcpkg/qt5-install-5.15.2-ubuntu-18.04-amd64.tar.xz'
                    elif u_major > 19:
                        self.__no_qt_package_error()
                    else:
                        self.__unsupported_error()
                else:
                    self.__no_qt_package_error()

            elif 'aarch64' == cpu_architecture:
                if distro.id() == 'ubuntu':
                    u_major = int( distro.major_version() )
                    u_minor = int( distro.minor_version() )

                    if u_major == 18:
                        self.qtUrl = 'http://motofckr9k.ddns.net/vircadia_packages/qt5-install-5.15.2-ubuntu-18.04-aarch64_test.tar.xz'
                    elif u_major > 19:
                        self.__no_qt_package_error()
                    else:
                        self.__unsupported_error()

                elif distro.id() == 'debian':
                    u_major = int( distro.major_version() )

                    if u_major == 10:
                        self.qtUrl = 'https://data.moto9000.moe/vircadia_packages/qt5-install-5.15.2-debian-10-aarch64.tar.xz'
                    elif u_major > 10:
                        self.__no_qt_package_error()
                    else:
                        self.__unsupported_error()

                else:
                    self.__no_qt_package_error()
            else:
                raise Exception('UNKNOWN CPU ARCHITECTURE!!!')

        else:
            print("System      : " + platform.system())
            print("Architecture: " + platform.architecture())
            print("Machine     : " + platform.machine())
            raise Exception('UNKNOWN OPERATING SYSTEM!!!')

    def showQtBuildInfo(self):
        print("")
        print("It's also possible to build Qt for your distribution, please see the documentation at:")
        print("https://github.com/vircadia/vircadia/tree/master/tools/qt-builder")
        print("")
        print("Alternatively, you can try building against the system Qt by setting the VIRCADIA_USE_SYSTEM_QT environment variable.")
        print("You'll need to install the development packages, and to have Qt 5.15.0 or later.")

    def writeConfig(self):
        print("Writing cmake config to {}".format(self.configFilePath))
        # Write out the configuration for use by CMake
        cmakeConfig = QtDownloader.CMAKE_TEMPLATE.format(self.cmakePath, self.cmakePath).replace('\\', '/')
        with open(self.configFilePath, 'w') as f:
            f.write(cmakeConfig)

    def installQt(self):
        if not os.path.isdir(self.fullPath):
            print ('Downloading Qt from AWS')
            print('Extracting ' + self.qtUrl + ' to ' + self.path)
            hifi_utils.downloadAndExtract(self.qtUrl, self.path)
            if 'Darwin' == platform.system():
                print('Allowing use of QtWebEngine >5.15.2')
                self.__allow_newer_qtwebengine()
        else:
            print ('Qt has already been downloaded')


    def __unsupported_error(self):
        import distro
        cpu_architecture = platform.machine()

        print('')
        hifi_utils.color('red')
        print("Sorry, " + distro.name(pretty=True) + " on " + cpu_architecture + " is too old and won't be officially supported.")
        hifi_utils.color('white')
        print("Please upgrade to a more recent Linux distribution.")
        hifi_utils.color('clear')
        print('')
        raise hifi_utils.SilentFatalError(3)

    def __no_qt_package_error(self):
        import distro
        cpu_architecture = platform.machine()

        print('')
        hifi_utils.color('red')
        print("Sorry, we don't have a prebuilt Qt package for " + distro.name(pretty=True) + " on " + cpu_architecture + ".")
        hifi_utils.color('white')
        print('')
        print("If this is a recent distribution, dating from 2021 or so, you can try building")
        print("against the system Qt by running this command, and trying again:")
        print("    export VIRCADIA_USE_SYSTEM_QT=1")
        print("")
        hifi_utils.color('clear')
        print("If you'd like to try to build Qt from source either for building Vircadia, or")
        print("to contribute a prebuilt package for your distribution, please see the")
        print("documentation at: ", end='')
        hifi_utils.color('blue')
        print("https://github.com/vircadia/vircadia/tree/master/tools/qt-builder")
        hifi_utils.color('clear')
        print('')
        raise hifi_utils.SilentFatalError(2)

    def __allow_newer_qtwebengine(self):
        print("Patching QtWebEngine")
        search_text = "5.15.6 ${_Qt5WebEngine_FIND_VERSION_EXACT}"
        replace_text = "5.15.2 ${_Qt5WebEngine_FIND_VERSION_EXACT}"
        with open(f"{self.fullPath}/lib/cmake/Qt5WebEngine/Qt5WebEngineConfig.cmake", "r") as file:
            data = file.read()
            data = data.replace(search_text, replace_text)
        with open(f"{self.fullPath}/lib/cmake/Qt5WebEngine/Qt5WebEngineCConfig.cmake", 'w') as file:
            file.write(data)
        print("Patched QtWebEngine")

        print("Patching QtWebEngineCore")
        search_text = "5.15.6 ${_Qt5WebEngineCore_FIND_VERSION_EXACT}"
        replace_text = "5.15.2 ${_Qt5WebEngineCore_FIND_VERSION_EXACT}"
        with open(f"{self.fullPath}/lib/cmake/Qt5WebEngineCore/Qt5WebEngineCoreConfig.cmake", "r") as file:

            data = file.read()
            data = data.replace(search_text, replace_text)
        with open(f"{self.fullPath}/lib/cmake/Qt5WebEngineCore/Qt5WebEngineCoreConfig.cmake", 'w') as file:
            file.write(data)
        print("Patched QtWebEngineCore")

        print("Patching QtWebEngineWidgets")
        search_text = "5.15.6 ${_Qt5WebEngineWidgets_FIND_VERSION_EXACT}"
        replace_text = "5.15.2 ${_Qt5WebEngineWidgets_FIND_VERSION_EXACT}"
        with open(f"{self.fullPath}/lib/cmake/Qt5WebEngineWidgets/Qt5WebEngineWidgetsConfig.cmake", "r") as file:
            data = file.read()
            data = data.replace(search_text, replace_text)
        with open(f"{self.fullPath}/lib/cmake/Qt5WebEngineWidgets/Qt5WebEngineWidgetsConfig.cmake", 'w') as file:
            file.write(data)
        print("Patched QtWebEngineWidgets")
