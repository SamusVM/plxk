let path = require('path');
let BundleTracker = require('webpack-bundle-tracker');
const {CleanWebpackPlugin} = require('clean-webpack-plugin');
let pathsToClean = ['./static/bundles/*.*'];
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
// const isProduction = process.env.NODE_ENV === 'production';

module.exports = {
  context: __dirname,
  entry: {
    boards: './static/index/boards.js',
    docs: './static/index/docs.js',
    edms: './static/index/edms.js',
    correspondence: './static/index/correspondence.js',
  },
  output: {
    path: path.resolve(__dirname, './static/bundles/'),
    filename: '[name]-[hash].js'
    // chunkFilename: '[name].bundle.js',
  },

  plugins: [
    new CleanWebpackPlugin({cleanAfterEveryBuildPatterns: pathsToClean}),
    new BundleTracker({filename: './webpack-stats.json'}),
    // new BundleAnalyzerPlugin()
  ],

  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        loader: 'babel-loader'
      }, // to transform JSX into JS
      {
        test: /\.css$/,
        include: /node_modules/,
        use: [
          {loader: 'style-loader'},
          {loader: 'css-loader'},
        ],
      },
      {test: /\.css$/, exclude: /node_modules/, loader: 'style-loader!css-loader'},
      {
        test: /\.(woff|woff2|ttf|eot|svg)(\?v=[a-z0-9]\.[a-z0-9]\.[a-z0-9])?$/,
        loader: 'url-loader?limit=100000'
      },
      // {
      //   test: /\.(?:png|jpe?g|svg)$/,
      //   loader: 'url-loader'
      // }
      {
        test: /\.(jpe?g|png|gif|svg)$/i,
        use: [
          {
            loader: 'file-loader'
          }
        ]
      }
    ]
  },

  resolve: {
    modules: [
      'node_modules',
      path.resolve(__dirname, 'static'),
      path.resolve(__dirname, 'templates'),
      path.resolve(__dirname, 'plxk'),
    ],
    extensions: ['.js', '.jsx', '.json'],
    alias: {
      static: path.resolve(__dirname, 'static'),
      templates: path.resolve(__dirname, 'templates'),
      edms: path.resolve(__dirname, 'edms'),
      docs: path.resolve(__dirname, 'docs'),
      plxk: path.resolve(__dirname, 'plxk'),
      correspondence: path.resolve(__dirname, 'correspondence'),
      boards: path.resolve(__dirname, 'boards'),
    }
  }
};
