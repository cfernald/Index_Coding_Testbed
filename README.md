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

If for any reason this USB gets lost, the instruction on how to create this USB is here: https://github.com/lopaka/instructions/blob/master/ubuntu-14.10-install-asus-x205ta.md#prepare-the-usb-flashdrive-to-be-used-as-the-install-media

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

#### decoding.py
Handles reducing encoded messages to a state where side information can be subtracted. decode_manager.py provides the interface. The main function in decoding.py is gauss(), which provides a precision-preserving form of gaussian elimination.

The first point to notice is that gauss keeps track of "decoding steps" which is a linear combination of the original encoded messages that will produce the accompanying coefficient row. The idea is that you will store the data of the received encoded messages, call gauss(), which will produce some rows with a single entry (a message that can be decoded) and then multiply the first encoded message by the first entry of that row's decoding steps add to the second encoded message scaled by the second entry of that row's decoding steps, and so forth. 

Gauss() will be called after decode_manager calls direct_decode() and removes side information from an encoded message. Gauss() performs row reduction on this side information to expose rows that contain a multiple of only one message (and thus can be divided by this multiple to extract the message). 

Since a precise (without floating point error) linear combination is needed to decode the message, gauss() eliminates rows by scaling rows to the product of the leading coefficient of the other in order to be able to subtract two rows and eliminate the leading coef. This has the potential to produce extremely large coefficients that take a long time to multiply.

A better solution to preserve precision would be to produce a data structure which stores a ratio that can be added, multiplied, divided, and ultimately reduced to an integer. If decoding worked properly, the ratio should resolve to an integer (that represents the original message).

## Algorithms

####algo_test.py
Looking at algo_test.py (a disorganized scratchpad for testing functions) is a good place to start seeing the high level interface for the Index Coding algorithms. 

####timeSVDAP() 
A function that runs SVD Alternating Projections over a range of Side Info Graphs (with different densities of don't cares). 

####sampleSideInfo() 
A helper that gives you a randomly generated side info graph and the actual percent of the graph that consists of don't cares. The don't cares are distributed randomly.
- Note that in real world experiments, though, the messages nodes lose tends to have some correlation, despite efforts to introduce uncorrelated movement and interference. This hurts Index Coding performance since if no node has a particular message as side information, it can't be included in an index code.

####timeLDG() 
The LDG analogue of timeSVDAP(), but returns slightly different information

####testAPYah() 
Will produce some plots if you ask nicely.



##algorithms.py

####LDG()  
The implementation of the least difference greedy algorithm. The don't care values in the side info graph are assumed to be 2, otherwise it breaks.

####SVDAP()
The implementation of SVD based alternating projections. There is an implementation of directional AP started, but it wasn't used. SVDAP was the index coding algorithm we spent the most time with (as might be apparent from all the optional parameters)
- startingMatrix optionally allows you to feed in a matrix from which you start your projections. We experimented with feeding in the result of LDG to start with a lower rank matrix (use expandLDG() to make the result of LDG square in a somewhat strategic way):
- startSize will be the max in a randomly generated matrix if startingMatrix=None
- eig_size_tolerance gives the minimum threshold for which a singular value will be considered 0. It's also fed to projectToD() to determine which entries on the diagonal have gotten to close to 0. 
- precisionDecimals tells how many decimals to round the non-zeros entries of the matrix at each projection (None is an option)
- max_iterations has a default cap of 100, as this is approximately 1 second of run time on a middling laptop, though the best rank reduction happens after 700 or so iterations
- return_analysis dictates whether we return just the best rank reduced matrix, or a package of information containing ( [last iteration matrix, last iteration rank, how many iterations run], [lowest rank matrix of any iteration, best (lowest) rank, the iteration where the lowest rank matrix was achieved] )

####projectToD() 
A helper which takes a matrix and and sets the main diagonal to be non-zero, and zeros out the positions of the matrix which are 0 in the side info graph. 
It also allows you to optionally round the entries to 'roundPrecision' many decimal place. This is helpful in practice; it actually helps lower the rank for instances where the side info graph is not very dense (I'd guesstimate perhaps 30% or less don't cares)

####thresholdRank() 
Returns you the number of singular values above the threshold you give. One can also use numpy.linalg.matrix_rank() and specify a tol, or if there is no tol:
“If tol is None, and S is an array with singular values for M, and eps is the epsilon value for datatype of S, then tol is set to S.max() * max(M.shape) * eps”
http://docs.scipy.org/doc/numpy-dev/reference/generated/numpy.linalg.matrix_rank.html




