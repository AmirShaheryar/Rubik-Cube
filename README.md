🧊 2×2×2 Rubik's Cube AI SolverAn interactive web application and command-line tool that solves a 2×2×2 Rubik's Pocket Cube using the A Search Algorithm* with an admissible heuristic.


🚀 FeaturesA Search Algorithm:* Guarantees the optimal (shortest) path to the solved state.Admissible Heuristic: Uses a custom tile-mismatch heuristic to guide the search efficiently.Interactive Web UI: Built with Streamlit, featuring real-time cube rendering and step-by-step playback.CLI Support: Run moves, check goal states, or solve directly from the terminal.Scramble & Play: Randomly scramble the cube and watch the AI find the solution in seconds.


🧠 How it WorksThe Search AlgorithmThe solver treats the cube as a state-space search problem. To reach the goal state (all faces uniform) from any scrambled state, it uses A Search*:$$f(n) = g(n) + h(n)$$$g(n)$: The cost (number of moves) to reach the current state.$h(n)$: The heuristic estimate. Our solver calculates the number of misplaced tiles on the faces and divides by the maximum tiles a single move can correct. This ensures the heuristic is admissible (never overestimates the cost), which guarantees optimality.Move SetThe solver supports all standard 2x2 notation moves:Clockwise: U, F, R, D, L, BCounter-Clockwise: U', F', R', D', L', B'


**Install dependencies:
**
pip install streamlit


Run the Web App:

streamlit run app.py


💻 Usage
Web Interface
Scramble: Use the "Scramble" slider and button to create a random puzzle.

Solve: Click "Solve with A*" to initiate the search.

Playback: Use the navigation buttons (Next, Prev, Auto-Play) to visualize the solution step-by-step.

Command Line Interface
You can interact with the core logic directly:

Print the cube: python RubiksCube2x2x2.py print <STATE>

Apply a move: python RubiksCube2x2x2.py move U <STATE>

Solve a state: python RubiksCube2x2x2.py solve <STATE>

State Format: A string of 24 characters representing the faces in order: White (U), Red (R), Green (G), Yellow (D), Orange (L), Blue (B).
Default: WWWWRRRRGGGGYYYYOOOOBBBB
