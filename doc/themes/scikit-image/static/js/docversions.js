var versions = ['latest', 'v0.1.0'];

function insert_version_links() {
    for (i = 0; i < versions.length; i++){
        open_list = '<li>'
        if (typeof(DOCUMENTATION_OPTIONS) !== 'undefined') {
            if ((DOCUMENTATION_OPTIONS['VERSION'] == versions[i]) ||
                (DOCUMENTATION_OPTIONS['VERSION'].match(/dev$/) && (i == 0))) {
                open_list = '<li id="current">'
            }
        }
        document.write(open_list);
        document.write('<a href="URL">vispy VERSION</a> </li>\n'
                        .replace('VERSION', versions[i])
                        .replace('URL', 'http://api.vispy.org/en/' + versions[i]));
    }
}

function stable_version() {
    return versions[1];
}
