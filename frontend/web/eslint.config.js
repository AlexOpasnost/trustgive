/**
 * ESLint flat config.
 *
 * This file did not exist until 2026-08-01. ESLint 9 requires a flat config and
 * refuses to run without one, so `npm run lint` — a required CI job — had failed
 * on every push since the repository was created. The job was not catching
 * anything; it was reporting "couldn't find eslint.config.js" and turning the
 * whole workflow red, which is how it came to be ignored.
 *
 * The `lint` script also passed `--ext ts,tsx`, an eslintrc-era flag that ESLint
 * 9 rejects outright. Under flat config the file set is declared here instead
 * (see `files` below), so the script is now just `eslint .`.
 *
 * Only plugins already in package.json are used, so no dependency or lockfile
 * change is needed to make CI meaningful again.
 */

import tsPlugin from "@typescript-eslint/eslint-plugin"
import tsParser from "@typescript-eslint/parser"
import reactHooks from "eslint-plugin-react-hooks"
import reactRefresh from "eslint-plugin-react-refresh"

export default [
  {
    ignores: [
      "dist/**",
      "node_modules/**",
      "coverage/**",
      // Generated from the OpenAPI schema by `npm run gen-api`; linting a
      // generated file only ever produces noise nobody can act on.
      "src/api/schema.d.ts",
    ],
  },
  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      parser: tsParser,
      ecmaVersion: "latest",
      sourceType: "module",
      parserOptions: {
        ecmaFeatures: { jsx: true },
      },
    },
    plugins: {
      "@typescript-eslint": tsPlugin,
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
    },
    rules: {
      ...tsPlugin.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,

      // Vite's fast-refresh boundary: a module that exports both a component and
      // something else loses HMR. A warning rather than an error, but CI runs
      // with --max-warnings 0, so it still has to be dealt with.
      "react-refresh/only-export-components": ["warn", { allowConstantExport: true }],

      // `any` is reported but not fatal: the API client is hand-written against
      // a schema that is generated separately, and a few boundary casts are
      // deliberate. Kept visible so the count can't grow unnoticed.
      "@typescript-eslint/no-explicit-any": "warn",

      // Underscore-prefixed arguments are the established convention here for
      // "required by the signature, deliberately unused".
      "@typescript-eslint/no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
          caughtErrorsIgnorePattern: "^_",
        },
      ],
    },
  },
  {
    // Test files may reach for `any` when building fixtures, and vitest globals
    // are injected rather than imported.
    files: ["**/*.test.{ts,tsx}", "src/test/**/*.{ts,tsx}"],
    rules: {
      "@typescript-eslint/no-explicit-any": "off",
    },
  },
]
