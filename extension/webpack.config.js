const path = require('path');
const CopyPlugin = require('copy-webpack-plugin');
const HtmlPlugin = require('html-webpack-plugin');

module.exports = {
  mode: "development",
  devtool: 'cheap-module-source-map',
  entry: {
    background: path.resolve('src/background/index.ts'),
    content: path.resolve('src/content/index.ts'),
    popup: path.resolve('src/popup/index.tsx'),
    sidebar: path.resolve('src/sidebar/index.tsx'),
    options: path.resolve('src/options/index.tsx'),
  },
  module: {
    rules: [
      {
        use: 'ts-loader',
        test: /\.tsx?$/,
        exclude: /node_modules/,
      },
      {
        use: ['style-loader', 'css-loader'],
        test: /\.css$/i,
      },
      {
        test: /\.(png|jpg|jpeg|gif|svg)$/i,
        type: 'asset/resource',
      },
    ]
  },
  plugins: [
    new CopyPlugin({
      patterns: [
        { 
          from: path.resolve('public'), 
          to: path.resolve('dist'),
        }
      ]
    }),
    new HtmlPlugin({
      title: 'Luna Sidebar',
      filename: 'sidebar.html',
      chunks: ['sidebar']
    }),
    new HtmlPlugin({
      title: 'Luna Popup',
      filename: 'popup.html',
      chunks: ['popup']
    }),
    new HtmlPlugin({
      title: 'Luna Options',
      filename: 'options.html',
      chunks: ['options']
    })
  ],
  resolve: {
    extensions: ['.tsx', '.ts', '.js'],
    alias: {
      '@': path.resolve('src'),
    }
  },
  output: {
    filename: '[name].js',
    path: path.resolve('dist'),
    clean: true, 
  },
  optimization: {
    splitChunks: {
      chunks: (chunk) => chunk.name !== 'content' && chunk.name !== 'background',
      name: 'vendor', 
    },
  },
};