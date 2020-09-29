var uglify = require('gulp-uglify'),
    gulp = require('gulp'),
    concat = require('gulp-concat'),
    ngTemplates = require('gulp-ng-templates');


// gulp.task('build-js-packages', function() {
//     gulp
//         .src([
//             './assets/bower_components/angular/angular.min.js',
//             './assets/bower_components/angular-i18n/angular-locale_ru-ru.js',
//             './assets/bower_components/angular-sanitize/angular-sanitize.min.js',
//             './assets/bower_components/angular-ui-router/release/angular-ui-router.js',
//             './assets/bower_components/angular-ui-tinymce/dist/tinymce.min.js'
//         ])
//         .pipe(concat('packages.js'))
//         .pipe(gulp.dest('./src/dashboard/static/assets/app/'));
// });

gulp.task('build-app', function() {
    gulp
        .src([
            './assets/js/app.js',
            './assets/js/factory.js',
            './assets/js/controllers.js'
        ])
        .pipe(concat('app.js'))
        // .pipe(uglify())
        .pipe(gulp.dest('./assets/dist/'));

    gulp
        .src([
            './assets/libs/angular.min.js',
            './assets/libs/angucomplete.js',
            './assets/libs/angular-translate.js',
            './assets/libs/modal.min.js'
        ])
        .pipe(concat('libs.js'))
        // .pipe(uglify())
        .pipe(gulp.dest('./assets/dist/'));

    gulp
        .src([
            './assets/templates/*.html'
        ])
        .pipe(ngTemplates({
            filename: 'templates.js',
            header: 'app.run(["$templateCache", function($templateCache) {'
        }))
        .pipe(gulp.dest('./assets/dist/'));
    gulp
        .src([
            './assets/dist/libs.js',
            './assets/dist/app.js',
            './assets/dist/templates.js'
        ])
        .pipe(concat('app.js'))
        .pipe(gulp.dest('./pizza/core/static/app/'));

});

gulp.task('watch', function() {
    gulp.watch([
        './assets/js/*.js',
        './assets/templates/*.html'
    ], function () {
        gulp.run('build-app');
    });
});

gulp.task('default', [
    'watch',
    // 'build-js-packages',
    'build-app'
]);
