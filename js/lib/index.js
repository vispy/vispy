// Entry point for the notebook bundle containing custom model definitions.
//
// Setup notebook base URL
//
// Some static assets may be required by the custom widget javascript. The base
// url for the notebook is not known at build time and is therefore computed
// dynamically.

// Export widget models and views, and the npm package version number.
// module.exports.VispyView = require('./webgl-backend.js').VispyView;
// module.exports.VispyModel = require('./webgl-backend.js').VispyModel;
module.exports = require('./webgl-backend.js');
module.exports['version'] = require('../package.json').version;
