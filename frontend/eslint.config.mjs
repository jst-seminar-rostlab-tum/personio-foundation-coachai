import { dirname } from 'path';
import { fileURLToPath } from 'url';
import { FlatCompat } from '@eslint/eslintrc';
import tsParser from '@typescript-eslint/parser';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  {
    ignores: [
      '**/node_modules/**',
      '**/.next/**',
      'eslint.config.mjs',
      'jest.setup.ts',
      'package.json',
      'postcss.config.mjs',
      '**/coverage/**',
    ],
  },
  ...compat.extends(
    'airbnb-base',
    'plugin:@typescript-eslint/recommended',
    'plugin:prettier/recommended',
    'next/core-web-vitals',
    'next/typescript'
  ),
  {
    files: ['**/*.{js,cjs,mjs,ts,tsx,jsx}'],
    rules: {
      'prettier/prettier': 'error',
      'no-use-before-define': 'off',
      '@typescript-eslint/no-use-before-define': 'off',
      'import/extensions': 'off',
      'no-underscore-dangle': 'off',
      'import/prefer-default-export': 'off',
      'no-restricted-syntax': [
        'error',
        {
          selector: "CallExpression[callee.object.name='console'][callee.property.name='log']",
          message: 'Unexpected console.log. Use console.warn or console.error instead.',
        },
      ],
      'no-console': 'off',
    },
  },
  {
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        project: './tsconfig.json',
        tsconfigRootDir: __dirname,
        sourceType: 'module',
      },
    },
    rules: {}, // Add any TypeScript-specific rules here
  },
];

export default eslintConfig;
