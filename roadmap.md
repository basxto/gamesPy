# Roadmap

## 0.1
* [x] Detect running game with unique name
* [x] Detect running game with non-unique name and unique argument
* [x] Notify user about detected game

## 0.2
* [x] Print played time
* [x] Represent games and sessions with classes
* [x] Store and accumulate played time temporarily

## 0.3
* [x] Read monitoring data of [Game Backup Monitor](https://github.com/MikeMaximus/gbm) SQLite database
* [x] Configuration file in correct XDG user directory
* [x] Accept command line arguments

## 0.4
* [x] Store detailed playing time in custom table (start/end)
* [x] Store playing time in [Game Backup Monitor](https://github.com/MikeMaximus/gbm) SQLite database
* ~~[ ] Also store there the last time a game got played~~ This option never existed

## 0.5
* [x] Download and import [Game Backup Monitor](https://github.com/MikeMaximus/gbm) XML file
* [x] Detect ~~duplicate~~ ambiguous game entries with RegEx support
* [x] Distinguish ~~duplicate~~ ambiguous game entries by full path ~~and user choice~~
* [x] Allow to run command when game start got detected
* [x] Allow to run command when game got closed
* [x] Example systemd service file

## 0.6
* [ ] Allow clients to request informations
  * [ ] Current running game
  * [x] Accumulated time a game was running
  * [x] Last time a game got played
  * [x] List all sessions of a game
  * [x] Sorted list of all games
* [x] Implement primitive cli client

## 0.7
* [ ] Export games as XML
* [ ] Improve communicability of games (at example FTL: Faster Than Light)
  * [ ] Steam ID (212680)
  * [ ] Amazon ID (B00D7GNPO2)
  * [ ] Lutris handle (ftl-faster-than-light)
  * [ ] Humble bundle handle (ftl-faster-than-light)
  * [ ] GOG handle (faster_than_light)
  * [ ] pcgamingwiki handle (FTL:_Faster_Than_Light)
  * [ ] holarse-linuxgaming handle (ftl)
* [ ] Detect game by Steam ID
 
## 0.8
* [ ] Optionally run with a tray icon
* [ ] Support for Windows and Mac

## 0.9
* [ ] Improve performance

## 1.0
* [ ] Document data format and API
* [ ] Full documented / automated build process
* [ ] Offer prepackaged executable
