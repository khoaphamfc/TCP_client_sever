import socket
import random
import copy
import time

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

START_TIME = time.time()
TIME_CYCLE = 600

# Server's IP and port
ip = "172.18.0.1" 
port = 1234

# Connect to server
serverAddress = (ip, port)
client.connect (serverAddress)
client.send ('network')
if (client.recv (1024) == "success"):
    print ("Connected success!")

    #Default values
    TOTAL_PACKETS = 500000   # number of packets

    sendList = []           # list need to be sent in sliding window
    receivedList = []       # list received in every sliding window
    lostList = []           # specific packet that dropped when client send packet to server
    r1= 1                   # r1 = sliding window - length of lost list
    ran_list = []           # initial dropped list
    whole_lost=[]           # list of all packets that dropped
    tempList=[]             # intial packet going to send
    allReceived = []        # the total packets that server received
    allLostList = []
    repeatedLost =[]        # the list of packet that dropped more than one time

    window_size_list = []
    time_index = 1

    #Generate the packet with sequence number 
    for i in range(TOTAL_PACKETS ):
        tempList.append(i+1)
    
    # Generate the list of dropped packets 
    
    z = 0
    
    while (z<TOTAL_PACKETS/200):      
        random.seed()
        b = TOTAL_PACKETS -2
        a= random.randint(1,b)              # Generate the random index that would be dropped
        if tempList[a] not in (ran_list):   # Avoid repeated drop 
            ran_list.append(tempList[a])
            z= z+1

    ran_list.sort()                         # Sort the list of random number that would be dropped
    len_init_drop = len(ran_list)           # Length of the list of random number that would be dropped
      
    # Drop the intial packet with random list
    for i in range(len(ran_list)):
         tempList.remove(ran_list[i])         
    current = 0 
    tempList.sort()                         # the remaining list of packet that dropped and that is sorted

             
    #Start sending data
    while ((current + len_init_drop <TOTAL_PACKETS)or (len(lostList)!=0)):
        
        sendList = copy.deepcopy(lostList)  # Copy lostList to sendList to resend
        cd= len(sendList)                   # Length of lost list that would be resent
        new_ran_list = []
       
     
       
        #index = len(tempList)
        for i in range (r1-cd):
            sendList.append (tempList[current])
            current = current + 1
            new_rand_list = []
        sendList.sort()

        # Generate the list of packet that would be dropped once there exist the packet that would be resent
        zz =0
        if((len(lostList)>0) and (len (sendList)>10)):
            len_sendList  = len(sendList)      
            while(zz<5):            # Number of packet that would be dropped
                random.seed()
                bb = len_sendList - 2 # Subtract 2 to avoid dropping last index
                aa= random.randint(1,bb)
                if sendList[aa] not in (new_ran_list):
                    new_ran_list.append(sendList[aa])
                    zz= zz+1
    
        new_ran_list.sort()   # Sort the new list of random number that would be dropped
        for i in range(len(new_ran_list)):
            sendList.remove(new_ran_list[i])
            if new_ran_list[i] in lostList:              # Check whether that dropped number is in the Lost List
                repeatedLost.append(new_ran_list[i])     # If yes, append that number to repeatedLost array, which means that number dropped again
        sendList.sort()      # Sort list in sliding window
              
        lostList = []               # Reset lostList -- The list dropped once client sent to server           
      
        receivedList = []           # Reset receivedList -- The list received in every sliding window   
        length1 = len(sendList)    # length of sliding window

        #check size of window every period of time
        if (time.time() - START_TIME) > (TIME_CYCLE * time_index):
            window_size_list.append(length1)

        #Send and receive data
        for i in range (length1):
            #Send data
            client.send (str(sendList[i]))              # Send every single packet
            receivedData = eval(client.recv (1024))     # Received every single packet
            receivedList.append((receivedData))         # Append received packet to receivedList array
            if receivedData not in (allReceived):       # Check whether that packet was in the list already to avoid duplicate
              allReceived.append((receivedData))
        allReceived.sort()
        print ("Packet Received: ")
        print(receivedList)
        k = len(receivedList)
        
        # Check whether there exist any dropped packet between 2 sliding window    
        if (receivedList[0]-1) not in (allReceived):
            index = allReceived.index(receivedList[0])
            gap1 = allReceived[index] - allReceived[index-1] -1
            for zzz in range (gap1):
                if (allReceived[index-1]+zzz+1) not in allReceived:  # Avoid resending packet that server already received from client
                    if (allReceived[index -1 ]+zzz+1) not in lostList:
                        lostList.append(allReceived[index -1]+zzz+1)
        # Check every two sequence packets to find missed packet in every sliding window once client sends to server.     
        for i in range(k-1):
            if (receivedList[i]) != (receivedList[i+1]-1):      # if two packet are not sequence, that would exist missed packet between them
                gap = receivedList[i+1] - receivedList[i] -1 
                for zz in range (gap):
                    if (receivedList[i]+zz+1) not in allReceived:   # Avoid resending packet that server already received from client
                        if (receivedList[i]+zz+1) not in lostList:  # Avoid duplicate missed packet
                            lostList.append(receivedList[i]+zz+1)


  
        bbb = len(lostList)         # length of current lost List
        
        # Adjust sliding window 
        if ( len(lostList) >0):             # Decrease sliding window       
            for k in range(len(lostList)):
                if (lostList[k] not in (whole_lost)):     # Avoid duplicate missed packet in whole_lost array
                    whole_lost.append(lostList[k])        # Append current missed packet to whole_lost array
          
            if r1>1:                       
                r1= r1/2        
                if(TOTAL_PACKETS - current-len_init_drop +bbb)<r1:
                    r1 = TOTAL_PACKETS - current - len_init_drop + bbb
                    print ("Lost list: ")
            print (lostList)
        else:                           # Increase sliding window
            if(2*r1<=65536):
                if (TOTAL_PACKETS - current -len_init_drop + bbb) > 2*r1:   
                    r1= 2*r1
                else:
                    r1= TOTAL_PACKETS - current - len_init_drop + bbb       # Avoid oversize sliding window
            print ("No packets lost!")

        print("Number of packet that received: ")
        print(len(allReceived))


    print("List of missed packets: ")
    print(whole_lost)
    print("Size of list of missed packets: ")
    print(len(whole_lost))


    repeatedLost.sort()
    print("List of packets that lost more than 1 time:")
    print(repeatedLost)
    print(len(repeatedLost))
    
    # Count resent packages
    one = 0
    two = 0
    three = 0
    four = 0
    five = 0
    other =0
    for i in range(len(whole_lost)):
        occurence = repeatedLost.count(whole_lost[i])
        if occurence == 0:
            one = one + 1
        elif occurence == 1:
            two = two + 1
        elif occurence == 2:
            three = three + 1
        elif occurence == 3:
            four = four + 1
        elif occurence == 4:
            five = five + 1
        else:
            other = other +1
    print("Number of packets dropped only one time: " + str(one))
    print("Number of packets dropped two times: " + str(two))
    print("Number of packets dropped three times: " + str(three))
    print("Number of packets dropped four times: " + str(four))
    print("Number of packets dropped five times: " + str(five))
    print("Number of packets dropped more than five times: " + str(other))
    client.close()     # Close the connection

    print('Size of window over a period of time: ' + str(window_size_list))
    with open('window_size_data.txt', 'w') as f:
        f.write(str(window_size_list))  
       
else:
    print ("Fail!!!")

client.close()


