#include "tcpmanager.h"
#include <QLocalSocket>
#include <QDebug>
#include <QTimer>

#define CMD_IP QString("192.168.0.101")
#define CMD_PORT 9999

tcpManager::tcpManager(QObject *parent)
    : QObject(parent)
    , cmd_client(new Client(CMD_IP, CMD_PORT, this))
    , fixgun(new QLocalSocket(this))
    ,isEnable_(false)
{
    QObject::connect(cmd_client, SIGNAL(readData(QByteArray)), this, SLOT(sendData(QByteArray)) );
    QObject::connect(cmd_client, &Client::connected, [=]()
    {
        qDebug()<<"connect";
    } );
    QObject::connect(cmd_client, &Client::disconnected, [=]()
    {
        qDebug()<<"disconnect";
    } );

//    fixgun->connectToServer("fixgun");
    QTimer *timer = new QTimer(this);
    QObject::connect(timer, &QTimer::timeout, [=]
    {
        if(fixgun->state()!=QLocalSocket::ConnectedState)
            fixgun->connectToServer("fixgun");
        else
            timer->stop();
    });

    if(fixgun->state()!=QLocalSocket::ConnectedState)
        timer->start(500);
    qDebug()<<"start tcpManager";
}

tcpManager::~tcpManager()
{
    qDebug()<<"shutdown tcpManager";
}

void tcpManager::setIP(QString ip)
{
    cmd_client->setIP(ip);
}

void tcpManager::setPORT(quint16 port)
{
    cmd_client->setPort(port);
}

void tcpManager::sendData(QByteArray byte)
{
    if(!isEnable_)
        return;

    QByteArray buffer;
    for(int i=0; i<9; i++)
    {
        QByteArray tmp = byte.mid(0,9);
        byte.remove(0,9);
        int16_t sign_len = (tmp.mid(1,1)=="+")?1:-1;
        int16_t sign_degree = (tmp.mid(5,1)=="+")?1:-1;

        int16_t abs_len = QString(tmp.mid(2,3)).toShort();
        int16_t abs_degree = QString(tmp.mid(6,3)).toShort();

        int16_t val_len = sign_len * abs_len;
        int16_t val_degree = sign_degree * abs_degree;

        buffer.append(shortTo2Byte(val_len));
        buffer.append(shortTo2Byte(val_degree));
    }

    emit getCmd(buffer);
    /*
    if(fixgun->state() == QLocalSocket::ConnectedState)
    {
        fixgun->write(buffer);
    }
    else
    {
        qDebug()<<"close";
    }
    */
}

void tcpManager::sendMotion(QByteArray byte)
{
    if(fixgun->state() == QLocalSocket::ConnectedState)
    {
        fixgun->write(byte);
    }
    else
    {
        qDebug()<<"close";
    }
}

void tcpManager::saveMotion(QByteArray motion)
{
    cmd_client->writeData(motion);
}

void tcpManager::doConnect()
{
    cmd_client->doConnect();
}

void tcpManager::doDisConnect()
{
    cmd_client->doDisConnect();
}

void tcpManager::fixgunConnetion()
{

}

void tcpManager::getPosition()
{
    QLocalSocket *socket = qobject_cast<QLocalSocket *>(sender());
    QByteArray buffer;
    while(socket->bytesAvailable())
    {
        buffer.append(socket->readLine());
    }
    emit getMotion(buffer);
}

void tcpManager::setEnable(bool enable)
{
    isEnable_ = enable;
}
