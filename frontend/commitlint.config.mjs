const Configuration = {
  extends: ['@commitlint/config-conventional'],
  parserPreset: {
    parserOpts: {
      headerPattern: /^(\w+)\((F-\d{1,4}|B-\d{1,4}|M)\):\s(.*)$/,
      headerCorrespondence: ['type', 'scope', 'subject'],
      issuePrefixes: [],
    },
  },
  formatter: '@commitlint/format',
  rules: {
    'type-enum': [
      2,
      'always',
      ['feat', 'fix', 'docs', 'style', 'refactor', 'test', 'revert', 'ci'],
    ],
    'scope-empty': [2, 'never'],
    'subject-empty': [2, 'never'],
    'subject-case': [1, 'always', ['sentence-case', 'lower-case']],
  },
  ignores: [
    (message) => {
      return message.includes('hotfix') || message.includes('chore') || message.includes('Merge');
    },
  ],
};

export default Configuration;
