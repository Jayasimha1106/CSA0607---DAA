server  program: #include <stdio.h>
#include <string.h>
#include <winsock2.h>
#include <time.h>

#pragma comment(lib, "ws2_32.lib")

int main()
{
    WSADATA wsa;
    SOCKET server_socket, client_socket;
    struct sockaddr_in server, client;
    int client_size;

    time_t now;
    char *date_time;

    // Step 1: Initialize Winsock
    WSAStartup(MAKEWORD(2, 2), &wsa);

    // Step 2: Create TCP socket
    server_socket = socket(AF_INET, SOCK_STREAM, 0);

    // Step 3: Assign server address and port
    server.sin_family = AF_INET;
    server.sin_addr.s_addr = INADDR_ANY;
    server.sin_port = htons(8080);

    // Step 4: Bind socket
    bind(server_socket,
         (struct sockaddr *)&server,
         sizeof(server));

    // Step 5: Listen for client
    listen(server_socket, 5);

    printf("Server is waiting for client...\n");

    // Step 6: Accept client connection
    client_size = sizeof(client);

    client_socket = accept(server_socket,
                           (struct sockaddr *)&client,
                           &client_size);

    printf("Client connected successfully!\n");

    // Step 7: Get current date and time
    now = time(NULL);
    date_time = ctime(&now);

    // Step 8: Send date and time to client
    send(client_socket, date_time,
         (int)strlen(date_time), 0);

    printf("Date and time sent to client.\n");

    // Step 9: Close sockets
    closesocket(client_socket);
    closesocket(server_socket);

    // Step 10: Cleanup Winsock
    WSACleanup();

    return 0;
}