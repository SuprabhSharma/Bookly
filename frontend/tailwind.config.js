export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: { extend: {
    colors: { brand: { 50: 'var(--brand-50)', 100: 'var(--brand-100)', 500: 'var(--brand-500)', 600: 'var(--brand-600)', 700: 'var(--brand-700)' }, ink: 'var(--ink)', muted: 'var(--muted)', surface: 'var(--surface)', line: 'var(--line)' },
    boxShadow: { card: '0 2px 12px rgb(15 23 42 / 0.06)', float: '0 12px 30px rgb(15 23 42 / 0.12)' },
    borderRadius: { card: '12px' }, fontFamily: { sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'] },
  } },
  plugins: [],
}
