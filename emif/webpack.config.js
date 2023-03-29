var path = require('path');
var BundleTracker = require('webpack-bundle-tracker');


module.exports = {
    mode: 'development',
    devtool: 'inline-source-map',

    context: __dirname,
    entry: './packs/main.js',
    output: {
        path: path.resolve('./webpack_bundles/'),
        filename: '[name]-[hash].js',
    },
    resolve: {
        modules: ['node_modules', '.'],
    },

    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
    ],

    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env'],
                        plugins: ['@babel/plugin-proposal-class-properties'],
                    }
                }
            },
            { test: /\.handlebars$/, loader: "handlebars-loader" }
        ]
    }
};
