// Server side implementation of UDP client-server model
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include "controller.c"
#include "header.h"

#define PORT	5050
#define MAXLINE 1024
#define IPADDR "127.0.0.1"
	
int main() {
    int server;
    struct sockaddr_in servAddr, client_addr;
    int client_struct_length=sizeof(client_addr);
    server=socket(AF_INET,SOCK_DGRAM,IPPROTO_UDP);
    if (server<0){
        printf("Error while creating socket \n");
    }
    servAddr.sin_family=AF_INET;
    servAddr.sin_port=htons(PORT);
    servAddr.sin_addr.s_addr=inet_addr(IPADDR);

    if(bind(server,(struct sockaddr *)&servAddr,sizeof(servAddr))<0){
        printf("Couldnt bind to the port \n");
        exit(1);
    }
    printf("Listening....\n \n");

    data_incoming_type data_incoming_struct;
    data_outgoing_type data_outgoing_struct;

    
    while(1){

    int bytes_received = recvfrom(server, &data_incoming_struct, sizeof(data_incoming_struct), 0,
                                    (struct sockaddr*) &client_addr, &client_struct_length);
    if (bytes_received < 0) {
        perror("recvfrom failed");
        continue; 
    }

    data_outgoing_struct=main_controller(data_incoming_struct);

    
    int bytes_sent = sendto(server, &data_outgoing_struct, sizeof(data_outgoing_struct), 0,
                                    (struct sockaddr*) &client_addr, client_struct_length);

    }
}