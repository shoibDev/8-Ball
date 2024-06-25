
# 8-Ball

This project, 8-Ball, showcases a sophisticated physics engine for simulating realistic movements, collisions, and interactions of billiard balls on a pool table. Built with C, Python, SQL, and JavaScript, it integrates a custom server and dynamic visual representations using SVGs.



## Features
- **Physics Engine:** Developed in C, the engine performs detailed calculations to simulate accurate ball dynamics.
- **Server Integration:** Utilizes Python to handle communication between the C-based physics engine and the web interface, facilitated by SWIG.
- **Dynamic Visuals:** Custom SVG graphics to represent the game state dynamically, showing ball positions and movements in real-time.
## Technologies
- **C:** For physics calculations and game logic.
- **Python:** Server-side logic, interfacing with the C backend.
- **SQL:** Database interactions for storing game states and player data.
- **JavaScript:** Frontend interactions and displaying SVGs dynamically.
- **SWIG:** Used to interface C components with Python.

## Visuals
(Low FPF due to it being a gif, will run MUCH smoother when playing)
![chrome-capture-2024-6-24 (1)](https://github.com/shoibDev/8-Ball/assets/86535871/46392146-413b-4c93-a8de-c3d4f33a8320)


## Installation

This project runs inside a Docker container to ensure a consistent development environment. Follow these steps to get started:

1. **Pull the Docker Image**
Start by pulling the Docker image from Docker Hub:
```bash
    docker pull socsguelph/socslinux
```

2. **Clone the Repository**
Clone the project repository to your local machine:
```bash
    git clone https://github.com/shoibDev/8-Ball.git
    cd 8-ball
```

3. **Run the Docker Container**
Launch the Docker container, mounting the current project directory to a directory inside the container:
```bash
    docker run -it --name 8-ball-env -v "$(pwd):/8-ball" socsguelph/socslinux
```
This command starts an interactive terminal inside the container and mounts the project directory to /8-ball.

4. **Compile the Project**
Inside the container, navigate to the mounted directory and compile the project:
```bash
    cd /8-ball
    make
```

5. **Start the Server**
Run the Python server within the Docker environment:
```bash
    export LD_LIBRARY_PATH=`pwd`
    python server.py
```

6. **Gameplay**
You can now play 8-ball in your brower and going to localhost:3000
