package Assignment3;
/*
   Michelle Chou myc345
   Cynthia Luu cl32284
 */

import java.net.*;
import java.io.*;
import java.util.StringTokenizer;



public class Client
{

    public static void main(String[] args)
    {
        //this is for udp
        boolean first=true;
        String cid = "";
        String ip = "";
        String command; //reserve or return

        int port = 0;
        String protocol = "";
        int sleep_time;
        String bi;
        String output = "";
        InetAddress ia;
        int len = 1024;
        boolean sleep=false;

        DatagramPacket sPacket, rPacket;

        try {

            BufferedReader stdinp = new BufferedReader(new InputStreamReader(System.in));
            String echoline = stdinp.readLine();

            //try to read in the input
            while (echoline!=null)
            {
                try {

                    StringTokenizer in = new StringTokenizer(echoline);

                    if (first)
                    {
                        cid = "c" + in.nextElement().toString();
                        ip = in.nextElement().toString();
                    }

                    else
                    {
                        bi= in.nextElement().toString();

                        if (bi.equals("sleep"))
                        {
                            sleep_time = Integer.parseInt(in.nextElement().toString());
                            Thread.sleep(sleep_time);
                            sleep = true;
                        }

                        else
                        {
                            command = in.nextElement().toString();
                            port = Integer.parseInt(in.nextElement().toString());
                            protocol = in.nextElement().toString();
                            output = cid + " " + bi + " " + command+'\n';
                        }
                    }

                    ia = InetAddress.getByName(ip);

                    if (protocol.equals("U") && !sleep && !first)
                    {
                        DatagramSocket datasocket = new DatagramSocket();
                        //this is the data to be sent
                        byte[] buffer = output.getBytes();
                        //this is the datapacket to be sent
                        sPacket = new DatagramPacket(buffer, buffer.length, ia, port);
                        datasocket.send(sPacket);
                        byte[] rbuffer = new byte[len];
                        rPacket = new DatagramPacket(rbuffer, rbuffer.length);
                        datasocket.receive(rPacket);
                        String retstring = new String(rPacket.getData());
                        System.out.println(retstring);
                        datasocket.close();
                    }

                    else if (protocol.equals("T") && !sleep && !first)
                    {
                        //make a socket
                        Socket sock = new Socket(ia, port);
                        //init stuff
                        DataOutputStream  pout = new DataOutputStream (sock.getOutputStream());
                        BufferedReader din = new BufferedReader(new InputStreamReader(sock.getInputStream()));
                        // this will allow the client to send something
                        pout.writeBytes(output+'\n');
                        pout.flush();
                        //this will print what it got
                        System.out.println(din.readLine());
                        sock.close();
                    }

                    sleep=false;
                    first=false;

                } catch (Exception e) {
                    System.err.println(e);
                }

                echoline = stdinp.readLine();
            }
            //stdinp.close();

        } catch (Exception e) {
            System.err.println(e);

        }
    }

}