package Assignment3;
import java.io.BufferedReader;
import java.io.DataOutputStream;

import java.io.IOException;
import java.io.InputStreamReader;

import java.net.*;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.util.Arrays;
import java.util.Iterator;
import java.util.StringTokenizer;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

/**
 * Created by Cool Beans on 3/22/2015.
 */
public class Server
{
    public class Library
    {
        boolean[] lib;
        boolean returning;
        boolean reserving;
        public Library(int num)
        {
            reserving=false;
            returning=false;
            lib = new boolean[num];
            for(int x=0;x<num;x++)
                lib[x] = true;
        }

        public synchronized boolean reserveBook(int num)
        {
            if(lib[num-1]==false)
                return false;
            else
                lib[num-1] = false;
            return true;
        }

        public synchronized boolean returnBook(int num)
        {
            if (lib[num-1]==true)
                return false;
            lib[num-1]=true;
            return true;
        }
    }

    public class UDPServer implements Runnable
    {
        DatagramSocket serverSock;
        int port;
        public UDPServer(int por)
        {
            port =por;
        }
        public void run()
        {
            //set up array the holds send adn receive messages

            String client;
            int book;
            String comm;
            String bookStr;

            try
            {
                DatagramChannel channel = DatagramChannel.open();
                channel.socket().bind((new InetSocketAddress(port)));
                DatagramSocket sock = channel.socket();
                channel.configureBlocking(false);
                Selector selector = Selector.open();
                channel.register(selector, SelectionKey.OP_READ);
                while (true)
                {
                    selector.select();
                    for(Iterator<SelectionKey> i = selector.selectedKeys().iterator();i.hasNext();)
                    {
                        SelectionKey key = i.next();
                        i.remove();
                        if(key.isReadable())
                        {
                            //this will take in the data
                            ByteBuffer rData = ByteBuffer.allocate(1024);
                            rData.clear();
                            SocketAddress clientSock = channel.receive(rData);
                            if(clientSock!=null)
                            {
                                String testing = new String (rData.array());
                                System.out.println("DEBUG: testing the Datagram channel "+testing);
                                System.out.println(rData.asCharBuffer().toString());
                                //get the input
                                StringTokenizer ln = new StringTokenizer(testing);
                                client = ln.nextToken();
                                bookStr = ln.nextToken();
                                book = Integer.parseInt(bookStr.substring(1));
                                comm = ln.nextToken();
                                System.out.println("DEBUG: UDP Input parsed");
                                if(comm.equalsIgnoreCase("return"))
                                {
                                    if(library.returnBook(book))
                                    {
                                        //then send went through
                                        String out = client +" " + bookStr;
                                        ByteBuffer outBuff =ByteBuffer.allocate(1024);
                                        outBuff.clear();
                                        outBuff.put(out.getBytes());
                                        outBuff.flip();
                                        channel.send(outBuff,clientSock);
                                        System.out.println("DEBUG: bookT "+ out+" returned\n");
                                    }
                                    else
                                    {
                                        //then send went through
                                        String out = "fail "+client +" " + bookStr;
                                        ByteBuffer outBuff =ByteBuffer.allocate(1024);
                                        outBuff.clear();
                                        outBuff.put(out.getBytes());
                                        outBuff.flip();
                                        channel.send(outBuff,clientSock);
                                        System.out.println("DEBUG: bookT "+ out+" not returned");
                                    }
                                }
                                else if(comm.equalsIgnoreCase("reserve"))
                                {
                                    if(library.reserveBook(book))
                                    {
                                        //then send went through
                                        String out = client +" " + bookStr;
                                        ByteBuffer outBuff =ByteBuffer.allocate(1024);
                                        outBuff.clear();
                                        outBuff.put(out.getBytes());
                                        outBuff.flip();
                                        channel.send(outBuff,clientSock);
                                        System.out.println("DEBUG: bookT "+ out+" reserved");
                                    }
                                    else
                                    {
                                        //then send went through
                                        String out = "fail " + client + " " + bookStr;
                                        ByteBuffer outBuff =ByteBuffer.allocate(1024);
                                        outBuff.clear();
                                        outBuff.put(out.getBytes());
                                        outBuff.flip();
                                        channel.send(outBuff,clientSock);
                                        System.out.println("DEBUG: bookT " + out + " not reserved");
                                    }
                                }
                                else if(comm.equalsIgnoreCase("sleep"))
                                {
                                    System.out.println("DEBUG: you can't send me sleep");
                                }
                                else
                                {
                                    System.out.println("DEBUG: "+'\'' +comm+'\''+"is not a command");
                                }
                            }
                        }
                    }
                }
            }
            catch (IOException e)
            {
                e.printStackTrace();
            }
        }
    }

    public class TCPServer implements Runnable
    {
        ServerSocket sSock;
        int port;

        public TCPServer(int num)
        {
            port = num;
        }

        public void run()
        {
            String rData;
            String sData;
            String client;
            String bookStr;
            String comm;
            int book;
            Selector selector = null;
            ServerSocketChannel sChannel = null;
            try
            {
                selector = Selector.open();
                sChannel = ServerSocketChannel.open();
                sChannel.socket().bind(new InetSocketAddress(port));
                sChannel.configureBlocking(false);
                sChannel.register(selector, SelectionKey.OP_ACCEPT);
            }
            catch (IOException e)
            {
                e.printStackTrace();
            }
            String debug;
            while(true)
            {
                try
                {
                    selector.select();
                    for(Iterator<SelectionKey> i = selector.selectedKeys().iterator(); i.hasNext();)
                    {
                        SelectionKey k = i.next();
                        i.remove();
                        if(k.isAcceptable())
                        {
                            SocketChannel clientChannel  = sChannel.accept();
                            clientChannel.configureBlocking(false);
                            clientChannel.socket().setTcpNoDelay(true);
                            clientChannel.register(selector, SelectionKey.OP_READ);
                            if(clientChannel!=null)
                            {
                                ByteBuffer buf = ByteBuffer.allocate(1024);
                                buf.clear();
                                int bytesRead = clientChannel.read(buf);
                                String testing = new String (buf.array());
                                debug = testing;
                                System.out.println("DEBUG: testing the socket channel "+testing);
                                System.out.println(buf.asCharBuffer().toString());
                                //get the input
                                StringTokenizer ln = new StringTokenizer(testing);
                                client = ln.nextToken();
                                bookStr = ln.nextToken();
                                book = Integer.parseInt(bookStr.substring(1));
                                comm = ln.nextToken();
                                if (comm.contains("\\"))
                                {
                                    comm = comm.substring(0, comm.indexOf('\\'));
                                }
                                System.out.println("DEBUG: TCP Input parsed");
                                if(comm.equalsIgnoreCase("return"))
                                {
                                    if(library.returnBook(book))
                                    {
                                        //then send went through
                                        String out = client +" " + bookStr+'\n';
                                        ByteBuffer outBuff =ByteBuffer.allocate(1024);
                                        outBuff.clear();
                                        outBuff.put(out.getBytes());
                                        outBuff.flip();
                                        while(outBuff.hasRemaining())
                                            clientChannel.write(outBuff);
                                        clientChannel.close();
                                        System.out.println("DEBUG: bookT "+ out+" returned");
                                    }
                                    else
                                    {
                                        //then send went through
                                        String out = "fail "+client +" " + bookStr;
                                        ByteBuffer outBuff =ByteBuffer.allocate(1024);
                                        outBuff.clear();
                                        outBuff.put(out.getBytes());
                                        outBuff.flip();
                                        while(outBuff.hasRemaining())
                                            clientChannel.write(outBuff);
                                        clientChannel.close();
                                        System.out.println("DEBUG: bookT "+ out+" not returned");
                                    }
                                }
                                else if(comm.equalsIgnoreCase("reserve"))
                                {
                                    if(library.reserveBook(book))
                                    {
                                        //then send went through
                                        String out = client +" " + bookStr;
                                        ByteBuffer outBuff =ByteBuffer.allocate(1024);
                                        outBuff.clear();
                                        outBuff.put(out.getBytes());
                                        outBuff.flip();
                                        while(outBuff.hasRemaining())
                                            clientChannel.write(outBuff);
                                        clientChannel.close();
                                        System.out.println("DEBUG: bookT "+ out+" reserved");
                                    }
                                    else
                                    {
                                        //then send went through
                                        String out = "fail " + client + " " + bookStr;
                                        ByteBuffer outBuff =ByteBuffer.allocate(1024);
                                        outBuff.clear();
                                        outBuff.put(out.getBytes());
                                        outBuff.flip();
                                        while(outBuff.hasRemaining())
                                            clientChannel.write(outBuff);
                                        clientChannel.close();
                                        System.out.println("DEBUG: bookT " + out + " not reserved");
                                    }
                                }
                                else if (comm.equalsIgnoreCase("sleep"))
                                {
                                    System.out.println("DEBUG: Sleep is not a command. Line was " + testing);
                                }
                                else
                                {
                                    System.out.println("DEBUG: input error line was "+debug);
                                }

                            }
                        }


                    }
                }
                catch (IOException e)
                {
                    e.printStackTrace();
                }
            }
        }
    }

    public Library library;
    public int portT;
    public int portU;
    public Runnable tcpServer;
    public Runnable udpServer;
    Thread tcpServe;
    Thread udpServe;
    public Server(int u, int t, int b)
    {
        library = new Library(b);
        tcpServer = new TCPServer(t);
        udpServer = new UDPServer(u);

        tcpServe = new Thread(tcpServer);
        udpServe = new Thread(udpServer);
        tcpServe.start();
        udpServe.start();

    }

    //get inputs from server
    //run the server
    public static void main(String[] args)
    {
        //take in input for setting up the server
        int books=0;
        int udpPort=0;
        int tcpPort=0;
        try
        {
            BufferedReader stdinp = new BufferedReader(new InputStreamReader(System.in));
            String input = stdinp.readLine();

            while(input!=null&&!input.isEmpty())
            {
                StringTokenizer ln = new StringTokenizer(input);
                //this gets all of the input for the server
                books = Integer.parseInt(ln.nextToken());
                udpPort = Integer.parseInt(ln.nextToken());
                tcpPort = Integer.parseInt(ln.nextToken());
                break;
            }
        }
        catch (IOException e)
        {
            e.printStackTrace();
        }

        //  System.out.println("DEBUG: Took all user input"+ books+ " books"+udpPort + " uport"+ tcpPort+ " tport");
        //now set up the server for UDP
        Server serve = new Server(udpPort,tcpPort,books);


    }
}