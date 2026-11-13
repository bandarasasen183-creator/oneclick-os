# OneClick's own pages for the Settings app. Compiled during the image build.
cmake_minimum_required(VERSION 3.16)
project(oneclick-settings-pages VERSION 0.1)

find_package(ECM 6.0 REQUIRED NO_MODULE)
set(CMAKE_MODULE_PATH ${ECM_MODULE_PATH})
include(KDEInstallDirs)
include(KDECMakeSettings)
include(KDECompilerSettings NO_POLICY_SCOPE)

find_package(Qt6 REQUIRED COMPONENTS Core Quick Network)
find_package(KF6 REQUIRED COMPONENTS KCMUtils CoreAddons)

add_subdirectory(update)
