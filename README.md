# Index Coding Testbed
This is the software written for Professor Vishwanath's Index Coding research at the University of Texas at Austin. This code is implemented in a combination of bash and python. For information on how the project works and the important parts of the code and networking see below.

Recommendation from the team would be to steal the python files with the exception of the experiment_AP and experiment_Node to buid a new system that can be more robust. These python files should contain all the python implementations for encoding and decoding in order to write a more robust system. To take the code to a lower level, replace the udp.py and ack_hadler.py files in order to call either lower level drivers or code.

## Computer Setup
These computers do not play as nicely with ubuntu as we would have liked. There is a USB drive in the lab labeled ubuntu that should have the proper version of ubuntu. The problem is that these laptops run a 64 bit processor with a 32 bit bootloader. To resolve this, we have to force boot via the grub command line and install the 32 bit grub. This USB should have the needed files for all of this. Please follow the following instructions to install ubuntu on these ASUS eeePc Laptops.

If for any reason this USB gets lost you can recreate it all by following these instructions: clone one from the usb_image file in the repo by running th command `dd if=/path/to/usb_image.dd of=/dev/sdb conv=notrunc` where sdb is the USB you wish to clone to. Be careful to make sure you have the address right for the USB.

  1. boot laptops wile pressing F2 with the USB plugged in
  2. Disable safe-boot from this menu
  3. Set the boot option to the USB
  4. Install Ubuntu as usual
  5. Reboot when finished (should do this anyways)
  6. Press F2 again on reboot
  7. Press c when in the grub menu
  8. Enter the following commands in this order. Note: The number of the linux value may vary, tab completion should work here. Just make sure to use the lower version of the linuz generic. Make sure its the same for both commands. This might take a few tries before it works.
      ```
      linux (hd1,gpt2)/boot/vmlinuz-3.16-0-23-generic root=/dev/mmcblk0p2 reboot=pci,force
      
      initrd (hd1,gpt2)/boot/initrd-3.16-0-23-generic
      
      boot
      ```
  9. Once booted, copy the node setup script and the internet script into the home directory
  10. Remove the USB
  11. Plug into ethernet
  12. Run node_setup script
  13. Reboot (this should not boot on its own)
  14. Run internet script
  15. WiFi USB should not work

## Networking
The networking for our tests currently works through the use of NetworkManager, so the computer hosting the networking must be running linux with NetworkManager installed. This is will need to be updated to wor with your hardware. You can change the hardware that this uses by editing the /scripts/research-ap to point to the desired mac-address. After this is done, you should simply be able to run ./ap_start and ./ap_stop to start and stop the AP from this directory. Many of thie scripts will not work if the nodes are not username:blue password:screen. I would also recommend adding your ssh keys to the authorized hosts file on the nodes to avoid using passwords during testing. 

- get_hosts: This script is used to discover nodes that are on the network. This is not a very robust script and will think anybody on the network is a node. 
- ap_start: copies the AP config file to the proper location then restarts NetorkManager to start AP.
- ap_stop: removes config and restarts NetworManager.
- sync: pushes files. This will need to be updated with whatever directory your repo is in
- sync_all: same as above but for all nodes in the "nodes" enviorment variable

## Running Tests
These tests can be run from and of the nodes as the access point. Just update the mac address as stated above. Follow the following commands to run the tests.
  1. Start access point, scripts/ap_start
  2. Discover nodes, `source scripts/get_hosts`
  3. Run start script, `./start test`
  4. Wait

## Python Modules

#### experiment_AP.py
This the over control script for the tests running. All the configs are changed in this file and it sends all messages and handles whent he start are started nd stopped. This fle will probably need to be scrapped as it runs in rounds scheme when we would like to advance to a moving window sceme of sending messages. 

#### experiment_Node.py
This is a very simple file for receiving messages and sending the to decode_manager as well as sending acks.

#### ack_handler.py
This file handles all acks both sending and receiving. 

#### algorithms.py
This file handles the redcing of messages as well as the combining of messages via messages.py. We will discuss this in more detail below

#### decode_manager.py
This is run on the Node side and takes care of all decoding via a row reduction method. It does this via gaussian elimination in the decoding.py file. This file handles all Node side databases.

#### encoding.py
Object representation of encoded messages. This is used to represent bytes and numbers for the sake of encoding and decoding. We also add a marker value to the beginning of each message to preserve the length during encoding. Be careful to add and remove markers appropriately.

#### messages.py
Handles the formatting and created on encoded messages on the server side. This is also used for extracting the metadata on the node side. All message foramatting is contained in this file.

## Algorithms
