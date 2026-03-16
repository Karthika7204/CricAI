/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "#020817",
                surface: "#0a1128",
                primary: "#00f5c4",
                secondary: "#1e293b",
                text: "#e2e8f0",
                accent: "#3b82f6",
                card: "rgba(10, 17, 40, 0.82)",
            },
            fontFamily: {
                outfit: ['Outfit', 'sans-serif'],
                inter: ['Inter', 'sans-serif'],
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                'glass': 'linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0))',
            },
            boxShadow: {
                'neon': '0 0 15px rgba(102, 252, 241, 0.3)',
            }
        },
    },
    plugins: [],
}
