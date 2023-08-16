'use strict';
var gulp = require('gulp');
var sourcemaps = require('gulp-sourcemaps');
var sass = require('gulp-sass')(require('sass'));
var paths = require('../paths');


/**
 * scss task
 * Run using "gulp scss"
 * Searches for sass files in paths.sassSrc
 * Compiles sass to css
 * Auto prefixes css
 * Optimizes css when used with --production
 * Writes css to paths.cssDir
 */
function scss() {
    return gulp
        .src(paths.sassSrc)
        .pipe(sourcemaps.init())
        .pipe(
            sass({outputStyle: 'compressed'})
            .on("error", sass.logError)
        )
        .pipe(sourcemaps.write('./'))
        .pipe(gulp.dest(paths.cssDir));
}


gulp.task('scss', scss);
exports.scss = scss;
