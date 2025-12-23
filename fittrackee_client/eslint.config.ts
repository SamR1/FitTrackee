import pluginVitest from '@vitest/eslint-plugin'
// @ts-expect-error  @typescript-eslint/ban-ts-comment
import skipFormatting from '@vue/eslint-config-prettier/skip-formatting'
import {
  defineConfigWithVueTs,
  vueTsConfigs,
} from '@vue/eslint-config-typescript'
import { globalIgnores } from 'eslint/config'
// @ts-expect-error  @typescript-eslint/ban-ts-comment
import importPlugin from 'eslint-plugin-import'
import pluginOxlint from 'eslint-plugin-oxlint'
// @ts-expect-error  @typescript-eslint/ban-ts-comment
import pluginVue from 'eslint-plugin-vue'

// To allow more languages other than `ts` in `.vue` files, uncomment the following lines:
// import { configureVueProject } from '@vue/eslint-config-typescript'
// configureVueProject({ scriptLangs: ['ts', 'tsx'] })
// More info at https://github.com/vuejs/eslint-config-typescript/#advanced-setup

export default defineConfigWithVueTs(
  {
    name: 'app/files-to-lint',
    files: ['**/*.{ts,mts,tsx,vue}'],
  },

  globalIgnores(['**/dist/**', '**/dist-ssr/**', '**/coverage/**']),

  pluginVue.configs['flat/essential'],
  vueTsConfigs.recommended,

  {
    ...pluginVitest.configs.recommended,
    files: ['src/**/__tests__/*'],
  },
  ...pluginOxlint.configs['flat/recommended'],
  skipFormatting,

  {
    name: 'app/misc',
    rules: {
      'no-console': ['warn', { allow: ['error'] }],
    },
  },

  {
    name: 'app/vuejs',
    rules: {
      'vue/component-name-in-template-casing': ['error', 'PascalCase'],
      'vue/define-props-declaration': ['error', 'type-based'],
      'vue/multi-word-component-names': 'off',
      'vue/no-required-prop-with-default': 'error',
    },
  },

  {
    name: 'app/typescript',
    rules: {
      '@typescript-eslint/array-type': 'error',
      '@typescript-eslint/no-unused-vars': 'error',
    },
  },

  {
    name: 'app/imports',
    plugins: {
      import: importPlugin,
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
    },
    settings: {
      'import/parsers': {
        '@typescript-eslint/parser': ['.ts', '.tsx', '.vue'],
      },
      'import/resolver': {
        typescript: {
          alwaysTryTypes: true,
          project: 'tsconfig.json',
        },
      },
    },
  }
)
