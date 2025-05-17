module.exports = {
  extends: ['@commitlint/config-conventional'],
  parserPreset: {
    parserOpts: {
      headerPattern: /^(\w+)(?:\((\d{1,4})\))?:\s(.*)$/,
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
    'scope-empty': [1, 'never'],
    'subject-empty': [2, 'never'],
    'subject-case': [1, 'always', ['sentence-case', 'lower-case']],
  },
  ignores: [
    (message) => {
      return message.includes('hotfix') || message.includes('chore');
    },
  ],
};
