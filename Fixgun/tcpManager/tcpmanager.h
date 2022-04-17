#ifndef TCPMANAGER_H
#define TCPMANAGER_H

#include "tcpManager_global.h"

#include <QObject>
#include <socket/client.h>
#include <convertToByte.hpp>
#include <QLocalSocket>

class TCPMANAGER_EXPORT tcpManager : public QObject
{
    Q_OBJECT
public:
    tcpManager(QObject *parent = nullptr);
    virtual ~tcpManager() override;

public slots:
    void setIP(QString);
    void setPORT(quint16);

    void sendData(QByteArray);
    void sendMotion(QByteArray);
    void saveMotion(QByteArray);

    void doConnect();
    void doDisConnect();

    void fixgunConnetion();
    void getPosition();

    void setEnable(bool enable);

signals:
    void finished();
    void getMotion(QByteArray);
    void getCmd(QByteArray);

private:
    Client *cmd_client;
    QLocalSocket *fixgun;
//    QSet<QLocalSocket*> fixgun_clients;

    bool isEnable_;
};

#endif // TCPMANAGER_H
