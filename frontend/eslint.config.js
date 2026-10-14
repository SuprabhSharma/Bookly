import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'

export default [{
  ignores: ['dist/**', 'node_modules/**'],
  files: ['**/*.{js,jsx}'],
  languageOptions: {
    ecmaVersion: 'latest', sourceType: 'module', parserOptions: { ecmaFeatures: { jsx: true } },
    globals: { window: 'readonly', document: 'readonly', localStorage: 'readonly', console: 'readonly', URLSearchParams: 'readonly', Intl: 'readonly', setTimeout: 'readonly', clearTimeout: 'readonly' },
  },
  plugins: { 'react-hooks': reactHooks, 'react-refresh': reactRefresh },
  rules: {
    // JSX identifiers are intentionally ignored here; the repo uses React's automatic JSX runtime.
    'no-unused-vars': 'off',
    'react-refresh/only-export-components': 'warn', 'react-hooks/rules-of-hooks': 'error', 'react-hooks/exhaustive-deps': 'warn',
  },
}]
