const names = require("all-the-package-names");
const fs = require('fs');
var json_names = JSON.stringify(names);
fs.writeFile("names.json", json_names, 'utf8', function(){});
