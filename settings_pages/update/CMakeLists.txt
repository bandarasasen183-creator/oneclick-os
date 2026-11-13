kcmutils_add_qml_kcm(kcm_oneclick_update SOURCES updatemodule.cpp updatemodule.h)
target_link_libraries(kcm_oneclick_update PRIVATE Qt6::Core Qt6::Quick KF6::KCMUtils KF6::CoreAddons)
