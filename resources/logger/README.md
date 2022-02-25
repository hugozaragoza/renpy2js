PHP CodeIgniter mini server app to log user actions and errors to improve stories.

It only has a single controller without views: Controllers/Logger.php

Make API calls to :

`logger/public/index.php/logger` : view log
`logger/public/index.php/logger/log/STORY_NAME/USER_NAME/MESSAGE` : write log

Log in the server goes to logger/public/actions.log

You can try start a local server with: `php spark serve`
