'use strict';
var gulp = require('gulp');
var gulpif = require('gulp-if');
var Eyeglass = require('eyeglass');
var postcss = require('gulp-postcss');
var sourcemaps = require('gulp-sourcemaps');
var sass = require('gulp-sass');
var autoprefixer = require('autoprefixer');
var cssnano = require('cssnano');
var argv = require('yargs').argv;
var paths = require('../paths');


var isProduction = argv.production ? true : false;
var sourcemap = argv.sourcemap ? true : false;

var eyeglass = new Eyeglass({
    outputStyle: isProduction ? 'compressed' : 'expanded',
});

var plugins = isProduction ? [cssnano(), autoprefixer()] : [autoprefixer()];


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
    return gulp.src(paths.sassSrc)
        .pipe(gulpif(sourcemap, sourcemaps.init()))
        .pipe(sass(eyeglass.options).on("error", sass.logError))
        .pipe(postcss(plugins))
        .pipe(gulpif(sourcemap, sourcemaps.write('./')))
        .pipe(gulp.dest(paths.cssDir));
}


gulp.task('sass', scss);
gulp.task('scss', scss);
exports.scss = scss;
exports.scss = scss;
