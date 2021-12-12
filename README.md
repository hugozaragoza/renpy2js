# renpy2js

Experimental engine to render renpy stories in HTML with pure JavaScript

Hugo Ballester 2021

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