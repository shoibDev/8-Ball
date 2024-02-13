#define _POSIX_C_SOURCE 200809L
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <ctype.h> // For tolower function
#include <stdbool.h>

// Global pointer to a pointer (2D array)
int **pipes;
pid_t *pids;
int active_children = 0; // Track the number of active child processes

void allocatePipesAndPids(int numFiles) {
    pipes = malloc(numFiles * sizeof(int*));
    pids = malloc(numFiles * sizeof(pid_t)); // Allocate array for child PIDs
    if (pipes == NULL || pids == NULL) {
        printf("Memory allocation failed\n");
        exit(1);
    }

    for (int i = 0; i < numFiles; i++) {
        pipes[i] = malloc(2 * sizeof(int));
        if (pipes[i] == NULL) {
            printf("Memory allocation failed for pipes[%d]\n", i);
            exit(1);
        }
        if (pipe(pipes[i]) == -1) {
            printf("Pipe creation failed\n");
            exit(1);
        }
    }
}

void freePipesAndPids(int numFiles) {
    for (int i = 0; i < numFiles; i++) {
        free(pipes[i]);
    }
    free(pipes);
    free(pids);
}


void sigchld_handler(int sig) {
    int child_status;
    pid_t child_pid;

    while ((child_pid = waitpid(-1, &child_status, WNOHANG)) > 0) {
        printf("Caught SIGCHLD, child PID: %d\n", child_pid);

        // Find the index for the child_pid in pids array
        for (int i = 0; i < 100 - 1; i++) {
            if (pids[i] == child_pid) {
                if (WIFEXITED(child_status) && WEXITSTATUS(child_status) == 0) {
                    printf("Child %d exited normally.\n", child_pid);
                    close(pipes[i][1]); // Close the writing end, only read
                    int histogram[26];
                    if (read(pipes[i][0], histogram, 26 * sizeof(int)) > 0) {
                        char filename[256];
                        sprintf(filename, "file%d.hist", child_pid);
                        FILE *fp = fopen(filename, "w");
                        if (fp != NULL) {
                            for (int j = 0; j < 26; j++) {
                                fprintf(fp, "%c: %d\n", 'a' + j, histogram[j]);
                            }
                            fclose(fp);
                        }
                        close(pipes[i][0]); // Close the reading end
                    }
                } else if (WIFSIGNALED(child_status)) {
                    printf("Child %d was killed by signal %d (%s)\n", child_pid, WTERMSIG(child_status), strsignal(WTERMSIG(child_status)));
                }
                break; // Exit the loop once the correct child is processed
            }
        }
        active_children--;
    }
}

void create_child_process(int index, char* filename){
    pid_t pid = fork();

    if(pid == 0){
       if(strcmp(filename, "SIG") == 0) {
            // If input is "SIG", set up to receive SIGINT without a custom handler
            signal(SIGINT, SIG_DFL);
            pause(); // Wait indefinitely for a signal
        } else {
            close(pipes[index][0]); // Close reading end
            FILE* file = fopen(filename, "r");

            // Find file length
            fseek(file, 0, SEEK_END);
            long length = ftell(file);
            fseek(file, 0, SEEK_SET);

            // Allocate memory for file content
            char *buffer = malloc(length);
            fread(buffer, 1, length, file);
            fclose(file);

            
            // Allocate and initialize histogram
            int histogram[26] = {0};
            for (long i = 0; i < length; i++) {
                char c = tolower(buffer[i]);
                if (c >= 'a' && c <= 'z') {
                    histogram[c - 'a']++;
                }
            }

            // Send histogram to parent
            write(pipes[index][1], histogram, 26 * sizeof(int));
            //sleep(10 + 3*index);

            close(pipes[index][1]);
            free(buffer);
            exit(0); // terminate child process
        }
    }else{
        pids[index] = pid;
         if(strcmp(filename, "SIG") == 0) {
            // If input is "SIG", send SIGINT to this child
            kill(pid, SIGINT);
        }
    }
}

int main(int argc, char* argv[]){
    if (argc < 2) {
        fprintf(stderr, "Error: No input files provided.\n");
        return 1;
    }

    allocatePipesAndPids(argc - 1);
    signal(SIGCHLD, sigchld_handler);

    for (int i = 1; i < argc; i++) {
        if(strcmp(argv[i], "SIG") != 0) {
            create_child_process(i - 1, argv[i]);
            active_children++; 
        } 
    }

    // Wait for all child processes to complete using active_children count
    while (active_children > 0) {
        pause(); // Wait for a signal indicating a child process has changed state
    }

    freePipesAndPids(argc - 1); // Cleanup after all children have completed
    printf("All child processes have completed.\n");
    return 0;
}