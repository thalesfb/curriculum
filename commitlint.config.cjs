module.exports = {
  extends: ['@commitlint/config-conventional'],
  parserPreset: {
    parserOpts: {
      headerPattern: /^(:[a-z_]+:)?\s*(feat|fix|security|config|docs|style|refactor|perf|test|build|ci|chore|revert|hotfix|raw|cleanup|remove)(?:\(([\w\s*\-]+)\))?:?\s*(.*)$/,
      headerCorrespondence: ['emoji', 'type', 'scope', 'subject']
    }
  },
  rules: {
    'header-max-length': [2, 'always', 150],
    'type-enum': [2, 'always', ['feat','fix','security','config','docs','style','refactor','perf','test','build','ci','chore','revert','hotfix','raw','cleanup','remove']]
  },
  ignores: [commit => commit.startsWith('Merge ') || commit.startsWith('Bump ')]
}
