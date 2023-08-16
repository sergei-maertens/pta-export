const gulp = require('gulp');
const {scss} = require('./scss');

gulp.task('build', scss);
exports.build = scss;
