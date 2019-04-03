var vispy = require('./index');
var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'vispy',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'vispy',
          version: vispy.version,
          exports: vispy
      });
  },
  autoStart: true
};