#include "client.h"
#include <cmath>
#include <QDataStream>
//static inline QByteArray IntToArray(qint32 source);
Client::Client(QString ip_addr, quint16 port, QObject * parent)
    : QObject (parent),
      ip_addr(ip_addr),
      port (port)
{
    qDebug()<<"TCP client Start :"<<ip_addr<<port;
    socket = new QTcpSocket(this);
    connect(socket, SIGNAL(readyRead()), this, SLOT(readReceivedData()));
    connect(socket, &QTcpSocket::connected, this, [=]()
    {
        emit connected();
    });
    connect(socket, &QTcpSocket::disconnected, [=]()
    {
        emit disconnected();
    });
}

void Client::setIP(QString str_ip)
{
      ip_addr = str_ip;
}

void Client::setPort(quint16 uint16_port)
{
      port = uint16_port;
}

void Client::doConnect(QString str_ip, quint16 uint16_port)
{
	setIP(str_ip);
	setPort(uint16_port);

	doConnect();
}

void Client::doSend(QString str)
{
	QByteArray str_;
    str_.append(str.toUtf8());

	writeData(str_);
}

bool Client::doConnect()
{
    qDebug()<<ip_addr<<port;
    socket->connectToHost(ip_addr, port);
    if(!socket->waitForConnected(100))
    {
        qDebug()<<"client connection"<<false;
         return false;
    }
    else
    {
        qDebug()<<"client connection"<<true;
//        writeData("CONNECT");
        return true;
    }
    }
bool Client::writeData(QByteArray data)
{
    if(socket->state() == QAbstractSocket::ConnectedState)
    {
        socket->write(data); //write the data itself;
        qDebug()<<"write"<<data;
        return socket->waitForBytesWritten(-1);
    }
    else
    {
        qDebug()<<socket->state();
        return false;
    }
}
void Client::doDisConnect()
{
    socket->close();
//    socket->deleteLater();
}


void Client::readReceivedData()
{
    QTcpSocket *socket = qobject_cast<QTcpSocket *>(sender());
    QByteArray buffer;
//    qDebug()<< "Client Recieve";
    /*
    while(socket->bytesAvailable())
    {
        buffer.append(socket->readLine());
//        qDebug()<<socket->readAll();
    }
    */
    buffer.append(socket->readAll());
    //qDebug()<<"socket read"<<buffer;
    Q_EMIT readData(buffer);
 }

bool Client::isConnected()
{
    return (socket->state() == QAbstractSocket::ConnectedState);
}
