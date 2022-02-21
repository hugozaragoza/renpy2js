# renpy2js

Engine to convert renpy script (interactive stories) into JavaScript HTML interactive experience.

(Python Django is used only for cetralised logging server and for deployment, the story experience runs in pure client JavaScript).

Hugo Ballester 2021

## Overview

python main.py --help

Data flow:
  * CodeDirectory is where this project is. 
  * StoryDirectory is where the story script (script.rpy) and the images (img/) are.
  * OutDirectory is where the story web will be created, under directory StoryName.
  * CodeDirectory/main.py reads the StoryDirectory and creates the OutDirectory/StoryName containing the story website:
    * script.js : story generated
    * renpy2js.js : display library
    * index.html : web interaction and story loading
    * style.css
    * styles.html : debugging styles
    * img/: (copy of StoryDirectory/img)
  * it also copies the logger app to OutDirectory/logger


## Renpy Compatibility
### Labels:

PARTIALLY IMPLEMENTED:
All labels must end with a jump command or a menu. To end the story, jump to "__END"

Special labels:

* start: starts the story
* __END: ends the story
* jump __none : is ignored and it is needed to close blocks wich jump with IF statements

### IF:

PARTIALLY IMPLEMENTED:
For now all you can do is:
if EXP:
say_block (mist end with jump)
else:
say_block (mist end with jump)

### Code lines

Only define character and variable assignment are allowed. Undefined variables default to 0

```
define I = Character('You',image='you')

$ VAR_NAME [+-*/]= NUM
$ VAR_NAME = VAR_NAME2
```

## TODO:

conditional menus:
"Hot Springs, AR" (300) if secret_unlocked:
        jump hot_springs_trip