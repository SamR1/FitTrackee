/* eslint-env node */
require('@rushstack/eslint-patch/modern-module-resolution')

module.exports = {
  root: true,
  extends: [
    'plugin:vue/vue3-essential',
    'eslint:recommended',
    '@vue/eslint-config-typescript',
    '@vue/eslint-config-prettier/skip-formatting',
    'plugin:import/recommended',
    'plugin:import/typescript',
  ],
  parserOptions: {
    ecmaVersion: 'latest',
  },
  settings: {
    'import/resolver': {
      typescript: {
        alwaysTryTypes: true,
        project: 'tsconfig.json',
      },
    },
  },
  rules: {
    'import/no-named-as-default': 0,
    'import/no-unresolved': ['off', { ignore: ['^@/'] }],
    'import/order': [
      'error',
      {
        'newlines-between': 'always',
        alphabetize: {
          order: 'asc',
          caseInsensitive: true,
        },
      },
    ],
    'no-console': ['warn', { allow: ['error'] }],
    'vue/component-name-in-template-casing': ['error', 'PascalCase'],
    'vue/define-props-declaration': ['error', 'type-based'],
    'vue/multi-word-component-names': 'off',
    'vue/no-required-prop-with-default': 'error',
    '@typescript-eslint/array-type': 'error',
    '@typescript-eslint/no-unused-vars': 'error',
  },
}
