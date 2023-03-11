const path = require('path');

module.exports = {
  mode: 'development',
  entry: './src/index.js',
  output: {
    filename: 'bundle.js',
    path: path.join(__dirname, 'static'),
  },
  module: { rules: [
    {
      test: /\.js$/,
      include: [
        path.resolve(__dirname, 'src')
      ],
      use: ['babel-loader'],
    },
    {
      test: /\.s[ac]ss$/i,
      use: [
        "style-loader",
        "css-loader",
        "sass-loader",
      ],
    },
    {
        test: /\.(css)$/,
        use: ['style-loader','css-loader']
    },
    {
        test: /\.(jpe?g|png|gif|svg)$/i, 
        use: 'file-loader?name=[name].[ext]',
        include: [
            path.join(__dirname, 'static')
        ],
        // loader: 'file-loader',
        // options: {
        //   name: '/img/[name].[ext]'
        // }
    }
  ]},
};