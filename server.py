import socket
import time

# Create a socket object
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#ip = socket.gethostbyname (socket.gethostname())
ip = "172.18.0.1"
port = 1234
serverAddress =(ip, port)

# Bind to the port
server.bind(serverAddress) 
print ("Binding success!")

# Now wait for client connection.
server.listen(5)                 
print ("Started listening on " + str(ip) + " : " + str(port))

n = 0

while (n < 1):
    flag = False
    # Establish connection with client.
    client, addr = server.accept()
    print ('Got connection from ', addr)

    data = client.recv (1024)
    if data == "network":
        client.send ('success')
        flag = True
    if flag == True:
        print ("Start receiving data!")
        #Init
        TOTAL_PACKETS = 500000  # Number of packets that server will be received
        TIME_CYCLE = 600        # Cycle time to count packet (seconds)
        temp = 1
        #Init looping range variable
        r = 0
        #Init lists
        receivedList = []       # List of all packets that sever received from client
        missingList = []        # List of all packets dropped when client sends to server
        receive_count =[]
        t0 = time.time()        # Set initial time
        packetPerTime =[]       # Contain the number of packets that sever received during time cycle
        goodPut =[]             # good-put (received packets/sent packets) periodically after every 1000 packets received at the server
        missedPeriod =[]        # Contains SUM of missed packets after every 1000 packets received at the server 
        receivedPerTime = []    # Contains SUM of received packets after every 1000 packets received at the server
        sumMissedPerTime = []   # Contains SUM of missed packets that dropped during time cycle
        missedPerTime = []      # Contain number of missed packing periodically during time cycle
        
        # Start receiving packets from client
        while (len(receivedList) < TOTAL_PACKETS):
            receivedData = eval(client.recv (1024))     #Receiving packets from client
            if receivedData not in receivedList:        # Avoid duplicate receiving
                receivedList.sort()                     
                receivedList.append (receivedData)      # Append received packet in an array       
                if(len(receivedList)> 0 and len(receivedList)%1000==0): # Every 1000 packets received at the server 
                    tt =  len(missedPeriod)              
                    
                    if tt >0:
                        ttt = len(missingList) - missedPeriod[tt-1] # Number of missed packets after every 1000 packets received at the server 
                        goodPut.append ((1.0-ttt*1.000/1000)*100.00)
                    else:
                        ttt = len(missingList)          # Avoid out of range when len(missedPeriod) = 0
                        goodPut.append ((1.0-ttt*1.000/1000)*100.00)
                    receive_count.append(ttt)           # Save missed packets after every 1000 packets received at the server 
                    missedPeriod.append(len(missingList)) # 
        
                   
                client.send ( str(receivedData))        # Send signal back to client for packet that sever was already received
                t1 =  time.time()
                #
                if (t1 - t0 > TIME_CYCLE):
                    kk =  len(receivedPerTime)          # Number of received packets during time cycle
                    vv = len (sumMissedPerTime)         # Number of missed packets during time cycle
                    if kk >0:
                        kkk = len(receivedList) - receivedPerTime[kk-1]

                    else:
                        kkk = len(receivedList)         # Avoid out of range when len(receivedPerTime) = 0
                    
                    if vv >0:
                        vvv = len(missingList) - sumMissedPerTime[vv-1]

                    else:
                        vvv = len(missingList)         # Avoid out of range when len(sumMissedPerTime) = 0
                    packetPerTime.append(kkk) 
                    receivedPerTime.append(len(receivedList))   # Save number of packets that server received during cycle time

                    missedPerTime.append(vvv)
                    sumMissedPerTime.append(len(missingList))                      # Save number of missed packets that dropped during cycle time
                    t0 = time.time()                            # Reset initial time
                
                # Find missed packets dropped once client sends to server
                b = len(receivedList)
                if (receivedList[b-1] != receivedList[b-2]+1):      # If two packet are not sequence, that would exist missed packet between them
                    gap = receivedList[b-1] - receivedList[b-2]-1   # The number of missed packets
                    for zz in range(gap):
                        if(receivedList[b-2]+zz+1) not in missingList:  # Avoid duplicate missed packet
                            missingList.append(receivedList[b-2]+zz+1)
                                        
                
        print("\nList of all packet that sever received from client: ")
        receivedList.sort()
        print(receivedList)
        print ("\nTotal received Packets: " + str(len(receivedList)))
        print("\nList of all packets dropped when client sends to server: ")
        print(missingList)
        
        print ("\nNumber of packets dropped when client sends to server: " + str(len(missingList)))
     
        print("\nList of received packets after every 1000 packets received at the server: ")
        print(receive_count)
        print("\nGood-put periodically after every 1000 packets received at the server:")
        print(goodPut)
        # Average Good-put
        sumGoodput = 0
        for i in range (len(goodPut)):
            sumGoodput = sumGoodput + goodPut[i]
        aveGoodput = sumGoodput*1.00/len(goodPut)
        print ("\nAverage Good-Put: " + str(aveGoodput) +"%")
        print ("\nNumber of packets after every " + str(TIME_CYCLE) + " seconds:")
        print(packetPerTime)
        print ("\nNumber of missed packets after every " + str(TIME_CYCLE) + " seconds:")
        print(missedPerTime)
        
        
        client.close ()                     # Close the socket when done
       

    n += 1

#write data to text file for graphing
with open('data_for_graph.txt', 'w') as f:
    f.write(str(receive_count))
    f.write('\n')
    f.write(str(packetPerTime))
    f.write('\n')
    f.write(str(goodPut))
    f.write('\n')
    f.write(str(missedPerTime))
    f.write('\n')
    f.write(str(packetPerTime))
