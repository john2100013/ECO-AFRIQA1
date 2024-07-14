module.exports = {
  purge: [
    './src/**/*.{js,jsx,ts,tsx}', // Include all your React components
    './public/index.html', // Include your index.html
  ],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {},
  },
  variants: {
    extend: {},
  },
  plugins: [],
  corePlugins: {
    preflight: false, // Disable Tailwind's preflight reset
  },
};
