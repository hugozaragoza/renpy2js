PHP CodeIgniter mini server app to log user actions and errors to improve stories.

It only has a single controller without views: Controllers/Logger.php

Make API calls to .../Logger/log/USER/MESSAGE to log a message to public/actions.log

You can try it locally with: php spark serve
