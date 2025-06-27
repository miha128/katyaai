# KatyaAI is a (very) multipurpose discord bot with text functions, LLM functions and downloading functions, supporting custom and modular app commands (Apps soon :3).

### Getting started with Katya

##### Requirements:

Discord bot (and the required token)

Python runtime and dependencies (module specific booo jumpscare)

#### Scroll past this if you already have a bot token

To get a bot token, one must go to the [discord developer portal](https://discord.com/developers/applications) and create a new application.
![Screenshot 2025-06-27 213437](https://github.com/user-attachments/assets/ccbc45b2-ed67-47f4-a5ef-786d4fa1aff2)

One must go to the application's Bot property and obtain a token by resetting it, it will ask for your password, then copy and paste it in config.yaml with the quotes present.

![Screenshot 2025-06-27 213456](https://github.com/user-attachments/assets/8c80e63f-bb92-4162-a341-d95feba137b3)
![Screenshot 2025-06-27 213514](https://github.com/user-attachments/assets/791c6526-d0ca-4af9-a81f-dbc56144c9cf)
![Screenshot 2025-06-27 213527](https://github.com/user-attachments/assets/31705d29-acc4-4764-b1aa-6b5e5a383243)
### Modules and their dependencies

Although it's possible to only run Katya using only discord.py, it's both impractical and limited, since you can't really do anything with pure python aside from string functions, and reading files...

#### Base KatyaAI (eye, fullwidth, italicize, restart, administration)

`pip install discord yaml` is all you need, yaml can be omitted if you store the config in a file instead of loading from config.yaml but whatever.

### Specific commands

The `ask` command requires `openai`. that's literally it. type `pip install openai` to install it. 

The `download` command requires both `yt-dlp` ==and ffmpeg.exe to be in the tools folder.== It's possible to also port this command to an UNIX system if you really want to, since Katya is modular.. and also should run on NT based systems since that's what the server uses

The `preview` command requires `selenium`  and [geckodriver.exe](https://github.com/mozilla/geckodriver/releases) to be in your PATH (quick fix, just move it in C:\Windows\System32), and a custom Firefox profile in the config for security reasons.

The `info` command is the most dependency-heavy one. It requires  `psutil`, `shutil`, `cpuinfo` and `pynvml`, though all can be disabled if you edit the code. 

### One size fits all command to install dependencies (ffmpeg and geckodriver ~~sold separately~~)

`pip install openai yt-dlp selenium psutil shutil cpuinfo pynvml discord` 

