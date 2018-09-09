## 0.5
* Accept XML format of GBM 1.1.4
* Allow to run commands when game got started or closed
* Offer systemd service file
* Download and import [Game Backup Monitor](https://github.com/MikeMaximus/gbm) XML file
* Distinguish ambiguous game entries by full path
* Store ambiguous sessions for later clarification
## 0.4
* Store and get sessions from database
* Store played time in hours in database
## 0.3
* Config file that follows XDG standard
* Read game list from database
* Command line arguments
## 0.2
* Represent games and sessions with classes
* Store and accumulate played time temporarily
* Print played time
## 0.1
* Detect games flexibly with process names allowing regex
* Ignore standard binary extensions in process names
* Detect games by argument if not unambiguous otherwise, also with regex
* Notify user when detected game gets started or closed
