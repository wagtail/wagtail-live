const path = require("path");
const webpack = require("webpack");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CopyPlugin = require("copy-webpack-plugin");

module.exports = {
  devtool: "source-map",
  entry: {
    main: path.resolve(__dirname, "src/wagtail_live/webapp_tmp/static_src/js/main.js"),
  },
  output: {
    path: path.resolve(__dirname, "src/wagtail_live/webapp_tmp/static/webapp"),
    publicPath: "",
    filename: "[name].js",
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: ["babel-loader"],
      },
      {
        test: /\.(s?)css$/,
        use: [MiniCssExtractPlugin.loader, "css-loader", "sass-loader"],
      },
      // {
      //   test: /\.(eot|ttf|woff|woff2|svg)$/,
      //   use: {
      //     loader: "file-loader",
      //     options: {
      //       name: "assets/[name].[ext]",
      //     },
      //   },
      // },
    ],
  },
  optimization: {
    splitChunks: {
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: "vendor",
          chunks: "all",
        },
      },
    },
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: "[name].css",
    }),
    // new CopyPlugin({
    //   // Copy files without processing by webpack.
    //   patterns: [
    //     {
    //       from: path.resolve(__dirname, "node_modules/jquery/dist/jquery.min.js"),
    //       to: path.resolve(
    //         __dirname,
    //         "sphinx_wagtail_theme/static/dist/jquery.min.js"
    //       ),
    //     },
    //   ],
    // }),
    new webpack.ProvidePlugin({}),
  ],
};
