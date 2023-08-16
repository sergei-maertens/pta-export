const gulp = require('gulp');
const {scss} = require('./scss');

gulp.task('default', scss);
exports.default = scss;
