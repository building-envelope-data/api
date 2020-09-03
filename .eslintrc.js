"use strict";

const fs = require("fs");
const path = require("path");

const databaseSchema = fs.readFileSync(
  path.join(__dirname, "apis/database.graphql"),
  "utf8"
);

// Inspired by https://github.com/apollographql/eslint-plugin-graphql#example-config-for-literal-graphql-files
module.exports = {
  parser: "@babel/eslint-parser",
  rules: {
    "graphql/template-strings": ['error', {
      env: 'literal',
      validators: 'all',
      schemaString: databaseSchema,
    }]
  },
  plugins: [
    'graphql'
  ]
}
