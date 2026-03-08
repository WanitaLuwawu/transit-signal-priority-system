# Transit Signal Priority Simulation

A Python simulation demonstrating Transit Signal Priority (TSP) using conditional green light extension. The 
project visualizes how a delayed bus can recover schedule delay by extending green lights at signalized intersections.

The simulation compares a baseline bus (on time) and a delayed version of the same bus, illustrating how 
priority affects delay recovery.

## Project Motivation

This project was inspired by a Transportation Talk hosted by the UWaterloo Institute of Transportation Engineers 
(ITE) and presented by Joanna Kervin. The presentation discussed the increasing use of 
technology in transit projects and the importance of software skills for civil engineers.

One example mentioned was the use of Transit Signal Priority on the Eglinton Crosstown LRT. This was my 
first exposure to the concept of TSP, which motivated me to build a simulation to better understand:

- how conditional signal logic works
- how priority affects bus delay recovery

## Simulation Overview
When the program runs:
1. The map is drawn on screen
2. Two buses appear:
   * Blue bus - baseline bus with no delay
   * Orange bus - delayed version of blue bus
3. The blue bus begins moving immediately
4. The orange bus begins moving once its delay timer reaches zero

The simulation continually calculates the distance between the two buses.

As long as the delayed bus is outside the recovery zone, it is considered late. In this state, the bus may
extend green lights when approaching an intersection.

Once the delayed bus enters the recovery zone, it is no longer considered late and it stops requesting
priority.

The recovered delay time is displayed on the screen.

The key concept is that the simulation shows two states of the same bus simultaneously:
- The baseline (on-time) state
- The delayed state

This allows the effect of signal priority on delay recovery to be visualized directly.

## Example Simulation

## Example Simulation

<table>
<tr>
<td align="center">

<img src="screenshots/delayed_start.png" width="300">

*Late bus starting after the baseline bus.*

</td>

<td align="center">

<img src="screenshots/green_extension.png" width="300">

*Delayed bus requests priority and extends the green phase.*

</td>

<td align="center">

<img src="screenshots/recovery.png" width="300">

*Late bus catches up and the recovered delay is displayed.*

</td>
</tr>
</table>

## How it Works
## 1. Traffic Signal Controller

The intersection is controlled by a two-phase signal controller.

### 1.1 Phases

NS (North–South) – northbound and southbound approaches

EW (East–West) – eastbound and westbound approaches

### 1.2 Signal States

The signal cycles through two states:

GREEN → YELLOW → phase swap

During GREEN:

- The active phase is green
- The opposing phase is red

During YELLOW:

- The active phase turns yellow
- The opposing phase remains red
- The controller prepares to swap phases

## 2. Transit Signal Priority Logic

Priority is triggered when the delayed bus:

1. Is late
2. Is approaching a stopline
3. Is within the extension distance

The bus sends a priority request to the signal controller.

The signal will only extend green if:

1. the signal is already green
2. the current phase has not already been extended

This prevents repeated extensions within the same signal phase.

## 3. Bus Behaviour
The map contains a 3 × 3 grid of nodes representing the road network.

Each bus follows a predefined path consisting of nodes. The default route loops around the network.

Example path:

node 7 → node 9 → node 3 → node 1 → repeat

For each path segment, the bus:

1. Determines which stopline it is approaching
2. Reads the signal colour
3. Adjusts its speed based on distance to the stopline

### 3.1 Speed adjustment

1. Go Zone 
    * Bus travels at normal speed
2. Slow Zone 
   * Bus slows if the signal is red or yellow
3. Stop Zone
   * Bus stops if the signal is red or yellow
   
### 3.2 Stopline detection
One challenge in the simulation was ensuring buses only reacted to the correct stopline.

Initially buses would sometimes stop inside the intersection because they reacted to stoplines on the exit 
side of the intersection.

This was solved by filtering stoplines using geometric distance calculations:

1. the bus determines which stoplines lie along its current path segment
2. stoplines on other approaches are filtered out
3. only the stopline on intersection entry is considered

## Technologies Used

- Python
- Turtle Graphics

## Possible Future Improvements

- adding a user interface to modify bus routes
- comparing different types of transit signal priority
- adding additional vehicles and traffic flows

## Running the Simulation

Requirements:
- Python 3.x

From the project directory, run:
- python main.py

A Turtle graphics window will open showing the animated simulation.