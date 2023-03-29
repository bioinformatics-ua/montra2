# New Asset Handling System

This file describes how you're supposed to setup and develop the static assets
used throughout the application. Old code has no such system and it will be
gradually ported to the new one.

## Requirements

 * Node.js

## Setup

In the application directory run:

``` bash
# This will install all required dependencies including the ones only required
# for development.
$ npm install

# This will watch all your static assets and recompile them as needed.
# Alternatively, you can run `npm build` for a single compilation.
$ npm run watch
```

## Development

Each file in the `packs/` directory corresponds to a single bundle. Currently we
only support one but this can change. This bundle file is required to reference
all other files you wish to include in the bundle.

The suggested organization for each app is:

```
app/
    assets/
        controllers/
            fancy_controller.js
            other_controller.js
            index.js
        utils/
            dom_helper.js
            index.js
        index.js
    templates/
    models.py
    views.py
    ...
```

Each `index.js` should, much like the bundle file, reference all modules it
needs to execute or reexport.

## Stimulus

Stimulus' controllers require some setup to function propertly. So, in each
app's `controller/index.js` make sure you include the following code:

``` javascript
import { Application } from "stimulus";
import { definitionsFromContext } from "stimulus/webpack-helpers";

const application = Application.start();
const context = require.context("controllers", true, /_controller\.js$/);
application.load(definitionsFromContext(context));
```

## Helpful Links

 * [JavaScript Modules](http://exploringjs.com/es6/ch_modules.html)
