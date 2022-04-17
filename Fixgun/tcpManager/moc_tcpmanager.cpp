/****************************************************************************
** Meta object code from reading C++ file 'tcpmanager.h'
**
** Created by: The Qt Meta Object Compiler version 67 (Qt 5.11.3)
**
** WARNING! All changes made in this file will be lost!
*****************************************************************************/

#include "tcpmanager.h"
#include <QtCore/qbytearray.h>
#include <QtCore/qmetatype.h>
#if !defined(Q_MOC_OUTPUT_REVISION)
#error "The header file 'tcpmanager.h' doesn't include <QObject>."
#elif Q_MOC_OUTPUT_REVISION != 67
#error "This file was generated using the moc from 5.11.3. It"
#error "cannot be used with the include files from this version of Qt."
#error "(The moc has changed too much.)"
#endif

QT_BEGIN_MOC_NAMESPACE
QT_WARNING_PUSH
QT_WARNING_DISABLE_DEPRECATED
struct qt_meta_stringdata_tcpManager_t {
    QByteArrayData data[16];
    char stringdata0[151];
};
#define QT_MOC_LITERAL(idx, ofs, len) \
    Q_STATIC_BYTE_ARRAY_DATA_HEADER_INITIALIZER_WITH_OFFSET(len, \
    qptrdiff(offsetof(qt_meta_stringdata_tcpManager_t, stringdata0) + ofs \
        - idx * sizeof(QByteArrayData)) \
    )
static const qt_meta_stringdata_tcpManager_t qt_meta_stringdata_tcpManager = {
    {
QT_MOC_LITERAL(0, 0, 10), // "tcpManager"
QT_MOC_LITERAL(1, 11, 8), // "finished"
QT_MOC_LITERAL(2, 20, 0), // ""
QT_MOC_LITERAL(3, 21, 9), // "getMotion"
QT_MOC_LITERAL(4, 31, 6), // "getCmd"
QT_MOC_LITERAL(5, 38, 5), // "setIP"
QT_MOC_LITERAL(6, 44, 7), // "setPORT"
QT_MOC_LITERAL(7, 52, 8), // "sendData"
QT_MOC_LITERAL(8, 61, 10), // "sendMotion"
QT_MOC_LITERAL(9, 72, 10), // "saveMotion"
QT_MOC_LITERAL(10, 83, 9), // "doConnect"
QT_MOC_LITERAL(11, 93, 12), // "doDisConnect"
QT_MOC_LITERAL(12, 106, 15), // "fixgunConnetion"
QT_MOC_LITERAL(13, 122, 11), // "getPosition"
QT_MOC_LITERAL(14, 134, 9), // "setEnable"
QT_MOC_LITERAL(15, 144, 6) // "enable"

    },
    "tcpManager\0finished\0\0getMotion\0getCmd\0"
    "setIP\0setPORT\0sendData\0sendMotion\0"
    "saveMotion\0doConnect\0doDisConnect\0"
    "fixgunConnetion\0getPosition\0setEnable\0"
    "enable"
};
#undef QT_MOC_LITERAL

static const uint qt_meta_data_tcpManager[] = {

 // content:
       7,       // revision
       0,       // classname
       0,    0, // classinfo
      13,   14, // methods
       0,    0, // properties
       0,    0, // enums/sets
       0,    0, // constructors
       0,       // flags
       3,       // signalCount

 // signals: name, argc, parameters, tag, flags
       1,    0,   79,    2, 0x06 /* Public */,
       3,    1,   80,    2, 0x06 /* Public */,
       4,    1,   83,    2, 0x06 /* Public */,

 // slots: name, argc, parameters, tag, flags
       5,    1,   86,    2, 0x0a /* Public */,
       6,    1,   89,    2, 0x0a /* Public */,
       7,    1,   92,    2, 0x0a /* Public */,
       8,    1,   95,    2, 0x0a /* Public */,
       9,    1,   98,    2, 0x0a /* Public */,
      10,    0,  101,    2, 0x0a /* Public */,
      11,    0,  102,    2, 0x0a /* Public */,
      12,    0,  103,    2, 0x0a /* Public */,
      13,    0,  104,    2, 0x0a /* Public */,
      14,    1,  105,    2, 0x0a /* Public */,

 // signals: parameters
    QMetaType::Void,
    QMetaType::Void, QMetaType::QByteArray,    2,
    QMetaType::Void, QMetaType::QByteArray,    2,

 // slots: parameters
    QMetaType::Void, QMetaType::QString,    2,
    QMetaType::Void, QMetaType::UShort,    2,
    QMetaType::Void, QMetaType::QByteArray,    2,
    QMetaType::Void, QMetaType::QByteArray,    2,
    QMetaType::Void, QMetaType::QByteArray,    2,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void,
    QMetaType::Void, QMetaType::Bool,   15,

       0        // eod
};

void tcpManager::qt_static_metacall(QObject *_o, QMetaObject::Call _c, int _id, void **_a)
{
    if (_c == QMetaObject::InvokeMetaMethod) {
        tcpManager *_t = static_cast<tcpManager *>(_o);
        Q_UNUSED(_t)
        switch (_id) {
        case 0: _t->finished(); break;
        case 1: _t->getMotion((*reinterpret_cast< QByteArray(*)>(_a[1]))); break;
        case 2: _t->getCmd((*reinterpret_cast< QByteArray(*)>(_a[1]))); break;
        case 3: _t->setIP((*reinterpret_cast< QString(*)>(_a[1]))); break;
        case 4: _t->setPORT((*reinterpret_cast< quint16(*)>(_a[1]))); break;
        case 5: _t->sendData((*reinterpret_cast< QByteArray(*)>(_a[1]))); break;
        case 6: _t->sendMotion((*reinterpret_cast< QByteArray(*)>(_a[1]))); break;
        case 7: _t->saveMotion((*reinterpret_cast< QByteArray(*)>(_a[1]))); break;
        case 8: _t->doConnect(); break;
        case 9: _t->doDisConnect(); break;
        case 10: _t->fixgunConnetion(); break;
        case 11: _t->getPosition(); break;
        case 12: _t->setEnable((*reinterpret_cast< bool(*)>(_a[1]))); break;
        default: ;
        }
    } else if (_c == QMetaObject::IndexOfMethod) {
        int *result = reinterpret_cast<int *>(_a[0]);
        {
            using _t = void (tcpManager::*)();
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&tcpManager::finished)) {
                *result = 0;
                return;
            }
        }
        {
            using _t = void (tcpManager::*)(QByteArray );
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&tcpManager::getMotion)) {
                *result = 1;
                return;
            }
        }
        {
            using _t = void (tcpManager::*)(QByteArray );
            if (*reinterpret_cast<_t *>(_a[1]) == static_cast<_t>(&tcpManager::getCmd)) {
                *result = 2;
                return;
            }
        }
    }
}

QT_INIT_METAOBJECT const QMetaObject tcpManager::staticMetaObject = {
    { &QObject::staticMetaObject, qt_meta_stringdata_tcpManager.data,
      qt_meta_data_tcpManager,  qt_static_metacall, nullptr, nullptr}
};


const QMetaObject *tcpManager::metaObject() const
{
    return QObject::d_ptr->metaObject ? QObject::d_ptr->dynamicMetaObject() : &staticMetaObject;
}

void *tcpManager::qt_metacast(const char *_clname)
{
    if (!_clname) return nullptr;
    if (!strcmp(_clname, qt_meta_stringdata_tcpManager.stringdata0))
        return static_cast<void*>(this);
    return QObject::qt_metacast(_clname);
}

int tcpManager::qt_metacall(QMetaObject::Call _c, int _id, void **_a)
{
    _id = QObject::qt_metacall(_c, _id, _a);
    if (_id < 0)
        return _id;
    if (_c == QMetaObject::InvokeMetaMethod) {
        if (_id < 13)
            qt_static_metacall(this, _c, _id, _a);
        _id -= 13;
    } else if (_c == QMetaObject::RegisterMethodArgumentMetaType) {
        if (_id < 13)
            *reinterpret_cast<int*>(_a[0]) = -1;
        _id -= 13;
    }
    return _id;
}

// SIGNAL 0
void tcpManager::finished()
{
    QMetaObject::activate(this, &staticMetaObject, 0, nullptr);
}

// SIGNAL 1
void tcpManager::getMotion(QByteArray _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(&_t1)) };
    QMetaObject::activate(this, &staticMetaObject, 1, _a);
}

// SIGNAL 2
void tcpManager::getCmd(QByteArray _t1)
{
    void *_a[] = { nullptr, const_cast<void*>(reinterpret_cast<const void*>(&_t1)) };
    QMetaObject::activate(this, &staticMetaObject, 2, _a);
}
QT_WARNING_POP
QT_END_MOC_NAMESPACE
