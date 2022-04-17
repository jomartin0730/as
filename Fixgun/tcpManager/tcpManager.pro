QT -= gui

QT += network

#TARGET = tcpManager
TEMPLATE = lib
DEFINES += TCPMANAGER_LIBRARY

CONFIG += c++11

# You can make your code fail to compile if it uses deprecated APIs.
# In order to do so, uncomment the following line.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

SOURCES += \
    socket/client.cpp \
    tcpmanager.cpp

HEADERS += \
    socket/client.h \
    tcpManager_global.h \
    tcpmanager.h

# Default rules for deployment.
unix {
    target.path = /usr/lib
}
!isEmpty(target.path): INSTALLS += target

win32:CONFIG(release, debug|release): LIBS += -L$$OUT_PWD/../convertToByte/release/ -lconvertToByte
else:win32:CONFIG(debug, debug|release): LIBS += -L$$OUT_PWD/../convertToByte/debug/ -lconvertToByte
else:unix: LIBS += -L$$OUT_PWD/../convertToByte/ -lconvertToByte

INCLUDEPATH += $$PWD/../convertToByte
DEPENDPATH += $$PWD/../convertToByte
