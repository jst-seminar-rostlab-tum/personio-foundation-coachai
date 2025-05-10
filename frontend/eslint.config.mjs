import { dirname } from 'path';
import { fileURLToPath } from 'url';
import { FlatCompat } from '@eslint/eslintrc';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  {
    ignores: ['**/node_modules/**', '**/.next/**'],
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
    },
  },
  {
    files: ['eslint.config.mjs'],
    rules: {
      'import/no-extraneous-dependencies': 'off',
    },
  },
];

export default eslintConfig;
