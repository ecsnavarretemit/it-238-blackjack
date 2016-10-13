# it-238-blackjack

[IT 238 Exercise 3](https://github.com/ecsnavarretemit/it-238-blackjack/tree/v1.1.0) - BlackJack Game with the application of Remote Method Invocation Concept using `Pyro4`

IT 238 Exercise 4 - Multiplayer Blackjack Game. Up to 4 players!

## Installation of Requirements

### All Operating Systems

1. Python 3.5.2 or greater is required!

### Ubuntu

1. Install Pip: `sudo apt-get install python3-pip`
2. Install VirtualENV: `sudo apt-get install python3-virtualenv`
3. Install Image and Tk Libraries:

	```
	sudo apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk
	```

4. Install Python 3 Development and Setuptools:

	`sudo apt-get install python3-dev python3-setuptools`

### OS X

1. Install via Homebrew:

	`brew install libtiff libjpeg libpng webp little-cms2`

## Running

1. Setup `virtualenv` for the project: `pyvenv venv`. Make sure this is executed inside the project root folder.
2. Activate `virtualenv` by running: `source venv/bin/activate`
3. Install application requirements via:`pip install -r requirements.txt`. This will install all required dependencies of the game.
4. Run the game server by running the command: `python server.py`
5. Run the game by running the command: `python game.py`


