#include <ctime>
#include <iostream>
#include <string>
#include <vector>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>

extern "C" {                   
#include "builtins.h"         
#include "shell.h"            
#include "variables.h"         
#include <readline/readline.h>
}

const char *SOCKET_PATH = "/tmp/bash_autocomplete.sock";

std::string get_prediction_from_server(const std::string &text_to_predict) {
  int client_socket;
  struct sockaddr_un server_addr;
  std::string prediction = ""; 

  client_socket = socket(AF_UNIX, SOCK_STREAM, 0);
  if (client_socket == -1) {
    perror("socket (client)"); 
    return "";                 
  }

  
  memset(&server_addr, 0, sizeof(struct sockaddr_un));
  server_addr.sun_family = AF_UNIX;
  strncpy(server_addr.sun_path, SOCKET_PATH, sizeof(server_addr.sun_path) - 1);

  
  if (connect(client_socket, (struct sockaddr *)&server_addr,
              sizeof(struct sockaddr_un)) == -1) {
    perror("connect (client)");
    close(client_socket);
    return "";
  }

  if (send(client_socket, text_to_predict.c_str(), text_to_predict.length(),
           0) == -1) {
    perror("send (client)");
    close(client_socket);
    return "";
  }

  char buffer[1024] = {0};
  ssize_t bytes_received = recv(client_socket, buffer, sizeof(buffer) - 1, 0);

  if (bytes_received > 0) {
    prediction = std::string(buffer, bytes_received);
  } else if (bytes_received == 0) {
  } else {
    perror("recv (client)");
  }

  close(client_socket);

  return prediction;
}

extern "C" int
suggester_cpp_builtin(WORD_LIST *list)
{
  std::string current_line_content;
  if (rl_line_buffer &&
      rl_end > 0) { 
    current_line_content.assign(rl_line_buffer, rl_end);
  }
  std::string predicted_text = get_prediction_from_server(current_line_content);
  
  if (predicted_text.empty()) {
    return EXECUTION_SUCCESS;
  }
  
  std::string text_to_insert = " " + predicted_text;
  if (current_line_content.empty()) {
    text_to_insert = predicted_text;
  }

  std::string new_readline_line_value = current_line_content + text_to_insert;
  int new_readline_point_value = new_readline_line_value.length();

  if (bind_variable("READLINE_LINE", (char *)new_readline_line_value.c_str(),
                    0) == NULL) {
    return EXECUTION_FAILURE;
  }

  std::string new_point_str = std::to_string(new_readline_point_value);
  if (bind_variable("READLINE_POINT", (char *)new_point_str.c_str(), 0) ==
      NULL) {
    return EXECUTION_FAILURE;
  }

  return EXECUTION_SUCCESS;
}
