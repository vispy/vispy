var vispy_jupyter = require('./index');
var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'vispy_jupyter',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'vispy_jupyter',
          version: vispy_jupyter.version,
          exports: vispy_jupyter
      });
  },
  autoStart: true
};