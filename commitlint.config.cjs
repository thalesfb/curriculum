module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'header-max-length': [2, 'always', 150],
    'type-enum': [2, 'always', ['feat','fix','security','config','docs','style','refactor','perf','test','build','ci','chore','revert','hotfix','raw','cleanup','remove']],
    'header-pattern': [2, 'always', '^(:[a-z_\\+\\-]+:)\\s*(feat|fix|security|config|docs|style|refactor|perf|test|build|ci|chore|revert|hotfix|raw|cleanup|remove)(?:\\([^)]+\\))?:\\s.+$']
  },
  ignores: [commit => commit.startsWith('Merge ') || commit.startsWith('Bump ')]
}
